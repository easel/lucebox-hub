# Qwen3.6 think vs nothink across providers: thinking helps, if you budget for it

*May 2026 · by [Davide Ciffa](https://x.com/davideciffa) and [Erik LaBianca](https://x.com/easel)*

We ran the same Qwen3.6-27B on ds4-eval-92 across three serving stacks, think and
nothink. Two things came out of it. Nothink is boringly consistent: ~55–58%
wherever we ran it. Thinking is not boring: with a full budget it adds 7–8 points,
and with a starved budget it does worse than not thinking at all. For Qwen,
unlike Gemma 4, the thinking budget is a real lever, and it cuts both ways.

> [Hero image: Qwen3.6 ds4-eval bars, nothink flat across providers, think split high/low]

## The numbers

| Serving | Mode | ds4-eval-92 | Note |
|---|---|---|---|
| RTX 3090 Ti (lucebox) | nothink | 57.6% | |
| RTX 5090 Laptop (lucebox) | nothink | 55.4% | |
| OpenRouter | nothink | 55.4% | |
| Mac Studio M2 Ultra (MLX) | nothink | _pending (omlx run in flight)_ | |
| OpenRouter | think | **63.0%** | full 16k budget |
| RTX 5090 Laptop (lucebox) | think | 32.6% | clamped 4k budget |
| Mac Studio M2 Ultra (MLX) | think | _pending (omlx run in flight)_ | |

<!-- TODO: fill the two MLX rows from vidar-m2ultra-qwen3.6-27b-mlx8bit-ds4eval-{nothink,think}-2026-05-27 when the run completes. -->

## Nothink is stable across providers

Three independent serves, three numbers within noise: 57.6%, 55.4%, 55.4%. A
desktop 3090 Ti on lucebox, a laptop 5090 on lucebox, and whatever OpenRouter
routes to all land in the same ~56% band. That's the comparison to anchor on,
and it's a useful contrast with Gemma 4, which swung ~5 points by provider. On
nothink, Qwen3.6 is what it is regardless of who serves it.

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

For Qwen3.6, thinking is worth turning on, but the budget is load-bearing. Pick
an effort tier with headroom, make sure the reply reserve is set, and thinking
buys you several points. Set it too tight and you'd have been better off with it
off. (We'll fold the Mac/MLX numbers into the table above once that run lands.)

---

*ds4-eval-92 from antirez/ds4 (MIT), run via luce-bench, single seed. Qwen3.6-27B
Q4_K_M via lucebox (RTX 3090 Ti, RTX 5090 Laptop), MLX 8-bit (Mac Studio M2
Ultra, pending), and OpenRouter. Methodology:
[Running the benchmarks](<Running the benchmarks — an intro to luce-bench.md>).
Project: [github.com/Luce-Org/lucebox-hub](https://github.com/Luce-Org/lucebox-hub).*

**Related**
- Running the benchmarks: an intro to luce-bench
- Putting Qwen's thinking on a budget: counting tokens and forcing the close
- Think vs nothink on Gemma 4: same accuracy, 10x the latency
- Every model we've run on ds4-eval-92
- What /props tells you about a lucebox server
- How lucebox auto-tunes itself to your GPU
- Model cards in lucebox: a typed sidecar for what the server actually needs
- Sampling parameters on a lucebox model card: what the knobs mean
- Multi-turn agentic loops as a benchmark target: what they look like, why they matter, what we've measured
