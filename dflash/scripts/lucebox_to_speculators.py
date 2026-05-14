#!/usr/bin/env python3
"""Convert a lucebox draft (z-lab format) into a speculators-format checkpoint.

Inverse of speculators_to_lucebox.py. Adds the four tensors speculators
expects but lucebox doesn't need:

    embed_tokens.weight   <- copy from the verifier (target) model
    lm_head.weight        <- copy from the verifier (and reduce via t2d
                              if --draft-vocab-size < verifier vocab)
    t2d                   <- target->draft vocab map (bool mask) or identity
    d2t                   <- draft->target vocab map (int offsets) or zeros

Writes the resulting checkpoint into <output>/model.safetensors + config.json
in the layout speculators' `from_pretrained` expects. Use it as
`scripts/train.py --from-pretrained <output>` to warm-start training from
z-lab's weights instead of random init.

Usage:
    python lucebox_to_speculators.py \\
        --lucebox-draft dflash/models/draft \\
        --verifier-gguf dflash/models/Qwen3.6-27B-Q4_K_M.gguf \\
        --output /tmp/draft-zlab-spec
"""
import argparse
import json
import shutil
import struct
from pathlib import Path

import torch
from safetensors import safe_open
from safetensors.torch import save_file


def read_gguf_tensor(gguf_path: Path, name: str) -> torch.Tensor:
    """Tiny GGUF reader scoped to the two tensors we actually need.

    Uses gguf's Python lib if available, else delegates to llama.cpp via the
    `gguf` package (which speculators already pulls in)."""
    from gguf import GGUFReader
    r = GGUFReader(str(gguf_path))
    for t in r.tensors:
        if t.name == name:
            return torch.from_numpy(t.data.copy())
    raise KeyError(f"{name!r} not found in {gguf_path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lucebox-draft", required=True, type=Path,
                    help="Dir containing z-lab format model.safetensors + config.json")
    ap.add_argument("--verifier-gguf", required=True, type=Path,
                    help="Path to verifier GGUF; we read tok_embd.weight and output.weight")
    ap.add_argument("--verifier-name-or-path", default="Qwen/Qwen3.6-27B",
                    help="HF repo id; used only for config metadata, no download")
    ap.add_argument("--output", required=True, type=Path)
    ap.add_argument("--draft-vocab-size", type=int, default=None,
                    help="If set, reduce embed/lm_head to top-N by token-freq using "
                         "--token-freq-path. None = full verifier vocab (no mapping).")
    ap.add_argument("--token-freq-path", type=Path, default=None)
    args = ap.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)

    # 1. Load all of z-lab's existing tensors verbatim.
    src_st = args.lucebox_draft / "model.safetensors"
    tensors: dict[str, torch.Tensor] = {}
    with safe_open(src_st, framework="pt") as f:
        for k in f.keys():
            tensors[k] = f.get_tensor(k)
    print(f"copied {len(tensors)} tensors from z-lab")

    # 2. Extract verifier embed + lm_head directly from GGUF.
    from gguf import GGUFReader, dequantize
    r = GGUFReader(str(args.verifier_gguf))
    print(f"loaded GGUF reader for {args.verifier_gguf}")
    embed_tokens = None
    lm_head = None
    for t in r.tensors:
        if t.name == "token_embd.weight":
            arr = dequantize(t.data, t.tensor_type)
            embed_tokens = torch.from_numpy(arr).to(torch.bfloat16).clone()
        elif t.name == "output.weight":
            arr = dequantize(t.data, t.tensor_type)
            lm_head = torch.from_numpy(arr).to(torch.bfloat16).clone()
    if embed_tokens is None:
        raise SystemExit("token_embd.weight not found in GGUF")
    if lm_head is None:
        # Qwen3.6 ties weights; fall back to embed
        lm_head = embed_tokens.clone()

    vocab_size = embed_tokens.shape[0]
    hidden_size = embed_tokens.shape[1]
    print(f"verifier vocab={vocab_size} hidden={hidden_size}")

    # 3. Build t2d/d2t.
    draft_vocab = args.draft_vocab_size if args.draft_vocab_size else vocab_size
    if draft_vocab == vocab_size:
        # Identity mapping (no reduction)
        t2d = torch.ones(vocab_size, dtype=torch.bool)
        d2t = torch.zeros(vocab_size, dtype=torch.long)
    else:
        # Reduce by token frequency
        if args.token_freq_path is None or not args.token_freq_path.is_file():
            raise SystemExit("--draft-vocab-size requires --token-freq-path")
        freq = torch.load(args.token_freq_path, weights_only=True)
        # freq is dict {token_id: count}
        if isinstance(freq, dict):
            pairs = sorted(freq.items(), key=lambda x: -x[1])
            top = [tid for tid, _ in pairs[:draft_vocab]]
        else:
            top = freq.topk(draft_vocab).indices.tolist()
        keep = sorted(top)
        t2d = torch.zeros(vocab_size, dtype=torch.bool)
        for tid in keep:
            t2d[tid] = True
        d2t = torch.tensor(keep, dtype=torch.long)
        embed_tokens = embed_tokens[keep, :].clone()
        lm_head = lm_head[keep, :].clone()
        print(f"reduced vocab to {draft_vocab} (top-frequency)")

    tensors["embed_tokens.weight"] = embed_tokens
    tensors["lm_head.weight"] = lm_head
    tensors["verifier_lm_head.weight"] = lm_head.clone()
    # speculators expects a `verifier_norm.weight` for the soft-target path.
    # Pull it from the z-lab draft (which has `norm.weight` — the output norm
    # the lucebox daemon uses for the same purpose).
    if "norm.weight" in tensors:
        tensors["verifier_norm.weight"] = tensors["norm.weight"].clone()
    tensors["t2d"] = t2d
    tensors["d2t"] = d2t

    save_file(tensors, str(args.output / "model.safetensors"))
    print(f"wrote {len(tensors)} tensors to {args.output / 'model.safetensors'}")

    # 4. Write a speculators-style config.json.
    #    Use the z-lab draft's config.json as a base and add the speculators
    #    bookkeeping fields. speculators reads aux_hidden_state_layer_ids,
    #    block_size, max_anchors, mask_token_id, and transformer_layer_config.
    zlab_cfg = json.loads((args.lucebox_draft / "config.json").read_text())
    spec_cfg = {
        "architectures": ["DFlashDraftModel"],
        "speculators_model_type": "dflash",
        "speculators_version": "0.5.0",
        "draft_vocab_size": draft_vocab,
        "aux_hidden_state_layer_ids": zlab_cfg.get("dflash_config", {}).get("target_layer_ids", [1, 16, 31, 46, 61]),
        "block_size": zlab_cfg.get("block_size", 16),
        "max_anchors": 256,
        "mask_token_id": zlab_cfg.get("dflash_config", {}).get("mask_token_id", 248077),
        "tie_word_embeddings": False,
        "transformer_layer_config": {
            "model_type": "qwen3",
            "hidden_size": zlab_cfg.get("hidden_size", 5120),
            "intermediate_size": zlab_cfg.get("intermediate_size", 17408),
            "num_hidden_layers": zlab_cfg.get("num_hidden_layers", 5),
            "num_attention_heads": zlab_cfg.get("num_attention_heads", 32),
            "num_key_value_heads": zlab_cfg.get("num_key_value_heads", 8),
            "head_dim": zlab_cfg.get("head_dim", 128),
            "hidden_act": zlab_cfg.get("hidden_act", "silu"),
            "rms_norm_eps": zlab_cfg.get("rms_norm_eps", 1e-6),
            "vocab_size": vocab_size,
            "max_position_embeddings": zlab_cfg.get("max_position_embeddings", 262144),
            "layer_types": zlab_cfg.get("layer_types", ["full_attention"] * zlab_cfg.get("num_hidden_layers", 5)),
            "sliding_window": zlab_cfg.get("sliding_window"),
            "use_sliding_window": zlab_cfg.get("use_sliding_window", False),
            "attention_bias": False,
            "attention_dropout": 0.0,
        },
    }
    (args.output / "config.json").write_text(json.dumps(spec_cfg, indent=2))
    print(f"wrote config.json")


if __name__ == "__main__":
    main()
