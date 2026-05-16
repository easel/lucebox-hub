"""Liveness smoke test.

Hits the running server's `/v1/chat/completions` with a five-token prompt and
asserts: HTTP 200, ≥1 content token streamed back, response within timeout.
Semantic correctness is the benchmark's job; smoke just proves the pipe works.

Talks to the server via the host docker socket — the server container's port
is mapped to host port `cfg.port`, and the orchestrator container reaches it
via `host.docker.internal` on Docker Desktop or via the docker bridge
gateway on Linux. We resolve to `host.docker.internal` first and fall back.
"""

from __future__ import annotations

import json
import socket
import time
from dataclasses import dataclass

import httpx

from lucebox.types import Config

DEFAULT_TIMEOUT_S = 60.0
DEFAULT_PROMPT = "Reply with exactly one word: hello"


@dataclass(frozen=True, slots=True)
class SmokeResult:
    ok: bool
    http_status: int
    n_tokens: int
    wall_s: float
    error: str = ""


def _server_base_url(cfg: Config) -> str:
    """Where to reach the server from inside the orchestrator container.

    Tries `host.docker.internal` (Docker Desktop, also added by recent
    docker-ce via --add-host), then falls back to the default bridge
    gateway 172.17.0.1.
    """
    host = "host.docker.internal"
    try:
        socket.gethostbyname(host)
    except OSError:
        host = "172.17.0.1"
    return f"http://{host}:{cfg.port}"


def run(cfg: Config, *, prompt: str = DEFAULT_PROMPT,
        timeout_s: float = DEFAULT_TIMEOUT_S) -> SmokeResult:
    url = _server_base_url(cfg) + "/v1/chat/completions"
    body = {
        "model": "luce-dflash",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 16,
        "stream": True,
    }

    t0 = time.perf_counter()
    n_tokens = 0
    try:
        with httpx.stream("POST", url, json=body, timeout=timeout_s) as resp:
            status = resp.status_code
            if status != 200:
                return SmokeResult(
                    ok=False, http_status=status, n_tokens=0,
                    wall_s=time.perf_counter() - t0,
                    error=f"HTTP {status}",
                )
            for line in resp.iter_lines():
                if not line.startswith("data:"):
                    continue
                payload = line[5:].strip()
                if payload == "[DONE]":
                    break
                try:
                    chunk = json.loads(payload)
                except json.JSONDecodeError:
                    continue
                choices = chunk.get("choices") or []
                if not choices:
                    continue
                delta = choices[0].get("delta") or {}
                if delta.get("content"):
                    n_tokens += 1
    except httpx.HTTPError as e:
        return SmokeResult(
            ok=False, http_status=0, n_tokens=n_tokens,
            wall_s=time.perf_counter() - t0,
            error=str(e),
        )

    wall = time.perf_counter() - t0
    return SmokeResult(
        ok=(status == 200 and n_tokens >= 1),
        http_status=status, n_tokens=n_tokens, wall_s=wall,
        error="" if n_tokens >= 1 else "no tokens streamed",
    )
