# Tuning Qwen3.6-27B decode on a 3090 Ti: the knobs that moved throughput

*May 2026 · by [Davide Ciffa](https://x.com/davideciffa) and [Erik LaBianca](https://x.com/easel)*

This started as a chase after a number that turned out to be wrong. An earlier
full-suite run on this box had Qwen3.6-27B decoding at around 11 to 13 tok/s,
which felt slow for a 27B dense model on a 3090 Ti when [club-3090](https://github.com/noonghunna/club-3090)
reports 52 to 60 tok/s for the same model on a single 3090. We expected to find a
tuning gap and close it. Instead the first clean measurement put the *default*
config at 51 tok/s, and the 11 to 13 figure dissolved into a measurement
artifact. The slow number was end-to-end completion over wall time (cold start
plus aggregated-block timing dragging the average down), not the decode rate.

So the real exercise was not "fix a slow box." It was "now that we are reading
the right number, which knobs actually move it." This is the lab notebook for
that sweep.

TL;DR:

- The earlier 11 to 13 tok/s was a wall-time artifact. A clean decode probe has
  the default config at 51.17 tok/s.
- DFlash speculative decode is doing the heavy lifting: 51.17 tok/s on, 20.47
  off, about 2.5x.
- KV-cache type is the single biggest knob after that. The server-default tq3_0
  came out well ahead of q4_0 and q8_0 on speed.
- Bigger speculative budgets were slower, not faster. Budget 16 was the fastest
  cell in the sweep.
- PFlash prefill in auto mode raised decode and lowered VRAM at the same time.
- This sweep measured decode throughput and VRAM only. Accuracy was not graded
  per cell. The "fastest" config below has a quality check still pending.

## Setup

One machine: sindri, a desktop RTX 3090 Ti, 24 GB. The power limit was held at
225 W for every cell. This is a tuning story about instructions-per-token and
memory, not a power story, so we did not touch the limit. Raising it is a
last-resort lever we deliberately left alone.

The model is Qwen3.6-27B, dense, Q4_K_M unless a cell says otherwise, served by
luce-dflash with DFlash speculative decode. Mode is nothink throughout.

The measurement is a fixed decode probe: 3 prompts, 256 max-tokens each, reading
the daemon's own per-probe `decode_tps` from `usage.timings`. That is the clean
decode rate, not end-to-end completion over wall time. The distinction is the
whole reason this post exists. The harness and the broader methodology live in
[Running the benchmarks](<Running the benchmarks — an intro to luce-bench.md>);
this post only covers the decode sweep.

The sweep ran in stages. A step-0 control to establish the default and to
measure DFlash on versus off, then three sweeps that each varied one family of
knobs while holding the rest at the step-0 best.

## Step 0: the control, and what DFlash is worth

The default heuristic config (budget 16, max context 65536, KV at the server
default tq3_0, DFlash on) decodes at 51.17 tok/s with a peak of about 20.2 GB.
Turning the draft off and leaving everything else identical drops it to 20.47
tok/s.

| Config | Decode tok/s | Peak VRAM |
|---|---|---|
| Default, DFlash on | 51.17 | ~20.2 GB |
| Same, DFlash off | 20.47 | ~18.8 GB |

That 20.47 is the autoregressive floor for this model on this card. DFlash is
worth about 2.5x on top of it. Worth saying clearly: this speedup is lossless.
The draft model proposes tokens, the target model verifies them, and the tokens
that get accepted are exactly the ones the target would have produced on its own.
DFlash changes how fast the answer comes out, not what the answer is.

## Sweep 1: speculative budget and KV-cache quant

This sweep crossed the speculative tree budget (the ddtree budget) with the
KV-cache quant type, at 65 K context with prefill off.

| Budget | KV quant | Decode tok/s | Peak VRAM |
|---|---|---|---|
| 16 | tq3_0 | 51.07 | ~20.2 GB |
| 22 | tq3_0 | 44.13 | ~20.7 GB |
| 32 | tq3_0 | 42.17 | ~21.4 GB |
| 8  | q8_0  | 34.30 | ~21.4 GB |
| 16 | q4_0  | 37.33 | ~20.4 GB |
| 16 | q8_0  | 35.30 | ~21.4 GB |
| 22 | q8_0  | 28.20 | ~21.9 GB |
| 32 | q8_0  | 25.27 | ~22.6 GB |

Two things came out of this, and one of them was a surprise.

The expected result: KV-cache type matters a lot. The tq3_0 server default ran
well ahead of both q4_0 and q8_0. At budget 16, tq3_0 hit 51.07, q4_0 hit 37.33,
and q8_0 hit 35.30. The server's kernels are tuned around tq3_0, and the
heavier 8-bit cache costs both speed and VRAM with nothing to show for it on
throughput.

The surprise: a bigger speculative budget was slower. We went in assuming a
larger tree would accept more tokens per step and pull the rate up. It went the
other way. tq3_0 dropped from 51.07 at budget 16 to 44.13 at 22 to 42.17 at 32.
A larger draft tree costs more to build and verify than the extra accepted tokens
pay back on these short probes, so 16 was the sweet spot. We only tested budget 8
on the q8_0 cache, not on tq3_0, and there the q8_0 choice was already dragging
the rate down to 34.30, so that cell says little about what budget 8 would do on
the fast path.

Both of these levers are lossless for the same reason DFlash is: the budget only
changes how many candidate tokens the draft tree proposes per step, and the
target still verifies every accepted token. KV-cache quant is different and we
come back to it under quality below.

The data also carries a `lazy` flag (lazy 0 at 51.07 versus lazy 1 at 47.33 on
the same cell), but the build appears to ignore it unless a prefill-drafter is
configured (`props.json` reports `lazy_draft: false` even when the flag is set),
so we are treating that difference as inconclusive rather than a real knob.

## Sweep 2: context length and PFlash prefill

Holding budget 16 and tq3_0, this sweep crossed max context with PFlash prefill
mode.

| Max ctx | Prefill | Decode tok/s | Peak VRAM |
|---|---|---|---|
| 32768 | off  | 36.67 | ~19.8 GB |
| 65536 | off  | 35.50 | ~20.2 GB |
| 98304 | off  | 40.20 | ~20.7 GB |
| 32768 | auto | 48.00 | ~18.8 GB |
| 65536 | auto | 44.03 | ~19.3 GB |

Max context from 32 K to 98 K barely moved decode rate on these short prompts.
The cells are close enough that the ordering is mostly variance, so the sane way
to choose max context here is on VRAM headroom, not speed. More context costs a
little more VRAM and buys nothing for throughput on short inputs.

PFlash auto did something nicer: it raised decode and lowered VRAM at the same
time. At 32 K it took the rate from 36.67 to 48.00 and the peak down to about
18.8 GB. Our probe prompts are short (30 to 40 tokens, well under the auto
trigger threshold), so part of this gain is variance rather than prefill doing
real work, and we would not bank the exact delta. But PFlash is the one knob in
this group worth flagging for quality, because unlike the budget and the draft
tree, PFlash prefill can be lossy. It approximates the prefill pass, so a
prefill-mode change is a quality-relevant change.

## Sweep 3: target model quant

Holding the best DFlash config, this sweep varied the target GGUF.

| Target quant | Decode tok/s | Peak VRAM |
|---|---|---|
| Q4_K_M | 48.60 | ~19.8 GB |
| IQ4_XS | 48.27 | ~18.5 GB |
| Q5_K_M | 34.40 | ~22.2 GB |

Q4_K_M and IQ4_XS decode at the same rate, but IQ4_XS does it in about 1.3 GB
less VRAM, which is real headroom on a 24 GB card already running near 20.
Q5_K_M is about 20% slower and 2 GB heavier, because the larger weights press on
memory bandwidth and there is no spare VRAM to absorb the KV cache anyway. Target
quant is the third quality-relevant knob: changing it changes the weights the
target verifies against, so it can change outputs.

## Quality: measured separately

Everything above is decode throughput and VRAM. It is worth being plain about
what the `ok` column in the data means: it counts probes that completed, not
answers that were correct. Nothing here grades accuracy per cell.

That matters most for the fastest config. tq3_0 is an aggressive 3-bit KV-cache
quant, and a 3-bit cache can cost accuracy in ways a throughput probe will never
see. So we are not crowning tq3_0/budget-16 a recommended config. It is the
fastest cell in this throughput sweep, with a quality check still owed.

The split is clean, though, and worth holding onto:

- Lossless knobs (speed only, no quality sweep needed): DFlash on/off, the
  speculative budget, the draft tree. The target verifies every accepted token,
  so these cannot change the output.
- Quality-relevant knobs (need grading): KV-cache quant, target model quant,
  and PFlash prefill mode. The first two change what gets computed or verified
  against, and PFlash can be lossy.

A graded sweep over the quality-relevant knobs is queued and the numbers will be
folded in here when it lands. The one accuracy anchor we have today is that the
default tq3_0 config scored 57.6% on ds4-eval-92 nothink over the full 92, but
that is a single point on the default config and does not isolate the KV-quant
cost, so do not read it as a verdict on tq3_0. (For the broader serving-stack
quality picture, see the [serving-paths comparison](<Gemma 4 26B across serving paths — a laptop GPU, a 3090 Ti, MLX, and OpenRouter.md>).)

## What the sweep says

The headline correction stands on its own: the box was never slow. The default
config decodes at 51 tok/s, which lands right inside club-3090's reported 52 to
60 tok/s for this model on a single 3090. Their setup uses MTP speculative
decode and ours uses DFlash, so this is a comparison across two speculative
schemes that happen to converge on similar throughput on similar silicon, and
we credit them for the reference point that sent us looking.

On the knobs themselves: KV-cache type is the big speed lever, the tq3_0 default
already sits at the fast end, the speculative budget wants to stay at 16 rather
than climb, and PFlash auto plus IQ4_XS both lower VRAM without costing decode
rate. The work that is left is quality, on the three knobs that can actually move
it.

All of this is one machine, one 3090 Ti, nothink, a small fixed decode probe,
power-limited to 225 W. The decode rate is mode-independent and should travel;
the exact VRAM peaks and the quality picture are specific to this card and this
config. If you would rather not run this sweep by hand, the auto-tuner does the
same shape of search and gates each candidate on capability and quality before it
persists anything, which is the right tool for getting a matched config without
hand-rolling flags: see [How lucebox auto-tunes itself to your GPU](<How lucebox auto-tunes itself to your GPU.md>).

---

*Decode probe on sindri (RTX 3090 Ti, 24 GB, 225 W), Qwen3.6-27B dense, nothink,
luce-dflash + DFlash. Single machine, 3 prompts × 256 max-tokens, reading
per-probe decode_tps. Throughput and VRAM only; accuracy not graded per cell.
Full sweep data:
`Luce-Org/luce-bench-baselines/sindri-rtx3090ti-qwen36-27b-2026-05-28-decode-tuning`.
External anchor: [club-3090](https://github.com/noonghunna/club-3090). Project:
[github.com/Luce-Org/lucebox-hub](https://github.com/Luce-Org/lucebox-hub).*

**Related**
- [How lucebox auto-tunes itself to your GPU](<How lucebox auto-tunes itself to your GPU.md>)
- [Meet lucebox: a local AI inference engine optimized for consumer hardware](<Meet lucebox — a local AI inference engine optimized for consumer hardware.md>)
- [Running the benchmarks: an intro to luce-bench](<Running the benchmarks — an intro to luce-bench.md>)
- [What `/props` tells you about a lucebox server](<What props tells you about a lucebox server.md>)
- [Putting Qwen's thinking on a budget: counting tokens and forcing the close](<Putting Qwen's thinking on a budget — counting tokens and forcing the close.md>)
- [Gemma 4 26B across serving paths: a laptop GPU, a 3090 Ti, MLX, and OpenRouter](<Gemma 4 26B across serving paths — a laptop GPU, a 3090 Ti, MLX, and OpenRouter.md>)
