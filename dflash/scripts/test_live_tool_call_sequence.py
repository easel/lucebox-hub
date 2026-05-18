"""Live-server regression repro for stale tool-call sequencing.

Run explicitly against a lucebox HTTP server:

    LUCEBOX_TEST_URL=http://127.0.0.1:1236 uv run --extra dev pytest \
      dflash/scripts/test_live_tool_call_sequence.py -q

The test is skipped by default because it requires a running Qwen3.6 lucebox
server. It captures the observed failure mode where a later forced tool call
returns an earlier tool-call transcript as prose instead of emitting the
requested tool.
"""

from __future__ import annotations

import json
import os
import urllib.request

import pytest


TOOLS = {
    "read_file": {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a UTF-8 text file.",
            "parameters": {
                "type": "object",
                "properties": {"path": {"type": "string"}},
                "required": ["path"],
            },
        },
    },
    "grep": {
        "type": "function",
        "function": {
            "name": "grep",
            "description": "Search files for a literal pattern.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {"type": "string"},
                    "path": {"type": "string"},
                },
                "required": ["pattern", "path"],
            },
        },
    },
    "shell": {
        "type": "function",
        "function": {
            "name": "shell",
            "description": "Run a read-only shell command.",
            "parameters": {
                "type": "object",
                "properties": {"cmd": {"type": "string"}},
                "required": ["cmd"],
            },
        },
    },
}


PROMPTS = {
    "read_file": (
        "Produce exactly this tool call and no prose:\n"
        "<tool_call>\n"
        "<function=read_file>\n"
        "<parameter=path>\n"
        "runtime-props-gap-analysis.md\n"
        "</parameter>\n"
        "</function>\n"
        "</tool_call>"
    ),
    "grep": (
        "Produce exactly this tool call and no prose:\n"
        "<tool_call>\n"
        "<function=grep>\n"
        "<parameter=pattern>\n"
        "tool_replay\n"
        "</parameter>\n"
        "<parameter=path>\n"
        ".\n"
        "</parameter>\n"
        "</function>\n"
        "</tool_call>"
    ),
    "shell": (
        "Produce exactly this tool call and no prose:\n"
        "<tool_call>\n"
        "<function=shell>\n"
        "<parameter=cmd>\n"
        "git status --short\n"
        "</parameter>\n"
        "</function>\n"
        "</tool_call>"
    ),
}


def post_forced_tool(url: str, name: str) -> dict:
    body = json.dumps({
        "model": "luce-dflash",
        "messages": [{"role": "user", "content": PROMPTS[name] + " Do not answer in prose."}],
        "tools": [TOOLS[name]],
        "tool_choice": {"type": "function", "function": {"name": name}},
        "temperature": 0,
        "max_tokens": 160,
        "stream": False,
        "chat_template_kwargs": {"enable_thinking": True},
    }).encode()
    req = urllib.request.Request(
        url.rstrip("/") + "/v1/chat/completions",
        data=body,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=180) as resp:
        return json.loads(resp.read())


def tool_names(response: dict) -> list[str]:
    choices = response.get("choices") or []
    msg = (choices[0].get("message") if choices else {}) or {}
    calls = msg.get("tool_calls") or []
    return [((call.get("function") or {}).get("name")) for call in calls]


def content(response: dict) -> str:
    choices = response.get("choices") or []
    msg = (choices[0].get("message") if choices else {}) or {}
    return msg.get("content") or ""


def test_forced_tool_sequence_does_not_replay_previous_tool_text() -> None:
    url = os.environ.get("LUCEBOX_TEST_URL")
    if not url:
        pytest.skip("set LUCEBOX_TEST_URL to run live lucebox tool-call repro")

    first = post_forced_tool(url, "grep")
    assert tool_names(first) == ["grep"], first

    second = post_forced_tool(url, "shell")
    assert tool_names(second) == ["shell"], second
    assert "<function=grep>" not in content(second), second
