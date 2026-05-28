# Qwen3.6 think vs nothink across providers: thinking helps, if you budget for it

*May 2026 · by [Davide Ciffa](https://x.com/davideciffa) and [Erik LaBianca](https://x.com/easel)*

We ran the same Qwen3.6-27B on ds4-eval-92 across four serving stacks, think and
nothink. Two things came out of it. Across the three 4-bit paths, nothink is
boringly consistent at ~55–58%, with one outlier: the 8-bit MLX serve scored 77%
nothink, which we flag below and cannot yet fully explain. Thinking is not boring:
with a full budget it adds 7–8 points, and with a starved budget it does worse
than not thinking at all. For Qwen, unlike Gemma 4, the thinking budget is a real
lever, and it cuts both ways.

> [Hero image: Qwen3.6 ds4-eval bars, nothink flat across providers, think split high/low]

## The numbers

| Serving | Mode | ds4-eval-92 | Note |
|---|---|---|---|
| RTX 3090 Ti (lucebox) | nothink | 57.6% | |
| RTX 5090 Laptop (lucebox) | nothink | 55.4% | |
| OpenRouter | nothink | 55.4% | |
| Mac Studio M2 Ultra (MLX 8-bit) | nothink | 77.2% | 8-bit; outlier, see below |
| OpenRouter | think | **63.0%** | full 16k budget |
| RTX 5090 Laptop (lucebox) | think | 32.6% | clamped 4k budget |
| Mac Studio M2 Ultra (MLX 8-bit) | think | _pending (run in flight)_ | |

<!-- TODO: fill the MLX think row from vidar-m2ultra-qwen3.6-27b-mlx8bit-ds4eval-think-2026-05-27 when the run completes (~30/92 as of last check). nothink backfilled: 77.2% (71/92). -->

## Nothink is stable across the 4-bit serves, with one outlier

Three independent 4-bit serves, three numbers within noise: 57.6%, 55.4%, 55.4%.
A desktop 3090 Ti on lucebox, a laptop 5090 on lucebox, and whatever OpenRouter
routes to all land in the same ~56% band. That's the comparison to anchor on,
and it's a useful contrast with Gemma 4, which swung ~5 points by provider. Run
Qwen3.6 at 4-bit and nothink scores about the same whoever serves it.

The 8-bit MLX serve on the Mac is the exception, and a large one: 77.2% nothink,
roughly 20 points clear of the 4-bit band and higher even than the best think
score. We checked the obvious confounder first. It is a genuine nothink run, zero
thinking tokens on all 92 cases, and its answers are not longer than the others
(a ~1.6k-token median, in line with the lucebox runs), so this is not the MLX
serve quietly reasoning its way to a better score. The leading suspect is the
quant itself, 8-bit MLX against the others' 4-bit, which would make weight
precision worth more on this set than we'd assumed. We are not asserting that
yet, because a serving or parsing difference could also be in play. It is exactly
the kind of question the queued
[model-quant quality sweep](<Tuning Qwen3.6-27B decode on a 3090 Ti — the knobs that moved throughput.md>)
should settle. For now, read the 4-bit band as the stable result and the 8-bit
number as an open lead.

## Thinking helps, when you give it room

Turn thinking on with a full budget and Qwen3.6 jumps to 63.0% on OpenRouter,
+7.6 over its own nothink score. That's a real dividend, and it's the opposite of
what we found on Gemma 4, where [think and nothink are a wash](<Think vs nothink on Gemma 4 — same accuracy, 10x the latency.md>).
Qwen actually uses the reasoning tokens.

The catch is in the budget. The same model on the laptop with a 4k thinking
budget scored **32.6%**, well below nothink. It isn't that thinking hurt; it's
that 4k tokens wasn't enough room to reason *and* answer, so the model got cut
off mid-derivation with nothing to show. A starved thinking budget is worse than
no thinking, because you pay for the reasoning and lose the reply.

That failure is exactly why the [thinking-budget machinery](<Putting Qwen's thinking on a budget — counting tokens and forcing the close.md>)
exists: count the output tokens, force the `</think>` close before the cap, and
reserve enough room for the answer. Give Qwen a generous effort tier (or a server
that force-closes cleanly with a real reply reserve) and the 63% is what you get;
clamp it without reserving reply room and you get the 32%.

## Takeaway

For Qwen3.6, turn thinking on, but the budget is load-bearing. Pick
an effort tier with headroom, make sure the reply reserve is set, and thinking
buys you several points. Set it too tight and you'd have been better off with it
off. (The MLX nothink number is in the table now; the MLX think run is still
in flight and goes in when it finishes.)

---

*ds4-eval-92 from antirez/ds4 (MIT), run via luce-bench, single seed. Qwen3.6-27B
Q4_K_M via lucebox (RTX 3090 Ti, RTX 5090 Laptop), MLX 8-bit (Mac Studio M2
Ultra; nothink in, think run in flight), and OpenRouter. Methodology:
[Running the benchmarks](<Running the benchmarks — an intro to luce-bench.md>).
Project: [github.com/Luce-Org/lucebox-hub](https://github.com/Luce-Org/lucebox-hub).*

**Related**
- [Running the benchmarks: an intro to luce-bench](<Running the benchmarks — an intro to luce-bench.md>)
- [Putting Qwen's thinking on a budget: counting tokens and forcing the close](<Putting Qwen's thinking on a budget — counting tokens and forcing the close.md>)
- [Think vs nothink on Gemma 4: same accuracy, 10x the latency](<Think vs nothink on Gemma 4 — same accuracy, 10x the latency.md>)
- [Every model we've run on ds4-eval-92](<Every model we've run on ds4-eval-92.md>)
- [What `/props` tells you about a lucebox server](<What props tells you about a lucebox server.md>)
- [How lucebox auto-tunes itself to your GPU](<How lucebox auto-tunes itself to your GPU.md>)
- [Model cards in lucebox: a typed sidecar for what the server actually needs](<Model cards in lucebox — a typed sidecar for what the server actually needs.md>)
- [Sampling parameters on a lucebox model card: what the knobs mean](<Sampling parameters on a lucebox model card — what the knobs mean.md>)
- [Multi-turn agentic loops as a benchmark target: what they look like, why they matter, what we've measured](<Multi-turn agentic loops as a benchmark target — what they look like, why they matter, what we've measured.md>)
- [The agentic stack is the product, not the model](<The agentic stack is the product, not the model.md>)
- [Tuning Qwen3.6-27B decode on a 3090 Ti: the knobs that moved throughput](<Tuning Qwen3.6-27B decode on a 3090 Ti — the knobs that moved throughput.md>)
