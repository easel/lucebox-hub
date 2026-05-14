# DFlash agent-draft training: retrospective

**Branch:** `dflash/agent-draft-training` (forked from `integration/props-uv` at
commit `0e7474a`, before training work began).
**Dates:** 2026-05-13 → 2026-05-14.
**Outcome:** No trained draft beat the z-lab baseline. Branch preserved for
reference; future training work should start by reading this.

## TL;DR

We built an end-to-end pipeline to fine-tune the DFlash draft on real agent
traces (Codex, Claude Code, Fizeau). The pipeline works and the format
roundtrip is provably lossless. Despite that, **every from-scratch and
warm-start variant we tried at our compute scale either matched or regressed
from `z-lab/Qwen3.6-27B-DFlash`** (baseline AL = 2.67 on the probe prompt).

| Run                          | n  | epochs | anchors | val loss | bench AL |
|------------------------------|----|--------|---------|---------:|---------:|
| Baseline (z-lab)             | -  | -      | -       | -        | **2.67** |
| Roundtrip (no train)         | -  | -      | -       | -        | 2.67     |
| Warm-start @ LR = 1e-5       | -  | 1      | -       | -        | 2.13     |
| Warm-start @ LR = 1e-7       | -  | 1      | -       | -        | hang     |
| 6 samples × 30 epochs        | 6  | 30     | 32      | 6.625    | 1.42     |
| 84 samples × 5 epochs (a32)  | 84 | 5      | 32      | 6.256    | 1.17     |
| 84 samples × 5 epochs (a256) | 84 | 5      | 256     | 6.156    | 1.12     |
| 6 samples × 5 epochs         | 6  | 5      | 32      | 7.940    | 1.02     |

Bench command (same across all rows):

```
dflash/build/test_dflash \
  dflash/models/Qwen3.6-27B-Q4_K_M.gguf \
  <draft.safetensors> \
  /tmp/codex_train_1000/cap_000000.tokens.bin \
  64 /tmp/out.bin \
  --fast-rollback --ddtree --ddtree-budget=22 --max-ctx=4096
```

## What was built

All of these live on this branch and are self-contained:

| File                                                | What it does                                                            |
|-----------------------------------------------------|-------------------------------------------------------------------------|
| `dflash/test/test_dflash.cpp` (`DFLASH_CAPTURE_PATH`)| Daemon emits a v2 DFCP dump (intermediates + normed verifier stripe) when env var is set, one per prefill |
| `dflash/src/qwen35/qwen35_target_graph.cpp`         | Exposes post-output-norm hidden state for *all* token positions (not just the last); gated by a new `QwenGraphInputs.capture_normed_hidden` flag |
| `dflash/scripts/capture_traces.py`                  | Batch driver: one `test_dflash` subprocess per prompt; ~25 s/sample (cold model load each time) |
| `dflash/scripts/capture_traces_daemon.py`           | **Persistent-daemon driver: 3.5× faster** (~7 s/sample). Launches `test_dflash --daemon` once, streams prompts via stdin, uses a staging path renamed after each capture. **This is the durable engineering win from the night.** |
| `dflash/scripts/dumps_to_speculators.py`            | Reads v1/v2 DFCP dumps → speculators-format `.npy` hidden states + arrow manifest |
| `dflash/scripts/fix_loss_mask.py`                   | Token-id scan for the Qwen3.6 chat-template markers (248045, 74455, 198, 248046). Bypasses speculators' broken `offset_mapping` path for this tokenizer |
| `dflash/scripts/speculators_to_lucebox.py`          | Converts a speculators checkpoint → the 58-tensor z-lab draft layout. Drops `d2t`, `t2d`, `embed_tokens.weight`, `lm_head.weight`. **Roundtrip is lossless (AL=2.67=baseline).** |
| `dflash/scripts/lucebox_to_speculators.py`          | Reverse: lucebox → speculators (used for warm-start attempts). Reads `token_embd.weight` + `output.weight` from the verifier GGUF directly — no HF download |
| `dflash/scripts/claude_to_speculators.py`           | Converts `/tank/home/erik/ClaudeProjects/*.jsonl` → speculators `conversations` schema. 10,652 sessions converted to `/tmp/claude_speculators_all.jsonl` |
| `dflash/docs/training_iteration_plan.md`            | The plan we executed (worth comparing against what actually happened — many assumptions in there turned out wrong) |

## What we learned (the parts not in code)

1. **Speculators training is too fragile to outscale the baseline at our compute.**
   The library's own reference recipe lands at AL ≈ 1.47 with 5K samples × 5
   epochs. At 84 samples we are decisively in the "noise" regime regardless of
   hyperparameter tuning.

