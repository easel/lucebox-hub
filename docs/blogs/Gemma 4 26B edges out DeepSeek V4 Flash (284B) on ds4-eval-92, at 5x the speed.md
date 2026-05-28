# Gemma 4 26B edges out DeepSeek V4 Flash (284B) on ds4-eval-92, at 5x the speed

*May 2026 · by [Davide Ciffa](https://x.com/davideciffa) and [Erik LaBianca](https://x.com/easel)*

We expected the 192 GB Mac to have the edge: far more memory, a far bigger model.
It didn't pan out. On ds4-eval-92, Gemma 4 26B (26B params, 4-bit, in 24 GB) tied
DeepSeek V4 Flash (284B params, run at ~2-bit to fit the Mac) at 78.3%, edged it
to 79.3% on that same Mac, and decoded about 5x faster.

> [Hero image: Gemma 4 26B on an RTX 5090 Laptop next to DeepSeek V4 on a MacBook]

## TL;DR

- ds4-eval-92, nothink: Gemma 4 26B (26B params, Q4_K_M, 24 GB) and DeepSeek V4
  Flash (284B params, ~2-bit, 192 GB Mac) both score 78.3%, and Gemma noses ahead
  to 79.3% on that same Mac via MLX. A model an eleventh the size, holding even.
- The gap is efficiency: 101.4 tok/s for Gemma vs 20.7 for DeepSeek (~5x decode),
  a 9.8 s median answer against 144.8 s, in 24 GB instead of 192.
- Why: Gemma 4 26B (a4b) activates ~4B params per token against DeepSeek's 13B, so
  batch-1 decode reads far less weight per step. DFlash amortizes that further, and
  Q4_K_M fits the whole model in 24 GB.
- DeepSeek lands ~78% in every mode and provider we measured; we run Gemma in
  nothink, whose accuracy is within noise of its think score.

## The benchmark

ds4-eval-92 comes from [antirez/ds4](https://github.com/antirez/ds4), Salvatore
Sanfilippo's DeepSeek V4 Flash engine, the same one we're running on the Mac here.
We ported its 92-case `ds4_eval.c` set into luce-bench; the provenance, grading,
and request rules are in
[Running the benchmarks](<Running the benchmarks — an intro to luce-bench.md>).
In our current run set, the top results cluster around 80-82% (see
[the full board](<Every model we've run on ds4-eval-92.md>)), so this is not a benchmark where
one model runs away with it.

## What we compared

Local Gemma 4 26B (26B total, ~4B active, Q4_K_M in 24 GB; RTX 5090 Laptop,
lucebox + DFlash) against local DeepSeek V4 Flash (284B total, 13B active, run at
ds4's ~2-bit IQ2_XXS to fit; 192 GB Mac Studio, M2 Ultra, 60-core GPU, native
`ds4_server`). Each at the size, quant, and mode you'd run locally, same eval set,
same `max_tokens` policy, same scoring. We run Gemma in nothink (see
[think vs nothink](<Think vs nothink on Gemma 4 — same accuracy, 10x the latency.md>));
DeepSeek runs in think and lands ~78% in every mode and provider we tried, so the
comparison doesn't hinge on its mode.

## Head to head

Each model at the size, quant, and mode you'd run locally:

| Model | Where | Mode | Pass | Accuracy | Wall (med) | tok/s |
|---|---|---|---|---|---|---|
| Gemma 4 26B (26B, 4-bit) | RTX 5090 Laptop, 24 GB | nothink | 72/92 | 78.3% | 9.8 s | 101.4 |
| DeepSeek V4 Flash (284B, ~2-bit) | Mac Studio, 192 GB | think | 72/92 | 78.3% | 144.8 s | 20.7 |

## Accuracy

> [Chart: ds4-eval-92 accuracy, nothink Gemma vs think DeepSeek. Both = 78.3%.]

It's close. On the laptop in nothink it's a dead heat, 78.3% each (72/92). On the
same Mac via MLX, Gemma noses ahead (79.3%).
So a 26B model edges a 284B one on this set. State the qualifier plainly: to run on the
Mac at all the big model is squeezed to ~2-bit, while Gemma runs at 4-bit, so part
of the story is that 284B at 2-bit doesn't pull away from 26B at 4-bit here.
DeepSeek V4 Flash is a strong model and this is one benchmark; the point isn't
that Gemma is better, it's that a model an eleventh the size kept pace, far more
efficiently. (Gemma's think and nothink scores are within noise; nothink is what
we'd run, see [think vs nothink](<Think vs nothink on Gemma 4 — same accuracy, 10x the latency.md>).)

## Throughput

> [Chart: Decode throughput, local, tok/s. Gemma 4 26B (nothink) on RTX 5090 Laptop = 101.4 tok/s, DeepSeek V4 Flash (think) on Mac 192 GB = 20.7 tok/s.]

On the same prompts, the laptop Gemma run decodes about 4.9x faster (101.4 vs
20.7 tok/s). The median
completion lands in 9.8 s against 144.8 s. The result points away from raw Mac capacity as the main explanation. The
tested DeepSeek path reads more active weights per decoded token, while the
Gemma path combines a smaller active footprint with CUDA DFlash.

## Why the laptop is so fast

A 192 GB Mac has 8x the memory and runs a model 11x the size, so the result looks
backwards. We think three things explain it, plus a fourth that doesn't.

- *Only ~4B active per token.* Gemma 4 26B (a4b) is a 26B MoE with roughly 4B
  active parameters per token. Batch-1 decode is bandwidth-bound, so what matters
  is bytes read per token, not total parameter count. Touching ~4B 4-bit weights
  per step is a small fraction of DeepSeek V4 Flash's 13B active (of 284B total).
  This is the main reason the laptop path is so fast.
- *DFlash speculative decode.* Each verified target step commits multiple
  accepted tokens per weight pass, amortizing the bandwidth-bound matmul across
  the accept window, on top of the already-small a4b footprint.
- *The model size is right.* 26B in Q4_K_M fits in 24 GB with room for a long
  context. DeepSeek V4 Flash is large enough that local Mac serving has to trade
  throughput against a usable context window.
- *Raw memory bandwidth alone does not explain it.* It's tempting to credit dedicated VRAM, but the M2
  Ultra's unified memory runs ~800 GB/s, in the same range as the laptop's GDDR7.
  The useful distinction is bytes read per committed token: Gemma touches fewer
  active weights per step, and DFlash can commit multiple accepted tokens per
  target pass. Capacity matters for fitting the model, but it does not explain
  this throughput gap by itself.

## Same Mac, smaller model

The laptop makes the speed gap dramatic, but it isn't what wins on quality. We
also ran Gemma 4 26B on the *same* 192 GB Mac Studio through Apple MLX (8-bit,
nothink): 79.3% on ds4-eval-92, a point above DeepSeek V4 Flash's 78.3% on that
box, and at ~40 tok/s against 20.7. On identical hardware, each model on its own
local stack, the small MoE held its own. This does not isolate model architecture from engine, quant, hardware, or
speculative decoding. It measures the local stacks we would actually run. It
shows that a 4B-active MoE can match a much larger one on this eval while
costing far less to run. (Caveat: different engines and quants, MLX
8-bit vs `ds4_server`,
and Gemma's nothink runs about level with its think, per
[think vs nothink](<Think vs nothink on Gemma 4 — same accuracy, 10x the latency.md>).)

## A note on serving

Gemma 4 26B is sensitive to how it's served: the same model on OpenRouter scored
73.9%, about 5 points under our local lucebox serve, while DeepSeek holds its
~78% across providers. We pull that thread in
[Gemma 4 26B across serving paths](<Gemma 4 26B across serving paths — a laptop GPU, a 3090 Ti, MLX, and OpenRouter.md>).

## Takeaway

DeepSeek V4 Flash is a quality model, and this isn't a knock on it. On
ds4-eval-92, in the local stacks we tested, a 24 GB laptop running Gemma 4 26B
matched it on accuracy and ran ~5x faster. On the same Mac, the smaller model
held its own. Read it
this way: a small MoE that happens to be strong on your workload can deliver that
quality at a fraction of the memory and latency. Find the model that does well on
your tasks, then size the hardware to it.

---

*ds4-eval-92 from antirez/ds4 (MIT), run via luce-bench, single seed. Hardware:
24 GB RTX 5090 Laptop vs 192 GB Mac Studio (M2 Ultra, 60-core GPU), local serving.
Project: [github.com/Luce-Org/lucebox-hub](https://github.com/Luce-Org/lucebox-hub).*

**Related**
- [Meet lucebox: a local AI inference engine optimized for consumer hardware](<Meet lucebox — a local AI inference engine optimized for consumer hardware.md>)
- [Running the benchmarks: an intro to luce-bench](<Running the benchmarks — an intro to luce-bench.md>)
- [Gemma 4 26B across serving paths: a laptop GPU, a 3090 Ti, MLX, and OpenRouter](<Gemma 4 26B across serving paths — a laptop GPU, a 3090 Ti, MLX, and OpenRouter.md>)
- [Think vs nothink on Gemma 4: same accuracy, 10x the latency](<Think vs nothink on Gemma 4 — same accuracy, 10x the latency.md>)
- [Every model we've run on ds4-eval-92](<Every model we've run on ds4-eval-92.md>)
