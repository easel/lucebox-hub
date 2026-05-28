# Multi-turn agentic loops as a benchmark target: what they look like, why they matter, what we've measured

I came into this expecting the hard part of benchmarking an agent to be the grading. It isn't. The hard part is the context. A coding session that starts as a 60-token prompt is a 30,000-token prompt twelve turns later, and the thing you actually want to know about a local engine is whether it stays responsive while that happens. So this post is partly a design note and partly an accounting of what we have and haven't measured yet.

Quick version: we have decent single-turn agent-shape data and a clear (if unflattering) tool-protocol result on the lucebox-served path, but the multi-turn `agentic-session` suite is built and not yet run. I'll lay out what the loop is, why it deserves its own suite, what the captured runs say, and a concrete matrix for the runs we should do once the omlx box frees up.

## What a multi-turn agentic loop actually is

The shape is simple and it repeats. The model emits a `tool_use` block. The harness (or the real agent runtime) executes that tool and hands back a `tool_result`. The model reads the result and emits the next `tool_use`. Repeat until it stops calling tools and answers.

The part that matters for benchmarking is what happens to the prompt across that loop. Every turn carries the full prior history: the system prompt, the user task, every assistant `tool_use` so far, and every `tool_result` so far. Tool results are the expensive part. A single `cat` of a source file or a directory listing can be a few thousand tokens, and the agent reads a lot of files. So the request the server sees on turn one is small, and the request it sees on turn ten contains turns one through nine in full. Context grows monotonically, and it grows fastest right where the work gets interesting.

You can see the seed of this even in our single-turn agent probes. The four cases we run carry prompts of roughly 1,600, 1,800, 4,900, and 5,500 tokens before the model writes a single token, and those are realistic Codex-style system prompts with one task attached. Stack ten turns of accumulated file reads on top of that and tens of thousands of tokens of history is the normal case, not the worst one.

## Why it's a distinct benchmark from single-shot Q&A

Our ds4-eval suite asks 92 questions and grades the final answer. Each question is independent and the prompt is short. That tells you about reasoning and knowledge. It tells you almost nothing about the failure modes an agent loop hits.

Two things make the loop its own category. First, the context consumption is extreme and it grows. That stresses the KV cache, it stresses prefix reuse (each turn's prompt is the previous turn's prompt plus a suffix, which is exactly the case prefix caching is supposed to win), and it eventually runs into the configured context limit. None of that shows up in a 200-token Q&A. Second, and this is the useful part, you can make the loop deterministic. If you record a real session once and replay the same `tool_result` history every time, the model's job is fixed turn over turn. That turns a messy interactive process into a repeatable measurement. You can read first-content latency, wall time, decode rate, and prompt-token growth at each turn, and compare two server configs on identical inputs.

That is the design behind `agentic-session`. It is inspired by club-3090's coding-session benchmark, and it uses the Anthropic Messages wire shape that Claude Code emits: streamed `tool_use` blocks followed by a deterministic, replayed `tool_result` history shaped from a captured session against a lucebox server. The spec records per-turn aggregate prompt tokens, first-content latency, wall time, request and history size, decode TPS, tool calls, and tool-result size, plus a top-line `final_wall_growth_vs_turn1`. One caveat worth stating up front: the server currently emits aggregated content blocks after decoding, so `first_content_ms` is the first streamed assistant block, not a token-level time-to-first-token from the daemon. Read it as a wall-bound first-content number, not a TTFT.

This sits next to two narrower suites. `agentic-tools` is the single-turn version: does one request emit one correctly-formatted tool call. `agent` (the area we have the most data for) is even simpler, it asks whether the model engages as an agent at all when handed a realistic system prompt, counting a code block, a JSON tool-call envelope, or an `apply_patch` block as a pass. `agentic-session` is the multi-turn one that exercises the context-growth behavior the other two skip.

