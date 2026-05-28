# Model cards in lucebox: a typed sidecar for what the server actually needs

When we load a model into luce-dflash, the server needs a handful of numbers before it can serve a single request well: what temperature to sample at, how many tokens the model is allowed to think for, how many to reserve for the visible answer, and what to say to the model when its thinking runs long. Every one of those numbers exists somewhere upstream. None of them live in one place we can read at startup.

So we wrote them down ourselves, once per model, in a small typed JSON file. We call it the model card sidecar. This post covers why the format exists, what it carries, how the server uses it, and why we ended up inventing a format instead of reusing what upstream ships.

## Why the format exists

An upstream model card is two things stapled together. The first is a HuggingFace README, which is human prose: a paragraph that says "we recommend temperature 1.0, top_p 0.95, top_k 20 for thinking mode," a table of context lengths, a sentence buried halfway down about a recommended output budget for hard problems. The second is `generation_config.json`, a loose machine-readable file that sometimes pins `temperature` and `top_p` and usually stops there.

Neither of those is a contract a server can consume. The README is for people. `generation_config.json` is closer, but it is partial by design: it carries decode defaults and nothing about the reasoning budget, the reply reserve, or how the model wants to be told to stop thinking. The Qwen3 technical report (arXiv 2505.09388) documents the exact sentence you inject to force a thinking model to wrap up, and that sentence appears in no config file anywhere. It is in a PDF.

The result is that the things luce-dflash actually needs to set good defaults are scattered across prose, partial in the config, or absent entirely. We needed one file, typed, that we could read at startup and validate in CI.

## What the sidecar carries

Each known model gets a file at `share/model_cards/<name>.json`, validated against `share/model_cards/_schema.json`. Four fields are required; the rest are optional and fall through to computed or family defaults when omitted.

| Field | What it carries |
|---|---|
| `name` | Display name. Informational. The filename is what the lookup keys on. |
| `source` | URL of the upstream card we transcribed from. |
| `verified_at` | ISO date we last checked the values against that source. |
| `max_tokens` | The card's standard recommended combined cap. Drives `default_max_tokens`. |
| `complex_problem_max_tokens` | Optional. The card's recommendation for hard reasoning or benchmark workloads. Drives the `x-high` and `max` effort tiers. |
| `hard_limit_reply_budget` | Optional. Tokens reserved after `</think>` for the visible answer. Default 4096. |
| `thinking_marker` | Optional. The bytes that signal end-of-thinking to our parsers. Empty means use the architecture default. |
| `thinking_terminator_hint` | Optional. The directive we inject mid-stream to tell the model to wrap up. |
| `sampling` | Optional. Recommended sampler defaults, applied when a request omits a field. |
| `reasoning_effort_tiers` | Optional. Explicit per-tier phase-1 budgets, overriding the computed defaults. |
| `download_urls` | Optional. Map of variant tag to GGUF URL, used by deployment tooling. |
| `notes` | Optional. Free-form provenance and caveats. |

The `source` and `verified_at` fields are the provenance pair. They exist so that future-us, staring at a `top_k` of 20, can click through to the exact README we read it from and see how stale our reading is. The Qwen3.6 27B card, for instance, points at `https://huggingface.co/Qwen/Qwen3.6-27B` and is dated 2026-05-25.

Here is the Qwen3.6 sidecar in full, since it exercises almost every field:

```json
{
  "name": "Qwen3.6 27B",
  "source": "https://huggingface.co/Qwen/Qwen3.6-27B",
  "verified_at": "2026-05-25",
  "max_tokens": 32768,
  "complex_problem_max_tokens": 81920,
  "hard_limit_reply_budget": 4096,
  "thinking_terminator_hint": "Considering the limited time by the user, I have to give the solution based on the thinking directly now.\n</think>\n\n",
  "sampling": {
    "temperature": 1.0,
    "top_p": 0.95,
    "top_k": 20,
    "min_p": 0.0,
    "presence_penalty": 0.0,
    "repetition_penalty": 1.0
  },
  "reasoning_effort_tiers": {
    "low": 4032,
    "medium": 16128,
    "high": 32256,
    "x-high": 56832,
    "max": 81408
  }
}
```

The two Gemma 4 cards (26B-A4B and 31B) are sparser. Both cap `max_tokens` at 16384, both keep the 4096 reply reserve, both set Gemma's `top_k` of 64, and both carry a `thinking_terminator_hint` of `"<channel|>\n\n"` rather than the Qwen sentence. They also carry a `download_urls` block and a `notes` field, because Gemma's GGUFs are community quantizations by bartowski and the DFlash drafters are ours, and that is exactly the kind of thing that belongs in provenance rather than memory. Laguna-XS.2 is a code model and pins a conservative `temperature` of 0.6, with a note recording that the upstream card does not pin sampling at all, so the value is our choice.

## How the server uses it

At startup, luce-dflash resolves one model card for the loaded GGUF. The resolution walks four sources and takes the first that provides each value:

1. An explicit CLI flag. `--think-max-tokens`, `--default-max-tokens`, and the rest always win.
2. The sidecar, keyed on the GGUF's `general.name` metadata normalized to a filename stem.
3. A per-family fallback table built into the C++ server, keyed on the detected architecture.
4. A hard fallback, the old `ds4_eval.c` reference values.

