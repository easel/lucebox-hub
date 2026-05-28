# Gemma 4 26B across serving paths: a laptop GPU, a 3090 Ti, MLX, and OpenRouter

*May 2026 · by [Davide Ciffa](https://x.com/davideciffa) and [Erik LaBianca](https://x.com/easel)*

We ran the same Gemma 4 26B four ways. The weights are identical and the mode is
fixed (nothink); only the serving path changes. On ds4-eval-92, accuracy moved
about 5 points with the serving stack and throughput moved 3x with the hardware.

> [Hero image: Gemma 4 26B fanning out to four serving paths: 3090 Ti, 5090 Laptop, Mac Studio/MLX, OpenRouter]

## The setup

One model (Gemma 4 26B, the a4b MoE with ~4B active params/token), scored on
luce-bench's `ds4-eval` area, every row nothink. The harness, the grading, and
the ds4 provenance live in [Running the benchmarks](<Running the benchmarks — an intro to luce-bench.md>);
think vs nothink is its own [post](<Think vs nothink on Gemma 4 — same accuracy, 10x the latency.md>).
Four serving paths:

- lucebox + DFlash (Q4_K_M) on two GPUs: a desktop RTX 3090 Ti and an RTX 5090 Laptop.
- Apple MLX (8-bit) on a 192 GB Mac Studio (M2 Ultra, 60-core GPU).
- OpenRouter, whatever the routed provider serves by default.

## The numbers

| Serving path | Stack / quant | Accuracy (ds4-eval-92) | Decode tok/s | Wall (med) |
|---|---|---|---|---|
| OpenRouter (hosted) | provider default | 73.9% (68/92) | — | 28.3 s |
| RTX 3090 Ti, 24 GB | lucebox + DFlash, Q4_K_M | 79.3% (73/92) | ~31 | 30.6 s |
| RTX 5090 Laptop, 24 GB | lucebox + DFlash, Q4_K_M | 78.3% (72/92) | ~103 | 9.5 s |
| Mac Studio M2 Ultra, 192 GB | MLX 8-bit | 79.3% (73/92) | ~40 | 23.3 s |

OpenRouter doesn't expose a decode rate, so its tok/s is blank; its 28.3 s is
end-to-end wall, not a like-for-like decode number.

## What the table says

The surprise is where the accuracy spread comes from: the serving stack, not the
GPU. The three local serves land in a tight band, 78.3% to 79.3%, across three
different chips, quants, and engines (a 3090 Ti and a 5090 Laptop on lucebox
Q4_K_M, and a Mac Studio on MLX 8-bit). The same weights on OpenRouter drop to
73.9%. That gap is how the endpoint renders Gemma's chat template and what
sampling it applies, and Gemma 4 is fussy about both. DeepSeek V4 Flash holds
~78% across local, hosted, and OpenRouter (see [the DeepSeek comparison](<Gemma 4 26B edges out DeepSeek V4 Flash (284B) on ds4-eval-92, at 5x the speed.md>)),
so this isn't open models being fragile in general. Some models bake assumptions
into their serving contract, and Gemma 4 is one of them.

Throughput is the opposite story: it tracks the hardware. On the same model and
stack the 3090 Ti decodes at ~31 tok/s and the 5090 Laptop at ~103, with MLX on
the Mac around 40. The fastest box isn't the most accurate; the two axes are
independent. Quant and engine count as serving too, since lucebox runs Q4_K_M
through DFlash on CUDA while MLX runs an 8-bit quant on Metal, the same weights
through different kernels. A bare "Gemma 4 26B score" doesn't mean much without
naming the stack.

So when we compare open models now, we pin the stack. Otherwise the number is
about the provider, not the model.

---

*ds4-eval-92 from antirez/ds4 (MIT), run via luce-bench, single seed, nothink.
Serving: lucebox+DFlash Q4_K_M (RTX 3090 Ti, RTX 5090 Laptop), Apple MLX 8-bit
(Mac Studio M2 Ultra 60-core), OpenRouter. Project:
[github.com/Luce-Org/lucebox-hub](https://github.com/Luce-Org/lucebox-hub).*

**Related**
- [Meet lucebox: a local AI inference engine optimized for consumer hardware](<Meet lucebox — a local AI inference engine optimized for consumer hardware.md>)
- [Running the benchmarks: an intro to luce-bench](<Running the benchmarks — an intro to luce-bench.md>)
- [Gemma 4 26B edges out DeepSeek V4 Flash (284B) on ds4-eval-92, at 5x the speed](<Gemma 4 26B edges out DeepSeek V4 Flash (284B) on ds4-eval-92, at 5x the speed.md>)
- [Think vs nothink on Gemma 4: same accuracy, 10x the latency](<Think vs nothink on Gemma 4 — same accuracy, 10x the latency.md>)
- [Every model we've run on ds4-eval-92](<Every model we've run on ds4-eval-92.md>)
- [Putting Qwen's thinking on a budget: counting tokens and forcing the close](<Putting Qwen's thinking on a budget — counting tokens and forcing the close.md>)
- [Qwen3.6 think vs nothink across providers: thinking helps, if you budget for it](<Qwen3.6 think vs nothink across providers — thinking helps if you budget for it.md>)
- [What `/props` tells you about a lucebox server](<What props tells you about a lucebox server.md>)
- [How lucebox auto-tunes itself to your GPU](<How lucebox auto-tunes itself to your GPU.md>)
- [Model cards in lucebox: a typed sidecar for what the server actually needs](<Model cards in lucebox — a typed sidecar for what the server actually needs.md>)
- [Sampling parameters on a lucebox model card: what the knobs mean](<Sampling parameters on a lucebox model card — what the knobs mean.md>)
- [Multi-turn agentic loops as a benchmark target: what they look like, why they matter, what we've measured](<Multi-turn agentic loops as a benchmark target — what they look like, why they matter, what we've measured.md>)
- [The agentic stack is the product, not the model](<The agentic stack is the product, not the model.md>)
