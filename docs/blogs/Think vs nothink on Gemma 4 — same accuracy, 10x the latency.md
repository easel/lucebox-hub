# Think vs nothink on Gemma 4: same accuracy, 10x the latency

*May 2026 · by [Davide Ciffa](https://x.com/davideciffa) and [Erik LaBianca](https://x.com/easel)*

On most reasoning models, turning "thinking" on trades latency for accuracy, and
we assumed Gemma 4 26B would be the same. It mostly isn't. Across two local rigs
on ds4-eval-92, think mode sits within noise of nothink on accuracy (on one rig
nothink came out ahead) while costing about 10x the wall time. The reason is
mechanical: for Gemma 4 the think/nothink switch routes reasoning into a separate
*channel*, it doesn't gate how much the model reasons.

> [Hero image: two bars, think vs nothink accuracy nearly equal, think wall time 10x taller]

## TL;DR

- Accuracy is a wash. ds4-eval-92: RTX 5090 Laptop think 80.4% vs nothink 78.3%;
  RTX 3090 Ti think 75.0% vs nothink 79.3%. Think helps ~2 points on one box and
  loses ~4 on another. No consistent direction.
- Latency isn't. Same 5090 Laptop: think median wall 100.5 s vs nothink 9.5 s, a
  10x tax for no reliable accuracy gain.
- On the 8 hardest ds4 cases, nothink passed 5/8 (62.5%); the best single thinking
  budget passed 2/8 (25%).
- A per-case picker does better than either: routing each case to its best mode
  hits 6/8 (75%).
- `enable_thinking` chooses which channel the reasoning lands in
  (`reasoning_content` vs `content`), not whether the model reasons. It isn't the
  compute knob it is on Qwen3.

## The setup

All runs score the same `gemma-4-26b` Q4_K_M through the `luce-dflash` daemon on
luce-bench's `ds4-eval` area, on two GPUs (RTX 5090 Laptop, RTX 3090 Ti). Eval
provenance and grading: [Running the benchmarks](<Running the benchmarks — an intro to luce-bench.md>). The only thing that changes
between "think" and "nothink" is the chat template's `enable_thinking` flag, and
it matters less than the name suggests.

## Accuracy: think barely moves it, and not in one direction

| Rig | think | nothink | Δ (think − nothink) |
|---|---|---|---|
| RTX 5090 Laptop (24 GB, DFlash) | 80.4% (74/92) | 78.3% (72/92) | +2.1 |
| RTX 3090 Ti (24 GB, DFlash) | 75.0% (69/92) | 79.3% (73/92) | −4.3 |

Think mode is +2 points on the laptop and −4 on the 3090 Ti. That's the shape of
a wash: run-to-run, rig-to-rig noise around the same ~78% band, not a thinking
dividend. (A separate single-seed laptop run scored think 81.5% / nothink 78.3%.
Same story, same band.)

## Latency: the part that isn't a wash

> [Chart: median wall time per ds4-eval answer, 5090 Laptop. think = 100.5 s, nothink = 9.5 s.]

On the 5090 Laptop the median think-mode answer takes 100.5 s and burns ~10k
completion tokens; the median nothink answer takes 9.5 s and ~1k tokens. You pay
roughly 10x the wall time and 10x the tokens for an accuracy delta inside the
noise. On a hard-reasoning workload, where thinking should earn its keep, on
Gemma 4 it mostly buys latency.

## On the hardest cases, nothink comes out ahead (a picker does better)

We took the 8 hardest ds4 cases (cross-backend disagreements plus universal-fail
cases) and swept thinking budgets ∈ {4k, 8k, 16k, 32k, 65k} against nothink:

| Mode | Pass on the 8-case subset |
|---|---|
| Always think, best single budget | 2/8 (25%) |
| Always nothink | 5/8 (62.5%) |
| Per-case picker (nothink vs 4k/65k think) | 6/8 (75%) |

Two findings fall out. First, nothink recovers cases thinking can't: four GPQA
Diamond cases that failed at every thinking budget (4k through 65k) pass with
thinking off. Given the `content` channel, Gemma terminates and commits; in the
dedicated reasoning channel it spirals and never finalizes. Second, some cases
genuinely need the headroom: `aime2025-02` passes only at 65k of thinking and
fails nothink. No global mode is optimal. The best policy is suite-aware routing,
GPQA Diamond to nothink and hard AIME to long think.

## Why the switch is cosmetic

Probing the mechanism directly (see
`docs/experiments/gemma4-26b-thinking-control-2026-05-25.md`) explains the wash:

- *`enable_thinking` only chooses the channel.* With thinking on, reasoning lands
  in `reasoning_content` and the visible `content` reply is short. With it off,
  the model still reasons, just inside `content`. Total compute is about the same; only the
  routing changes. Verbatim from the writeup: *"Pass-rate comparisons between
  --think/--no-think on Gemma 4 are measuring channel routing, not thinking
  behavior."*
- *nothink terminates better.* The `content` channel has a much stronger
  end-of-answer prior than the reasoning channel, so nothink runs hit a clean
  `stop` while think runs more often exhaust the budget at `length`. That's why
  nothink recovers hard cases instead of losing them.
- *Budget force-close produces garbage.* Hard-closing the thinking channel at a
  token budget cuts the model off mid-derivation, and the post-close `content` is
  incoherent. The budget is a guillotine here, not the graceful wrap-up Qwen3
  does.
- *Prompt-side control doesn't work.* Natural-language "answer briefly" or "don't
  reason" instructions are ignored, stop sequences hide output without saving
  compute, and an answer-prefill makes it worse. Reasoning is emergent from Gemma
  4's training, not instruction-gated.

Qwen3 is the opposite: a thinking budget triggers trained wrap-up behavior and is
a real effort dial. On Gemma 4 the dial isn't wired to compute.

## What we do with Gemma 4

We default to nothink for agentic and latency-sensitive use. You get the same
~78% at a tenth of the wall time and dodge the non-termination failure mode on
hard cases. We reserve long thinking for a known-hard tier like competition math,
ideally through per-case routing rather than a global flag. And we don't treat
`thinking: {budget}` as an effort knob on Gemma 4: report `wall_s` and
`completion_tokens` next to any think/nothink number so the latency cost stays
visible, because the conventional "think helps" reading inverts here.

## Reproduce

```bash
# nothink vs think on the same model, same cases
uvx luce-bench --area ds4-eval --base-url http://127.0.0.1:8080 \
  --model dflash --no-think --name gemma-nothink
uvx luce-bench --area ds4-eval --base-url http://127.0.0.1:8080 \
  --model dflash --think --name gemma-think

# single-case multi-budget probe (think/nothink/budget=N/...)
uvx --from 'luce-bench' lucebench-probe --case-id aime2025-02 \
  --url http://localhost:8080 --out-dir ./probes/gemma
```

---

*ds4-eval-92 from antirez/ds4 (MIT), run via luce-bench. Gemma 4 26B Q4_K_M via
luce-dflash on RTX 5090 Laptop and RTX 3090 Ti, single seed. Mechanism notes:
`docs/experiments/gemma4-26b-thinking-control-2026-05-25.md`.*

**Related**
- Meet lucebox: a local AI inference engine optimized for consumer hardware
- Running the benchmarks: an intro to luce-bench
- Gemma 4 26B edges out DeepSeek V4 Flash (284B), at 5x the speed
- Gemma 4 26B across serving paths: a laptop GPU, a 3090 Ti, MLX, and OpenRouter
- Every model we've run on ds4-eval-92
- Putting Qwen's thinking on a budget: counting tokens and forcing the close
- Qwen3.6 think vs nothink across providers: thinking helps, if you budget for it
- What /props tells you about a lucebox server
- How lucebox auto-tunes itself to your GPU
