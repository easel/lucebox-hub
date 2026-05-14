#!/usr/bin/env python3
"""Convert lucebox target_feat dumps + speculators arrow dataset → hidden_states/*.safetensors.

Reads the .bin files produced by test_dflash with DFLASH_CAPTURE_PATH set
(see commit 2156c87), pairs each with the corresponding row in the
preprocessed speculators arrow dataset, and writes hs_{idx}.safetensors
matching the layout speculators' train/data.py expects:

    {
      "hidden_states": [seq_len, K, hidden_size]    bf16
      "token_ids":     [seq_len]                    int64
    }

Where K = 5 intermediates + 1 verifier. **Current state**: the lucebox
patch only captures the 5 intermediates today, so this converter
duplicates the last intermediate as a stand-in verifier_last_hidden_state
so the speculators pipeline can be validated end-to-end. Once
test_dflash also captures the post-output-norm hidden state, replace the
stub with the real one.

Usage:
    python dumps_to_speculators.py \\
        --captures-dir /tmp/codex_captures_10 \\
        --prepared-dataset /tmp/codex_prepared_100 \\
        --output-dir /tmp/codex_prepared_100/hidden_states \\
        --hidden-size 5120
"""
import argparse
import struct
from pathlib import Path

import numpy as np
import torch
from datasets import load_from_disk
from safetensors.torch import save_file


def read_dump(path: Path) -> tuple[int, int, np.ndarray]:
    """Read a DFCP target_feat dump.

    Returns (n_pos, features_per_pos, data) where data is a uint16 ndarray
    of shape (n_pos, features_per_pos) representing bf16 values.
    """
    with path.open("rb") as f:
        hdr = f.read(32)
        if len(hdr) != 32:
            raise ValueError(f"{path}: header truncated")
        magic, version, n_pos, fpp, dtype = struct.unpack("<5I", hdr[:20])
        if magic != 0x50434644:
            raise ValueError(f"{path}: bad magic 0x{magic:08x}")
        if dtype != 2:
            raise ValueError(f"{path}: unexpected dtype {dtype} (expected 2=bf16)")
        raw = f.read(n_pos * fpp * 2)
        if len(raw) != n_pos * fpp * 2:
            raise ValueError(f"{path}: data truncated")
        arr = np.frombuffer(raw, dtype=np.uint16).reshape(n_pos, fpp)
    return n_pos, fpp, arr


def bf16_uint16_to_tensor(buf: np.ndarray) -> torch.Tensor:
    """Reinterpret a uint16 numpy view as bfloat16 torch tensor."""
    t = torch.from_numpy(buf).clone()
    return t.view(torch.bfloat16)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--captures-dir", required=True, type=Path,
                    help="Directory containing cap_*.bin dumps")
    ap.add_argument("--prepared-dataset", required=True, type=Path,
                    help="Arrow dataset path from prepare_data.py")
    ap.add_argument("--output-dir", required=True, type=Path,
                    help="Output dir for hs_{idx}.safetensors files")
    ap.add_argument("--hidden-size", type=int, default=5120,
                    help="Per-layer hidden size (Qwen3.6-27B = 5120)")
    ap.add_argument("--n-intermediates", type=int, default=5,
                    help="Number of intermediate hidden states in the dump")
    args = ap.parse_args()

    ds = load_from_disk(str(args.prepared_dataset))
    print(f"loaded {len(ds)} prepared samples from {args.prepared_dataset}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    expected_fpp = args.n_intermediates * args.hidden_size

    n_written = 0
    n_skipped = 0
    for idx in range(len(ds)):
        cap_path = args.captures_dir / f"cap_{idx:06d}.bin"
        if not cap_path.is_file():
            n_skipped += 1
            continue
        try:
            n_pos, fpp, arr_u16 = read_dump(cap_path)
        except ValueError as e:
            print(f"  [{idx}] skip: {e}")
            n_skipped += 1
            continue
        if fpp != expected_fpp:
            print(f"  [{idx}] skip: fpp={fpp} != expected {expected_fpp}")
            n_skipped += 1
            continue

        # Reshape to [n_pos, n_intermediates, hidden_size] bf16
        arr_3d_u16 = arr_u16.reshape(n_pos, args.n_intermediates, args.hidden_size)
        intermediates = bf16_uint16_to_tensor(arr_3d_u16)  # [n_pos, 5, hidden]

        # Stub verifier_last: duplicate the last intermediate. Replace with
        # real post-output-norm capture once test_dflash exposes it.
        verifier_stub = intermediates[:, -1:, :].clone()  # [n_pos, 1, hidden]
        hidden_states = torch.cat([intermediates, verifier_stub], dim=1)
        # shape: [n_pos, 6, hidden] — speculators dataloader takes [:, :-1]
        # for the 5*hidden fc input and [:, -1] as verifier.

        # Match the speculators arrow's tokenization for this row
        input_ids = ds[idx]["input_ids"]
        if not isinstance(input_ids, torch.Tensor):
            input_ids = torch.tensor(input_ids, dtype=torch.long)
        # Truncate / pad token_ids to match n_pos (the captured prefill length)
        if input_ids.numel() > n_pos:
            input_ids = input_ids[:n_pos]
        elif input_ids.numel() < n_pos:
            print(f"  [{idx}] warning: input_ids({input_ids.numel()}) < n_pos({n_pos})")
            n_skipped += 1
            continue

        out_path = args.output_dir / f"hs_{idx}.safetensors"
        save_file({
            "hidden_states": hidden_states.contiguous(),
            "token_ids":     input_ids.to(torch.int64).contiguous(),
        }, str(out_path))
        n_written += 1
        if n_written <= 3:
            print(f"  [{idx}] wrote {out_path.name} hs={tuple(hidden_states.shape)} ids={tuple(input_ids.shape)}")

    print(f"wrote {n_written} safetensors, skipped {n_skipped}")


if __name__ == "__main__":
    main()
