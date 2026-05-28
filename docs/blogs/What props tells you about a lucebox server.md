# What `/props` tells you about a lucebox server

*May 2026 · by [Davide Ciffa](https://x.com/davideciffa) and [Erik LaBianca](https://x.com/easel)*

Every benchmark we run starts with the same nagging question: what was the server
actually configured to do when this number came out? Which sampler defaults were
live, which quant, what context length, was speculative decode on, was a thinking
budget in force. For a long time the honest answer was "read the startup banner,
or grep the launch command, or trust the run notes." That is exactly the kind of
guessing that makes a benchmark hard to reproduce six weeks later. So lucebox
servers answer it directly, over HTTP, with `GET /props`.

The thesis is simple. Every sampling, model, engine, and hardware detail a client
might care about should be discoverable from the running server, not inferred. A
benchmark harness should be able to ask the server what it is rather than hardcode
assumptions about it. A snapshot of `/props` committed next to a result makes that
result self-describing.

## What's in the body

`GET /props` is unauthenticated (same posture as `/health`, so deployment probes
work) and never blocks on the worker thread. It reads config snapshots and atomic
counters only, so a long generate request in flight will not delay it. The body is
one JSON object with about twenty top-level keys. Rather than dump all of them,
here are the groups that matter when you are reading a result back.

### Sampling: what the model card actually recommends

The single field that bit us hardest in practice is the sampler default. A Gemma 4
card wants `temperature=1.0, top_p=0.95, top_k=64`; run it at the greedy fallback
of `temperature=0.0` and you get degenerate-decode collapse and a quietly wrong
benchmark. So `default_generation_settings` reports the values the server will
actually apply when a request omits a field, drawn from the loaded card rather than
a hardcoded greedy default:

```json
"default_generation_settings": {
  "n_ctx":          98304,
  "temperature":    1.0,
  "top_p":          0.95,
  "top_k":          20,
  "min_p":          0.0,
  "repeat_penalty": 1.0
}
```

Those field names follow the llama.cpp wire convention (`repeat_penalty`, not
`repetition_penalty`) so consumers written against llama-server keep working. The
authored model-card recommendation appears separately and verbatim under
`model_card.sampling`, and a `sampling.capabilities` block advertises which request
fields the server honors (`supports_temperature`, `supports_top_k`,
`supports_seed`, and so on) so a client can skip sending fields that would be
silently ignored.

### Model: which weights, which quant, which tokenizer

`model_path` is the absolute path of the loaded target GGUF, which answers "which
weights is this actually serving" without ambiguity. `model.arch` is the
normalized `general.architecture` from the GGUF (`qwen35`, `gemma4`, and so on),
`model.draft_path` is the speculative draft GGUF or `null`, and `model.tokenizer_id`
is a best-effort family hint. `model_alias` is the string clients pass back as the
`model` field on a request.

The `model_card` block is the on-disk sidecar emitted 1:1, or `null` when the
server fell back to a family or hard default (in which case
`budget_envelope.model_card_source` still records `family:<arch>` or
`hard-fallback`). The sidecar's fields and resolution order are their own topic:
[Model cards in lucebox](<Model cards in lucebox — a typed sidecar for what the server actually needs.md>).

### Engine: speculative decode, the budget envelope, the caches

This is where lucebox carries more than the baseline convention. `speculative_mode`
reports the active path (`off`, `dflash`, or `pflash`), and `speculative` carries
the DDTree `enabled` flag plus the `ddtree_budget`. There is a separate `pflash`
block for the speculative-prefill-compression state (mode, threshold, keep ratio,
and tunables), all `null` when it is off.

The `budget_envelope` block is the source of truth for what the server will do with
a thinking request, as opposed to what the card authored. It carries the
runtime-resolved knobs after CLI overrides and after the per-tier clamp to
`max_ctx - hard_limit_reply_budget`:

```json
"budget_envelope": {
  "model_card_source":       "share/model_cards/qwen3.6-27b.json",
  "default_max_tokens":      32768,
  "hard_limit_reply_budget": 512,
  "think_max_tokens":        32256,
  "effort_tiers": { "low": 4032, "medium": 16128, "high": 32256, "x-high": 56832, "max": 81408 }
}
```

These can diverge from `model_card.reasoning_effort_tiers` because of that clamp,
which is exactly the kind of drift you want recorded rather than reconstructed. The
mechanics behind those tiers are their own
[story](<Putting Qwen's thinking on a budget — counting tokens and forcing the close.md>).
Alongside that, `reasoning` advertises the supported efforts and any default, the
`prefix_cache` and `full_cache` blocks report KV-reuse occupancy, and `tool_replay`
reports the tool-call replay cache.

### Hardware and runtime: the GPU-facing knobs

`runtime` collapses every startup-resolved knob into one snapshot: the compute
`backend` (`cuda`, `hip`, or `cpu`), the KV cache dtypes (`kv_cache_k` /
`kv_cache_v`, where the auto-default depends on context size), the sliding-window
`fa_window`, the prefill `chunk` size, whether the target is sharded across GPUs
(`target_sharding`), and the resolved `target_device` / `draft_device` placement
strings. Add `build_info` and the structured `server` block (name, version, and the
integer `props_schema`, currently 2), and you can tell two runs apart down to the
KV quant and which GPU the draft landed on.

## How lucebox uses it

Two pieces of tooling consume `/props`, and together they make every committed
benchmark run self-describing.

`luce-bench`'s preflight hits `/props` before a run as a soft check. If the
endpoint is absent it just notes "non-dflash server, skipped" and moves on (so
OpenRouter and vLLM targets still run). If it is present, it surfaces the
`budget_envelope.model_card_source` and `hard_limit_reply_budget` right in the
preflight output, so you see which card resolved and what reply reserve is live
before you spend an hour generating.

The `run-baseline.sh` script in
[Luce-Org/luce-bench-baselines](https://github.com/Luce-Org/luce-bench-baselines)
goes one step further. At the start of every run it curls `/props` and writes the
whole body to `props.json` inside the run directory, next to the result and the
exact command line. On a non-lucebox target the file simply does not get created.
The payoff is that a baseline committed today still carries its own sampler
defaults, quant, budget envelope, and KV config when you open it months from now.
No banner archaeology, no guessing.

That is the whole point of the endpoint. The server already knows everything about
itself, so it should be the one to tell you, in a form a client can read.

## Where the convention comes from

We did not invent the endpoint name. The llama.cpp server has carried a `/props`
endpoint for a long time as a server-state snapshot (it documents
[`GET /props`](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)
as "server global properties"), and aligning with that convention is why our wire
field names match llama-server's. lucebox extends the idea to carry the full
sampling-plus-model-plus-engine picture our tooling needs.

We think ds4 should have the same thing for the same reason, so we opened
[antirez/ds4 #81](https://github.com/antirez/ds4/pull/81) to propose a `/props`
endpoint upstream. That PR is still open and unmerged. The motivation matches our
own experience: when you are benchmarking a bunch of different providers and model
settings, querying the server directly beats keeping external notes.

---

*Spec: `docs/specs/props-endpoint.md` and `docs/specs/openapi-props.yaml` (current
`props_schema` is 2). Handler: `build_props_body` in
`server/src/server/http_server.cpp`. Preflight: `luce-bench/src/lucebench/cli.py`;
snapshotting: `scripts/run-baseline.sh` in `Luce-Org/luce-bench-baselines`. The
`/props` convention follows the
[llama.cpp server](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md);
we proposed it for ds4 in the open
[antirez/ds4 #81](https://github.com/antirez/ds4/pull/81). Project:
[github.com/Luce-Org/lucebox-hub](https://github.com/Luce-Org/lucebox-hub).*

**Related**
- Running the benchmarks: an intro to luce-bench
- Meet lucebox: a local AI inference engine optimized for consumer hardware
- Putting Qwen's thinking on a budget: counting tokens and forcing the close
- Every model we've run on ds4-eval-92
- How lucebox auto-tunes itself to your GPU
- Model cards in lucebox: a typed sidecar for what the server actually needs
- Sampling parameters on a lucebox model card: what the knobs mean
- Multi-turn agentic loops as a benchmark target: what they look like, why they matter, what we've measured
