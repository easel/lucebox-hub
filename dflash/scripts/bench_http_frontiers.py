"""HTTP long-context frontier probe for lucebox.

This is not antirez/ds4's `ds4-eval` or full `ds4-bench` suite. It borrows one
useful idea from `ds4-bench`: measure generation behavior at a series of
long-context frontiers instead of reporting one whole-run average. Lucebox's
public HTTP API does not expose DS4's in-memory KV save/restore primitive, so
this script uses deterministic prompts sized to target frontiers and records
server-reported prompt_tokens when available.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
import urllib.request
from pathlib import Path
from typing import Any


CORPUS_BLOCKS = [
    "You are auditing a repository for a local inference server. "
    "Track API compatibility, tool-call behavior, startup configuration, "
    "benchmark fidelity, and Docker reproducibility.\n",
    "File: lucebox/lucebox/smoke.py\n"
    "The smoke check must prove /props is populated, text streams, and tools "
    "are emitted in OpenAI format.\n",
    "File: dflash/scripts/server.py\n"
    "The server renders Qwen chat templates, streams SSE deltas, parses XML "
    "tool calls, and reports runtime properties.\n",
    "Review note: preserve patch isolation so /props, Docker startup, uv "
    "bootstrap, and benchmark harness changes can be split later.\n",
]


def make_prompt(target_tokens: int, chars_per_token: int) -> str:
    target_chars = max(256, target_tokens * chars_per_token)
    pieces: list[str] = []
    i = 0
    while sum(len(p) for p in pieces) < target_chars:
        pieces.append(f"[chunk {i:05d}] {CORPUS_BLOCKS[i % len(CORPUS_BLOCKS)]}")
        i += 1
    body = "".join(pieces)[:target_chars]
    return (
        "Use the following repository context to answer the final instruction. "
        "Do not call tools for this benchmark.\n\n"
        f"{body}\n\n"
        "Final instruction: write exactly one sentence beginning with 'Risk:' "
        "that summarizes the highest-risk reliability issue."
    )


def run_one(url: str, prompt: str, gen_tokens: int, timeout_s: int) -> dict[str, Any]:
    body = json.dumps({
        "model": "luce-dflash",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": gen_tokens,
        "temperature": 0,
        "stream": True,
        "stream_options": {"include_usage": True},
    }).encode()
    req = urllib.request.Request(
        url + "/v1/chat/completions",
        data=body,
        headers={"Content-Type": "application/json", "Accept": "text/event-stream"},
    )

    t0 = time.perf_counter()
    t_first = 0.0
    t_last = 0.0
    n_tok = 0
    usage: dict[str, int] = {}
    finish_reason = None
    with urllib.request.urlopen(req, timeout=timeout_s) as r:
        for raw in r:
            line = raw.decode("utf-8", errors="replace").strip()
            if not line.startswith("data:"):
                continue
            payload = line[5:].strip()
            if payload == "[DONE]":
                break
            try:
                chunk = json.loads(payload)
            except json.JSONDecodeError:
                continue
            if chunk.get("usage"):
                usage = chunk["usage"]
                continue
            choices = chunk.get("choices") or []
            if not choices:
                continue
            finish_reason = choices[0].get("finish_reason") or finish_reason
            delta = choices[0].get("delta") or {}
            if delta.get("content") or delta.get("reasoning_content"):
                if n_tok == 0:
                    t_first = time.perf_counter()
                n_tok += 1
                t_last = time.perf_counter()

    wall = time.perf_counter() - t0
    decode = t_last - t_first if n_tok > 1 else 0.0
    return {
        "prompt_chars": len(prompt),
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": n_tok,
        "finish_reason": finish_reason,
        "wall_s": round(wall, 3),
        "ttft_s": round(t_first - t0, 3) if t_first else None,
        "decode_s": round(decode, 3),
        "wall_tps": round(n_tok / wall, 2) if wall > 0 else 0.0,
        "decode_tps": round((n_tok - 1) / decode, 2) if decode > 0 else 0.0,
    }


def run_frontier(
    url: str,
    prompt: str,
    gen_tokens: int,
    timeout_s: int,
    retries: int,
) -> dict[str, Any]:
    """Run one frontier, retrying empty completions once the server is warm."""
    last: dict[str, Any] | None = None
    for attempt in range(1, retries + 2):
        attempt_prompt = prompt
        if attempt > 1:
            attempt_prompt += f"\n\nRetry marker: http-frontier-attempt-{attempt}."
        row = run_one(url, attempt_prompt, gen_tokens, timeout_s)
        row["attempt"] = attempt
        last = row
        if row["completion_tokens"] > 0:
            return row
    assert last is not None
    return last


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "frontier_target_tokens", "prompt_chars", "prompt_tokens",
        "completion_tokens", "attempt", "finish_reason", "wall_s", "ttft_s",
        "decode_s", "wall_tps", "decode_tps",
    ]
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in fields})


def main() -> int:
    ap = argparse.ArgumentParser(description="Run long-context frontiers over HTTP.")
    ap.add_argument("--url", default="http://127.0.0.1:8000", help="Server base URL.")
    ap.add_argument("--frontiers", default="2048,4096,8192,16384",
                    help="Comma-separated target prompt-token frontiers.")
    ap.add_argument("--chars-per-token", type=int, default=4,
                    help="Prompt sizing estimate; actual tokens come from usage when available.")
    ap.add_argument("--gen-tokens", type=int, default=128)
    ap.add_argument("--retries", type=int, default=2,
                    help="Retry empty completions; useful for cold lazy-draft starts.")
    ap.add_argument("--timeout", type=int, default=900)
    ap.add_argument("--json-out", type=Path)
    ap.add_argument("--csv-out", type=Path)
    args = ap.parse_args()

    rows: list[dict[str, Any]] = []
    frontiers = [int(x) for x in args.frontiers.split(",") if x.strip()]
    print(f"[http-frontiers] url={args.url} frontiers={frontiers} gen={args.gen_tokens}", flush=True)
    print(f"{'target':>8s} {'prompt_tok':>10s} {'ttft':>8s} {'decode_tps':>10s} {'wall':>8s}")
    for frontier in frontiers:
        prompt = make_prompt(frontier, args.chars_per_token)
        row = run_frontier(args.url, prompt, args.gen_tokens, args.timeout, args.retries)
        row["frontier_target_tokens"] = frontier
        rows.append(row)
        prompt_tok = row["prompt_tokens"] if row["prompt_tokens"] is not None else "?"
        print(f"{frontier:8d} {prompt_tok!s:>10s} {row['ttft_s']!s:>8s} "
              f"{row['decode_tps']:10.2f} {row['wall_s']:8.2f}", flush=True)

    payload = {
        "suite": "http-frontiers",
        "source": "ds4-bench-inspired-http-frontier-probe",
        "rows": rows,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        args.json_out.write_text(json.dumps(payload, indent=2) + "\n")
    if args.csv_out:
        _write_csv(args.csv_out, rows)
    return 0 if all(row["completion_tokens"] > 0 for row in rows) else 1


if __name__ == "__main__":
    raise SystemExit(main())