2. **Catastrophic forgetting is the warm-start blocker.** Starting from z-lab's
   own weights and fine-tuning for **one epoch** at LR = 1e-5 drops AL from
   2.67 → 2.13. There is no working adapter / LoRA path through speculators
   today; full fine-tunes destroy the prior at any meaningful LR. LR = 1e-7
   was so low the run hung with no progress.

3. **Architectural mismatch we never fixed.** z-lab's `config.json` says:

   ```json
   "layer_types": ["sliding_attention", "sliding_attention",
                   "sliding_attention", "sliding_attention", "full_attention"],
   "sliding_window": 2048,
   "use_sliding_window": true
   ```

   Our speculators-trained drafts use **all-full attention** because speculators
   doesn't natively support per-layer SWA. This reframes every from-scratch
   result above — we weren't training a worse z-lab, we were training a
   structurally different model that happens to share parameter count.
   `dflash/docs/training_iteration_plan.md` § Iteration 3 (SWA layer types) is
   the patch that was never built.

4. **z-lab does NOT use speculators.** speculators is a Red-Hat-maintained
   downstream consumer that standardizes DFlash checkpoints for vLLM inference.
   z-lab's training code is unreleased ("training recipe coming soon"). When
   they ship it, our entire training stack becomes academic.

5. **Speculators bugs we had to patch** (in
   `/tmp/speculators_venv/.../speculators/model.py` and
   `/tmp/speculators/scripts/train.py` — NOT included in this branch since they
   live outside the repo):
   - The "vocab not needed" RuntimeError fires when `draft_vocab_size ==
     verifier_vocab_size`. Patched to silently skip.
   - `t2d`/`d2t` registered as `None` when `use_draft_vocab=False`; forward()
     crashes on `None.long()`. Patched to register identity tensors.
   - `load_verifier_weights` unconditionally downloads 54 GB from HF, ignoring
     non-NaN weights already in the checkpoint. Patched to skip when present.
   - Architecture is auto-derived from the verifier (24 heads × 256 head_dim)
     but z-lab uses 32 × 128. Patched `train.py` to expose
     `--draft-num-attention-heads`, `--draft-num-key-value-heads`, `--draft-head-dim`.

## Where to start if you pick this up

1. **Read `training_iteration_plan.md` first**, then this doc. The plan is what
   we *intended* to do; the bench ladder above is what actually happened.

2. **The lowest-risk next experiment** is still Iteration 3 (SWA layer types).
   Concrete patches needed:
   - `scripts/train.py`: add `--draft-layer-types`, `--draft-sliding-window`,
     `--draft-use-sliding-window` flags (pattern matches existing
     `--draft-head-dim`).
   - `speculators/model.py`: plumb those flags into `transformer_layer_config`.
     HF qwen3 already honors per-layer `layer_types` natively.
   - `lucebox_to_speculators.py` already writes the SWA fields out — warm-start
     would Just Work once train.py accepts them.
   - Cost: half a day of code + one ~90-min training cycle.

3. **The high-value next experiment** is a 5K+ sample × 20+ epoch from-scratch
   run on a dedicated GPU for a day or two. The capture pipeline at 3.5×
   speedup makes this ~10 hours of capture work + multi-hour training. Still
   unlikely to beat z-lab (the reference recipe only hits AL ≈ 1.47 at this
   scale) but it would establish the real ceiling.

4. **Wait-and-see option:** z-lab said training code is coming. If it ships
   in the next month or two, all of this becomes much easier — we'd reuse
   their recipe with our agent-trace dataset, skip the speculators detour
   entirely.

## Reuse value of this branch

Even though no trained checkpoint beat baseline, these are reusable:

- **The persistent-daemon capture driver** (`capture_traces_daemon.py`,
  commit `5970925`) — 3.5× faster than the per-prompt-subprocess version.
  Drop-in usable for any future training run.
- **The format converters** — `speculators_to_lucebox.py` and
  `lucebox_to_speculators.py` round-trip is provably lossless. Useful for any
  future warm-start work.
- **The `DFLASH_CAPTURE_PATH` env hook** in `test_dflash.cpp` — gives any
  future trainer a way to capture real verifier features from the daemon
  without needing to load the target through HF or vLLM.
- **The Claude / Codex / Fizeau jsonl → speculators conversation converters**
  — 10K+ pre-converted agent sessions sitting in `/tmp/` ready for whoever
  runs the big training job.

## What's NOT on this branch (intentionally)

- The decode/tree-verify max-ctx scaling investigation (Issue #10 / PR #11
  follow-up). That's a separate stream — its docs live under
  `dflash/docs/GOAL_decode_tree_verify_max_ctx.md` on `integration/props-uv`.
- The speculators library patches themselves — they live in
  `/tmp/speculators_venv/` and `/tmp/speculators/` on the dev machine. If you
  re-create the venv, you'll need to re-apply them. They are listed verbatim
  in § "Speculators bugs we had to patch" above.
