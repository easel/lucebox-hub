#!/usr/bin/env python3
"""Convert a speculators-trained DFlash checkpoint to lucebox draft format.

Speculators saves a few extra weights that lucebox's daemon doesn't load
(`embed_tokens.weight`, `lm_head.weight` and the `t2d`/`d2t` vocab maps).
With the `--draft-num-attention-heads / --draft-num-key-value-heads /
--draft-head-dim` overrides on speculators' train.py, the remaining 58
tensors are key-for-key identical to z-lab/Qwen3.6-27B-DFlash.

This script drops the 4 extra tensors and re-emits a single safetensors
file alongside a lucebox-compatible config.json. The output directory
can be passed directly to `--draft <dir>` on test_dflash / server.py.

Usage:
    python speculators_to_lucebox.py \\
        --speculators-checkpoint /tmp/codex_trained_draft/0 \\
        --reference-draft dflash/models/draft \\
        --output dflash/models/draft-trained
"""
import argparse
import json
import shutil
from pathlib import Path

from safetensors import safe_open
from safetensors.torch import save_file

DROP_KEYS = {"d2t", "t2d", "embed_tokens.weight", "lm_head.weight"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--speculators-checkpoint", required=True, type=Path,
                    help="speculators output dir, e.g. /tmp/codex_trained_draft/0")
    ap.add_argument("--reference-draft", required=True, type=Path,
                    help="z-lab draft dir for config.json reference + assets/")
    ap.add_argument("--output", required=True, type=Path)
    args = ap.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)

    src_st = args.speculators_checkpoint / "model.safetensors"
    out_st = args.output / "model.safetensors"

    tensors: dict[str, "torch.Tensor"] = {}
    dropped: list[str] = []
    with safe_open(src_st, framework="pt") as f:
        for k in f.keys():
            if k in DROP_KEYS:
                dropped.append(k)
                continue
            tensors[k] = f.get_tensor(k)
    save_file(tensors, str(out_st))
    print(f"wrote {len(tensors)} tensors to {out_st}")
    print(f"dropped {dropped}")

    # Reuse z-lab's config.json (lucebox loader reads model_type, layer_types,
    # sliding_window, dflash_config.target_layer_ids, num_target_layers).
    # Diff against speculators' to make sure shapes are compatible.
    ref_cfg = json.loads((args.reference_draft / "config.json").read_text())
    spec_cfg = json.loads((args.speculators_checkpoint / "config.json").read_text())

    # Update target_layer_ids from speculators (in case caller passed different
    # ids to train.py than z-lab's defaults).
    aux_ids = spec_cfg.get("aux_hidden_state_layer_ids")
    if aux_ids:
        ref_cfg.setdefault("dflash_config", {})["target_layer_ids"] = list(aux_ids)

    (args.output / "config.json").write_text(json.dumps(ref_cfg, indent=2))
    print(f"wrote config.json (model_type={ref_cfg.get('model_type')}, "
          f"target_layer_ids={ref_cfg.get('dflash_config',{}).get('target_layer_ids')})")

    # Carry assets/ over if it exists (z-lab's draft has a small assets dir).
    src_assets = args.reference_draft / "assets"
    if src_assets.is_dir():
        dst_assets = args.output / "assets"
        if dst_assets.exists():
            shutil.rmtree(dst_assets)
        shutil.copytree(src_assets, dst_assets)


if __name__ == "__main__":
    main()
