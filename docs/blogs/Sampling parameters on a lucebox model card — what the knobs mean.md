# Sampling parameters on a lucebox model card: what the knobs mean

Every lucebox model card carries a `sampling` block, and the companion post on the card format ([Model cards in lucebox](<Model cards in lucebox — a typed sidecar for what the server actually needs.md>)) explains where those numbers come from and how the server resolves them. This post is the other half. It does not tell you what value a given model wants. It tells you what each knob actually does, so that when you read `top_k: 64` on the Gemma 4 card you know what you are looking at and why it is 64 and not 20.

The recommended values are model-specific. They live on the card precisely because there is no universal good setting. So the worked plan here is: define the mechanism, say when it matters, point at the authoritative source, and then show one place where getting it wrong bit us.

## The block as it ships

Here is the `sampling` section from the Qwen3.6 27B sidecar, which exercises every field the schema allows:

```json
"sampling": {
  "temperature": 1.0,
  "top_p": 0.95,
  "top_k": 20,
  "min_p": 0.0,
  "presence_penalty": 0.0,
  "repetition_penalty": 1.0
}
```

The schema (`share/model_cards/_schema.json`) permits exactly those six keys and nothing else. When a request omits a field, the server fills it from here. When the card itself omits a field, the server falls back to a neutral default. You can see both layers reflected over `GET /props`: `default_generation_settings` reports the concrete value the server will apply, and `sampling.capabilities` advertises which knobs the server honors at all. The full endpoint is covered in [What `/props` tells you about a lucebox server](<What props tells you about a lucebox server.md>).

One naming wrinkle to keep in your head before we start. Our card field is `repetition_penalty`, but the value the server emits in `default_generation_settings` is keyed `repeat_penalty`. That is the llama.cpp wire name, and `build_props_body` in `server/src/server/http_server.cpp` maps our field onto it. Same number, two spellings, depending on which side of the boundary you are reading.

## The decoding pipeline, in order

A language model does not emit a token. It emits a probability distribution over the entire vocabulary, every step. Sampling is the policy that turns that distribution into one chosen token. The knobs below are stages in a pipeline, and order matters: the truncation filters (`top_k`, `top_p`, `min_p`) cut the candidate set down, temperature reshapes how peaked the distribution is, and the penalty terms bias against tokens you have already seen. Get the stages confused and the values stop making sense.

| Knob | What it controls | When it matters |
|---|---|---|
| `temperature` | How peaked or flat the distribution is before sampling | Always. The master diversity dial. |
| `top_p` | Keep the smallest set of tokens whose mass sums to p | Long-form generation; the standard truncation. |
| `top_k` | Keep only the k highest-probability tokens | Caps the tail to a fixed count. |
| `min_p` | Drop tokens below a fraction of the top token's probability | Adapts the cut to how confident the model is. |
| `repetition_penalty` | Down-weights tokens already in the context | Loops and degenerate repetition. |
| `seed` | Pins the RNG so a run is reproducible | Benchmarks, bug repro, anything you need twice. |

### temperature

Temperature divides the logits before the softmax. Below 1.0 it sharpens the distribution, concentrating mass on the already-likely tokens; above 1.0 it flattens it, lifting the tail. At exactly 0 the model is greedy: it takes the single most probable token every step, deterministically. This is the knob with the widest reach, because every other stage operates on the distribution temperature has already reshaped.

The intuition that temperature 0 is the safe, accurate choice is wrong often enough to be dangerous. Some models are trained and tuned to be sampled at temperature 1.0, and running them greedy walks them straight into degenerate decoding. We hit exactly this with Gemma 4. Its card asks for temperature 1.0, top_p 0.95, top_k 64. A bug in `/props` was reporting a greedy fallback regardless of what the card said, so clients that read the endpoint to shape their requests ran the model at temperature 0, and the benchmark collapsed into degenerate-decode loops. The comment that now sits above the fix in `build_props_body` records it plainly: the endpoint must reflect the card's defaults, not a hard-coded greedy fallback. The card knows the model wants heat. The client has to be told.

### top_p (nucleus sampling)

`top_p` keeps the smallest set of tokens whose cumulative probability reaches `p`, then samples from that set after renormalizing. At `top_p: 0.95` you keep the most probable tokens that together hold 95 percent of the mass and discard the long, noisy tail. The size of the kept set changes step to step: when the model is confident, a handful of tokens already cover 95 percent; when it is unsure, the set widens. That adaptivity is the point.

