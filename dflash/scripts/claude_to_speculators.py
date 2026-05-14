#!/usr/bin/env python3
"""Convert Claude Code session jsonl → speculators training jsonl.

Claude Code stores each session as jsonl where each line is one of several
record types. We extract `type: user` and `type: assistant` records and
flatten their `message.content` into the speculators conversations schema:

    {"conversations": [{"role": "user", "content": "..."}, ...]}

Assistant content is a list of blocks — `text`, `thinking`, `tool_use`,
`tool_result`. We concatenate `text` and `thinking` into one assistant
turn (the draft should learn the full output the model produces),
serialize `tool_use` blocks as JSON, and drop `tool_result` (those are
already in the next user turn).

Usage:
    python claude_to_speculators.py \\
        --input-dir /tank/home/erik/ClaudeProjects \\
        --output /tmp/claude_speculators_all.jsonl
"""
import argparse
import json
import sys
from pathlib import Path


def extract_assistant_text(blocks) -> str:
    """Flatten a Claude assistant message.content list to plain text."""
    if isinstance(blocks, str):
        return blocks
    if not isinstance(blocks, list):
        return ""
    parts = []
    for b in blocks:
        if not isinstance(b, dict):
            continue
        t = b.get("type")
        if t == "text":
            parts.append(b.get("text", ""))
        elif t == "thinking":
            # Keep thinking output — the draft should learn the model's full
            # emission pattern, including the <think> block.
            parts.append(b.get("thinking", ""))
        elif t == "tool_use":
            # Serialize as the tool-call JSON the model emitted.
            parts.append(json.dumps({
                "type": "tool_use",
                "name": b.get("name"),
                "input": b.get("input"),
            }))
        # tool_result blocks belong to the next user turn (Claude renders
        # them as user messages); skip here.
    return "\n".join(p for p in parts if p)


def extract_user_text(content) -> str:
    """User messages can be string or list-of-blocks (with tool_result)."""
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts = []
    for b in content:
        if not isinstance(b, dict):
            continue
        t = b.get("type")
        if t == "text":
            parts.append(b.get("text", ""))
        elif t == "tool_result":
            inner = b.get("content")
            if isinstance(inner, list):
                for ib in inner:
                    if isinstance(ib, dict) and ib.get("type") == "text":
                        parts.append(ib.get("text", ""))
            elif isinstance(inner, str):
                parts.append(inner)
    return "\n".join(p for p in parts if p)


def session_to_conversations(path: Path) -> list[dict]:
    msgs: list[dict] = []
    try:
        with path.open() as f:
            for ln in f:
                ln = ln.strip()
                if not ln:
                    continue
                try:
                    rec = json.loads(ln)
                except json.JSONDecodeError:
                    continue
                rtype = rec.get("type")
                if rtype not in ("user", "assistant"):
                    continue
                m = rec.get("message") or {}
                content = m.get("content")
                if rtype == "assistant":
                    text = extract_assistant_text(content)
                else:
                    text = extract_user_text(content)
                if not text.strip():
                    continue
                msgs.append({"role": rtype, "content": text})
    except OSError:
        return []
    return msgs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-dir", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--max-sessions", type=int, default=None)
    ap.add_argument("--min-turns", type=int, default=3)
    ap.add_argument("--min-assistant-chars", type=int, default=200)
    args = ap.parse_args()

    files = sorted(args.input_dir.rglob("*.jsonl"))
    print(f"found {len(files)} session files in {args.input_dir}", file=sys.stderr)

    written = 0
    dropped_short = 0
    dropped_no_assistant = 0
    dropped_no_user = 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w") as out:
        for fp in files:
            if args.max_sessions is not None and written >= args.max_sessions:
                break
            msgs = session_to_conversations(fp)
            if len(msgs) < args.min_turns:
                dropped_short += 1
                continue
            first_user = next((i for i, m in enumerate(msgs) if m["role"] == "user"), None)
            if first_user is None:
                dropped_no_user += 1
                continue
            msgs = msgs[first_user:]
            assistant_chars = sum(len(m["content"]) for m in msgs if m["role"] == "assistant")
            if assistant_chars < args.min_assistant_chars:
                dropped_no_assistant += 1
                continue
            out.write(json.dumps({"conversations": msgs}, ensure_ascii=False))
            out.write("\n")
            written += 1
            if written % 500 == 0:
                print(f"  {written} written...", file=sys.stderr)

    print(
        f"wrote {written} sessions; dropped {dropped_short} too-short, "
        f"{dropped_no_assistant} no-assistant, {dropped_no_user} no-user",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()
