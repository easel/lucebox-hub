# DFlash agent-draft training: iteration plan

## Goal

Produce a DFlash draft model that **outperforms `z-lab/Qwen3.6-27B-DFlash` on
Codex-style agent traffic** when deployed in `dflash/build/test_dflash` against
the Qwen3.6-27B Q4_K_M target.

### Quantitative target

| Metric | Baseline (z-lab) | First-pass target | Stretch |
|---|---|---|---|
| AL on held-out agent traces | 3.20 | **≥ 4.5** | ≥ 6.0 |
| Decode tok/s on real agent traffic | 29 | ≥ 40 | ≥ 60 |
| Eval set | 200 held-out Codex sessions | same | same |

### Stop conditions

- Hit first-pass target on held-out eval, OR
- Three consecutive iterations show < 0.2 AL improvement, OR
- Exhausted compute (no fixed wall clock yet; budget per iteration is ~4 h on
  this 3090 Ti).

## Pipeline (stable as of this branch)

```
Codex sessions  ──► codex_to_speculators.py     (CPU, ~min)
                ──► prepare_data.py             (CPU, ~min)
                ──► fix_loss_mask.py            (CPU, ~min)
                ──► capture_traces.py           (GPU, ~10 s/prompt)
                ──► dumps_to_speculators.py     (CPU, ~min)
                ──► speculators train.py        (GPU, ~min/epoch/sample)
                ──► speculators_to_lucebox.py   (CPU, ~min)
                ──► drop into dflash/models/draft-trained/ and bench
```

## Iterations

### Iteration 1 — real verifier features (architectural, NOT skippable)

**Why first:** without real verifier features the speculators training has no
useful supervision signal — the model can't learn what the target would predict
at each position. Current pipeline stubs the verifier by duplicating the last
intermediate; loss never goes below random.

**Work:**

1. Extend `test_dflash.cpp` capture path: after target prefill, also apply
   `rms_norm + w.out_norm` to the activation at every position (currently only
   done for the last position to seed decode) and append the result to the
   DFCP dump as a 6th feature stripe.
2. Update `dumps_to_speculators.py` to read 6 features and drop the stub
   duplication.
3. Re-capture the same 10 sample bench set, retrain 1 epoch, verify loss is
   meaningfully different from the stub-verifier run.

**Success criterion:** validation loss after 1 epoch < 9.0 (random is ~11.1).

### Iteration 2 — scale to 1000 samples

**Work:**

1. `capture_traces.py /home/erik/.codex/sessions` for 1000 sessions ≈ 3 h.
2. `prepare_data` with `--max-samples 1000`, then `fix_loss_mask`, then drop
   empty-mask rows. Expect ~600 effective samples.
3. Train 5 epochs.
4. Hold out the first 200 sessions (by sort order) for eval — capture them
   separately into a non-overlapping `/tmp/codex_eval_200/`.

**Success criterion:** AL on the held-out 200 samples ≥ 4.0.

### Iteration 3 — SWA layer types

**Why:** z-lab's draft uses 4 sliding-attention + 1 full layer. We trained
all-full so far. The trained draft can technically run in lucebox without SWA
(layers default to full attention) but matches the deployed architecture
better with SWA on.

**Work:**

1. Find how speculators sets `layer_types` on the draft. Patch
   `create_transformer_layer_config` to allow `--draft-layer-types sliding,sliding,sliding,sliding,full`.
2. Retrain.
3. Convert (the lucebox draft loader already reads `layer_types` from config).
4. Bench.

**Success criterion:** AL ≥ Iteration 2 AL (i.e. no regression from SWA).

### Iteration 4 — hyperparameter sweep (only if first three didn't hit target)

Levers: LR ∈ {1e-4, 3e-4, 1e-3}, block_size ∈ {8, 16, 32}, max_anchors ∈ {32, 128, 256}, num_layers ∈ {3, 5, 7}.

Each combo ≈ 30 min on 3090 Ti at 1000 samples × 3 epochs. ~12 combos = ~6 h.

## Capture/training compute budget (3090 Ti)

| Step | Per-sample cost | At 1000 samples |
|---|---|---|
| capture_traces (target prefill + dump) | ~7 s | ~2 h |
| prepare_data + fix_loss_mask | ~ms | < 1 min |
| dumps_to_speculators | ~ms | < 1 min |
| speculators train.py (1 epoch) | ~? (TBD) | TBD |
| Total per iteration | — | < 4 h |

Disk: ~150 MB per sample × 1000 = 150 GB scratch. We have 3.4 TB free.

## Status as of session-end

- [x] Pipeline working end-to-end with stub verifier (proves all interfaces)
- [ ] Iteration 1: real verifier features (NEXT)
- [ ] Iteration 2: 1000-sample run
- [ ] Iteration 3: SWA training
- [ ] Iteration 4: HP sweep (contingent)
