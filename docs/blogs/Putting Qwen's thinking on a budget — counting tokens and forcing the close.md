# Putting Qwen's thinking on a budget: counting tokens and forcing the close

*May 2026 · by Davide Ciffa and Erik LaBianca*

Qwen3.6 is a strong reasoner when you let it think, and a problem when you try to
bound how much. We spent a while getting its thinking under control, and the
answer turned out to be unglamorous: count the output tokens ourselves and, when
the budget runs low, force the model out of its reasoning block by jamming a
`</think>` into the stream. Here's why the obvious approaches don't work and what
does.

## The problem: one cap isn't enough

Qwen wraps its scratch work in `<think> … </think>`. Everything before the close
tag is reasoning; everything after is the visible reply. The chat template
pre-opens the block, so the model starts decoding already inside `<think>`.

A single `max_tokens` cap can't govern that. On a hard prompt the model spends
its entire budget inside `<think>` and never emits `</think>`, and the response
comes back with no parseable answer at all. Tighten the cap and you get the
opposite failure: the model closes `</think>` with no tokens left to actually
answer. Either way you've burned the compute and have nothing to show a user.

## What doesn't work

Asking nicely. "Answer briefly," "don't overthink," "stop reasoning after a few
steps" in the system prompt are ignored. Reasoning is trained in, not
instruction-gated. (Gemma 4 takes this even further, which is its own
[story](<Think vs nothink on Gemma 4 — same accuracy, 10x the latency.md>).)

Letting the model self-close on a budget. If you just cap reasoning length and
hope the model wraps up, it doesn't. It gets truncated mid-derivation and the
leftover budget produces a fragment, not an answer.

## What works: two caps and a forced close

We split the single cap into two. A **phase-1 budget** bounds the reasoning, a
**combined cap** bounds the whole response, and a **reply-budget reserve** sits
between them to guarantee room for the answer. A request opts in with a
`thinking` block (Anthropic-style) or `reasoning.effort` (OpenAI-style), and the
effort tiers come from the model card sidecar (Qwen3.6 ships
`low=4032 … max=81408`).

Then the part that actually tames it: the server **counts tokens as it decodes**
and forces the close itself. In the autoregressive loop it tracks
`generated = committed_now − committed_at_entry`, and when
`remaining = n_gen − generated` drops to the reply reserve, it overrides the next
sampled token with `</think>`. That injected close tag is the whole trick: the
model was mid-thought, and the `</think>` yanks it into the reply phase, where its
strong end-of-answer prior takes over and it writes the actual answer with the
reserved tokens. The shibboleth that ends thinking is just the close tag, forced
into the stream on our schedule rather than the model's.

We run this two ways:

- **Level 2 (in-process force-close).** Override the next token with `</think>`
  right in the generation loop. No reprompt, KV cache preserved, and the reply is
  higher quality because the reasoning is still in frame when the model answers.
  This is the path for Qwen3.5/3.6, Gemma 4, and Laguna.
- **Level 1 (reprompt fallback).** For backends without the in-loop hook: when
  phase 1 ends with no `</think>`, build a fresh prompt with the reasoning plus an
  injected `</think>` and decode the reply. It works anywhere but costs a second
  prefill of the whole reasoning trace.

Level 2 fires first; Level 1 is the safety net.

## The gotcha: how much to reserve

The reply reserve is the knob that bit us. We inherited 512 tokens from
`ds4_eval.c`, which was sized for DeepSeek V4 Flash's terse answers. On Qwen (and
Gemma, and almost everything else) 512 tokens forced the close and then ran out
mid-answer, so the force-close "worked" and still produced garbage. Our Gemma
thinking probes were getting cut off mid-coordinate-geometry-proof. We raised the
default to 4096, which Qwen3.6 and the Gemma sidecars now ship. Terse models can
override it back down. Force-closing is necessary but not sufficient: you have to
leave the model enough runway to land.

## Where it leaves Qwen

With the two caps and the forced close, a thinking budget is finally a real dial
on Qwen3.6. You set an effort tier, the model reasons up to it, and it reliably
produces an answer within the combined cap instead of trailing off inside
`<think>`. That's the opposite of what we found on Gemma 4, where the think/nothink
switch is mostly cosmetic; on Qwen the thinking is doing work, and the budget is
the lever that makes it usable.

---

*Mechanism: `docs/specs/thinking-budget.md` and
`docs/experiments/thinking-mechanism-explainer.md`. Force-close (Level 2) lives in
the Qwen3.5/3.6, Gemma 4, and Laguna backends; the reply-reserve default and the
ds4_eval.c history are in the spec. Project:
[github.com/Luce-Org/lucebox-hub](https://github.com/Luce-Org/lucebox-hub).*

**Related**
- Running the benchmarks: an intro to luce-bench
- Meet lucebox: a local AI inference engine optimized for consumer hardware
- Think vs nothink on Gemma 4: same accuracy, 10x the latency
- Every model we've run on ds4-eval-92