The normalization step has one rule that matters in practice. `normalize_model_card_stem` lowercases, turns spaces, tabs, and underscores into `-`, keeps `[a-z0-9.-]`, and silently drops everything else. So a GGUF whose `general.name` reads "Qwen3.6 27B" resolves to `qwen3.6-27b.json`. The match is on that normalized stem alone; the `name` field inside the file is decorative.

If no sidecar matches, the family table catches known architectures. `qwen3` / `qwen35` / `qwen36` get `max_tokens` 32768 and a 4096 reply reserve; `gemma4` gets 16384; `laguna` gets 32768. These are deliberately conservative and not aspirational. The expectation is that a production model ships a real sidecar, and the family table is a safety net for the day someone loads a GGUF we have not transcribed yet.

The hard fallback, when even the architecture is unknown, is `max_tokens` 16000 with the 4096 reply reserve, giving a derived `think_max_tokens` of about 11904.

Once a card is resolved, the server derives the rest. `think_max_tokens` is `max_tokens - hard_limit_reply_budget`. Any effort tier the sidecar did not pin is computed from a ratio formula: `low` is one-eighth of `think_max`, `medium` is half, `high` is the full `think_max`, and `x-high` and `max` interpolate up toward the complex-problem budget when the card has one (and collapse down to `high` when it does not). The tiers are then clamped to be monotonically non-decreasing, with a warning if the card violated that.

All of this surfaces over `GET /props`. The server stashes the parsed sidecar verbatim and re-emits it under `model_card`, so anyone hitting the endpoint sees exactly the file on disk, validated against the same schema. When the server fell through to a family or hard fallback, `model_card` is `null` and the source label shows up separately under `budget_envelope.model_card_source`. That is the link between this format and what a caller actually observes at runtime; see <What props tells you about a lucebox server.md> for the full endpoint.

## The thinking terminator, and why it ties to the force-close

The `hard_limit_reply_budget` and `thinking_terminator_hint` fields are the half of the card that the engine, not the sampler, consumes. They are also the half that has no upstream home at all.

When a thinking request runs long, the decode loop tracks how many tokens it has generated. The moment `(n_gen - generated) <= hard_limit_reply_budget`, the remaining headroom is reserved for the visible answer, and the engine overrides the next sampled tokens with the `thinking_terminator_hint` sequence verbatim. The server does not auto-append a close marker. If the operator wants the `</think>` in the inject, they put it in the hint. That is deliberate: it lets us test whether a hint alone induces the model to self-close versus whether we have to force the close ourselves.

For Qwen3.x the canonical hint, the one from the technical report, embeds the marker: `"Considering the limited time by the user, I have to give the solution based on the thinking directly now.\n</think>\n\n"`. That single string is the whole reason this field exists. It is a trained directive, it lives in a PDF, and it is the difference between a force-closed Qwen3.6 finishing its answer cleanly and one that keeps deriving in the visible reply. The force-close mechanism is covered in <Putting Qwen's thinking on a budget — counting tokens and forcing the close.md>.

The default `hard_limit_reply_budget` used to be 512, inherited from `ds4_eval.c`, which was sized for DeepSeek-V4-flash's terse style. We raised it to 4096 on 2026-05-25 after watching it silently truncate almost every other model mid-answer; one bench probe got cut off in the middle of a coordinate-geometry proof. Terse models can override back down to 512 in their sidecar. Verbose math and code models keep 4096. That override is exactly the kind of per-model decision the sidecar exists to record.

## Why a sidecar, and why we invented it

The obvious alternative is to bake these values into the GGUF metadata. We did not, for a few reasons.

The values change independently of the weights. We bumped a default and re-read a card without anyone re-quantizing a model; a sidecar lets us edit a number and ship it without touching a multi-gigabyte artifact. The GGUFs we serve are frequently community quantizations we do not control. We can ship a sidecar for a bartowski quant the same day it appears, keyed on the normalized `general.name`, without owning the file. And provenance wants to be diffable. `source` and `verified_at` belong in version control next to a date and a commit, not embedded in a binary blob where nobody will ever look at them.

As for inventing a format rather than reusing one: we looked, and there is no upstream contract that carries what the server needs. The README is prose. `generation_config.json` is partial and decode-only. The reasoning budget, the reply reserve, the effort-tier curve, and the terminator hint are not in any of them. So the sidecar is a small, typed, validated transcription layer. It reads the human card and the loose config and the technical report, and it writes down the subset luce-dflash can act on, with a URL and a date so the next person can check our work.

It is a boring file. That is the point. The interesting parts of a model card are for people to read; the sidecar is the part a server can run.

*Schema: `share/model_cards/_schema.json`. Resolution and field reference: `docs/specs/thinking-budget.md` §3. Loader: `server/src/server/model_card.cpp`.*

**Related**

- <Meet lucebox — a local AI inference engine optimized for consumer hardware.md>. The engine and the Docker workflow.
- <What props tells you about a lucebox server.md>. The endpoint that re-emits the resolved card.
- <Putting Qwen's thinking on a budget — counting tokens and forcing the close.md>. The force-close the terminator hint feeds.
- <Running the benchmarks — an intro to luce-bench.md>. The harness that snapshots `/props` per run.
- Sampling parameters on a lucebox model card: what the knobs mean
- Multi-turn agentic loops as a benchmark target: what they look like, why they matter, what we've measured
