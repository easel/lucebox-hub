# Every model we've run on ds4-eval-92

*May 2026 · by [Davide Ciffa](https://x.com/davideciffa) and [Erik LaBianca](https://x.com/easel)*

We've pointed ds4-eval-92 at a lot of models by now, across local rigs and hosted
providers, open weights and proprietary APIs. Here's the whole field on one
chart. The short version: on this reasoning set the Gemma 4 family and the
DeepSeek V4 models cluster at the top around 79–81%, the frontier chat models
land a notch below, and the small/fast models trail. The result we keep coming
back to is that the smallest model on the board is at the top of it.

> [Hero image: horizontal bar chart of ds4-eval-92 accuracy by model]

## The board

Best clean ds4-eval-92 result we recorded per model. Configs vary (provider,
quant, mode), so read this as a field map, not a controlled run; the apples-to-
apples comparisons live in the other posts.

| Model | Params (active) | ds4-eval-92 | Where / mode | Wall (med) | In tok | Out tok | tok/s (e2e) |
|---|---|---|---|---|---|---|---|
| Gemma 4 26B (a4b) | 26B (~4B) | **81.5%** | RTX 5090 Laptop, think (78–79% nothink) | 104.9s | 244 | 10710 | 101.6 |
| DeepSeek V4 Flash | 284B (13B) | 80.4% | OpenRouter, think (78.3% local Mac) | 19.4s | 225 | 1646 | 97.8 |
| Gemma 4 31B | 31B | 80.4% | OpenRouter, think | 31.6s | 249 | 682 | 23.6 |
| DeepSeek V4 Pro | larger MoE | 79.3% | OpenRouter, think | 47.3s | 225 | 2099 | 48.6 |
| Claude Sonnet 4.6 | — | 75.0% | OpenRouter, nothink | 9.3s | 256 | 608 | 56.5 |
| Qwen3.6-27B | 27B | 63.0% | OpenRouter, think (~56% nothink) | 166.5s | 255 | 13025 | 63.9 |
| GPT-5.4-mini | — | 59.8% | OpenRouter, nothink | 1.2s | 235 | 14 | 25.1 |
| Laguna XS.2 | — | 57.6% | OpenRouter | 25.8s | 256 | 2942 | 100.1 |

## What stands out

The efficiency story is the headline. Gemma 4 26B is a 25.2B-total MoE with only
3.8B active parameters per token (128 experts, 8 active plus 1 shared), and it
tops the board, level with or ahead of its own dense 31B sibling (30.7B params,
all of them active), both DeepSeek V4 models (Flash at 284B, the larger Pro), and
the frontier proprietary models. On this set, more parameters didn't buy more
accuracy, and the sparse model matched the dense one it shares a generation with. We dug into the DeepSeek matchup, including the same-Mac control, in
[the DeepSeek comparison](<Gemma 4 26B edges out DeepSeek V4 Flash (284B) on ds4-eval-92, at 5x the speed.md>).

The frontier generalists land mid-table, and the caveat there needs saying
loudly: ds4-eval-92 is a narrow, hard reasoning set (GPQA Diamond, SuperGPQA,
AIME2025, COMPSEC). Claude Sonnet 4.6 at 75% and GPT-5.4-mini at 60% are not
"worse models" than a Gemma here in any general sense; they're a generalist and
a small fast model measured on a reasoning slice that the DeepSeek and Gemma
reasoners are specifically strong on. A model that trails here can be the better
pick for chat, code, latency, or tool use. This is a benchmark, not a ranking.

Mode matters, and not the same way for every model. Qwen3.6-27B does better with
thinking on (63% vs ~56%); Sonnet and GPT-5.4-mini are flat-to-slightly-better
without it; Gemma 4 is a wash. We pull that apart in
[think vs nothink](<Think vs nothink on Gemma 4 — same accuracy, 10x the latency.md>).

## A serving caution

Two numbers aren't on the board because they measured the stack, not the model.
Gemma 4 31B scored 79–80% on OpenRouter but **8.7%** on our first local serve,
and a couple of Laguna runs came back at 0%, both from template/quant
misconfiguration rather than the model. We pulled that thread in
[Gemma 4 26B across serving paths](<Gemma 4 26B across serving paths — a laptop GPU, a 3090 Ti, MLX, and OpenRouter.md>):
the same weights can swing several points (or fall over entirely) depending on
who serves them and how. So treat any single number here as "this model, this
stack," and pin the stack before comparing.

## On performance

The four perf columns are end-to-end and need a caveat before anyone reads them
as a decode-rate chart. tok/s here is just median completion tokens over median
wall, with the run non-streaming, so the wall on the OpenRouter rows bundles
network round-trip, queueing, and time-to-first-token in with the actual
generation. The local lucebox row is almost pure decode by comparison; prefill
on these prompts is around 120 ms. That asymmetry flatters the local number, and
the right way to read the table is "what you'd feel start to finish," not "how
fast each stack generates."

We don't measure TTFT yet. The luce-bench runner posts a request and waits for
the full response, so there's no first-chunk timestamp to subtract. Adding it is
straightforward: stream the response and record when the first token arrives.
Until we do, treat the wall column as inclusive of everything that happens
between the request and the last token.

With that framing, the defensible read is that on this end-to-end metric the
local lucebox box holds its own. Gemma 4 26B running DFlash speculative decode on
a 24 GB laptop lands at 101.6 tok/s, level with or ahead of the hosted serves on
the same measurement, even though it's emitting an order of magnitude more tokens
per question. That lines up with the idea that the inference stack (speculative
decode, prefill, caching) drives throughput as much as the weights and the GPU
do. It is not a claim that local beats the frontier APIs in general; on what we
measure here it keeps pace, and that is the result that surprised us.

---

*ds4-eval-92 from antirez/ds4 (MIT), run via luce-bench, single seed, best clean
result per model across local rigs and hosted providers (mix of quants and
modes). Frontier and hosted models via OpenRouter at provider defaults.
Methodology and provenance:
[Running the benchmarks](<Running the benchmarks — an intro to luce-bench.md>).
Project: [github.com/Luce-Org/lucebox-hub](https://github.com/Luce-Org/lucebox-hub).*

**Related**
- [Running the benchmarks: an intro to luce-bench](<Running the benchmarks — an intro to luce-bench.md>)
- [Meet lucebox: a local AI inference engine optimized for consumer hardware](<Meet lucebox — a local AI inference engine optimized for consumer hardware.md>)
- [Gemma 4 26B edges out DeepSeek V4 Flash (284B) on ds4-eval-92, at 5x the speed](<Gemma 4 26B edges out DeepSeek V4 Flash (284B) on ds4-eval-92, at 5x the speed.md>)
- [Gemma 4 26B across serving paths: a laptop GPU, a 3090 Ti, MLX, and OpenRouter](<Gemma 4 26B across serving paths — a laptop GPU, a 3090 Ti, MLX, and OpenRouter.md>)
- [Think vs nothink on Gemma 4: same accuracy, 10x the latency](<Think vs nothink on Gemma 4 — same accuracy, 10x the latency.md>)
- [Putting Qwen's thinking on a budget: counting tokens and forcing the close](<Putting Qwen's thinking on a budget — counting tokens and forcing the close.md>)
- [Qwen3.6 think vs nothink across providers: thinking helps, if you budget for it](<Qwen3.6 think vs nothink across providers — thinking helps if you budget for it.md>)
- [What `/props` tells you about a lucebox server](<What props tells you about a lucebox server.md>)
- [How lucebox auto-tunes itself to your GPU](<How lucebox auto-tunes itself to your GPU.md>)
- [Model cards in lucebox: a typed sidecar for what the server actually needs](<Model cards in lucebox — a typed sidecar for what the server actually needs.md>)
- [Sampling parameters on a lucebox model card: what the knobs mean](<Sampling parameters on a lucebox model card — what the knobs mean.md>)
- [Multi-turn agentic loops as a benchmark target: what they look like, why they matter, what we've measured](<Multi-turn agentic loops as a benchmark target — what they look like, why they matter, what we've measured.md>)
- [The agentic stack is the product, not the model](<The agentic stack is the product, not the model.md>)
