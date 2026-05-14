#!/usr/bin/env python3
"""Rewrite the loss_mask column of a speculators arrow dataset.

speculators' built-in assistant-span detection produces an all-False
loss_mask with the Qwen3.6 tokenizer + a custom `--assistant-pattern`
(offset_mapping path returns wrong offsets for some chat templates).

This script bypasses that by scanning input_ids directly for the
sequence `<|im_start|>assistant <newline> ... <|im_end|>` (Qwen tokens
248045 74455 198 ... 248046) and marking the inner span as trainable.

The "thinking" block `<think>...</think>` inside the assistant turn is
INCLUDED in the mask — speculators trains on whatever the assistant
emits.

Usage:
    python fix_loss_mask.py \\
        --input /tmp/codex_prepared_10 \\
        --output /tmp/codex_prepared_10_fixed
"""
import argparse
from pathlib import Path

import torch
from datasets import load_from_disk

# Qwen3 / Qwen3.6 chat-template control tokens
TOK_IM_START = 248045
TOK_ASSISTANT = 74455
TOK_NEWLINE = 198
TOK_IM_END = 248046


def compute_loss_mask(input_ids: list[int]) -> list[bool]:
    """Find <|im_start|>assistant\\n ... <|im_end|> spans, mark the content trainable."""
    n = len(input_ids)
    mask = [False] * n
    i = 0
    while i < n - 3:
        if (input_ids[i] == TOK_IM_START
                and input_ids[i + 1] == TOK_ASSISTANT
                and input_ids[i + 2] == TOK_NEWLINE):
            # Span starts AFTER the marker (don't train on the role tag itself)
            start = i + 3
            # Find the closing <|im_end|>
            j = start
            while j < n and input_ids[j] != TOK_IM_END:
                j += 1
            if j < n:
                for k in range(start, j):
                    mask[k] = True
                i = j + 1
                continue
        i += 1
    return mask


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()

    ds = load_from_disk(str(args.input))
    print(f"loaded {len(ds)} samples from {args.input}")

    def rewrite(example):
        ids = example["input_ids"]
        if isinstance(ids, torch.Tensor):
            ids = ids.tolist()
        new_mask = compute_loss_mask(ids)
        return {"loss_mask": new_mask}

    fixed = ds.map(rewrite, num_proc=4, desc="rewriting loss_mask")

    # Report mask coverage
    total = 0
    trainable = 0
    for i in range(len(fixed)):
        m = fixed[i]["loss_mask"]
        total += len(m)
        trainable += sum(1 for x in m if x)
    pct = 100.0 * trainable / total if total else 0.0
    print(f"loss_mask trainable: {trainable}/{total} ({pct:.1f}%) tokens")

    fixed.save_to_disk(str(args.output))
    print(f"wrote {args.output}")


if __name__ == "__main__":
    main()
