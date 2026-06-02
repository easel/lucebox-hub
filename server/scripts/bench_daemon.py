"""HTTP daemon benchmark for the HumanEval prompts used by bench_he.py.

Start dflash_server separately, then run:

    python3 server/scripts/bench_daemon.py --url http://localhost:8000 --n-gen 256

The script streams /v1/chat/completions responses and reports both total
request wall time and first-token-to-last-token decode time.
"""

import argparse
import json
import sys
import time
import urllib.request
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent))
from bench_he import PROMPTS  # noqa: E402


def run(url: str, prompt: str, n_gen: int) -> tuple[int, float, float]:
    """Return (n_tokens, wall_seconds, decode_seconds)."""
    body = json.dumps({
        "model": "luce-dflash",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": n_gen,
        "stream": True,
    }).encode()
    req = urllib.request.Request(
        url.rstrip("/") + "/v1/chat/completions",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Accept": "text/event-stream",
        },
    )

    t0 = time.perf_counter()
    t_first = 0.0
    t_last = 0.0
    n_tok = 0
    with urllib.request.urlopen(req, timeout=600) as response:
        for raw in response:
            line = raw.decode("utf-8", errors="replace").rstrip()
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
            if delta.get("content") or delta.get("reasoning_content"):
                now = time.perf_counter()
                if n_tok == 0:
                    t_first = now
                n_tok += 1
                t_last = now

    wall = time.perf_counter() - t0
    decode = (t_last - t_first) if n_tok > 1 else 0.0
    return n_tok, wall, decode


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://localhost:8000",
                        help="Base URL of the running server")
    parser.add_argument("--n-gen", type=int, default=256)
    parser.add_argument("--warmup", action="store_true",
                        help="Run the first prompt once before timing")
    args = parser.parse_args()

    if args.warmup:
        print("[bench] warmup...", flush=True)
        run(args.url, PROMPTS[0][1], args.n_gen)

    print(f"[bench] daemon API n_gen={args.n_gen} url={args.url}", flush=True)
    print(f"{'prompt':28s} {'n_tok':>5s} {'wall_s':>7s} {'dec_s':>7s} "
          f"{'wall_tps':>9s} {'dec_tps':>9s}")
    print("-" * 72)

    wall_tps_values: list[float] = []
    dec_tps_values: list[float] = []
    total_tok = 0
    total_wall = 0.0
    total_decode = 0.0
    for name, text in PROMPTS:
        try:
            n_tok, wall, decode = run(args.url, text, args.n_gen)
        except Exception as exc:
            print(f"  {name:26s} FAILED: {exc}", flush=True)
            continue

        if n_tok == 0:
            print(f"  {name:26s} {n_tok:5d} {wall:7.2f}    --         --        --",
                  flush=True)
            continue

        wall_tps = n_tok / wall if wall > 0 else 0.0
        dec_tps = (n_tok - 1) / decode if decode > 0 else 0.0
        wall_tps_values.append(wall_tps)
        if dec_tps > 0:
            dec_tps_values.append(dec_tps)
            total_decode += decode
        total_tok += n_tok
        total_wall += wall
        print(f"  {name:26s} {n_tok:5d} {wall:7.2f} {decode:7.2f} "
              f"{wall_tps:9.2f} {dec_tps:9.2f}", flush=True)

    print("-" * 72)
    if not wall_tps_values:
        print("no successful runs")
        return 1

    print(f"wall tok/s mean:        {sum(wall_tps_values) / len(wall_tps_values):7.2f}")
    if dec_tps_values:
        aggregate = ((total_tok - len(dec_tps_values)) / total_decode
                     if total_decode > 0 else 0.0)
        print(f"decode tok/s mean:      {sum(dec_tps_values) / len(dec_tps_values):7.2f}")
        print(f"decode tok/s aggregate: {aggregate:7.2f}")
        print(f"decode tok/s range:     {min(dec_tps_values):.2f} - {max(dec_tps_values):.2f}")
    print(f"wall tok/s aggregate:   {total_tok / total_wall if total_wall > 0 else 0.0:7.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
