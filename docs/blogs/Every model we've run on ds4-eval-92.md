# Every model we've run on ds4-eval-92

*May 2026 · by Davide Ciffa and Erik LaBianca*

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

| Model | Params (active) | ds4-eval-92 | Where / mode |
|---|---|---|---|
| Gemma 4 26B (a4b) | 26B (~4B) | **81.5%** | RTX 5090 Laptop, think (78–79% nothink) |
| DeepSeek V4 Flash | 284B (13B) | 80.4% | OpenRouter, think (78.3% local Mac) |
| Gemma 4 31B | 31B | 80.4% | OpenRouter, think |
| DeepSeek V4 Pro | larger MoE | 79.3% | OpenRouter, think |
| Claude Sonnet 4.6 | — | 75.0% | OpenRouter, nothink |
| Qwen3.6-27B | 27B | 63.0% | OpenRouter, think (~56% nothink) |
| GPT-5.4-mini | — | 59.8% | OpenRouter, nothink |
| Laguna XS.2 | — | 59.8% | OpenRouter |

## What stands out

The efficiency story is the headline. Gemma 4 26B is a 26B MoE with ~4B active
parameters per token, and it tops the board, level with or ahead of its own 31B
sibling, both DeepSeek V4 models (Flash at 284B, the larger Pro), and the
frontier proprietary models. On this set, more parameters didn't buy more
accuracy. We dug into the DeepSeek matchup, including the same-Mac control, in
[the DeepSeek comparison](<Gemma 4 26B edges out DeepSeek V4 Flash (284B) on ds4-eval-92, at 5x the speed.md>).

The frontier generalists land mid-table, and that's the caveat worth stating
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

---

*ds4-eval-92 from antirez/ds4 (MIT), run via luce-bench, single seed, best clean
result per model across local rigs and hosted providers (mix of quants and
modes). Frontier and hosted models via OpenRouter at provider defaults.
Methodology and provenance:
[Running the benchmarks](<Running the benchmarks — an intro to luce-bench.md>).
Project: [github.com/Luce-Org/lucebox-hub](https://github.com/Luce-Org/lucebox-hub).*

**Related**
- Running the benchmarks: an intro to luce-bench
- Meet lucebox: a local AI inference engine optimized for consumer hardware
- Gemma 4 26B edges out DeepSeek V4 Flash (284B), at 5x the speed
- Gemma 4 26B across serving paths: a laptop GPU, a 3090 Ti, MLX, and OpenRouter
- Think vs nothink on Gemma 4: same accuracy, 10x the latency