This is nucleus sampling, introduced by Holtzman et al. in ["The Curious Case of Neural Text Degeneration"](https://arxiv.org/abs/1904.09751). Their finding was that maximizing likelihood, greedy or beam search, produces bland, repetitive text, while truncating the unreliable tail before sampling produces output that is both diverse and coherent. Three of our four cards set `top_p: 0.95`, which is close to the value that paper landed on.

### top_k

`top_k` is the blunter sibling. It keeps the `k` highest-probability tokens, full stop, and samples from those. Where `top_p` adapts the cut to the shape of the distribution, `top_k` fixes the candidate count regardless of how confident the model is. The two compose: when both are set, the model takes whichever cut is tighter at that step.

Top-k sampling for neural generation was popularized by Fan et al. in ["Hierarchical Neural Story Generation"](https://arxiv.org/abs/1805.04833), where truncating to the top k candidates kept story generation from drifting into incoherence. This is the knob where our cards diverge most visibly, and that divergence is the whole argument for putting it on a card. Qwen3.6 wants `top_k: 20`. Both Gemma 4 cards want `top_k: 64`. Laguna-XS.2, a code model, sits at 50. Same field, three different numbers, because three different labs tuned three different models. There is no portable default to fall back on.

### min_p

`min_p` sets a floor relative to the top token. With `min_p: 0.05`, any token whose probability is below 5 percent of the most likely token's probability is dropped. When the model is confident and one token dominates, the floor rises and the candidate set shrinks toward greedy; when the model is uncertain and the top token is only modestly ahead, the floor drops and more candidates survive. It adapts to confidence in a way the fixed cuts do not.

The method is from Nguyen et al., ["Turning Up the Heat: Min-p Sampling for Creative and Coherent LLM Outputs"](https://arxiv.org/abs/2407.01082), which shows it holds coherence at higher temperatures where top-p starts to wander. All four of our current cards set `min_p: 0.0`, which disables it. The field is present because the schema supports it and a future model may ask for it, not because anything we serve today leans on it.

### repetition_penalty, and how it differs from the others

`repetition_penalty` discourages the model from repeating itself by dividing the logit of any token that already appeared in the context. A value of 1.0 is a no-op; above 1.0 it dampens repeats. It is the cure for the loop, the model that locks into "the the the" or restates the same sentence forever.

The mechanism comes from Keskar et al.'s CTRL paper, ["CTRL: A Conditional Transformer Language Model for Controllable Generation"](https://arxiv.org/abs/1909.05858), which proposed the multiplicative penalty on the logits of seen tokens. It differs from the two penalties people reach for next to it, and the difference is easy to get wrong. Frequency penalty scales with how many times a token has appeared, so the more you repeat something the harder it gets pushed down. Presence penalty is a flat one-time subtraction the instant a token appears at all, regardless of count. CTRL-style repetition penalty is multiplicative on the logit rather than additive, and it triggers on presence rather than count. Our schema carries `repetition_penalty` and `presence_penalty` as separate fields for exactly this reason; they are not the same lever. Every card we ship today sets `repetition_penalty: 1.0` and `presence_penalty: 0.0`, both off, because these are well-behaved models that do not need to be pulled out of loops.

A note on the wire: this is the field that surfaces as `repeat_penalty` in `/props` `default_generation_settings`, per the llama.cpp naming. If you are reading the endpoint and the card side by side, that is the one pair that does not spell the same.

### seed

`seed` is not a shape knob; it is a reproducibility knob. Sampling draws from the truncated, reshaped distribution using a random number generator, and pinning the seed makes that draw deterministic. Same prompt, same parameters, same seed, same output, token for token. It changes nothing about quality and everything about whether you can repeat a run.

It is not a `sampling` field on the card, because there is no recommended seed; a seed is a per-run choice, not a model property. It shows up instead under `sampling.capabilities` in `/props` as `supports_seed: true`, which is the server's way of saying you may pin it. We rely on it constantly for the benchmarks. A single committed seed is what makes a luce-bench result comparable across runs, which is why the harness records it; see [Running the benchmarks](<Running the benchmarks — an intro to luce-bench.md>).

## The takeaway

These six knobs are stages in one pipeline: truncate the tail, reshape the distribution, bias against repeats, and pin the draw if you need it twice. The mechanisms are stable and well documented. The values are not portable. Qwen3.6 wants `top_k: 20` and Gemma 4 wants 64, and the only correct way to know that is to read it off the card the model shipped with. The Gemma-at-temperature-0 collapse is the cautionary version of the same point: a sane-sounding default applied to the wrong model is a real failure, not a hypothetical one. That is why the numbers live on a typed sidecar the server reads at startup rather than in anyone's head.

*Schema: `share/model_cards/_schema.json` (the `sampling` block). Server mapping: `build_props_body` in `server/src/server/http_server.cpp`. Recommended values per model live on the card; see the companion post below.*

**Related**
- [Model cards in lucebox: a typed sidecar for what the server actually needs](<Model cards in lucebox — a typed sidecar for what the server actually needs.md>). Where these values come from and how the server resolves them.
- [What `/props` tells you about a lucebox server](<What props tells you about a lucebox server.md>). The endpoint that reports `default_generation_settings` and `sampling.capabilities`.
- [Running the benchmarks: an intro to luce-bench](<Running the benchmarks — an intro to luce-bench.md>). The harness that pins the seed so a run is comparable.
- [Multi-turn agentic loops as a benchmark target: what they look like, why they matter, what we've measured](<Multi-turn agentic loops as a benchmark target — what they look like, why they matter, what we've measured.md>)
- [The agentic stack is the product, not the model](<The agentic stack is the product, not the model.md>)
- [Tuning Qwen3.6-27B decode on a 3090 Ti: the knobs that moved throughput](<Tuning Qwen3.6-27B decode on a 3090 Ti — the knobs that moved throughput.md>)
