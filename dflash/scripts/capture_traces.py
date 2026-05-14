#!/usr/bin/env python3
"""Batch-drive `test_dflash` over agent traces to capture target hidden states.

Reads a speculators-prep jsonl (one {"conversations":[...]} line per session),
renders each conversation with the target chat template, tokenizes, writes a
prompt.bin, then invokes `test_dflash` with DFLASH_CAPTURE_PATH set so the
daemon dumps `target_feat` after prefill. Per-prompt output:

    <out-dir>/cap_{idx:06d}.bin      raw target_feat dump (see test_dflash patch)
    <out-dir>/cap_{idx:06d}.tokens   little-endian u32 token ids (matches the prompt
                                     range whose hidden states were dumped)
    <out-dir>/manifest.jsonl         one line per capture with metadata

Intended next step: a separate converter that reads these files and writes
the speculators-compatible safetensors layout under
`<speculators-prep>/hidden_states/`.
"""
import argparse
import json
import os
import struct
import subprocess
import sys
from pathlib import Path

from transformers import AutoTokenizer


def render_and_tokenize(tokenizer, conversation: list[dict], max_len: int) -> list[int]:
    """Apply the target chat template and tokenize. Returns ids truncated to max_len."""
    text = tokenizer.apply_chat_template(
        conversation,
        tokenize=False,
        add_generation_prompt=False,
    )
    ids = tokenizer.encode(text, add_special_tokens=False)
    return ids[:max_len]


def write_tokens_bin(path: Path, ids: list[int]) -> None:
    # test_dflash expects little-endian u32 token ids
    with path.open("wb") as f:
        for tid in ids:
            f.write(struct.pack("<I", int(tid)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input-jsonl", required=True, type=Path,
                    help="Speculators-prep jsonl (one {conversations:[...]} per line)")
    ap.add_argument("--out-dir", required=True, type=Path)
    ap.add_argument("--target", required=True, type=Path,
                    help="Path to target GGUF")
    ap.add_argument("--draft", required=True, type=Path,
                    help="Path to draft safetensors (required by test_dflash even in capture-only flows)")
    ap.add_argument("--bin", required=True, type=Path,
                    help="Path to test_dflash binary")
    ap.add_argument("--tokenizer", default="Qwen/Qwen3.6-27B")
    ap.add_argument("--max-prompt-tokens", type=int, default=4000,
                    help="Truncate prompts to this many tokens (must fit target_feat_cap)")
    ap.add_argument("--max-ctx", type=int, default=4096)
    ap.add_argument("--budget", type=int, default=22)
    ap.add_argument("--n-gen", type=int, default=1,
                    help="Generate this many tokens (1 is the minimum; we only want prefill)")
    ap.add_argument("--max-samples", type=int, default=None)
    ap.add_argument("--start-idx", type=int, default=0)
    args = ap.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    tok = AutoTokenizer.from_pretrained(args.tokenizer)
    manifest = (args.out_dir / "manifest.jsonl").open("a")

    with args.input_jsonl.open() as f:
        for idx, line in enumerate(f):
            if idx < args.start_idx:
                continue
            if args.max_samples is not None and idx - args.start_idx >= args.max_samples:
                break
            rec = json.loads(line)
            conv = rec.get("conversations") or []
            if not conv:
                continue
            try:
                ids = render_and_tokenize(tok, conv, args.max_prompt_tokens)
            except Exception as e:
                print(f"[{idx}] tokenize fail: {e}", file=sys.stderr)
                continue
            if len(ids) < 32:
                continue

            prompt_bin = args.out_dir / f"cap_{idx:06d}.tokens.bin"
            cap_bin = args.out_dir / f"cap_{idx:06d}.bin"
            tokens_path = args.out_dir / f"cap_{idx:06d}.tokens"

            write_tokens_bin(prompt_bin, ids)
            # Plain little-endian u32 mirror for downstream consumers that
            # don't want to parse the test_dflash prompt format.
            tokens_path.write_bytes(prompt_bin.read_bytes())

            env = os.environ.copy()
            env["DFLASH_CAPTURE_PATH"] = str(cap_bin)
            # Stay below target_feat_cap; even though we set --n-gen 1, we
            # need the daemon to actually run prefill.
            cmd = [
                str(args.bin), str(args.target), str(args.draft), str(prompt_bin),
                str(args.n_gen), str(args.out_dir / f"cap_{idx:06d}.gen.bin"),
                "--fast-rollback", "--ddtree", f"--ddtree-budget={args.budget}",
                f"--max-ctx={args.max_ctx}",
            ]
            r = subprocess.run(cmd, env=env, capture_output=True, text=True, timeout=300)
            ok = cap_bin.is_file() and cap_bin.stat().st_size > 32
            manifest.write(json.dumps({
                "idx": idx,
                "n_tokens": len(ids),
                "cap_bin": str(cap_bin) if ok else None,
                "tokens": str(tokens_path),
                "exit": r.returncode,
                "stderr_tail": r.stderr[-300:] if not ok else "",
            }) + "\n")
            manifest.flush()
            print(f"[{idx}] tokens={len(ids):>5}  cap_ok={ok}  exit={r.returncode}",
                  file=sys.stderr)

    manifest.close()


if __name__ == "__main__":
    main()
