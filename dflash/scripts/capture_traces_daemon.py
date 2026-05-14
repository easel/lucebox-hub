#!/usr/bin/env python3
"""Persistent-daemon variant of capture_traces.py — ~10× faster.

`capture_traces.py` spawns a new `test_dflash` per prompt, paying the
~15 s model-load cost every time. This script launches `test_dflash` in
daemon mode ONCE and pushes prompts through its stdin protocol, paying
that cost a single time per run.

The DFLASH_CAPTURE_PATH env var is read on every prefill, but the
daemon was spawned with a fixed value. To get per-prompt dumps we set
the env var to a single staging path, then `mv` it to a per-prompt
filename after each `[capture] wrote ...` line.

Usage:
    python capture_traces_daemon.py \\
        --input-jsonl /tmp/codex_speculators_all.jsonl \\
        --out-dir /tmp/codex_daemon_caps \\
        --target dflash/models/Qwen3.6-27B-Q4_K_M.gguf \\
        --draft dflash/models/draft/model.safetensors \\
        --bin dflash/build/test_dflash \\
        --max-samples 1000 --max-ctx 4096 --max-prompt-tokens 3500
"""
import argparse
import json
import os
import shutil
import struct
import subprocess
import sys
import threading
import time
from pathlib import Path

from transformers import AutoTokenizer


CAPTURE_DONE_PREFIX = "[capture] wrote"  # daemon line that signals capture file ready


def render_and_tokenize(tokenizer, conversation, max_len):
    text = tokenizer.apply_chat_template(conversation, tokenize=False, add_generation_prompt=False)
    ids = tokenizer.encode(text, add_special_tokens=False)
    return ids[:max_len]


def write_tokens_bin(path, ids):
    with path.open("wb") as f:
        for tid in ids:
            f.write(struct.pack("<I", int(tid)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-jsonl", required=True, type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--target", required=True, type=Path)
    ap.add_argument("--draft", required=True, type=Path)
    ap.add_argument("--bin", required=True, type=Path)
    ap.add_argument("--tokenizer", default="Qwen/Qwen3.6-27B")
    ap.add_argument("--max-prompt-tokens", type=int, default=3500)
    ap.add_argument("--max-ctx", type=int, default=4096)
    ap.add_argument("--budget", type=int, default=22)
    ap.add_argument("--max-samples", type=int, default=None)
    ap.add_argument("--start-idx", type=int, default=0)
    ap.add_argument("--idle-timeout", type=float, default=180.0,
                    help="Per-prompt timeout waiting for [capture] line")
    args = ap.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(args.tokenizer)

    # Single staging path; renamed after each prefill.
    staging = args.out_dir / "_staging.bin"
    env = os.environ.copy()
    env["DFLASH_CAPTURE_PATH"] = str(staging)

    # Launch the daemon with --daemon. We pass a placeholder prompt.bin
    # via argv (the daemon binary requires the positional args even in
    # daemon mode); the daemon will read additional command lines from
    # stdin in the format `<prompt.bin> <n_gen> ...`.
    placeholder = args.out_dir / "_placeholder.bin"
    write_tokens_bin(placeholder, tok.encode("hello", add_special_tokens=False) or [9])
    cmd = [
        str(args.bin), str(args.target), str(args.draft),
        str(placeholder), "1", str(args.out_dir / "_placeholder_out.bin"),
        "--daemon",
        "--fast-rollback", "--ddtree", f"--ddtree-budget={args.budget}",
        f"--max-ctx={args.max_ctx}",
    ]
    print(f"[driver] launching daemon: {' '.join(cmd)}", file=sys.stderr)
    daemon = subprocess.Popen(
        cmd, env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=0,  # unbuffered
        text=True,
    )

    # Background thread to read daemon stdout and surface a "capture seen"
    # signal whenever a [capture] wrote line lands.
    capture_event = threading.Event()
    daemon_died = threading.Event()
    last_lines: list[str] = []

    def reader():
        for ln in iter(daemon.stdout.readline, ""):
            last_lines.append(ln.rstrip())
            if len(last_lines) > 50:
                del last_lines[:25]
            if ln.startswith(CAPTURE_DONE_PREFIX):
                capture_event.set()
        daemon_died.set()

    t = threading.Thread(target=reader, daemon=True)
    t.start()

    manifest = (args.out_dir / "manifest.jsonl").open("a")
    written = 0
    skipped = 0
    drainer_start = time.time()
    # Drain the daemon's startup chatter — wait for "ready" line.
    while not daemon_died.is_set():
        if any("daemon] ready" in l for l in last_lines):
            break
        if time.time() - drainer_start > 60:
            print("[driver] daemon did not become ready in 60s; aborting", file=sys.stderr)
            daemon.kill()
            return 1
        time.sleep(0.2)
    print("[driver] daemon ready", file=sys.stderr)

    with args.input_jsonl.open() as f:
        for idx, line in enumerate(f):
            if idx < args.start_idx:
                continue
            if args.max_samples is not None and written >= args.max_samples:
                break
            try:
                rec = json.loads(line)
                conv = rec.get("conversations") or []
                if not conv:
                    continue
                ids = render_and_tokenize(tok, conv, args.max_prompt_tokens)
            except Exception as e:
                print(f"[{idx}] tokenize fail: {e}", file=sys.stderr)
                skipped += 1
                continue
            if len(ids) < 32:
                skipped += 1
                continue

            prompt_bin = args.out_dir / f"cap_{idx:06d}.tokens.bin"
            cap_bin = args.out_dir / f"cap_{idx:06d}.bin"
            tokens_path = args.out_dir / f"cap_{idx:06d}.tokens"
            write_tokens_bin(prompt_bin, ids)
            tokens_path.write_bytes(prompt_bin.read_bytes())

            # Send prefill-only command: prompt.bin, n_gen=1
            cmd_line = f"{prompt_bin} 1\n"
            capture_event.clear()
            t0 = time.time()
            try:
                daemon.stdin.write(cmd_line)
                daemon.stdin.flush()
            except (BrokenPipeError, OSError) as e:
                print(f"[{idx}] daemon stdin write failed: {e}", file=sys.stderr)
                break

            ok = capture_event.wait(timeout=args.idle_timeout) and staging.is_file()
            elapsed = time.time() - t0
            if ok:
                shutil.move(str(staging), str(cap_bin))
                written += 1
                print(f"[{idx}] tokens={len(ids):>5}  ok  {elapsed:.1f}s", file=sys.stderr)
            else:
                print(f"[{idx}] tokens={len(ids):>5}  TIMEOUT  daemon-tail={last_lines[-3:]}", file=sys.stderr)
                skipped += 1
                if daemon_died.is_set():
                    break
            manifest.write(json.dumps({
                "idx": idx, "n_tokens": len(ids),
                "cap_bin": str(cap_bin) if ok else None,
                "tokens": str(tokens_path), "elapsed_s": elapsed,
            }) + "\n")
            manifest.flush()

    manifest.close()
    print(f"[driver] done. wrote={written} skipped={skipped}", file=sys.stderr)
    try:
        daemon.stdin.write("exit\n")
        daemon.stdin.flush()
    except Exception:
        pass
    daemon.terminate()
    try:
        daemon.wait(timeout=10)
    except subprocess.TimeoutExpired:
        daemon.kill()
    return 0


if __name__ == "__main__":
    sys.exit(main())