Zoom out further and even `agentic-session` is a controlled slice. A true agentic benchmark like [Terminal-Bench](https://www.tbench.ai/) (89 hard terminal tasks driven through a harness such as Harbor, where frontier agents still score under 65%) measures the whole pipeline at once: the agent's context management, the tools it is handed, the harness that runs the loop, the inference stack that serves the tokens, and the model. Every one of those is a contributor to the final score, which is both the point and the difficulty. You cannot read a Terminal-Bench result as a statement about the model alone. Our suites deliberately hold most of that fixed and move one piece at a time: `agent` and `forge` check whether tool calls come out in the right shape at all, and `agentic-session` replays a fixed `tool_result` history to isolate how the inference stack behaves as context grows. They are diagnostics for the layer we own, the engine. A full end-to-end agent evaluation is a larger thing, and Terminal-Bench is what that looks like.

## Why this matters for a local engine specifically

On a hosted API you mostly don't think about any of this. The provider has the KV cache headroom and the context window, and you pay per token. On a 24 GB consumer GPU you think about all of it, because the loop is exactly where the tuning decisions in lucebox get tested.

Prefix caching is the obvious one. Turn N's prompt is turn N-1's prompt with a new `tool_result` appended, so a server that reuses the cached prefix only has to prefill the new suffix, while one that doesn't re-prefills the whole growing history every turn. KV cache dtype decides how much of that history fits before you run out of VRAM. And context headroom decides whether the session completes at all or dies partway through with an out-of-memory or a context-limit error. We already saw the headroom edge in autotuner stress testing: on a 3090 Ti, a `114688/22` context-and-budget setting left only a few hundred MiB of VRAM free under repeated tool traffic, which is not enough for CUDA scratch, so the safe default for 24 GB-class cards dropped to `65536/16`. That is the agent loop deciding a tuning default. The autotuner's level3 profile runs a multi-turn agentic session for precisely this reason, and the `/props` snapshot is where you read back the context limit and cache settings the loop will live or die by.

## What we've measured so far, and the gaps

Here is the state of the captured data. All Gemma 4 26B unless noted, single seed, `max_tokens` 4096.

Agent-shape (the `agent` area, four Codex-style cases):

| Run | Serve | Mode | Pass rate | Wall median | Decode |
|---|---|---|---|---|---|
| bragi sweep | lucebox / 5090 laptop | nothink | 3/4 (75%) | 7.1 s | ~104 tok/s |
| bragi sweep | lucebox / 5090 laptop | think | 2/4 (50%) | 10.5 s | ~102 tok/s |
| bragi matrix-v2 | lucebox / 5090 laptop | nothink | 3/4 (75%) | 41.2 s | ~102 tok/s |
| bragi matrix-v2 | lucebox / 5090 laptop | think | 2/4 (50%) | 41.8 s | ~101 tok/s |
| sindri | lucebox / 3090 Ti | nothink | 3/4 (75%) | n/a | n/a |
| sindri | lucebox / 3090 Ti | think | 2/4 (50%) | n/a | n/a |
| vidar MLX | MLX 8-bit / M2 Ultra | nothink | 1/4 (25%) | 7.0 s | n/a |

The nothink agent-shape result is stable at 75% across the 5090 laptop and the 3090 Ti. The one case that fails on the strong setups is `codex-mini-read-task`, where the model narrates ("I would use `cat`...") instead of emitting a tool envelope. Think mode is consistently worse here (50%), which tracks with what we have seen elsewhere on Gemma 4. The MLX 8-bit run is the outlier at 25%, with three of four cases producing very short or empty completions; that is worth a closer look but it is one run.

The wall-median jump between the bragi sweep (7 s) and bragi matrix-v2 (41 s) comes from generation length, not a speed regression. In the sweep, the `apply-patch` case stopped at 432 tokens; in matrix-v2 it ran to the full 4,096-token cap. Decode rate held at ~102 tok/s across both, which is the comparable number. This is a good reminder that wall is token-count-dependent and decode rate is not.

Tool-calling protocol (the `forge` area, 30 mock scenarios) is where the gap is loud. On the lucebox-served path, every run scores 0/30:

| Run | Serve | Pass rate | Dominant finish reason |
|---|---|---|---|
| bragi matrix-v2 nothink | lucebox / 5090 laptop | 0/30 | length (23/30) |
| bragi matrix-v2 think | lucebox / 5090 laptop | 0/30 | length |
| sindri nothink | lucebox / 3090 Ti | 0/30 | length (25/30) |
| vidar MLX | MLX 8-bit / M2 Ultra | 0/30 | tool_calls (28/30) |

Compare that to the same scenarios run through OpenRouter, where the models are served behind a proper tool-use protocol:

| Model (OpenRouter) | forge pass rate |
|---|---|
| DeepSeek V4 Flash | 30/30 (100%) |
| Gemma 4 31B | 26/30 (87%) |
| Gemma 4 26B | 25–26/30 (83–87%) |
| Qwen3.6 27B | 28/30 (93%) |
| Laguna XS.2 | 5/30 (17%) |

So Gemma 4 26B can do these scenarios. The 0/30 on the lucebox path comes from a protocol and budget mismatch rather than the model failing the task: the served runs hit the 4,096-token cap (`finish_reason: length`) and emit a raw `call:get_country_info{country: "France"}` text syntax instead of the structured tool call the grader parses. The grader sees `ValidationError` or no tool call and fails the row. The MLX run is a different flavor of the same problem, finishing on `tool_calls` but still grading 0. This is a concrete finding we can act on, and it is the strongest argument for running the multi-turn suite deliberately rather than inferring multi-turn behavior from these numbers.

The gap we can't paper over: we have zero captured `agentic-session` runs. No `bench-agentic-session.json` exists in the baselines repo. The suite is specified, the snapshot exporter normalizes its output into `[benchmark.agentic_session]` and per-turn sections, and the autotuner's level3 profile invokes it, but nothing has been recorded to disk yet. Everything I said above about context growth is measured at turn one from the agent probes and reasoned forward from the design. The turn-over-turn curve, the actual first-content and wall growth as history accumulates, is the thing we have not yet put a number on.

## What we should run

This is the matrix I'd execute once vidar (the omlx server at vidar:1237) is free and we're ready to spend OpenRouter budget. The point is to fill the multi-turn cells and to get the lucebox forge path to a fair number by raising the token cap and confirming the tool-call format.

| Model | Serve / host | agent | forge | agentic-session |
|---|---|---|---|---|
| Gemma 4 26B | lucebox / 5090 laptop (bragi) | have (75% nothink) | rerun, raise max_tokens | run, primary |
| Gemma 4 26B | lucebox / 3090 Ti (sindri) | have (75% nothink) | rerun, raise max_tokens | run, headroom check |
| Gemma 4 26B | MLX 8-bit / M2 Ultra (vidar) | rerun, investigate 25% | rerun | run |
| Gemma 4 31B | lucebox / 5090 laptop | run | run | run |
| Qwen3.6 27B | lucebox / 5090 laptop | run | run | run |
| Gemma 4 26B | OpenRouter | reference | have (83–87%) | reference |
| DeepSeek V4 Flash | OpenRouter | reference | have (100%) | reference |

Notes on the matrix. The forge reruns should lift `max_tokens` well above 4,096 and confirm the served tool-call format before we read anything into the pass rate; the current 0/30 is a cap-and-format artifact rather than a capability ceiling. The `agentic-session` column is the actual gap to close, and the two lucebox hosts (5090 laptop and 3090 Ti) are the interesting pair because they differ in VRAM headroom, which is exactly the variable the loop stresses. The OpenRouter rows are references for what the model can do unconstrained, not comparable wall-time numbers. Single seed to start; if a session shows variance in tool-call reliability turn over turn, repeat it. And the thing to actually plot from the session runs is prompt tokens, first-content, and wall against turn number, so we can see where (and whether) the loop stops being responsive on 24 GB.

---

Runs and provenance live in `Luce-Org/luce-bench-baselines`, produced by `scripts/run-baseline.sh`. The `agentic-session` design is in `server/docs/BENCHMARK_SNAPSHOT_SPEC.md`; the agent and forge areas ship in `luce-bench` inside lucebox-hub. Club-3090's coding-session benchmark is the inspiration for the multi-turn shape. As always, these are single-seed results on small suites, scoped to what they measure.

**Related**

- [Running the benchmarks: an intro to luce-bench](<Running the benchmarks — an intro to luce-bench.md>)
- [How lucebox auto-tunes itself to your GPU](<How lucebox auto-tunes itself to your GPU.md>)
- [What `/props` tells you about a lucebox server](<What props tells you about a lucebox server.md>)
- [Every model we've run on ds4-eval-92](<Every model we've run on ds4-eval-92.md>)
- Model cards in lucebox: a typed sidecar for what the server actually needs
- Sampling parameters on a lucebox model card: what the knobs mean
