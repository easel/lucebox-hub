# Qwen3.6 think vs nothink across providers: thinking helps, if you budget for it

*May 2026 · by [Davide Ciffa](https://x.com/davideciffa) and [Erik LaBianca](https://x.com/easel)*

We ran the same Qwen3.6-27B on ds4-eval-92 across four serving stacks, think and
nothink. Three things came out of it. On the two lucebox 4-bit serves, nothink
lands around 56%, while the 8-bit MLX serve scored 77% nothink, an outlier we
flag below. Thinking helps when you give it room: a full budget adds 7–8 points,
a starved one does worse than not thinking at all. And the part we did not expect
going in, controlling thinking is not portable: the same nothink request that MLX
and lucebox honored, OpenRouter quietly ignored, which is its own lesson about
benchmarking reasoning models across providers.

> [Hero image: Qwen3.6 ds4-eval bars, nothink flat across providers, think split high/low]

## The numbers

| Serving | Mode | ds4-eval-92 | Note |
|---|---|---|---|
| RTX 3090 Ti (lucebox) | nothink | 57.6% | |
| RTX 5090 Laptop (lucebox) | nothink | 55.4% | |
| OpenRouter | nothink (ignored) | 55.4% | provider reasoned on 83/92, 27 truncated |
| Mac Studio M2 Ultra (MLX 8-bit) | nothink | 77.2% | 8-bit; outlier, see below |
| OpenRouter | think | **63.0%** | full 16k budget |
| RTX 5090 Laptop (lucebox) | think | 32.6% | clamped 4k budget |
| Mac Studio M2 Ultra (MLX 8-bit) | think | _pending (run in flight)_ | |

<!-- TODO: fill the MLX think row from vidar-m2ultra-qwen3.6-27b-mlx8bit-ds4eval-think-2026-05-27 when the run completes (~30/92 as of last check). nothink backfilled: 77.2% (71/92). -->

## Nothink, on the serves that honored it

The clean nothink comparison is narrower than four rows, because one of them is
not a nothink result at all. The OpenRouter row is set aside here and explained in
the next section: its provider reasoned on 83 of 92 cases despite the nothink
request, so its 55.4% is a starved-think score wearing a nothink label.

That leaves three genuine nothink runs, all with zero thinking tokens. The two
lucebox 4-bit serves land within noise of each other: a desktop 3090 Ti at 57.6%
and a laptop 5090 at 55.4%. Run Qwen3.6 at 4-bit and nothink scores about the same
on either card, a useful contrast with Gemma 4, which swung ~5 points by provider.

The 8-bit MLX serve on the Mac is the exception, and a large one: 77.2% nothink,
roughly 20 points clear of the 4-bit pair and higher even than the best think
score below. We checked the obvious confounder first. It is a genuine nothink run,
zero thinking tokens on all 92 cases, and its answers are not longer than the
others (a ~1.6k-token median, in line with the lucebox runs), so the MLX serve is
not quietly reasoning its way to a better score. The leading suspect is the quant,
8-bit MLX against the others' 4-bit, which would make weight precision worth more
on this set than we'd assumed. We are not asserting that yet, because a serving or
sampling difference could also be in play, and a cross-provider gap cannot isolate
the quant from the stack. The queued
[model-quant quality sweep](<Tuning Qwen3.6-27B decode on a 3090 Ti — the knobs that moved throughput.md>)
varies quant on one fixed stack, which is what it takes to settle this. For now,
read the 4-bit pair as the stable result and the 8-bit number as an open lead.

## Controlling thinking across providers

The OpenRouter row taught us something we should have checked sooner: the request
that turns thinking off is not honored everywhere, and a server that ignores it
fails quietly. The benchmark sends the same nothink request to every endpoint and
trusts the score. That trust is misplaced unless you verify the model actually
stopped thinking.

There is no single field that disables thinking across stacks, so luce-bench sends
three in every request and lets each server take the one it understands:

```json
"chat_template_kwargs": {"enable_thinking": false},
"thinking": {"type": "disabled"},
"reasoning_effort": "none"
```

The first is the vLLM, SGLang, and MLX convention. The second is the Anthropic
shape that lucebox reads. The third is the OpenAI and OpenRouter convention.
Disabling thinking is a template-level switch: `enable_thinking: false` makes the
chat template skip the thinking opener so the model never starts a `<think>`
block. `mlx_lm` applied it and produced clean nothink (zero thinking tokens, terse
answers, every case finishing on `stop`), and lucebox honored its own shape the
same way. OpenRouter's routed provider honored none of the three: 83 of 92 cases
reasoned anyway, 27 of them ran straight into the length cap. So nothink held on
two of the three stacks and silently did not on the third.

The practical rule that falls out of this: do not trust the flag you sent, check
the thinking-token count that came back. A nothink run with thinking tokens on
most of its rows is not a nothink run.

Disabling thinking and limiting thinking are different problems, and the second
one also varies by stack. Limiting lives server-side, and it is lucebox-specific
here: count the output tokens, force the `</think>` close before the cap, and
reserve room for the visible answer. MLX has none of that machinery. In think mode
it runs to `max_tokens` with no force-close, which is why its hard cases pile up at
the 16k cap. The
[thinking-budget machinery](<Putting Qwen's thinking on a budget — counting tokens and forcing the close.md>)
post covers how lucebox does the limiting; the next section is what it buys you.

## Thinking helps, when you give it room

Turn thinking on with a full 16k budget and Qwen3.6 reaches 63.0% on OpenRouter,
about 7 points over the clean 4-bit nothink baseline of ~56%. That's a real
dividend, and it's the opposite of what we found on Gemma 4, where
[think and nothink are a wash](<Think vs nothink on Gemma 4 — same accuracy, 10x the latency.md>).
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
off. And whatever mode you ask for, verify the server delivered it: check the
thinking-token count that comes back, not just the flag you sent, because a
provider that ignores it will hand you the wrong run with no error. (The MLX
nothink number is in the table now; the MLX think run is still in flight and goes
in when it finishes.)

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
