# How lucebox auto-tunes itself to your GPU

*May 2026 · by [Davide Ciffa](https://x.com/davideciffa) and [Erik LaBianca](https://x.com/easel)*

We kept hand-rolling `DFLASH_*` flags for every card we tested on, and we kept
getting it slightly wrong. Too much context and a 24 GB card OOMs under tool
traffic. Too little and you leave headroom on the floor. A managed provider has
a team that tunes prefill, caching, speculative decode, and context window per
chip before you ever send a request. On a consumer GPU that job lands on the
operator. So we taught lucebox to do the tuning itself.

`lucebox benchmark` runs an auto-tuner. It sweeps the engine's tunables on your
actual hardware, gates each candidate on capability and quality checks against
prompts the server will actually see, and writes the winning config to
`~/.lucebox/config.toml`. The thesis behind it is
that high-quality local inference is more than weights plus a GPU. The
difference between a config that fits and one that crashes (or one that runs at
half speed) is in the tuning, and that part is automatable.

TL;DR:

- `lucebox benchmark` sweeps tunables, validates candidates, persists the winner.
- Three profiles escalate the work: `level1` (default, conservative), `level2`
  (context-vs-budget sweep within a speed floor), `level3` (stress validation
  for new architectures).
- The starting point is a VRAM-tiered heuristic, so the sweep refines a config
  that already "should work" rather than searching blind.
- Winning values merge back into `config.toml`; reports land under
  `models/.lucebox/`.

## The heuristic floor comes first

Before any sweeping, lucebox picks a conservative baseline from one fact about
your machine: VRAM. The tiers target Qwen3.6-27B Q4_K_M (about 16 GB) plus a
Q4_K_M DFlash draft (about 1 GB), and they get more generous as the card gets
bigger. Under 12 GB it caps context at 4096 and forces lazy draft as a floor, so
a too-small card gets an explicit daemon error instead of a silent OOM. The
24 GB consumer flagships (3090, 4090, 5090) cap at 96 K by default, because 112 K
can start but long prompts have reproduced CUDA VMM allocation failures on those
cards. WSL2 starts lower still (65536 context, budget 16) because it needs more
VMM headroom, and it leans on the stress profile to prove anything higher before
persisting it. At 40 GB and up you get the full 128 K.

That heuristic is what `lucebox configure` writes on its own. The auto-tuner
treats it as a starting point and refines specific fields from there. If there
is no VRAM signal at all, it stays on the engine's class defaults rather than
guessing.

## Sweep, validate, persist

The auto-tuner runs the optimizer inside the container, then the host reads back
a `bench-report.json` and acts on it. The shape is the same across profiles.

Sweep. For each combination of the swept tunables (budgets, context lengths, and
whatever else you widen the sweep with) it starts a server cell, measures decode
throughput over a handful of prompts, and records the cell. Budgets sweep
`8,16,22,32` by default, with five prompts per cell and 256 generated tokens.

Validate. A fast decode number is not enough to win. Candidates are gated on
real capability and quality suites: a smoke capability check, short HTTP
frontiers, and agentic tool-call validation at `level1`, with heavier suites
available on demand. A hard-gated suite that fails rejects the current candidate.
The optimizer then tries the next ranked candidate before it gives up. If every
candidate fails its gates, the config is left unchanged. Speed never overrides
correctness.

Persist. The winning cell's `budget`, `max_ctx`, lazy-draft flag, prefix-cache
slots, KV-cache types, and pFlash settings merge back onto the heuristic
baseline and get written to `config.toml`, with an `autotune.source = benchmark`
marker and a `benchmark` block recording the winner and the mean decode rate.
The per-run reports land under `models/.lucebox/`, and `lucebox profile
--export-snapshot` can fold them into the local append-only profile store. (For
what the running server then advertises about that config, see [what `/props`
reports](<What props tells you about a lucebox server.md>).)

## The three profiles

The profiles are about how hard the auto-tuner works to earn a config, not about
which knobs exist.

`level1` is the default and the conservative one. It starts from the VRAM
heuristic, sweeps the selected tunables at the configured context, and requires
smoke capability, short HTTP frontiers, and agentic tool-call validation to pass
before it persists anything.

`level2` widens the search to context. It sweeps `DFLASH_MAX_CTX × DFLASH_BUDGET`
(plus any cache, pFlash, or lazy values you requested) and then picks the highest
reliable context that still clears the standard validation gates and stays within
a speed floor. The floor is `--min-context-speed-ratio`, default `0.85`, meaning
a candidate has to hold at least 85% of the fastest cell's decode rate to be
kept. This is the profile for "I want as much usable context as this card can
actually sustain."

`level3` is stress validation, for a new architecture or after a code change.
It runs a context-first sweep, repeated agentic tool calls, a multi-turn agentic
session, and broader HTTP frontier coverage before it will accept aggressive
settings. This is how you prove that, say, `114688/22` is safe on a 3090 Ti
before you commit to it, rather than discovering the headroom problem in
production.

## The parameters it manages

These are the engine tunables the sweep can set and persist. Defaults are the
engine's class defaults; the heuristic and the sweep override them per machine.

| Parameter | Env var | Default | What it controls |
|-----------|---------|---------|------------------|
| budget | `DFLASH_BUDGET` | `22` (8 on AMD RDNA3) | DDTree speculative tree budget |
| max_ctx | `DFLASH_MAX_CTX` | autotuned (heuristic 16384) | Context length |
| lazy | `DFLASH_LAZY` | `false` | Lazy draft loading |
| prefix_cache_slots | `DFLASH_PREFIX_CACHE_SLOTS` | `0` | System-prompt prefix-cache snapshots |
| prefill_cache_slots | (sweep only) | `0` | Prefill-cache slots |
| cache_type_k | `DFLASH_CACHE_TYPE_K` | auto | K-cache quant type |
| cache_type_v | `DFLASH_CACHE_TYPE_V` | auto | V-cache quant type |
| prefill_mode | `DFLASH_PREFILL_MODE` | `off` | pFlash long-prompt prefill (`off`/`auto`/`always`) |
| prefill_keep_ratio | (sweep only) | `0.05` | pFlash keep ratio |
| prefill_threshold | (sweep only) | `32000` | pFlash auto-trigger token threshold |
| prefill_drafter | `DFLASH_PREFILL_DRAFTER` | unset | pFlash drafter GGUF (Qwen3-0.6B BF16) |
| think_max | (config) | `15488` | Thinking-token budget |

`prefix_cache_slots` is interesting because the heuristic keeps it at 0 even
though it is a real tunable: the daemon's snapshot path for tool prompts is not
yet reliable with prefix slots on, so the auto-tuner only enables it if you
sweep it in explicitly. The `think_max` default of 15488 is `16000 - 512`, which
matches antirez/ds4's `ds4_eval.c` generation budget rather than the server's own
hardcoded 10000 (more on that thinking budget in [Putting Qwen's thinking on a
budget](<Putting Qwen's thinking on a budget — counting tokens and forcing the close.md>)).

You widen the sweep with `--lazy-values`, `--prefix-cache-slots-values`,
`--kv-values`, `--prefill-modes`, `--prefill-keep-ratios`, and
`--prefill-thresholds`. KV modes accept `auto,f16,q4_0,q4_1,q5_0,q5_1,q8_0,tq3_0`.
pFlash modes accept `off,auto,always`.

## Attaching validation suites

The gates above are the defaults per profile, but you can attach more with
`--extra-suites`. The options are `http-frontiers`, `capability`, `ds4-eval`,
`capability-long`, `agentic-tools`, and `agentic-session`. A failed hard-gated
suite rejects the current candidate, so adding suites makes the bar higher rather
than just adding reports.

Two of these need naming precisely. `http-frontiers` is a DS4-bench
inspired HTTP throughput probe, not antirez/ds4's `ds4-eval`. The `ds4-eval`
suite is the real thing: it ports all 92 embedded ds4-eval questions with the
same `source/id` names, final-answer grading, and trace pattern, score-only, with
thinking enabled and the upstream 16k-token budget. `capability` is the short
lucebox API smoke gate. `agentic-session` is inspired by club-3090's
coding-session benchmark and uses the Anthropic Messages wire shape that Claude
Code emits: streamed `tool_use` blocks followed by deterministic `tool_result`
history, so it can watch first-content latency, wall time, decode rate, and
context growth as tool results pile up across turns. The full methodology lives
in our benchmark hub, [Running the benchmarks](<Running the benchmarks — an intro to luce-bench.md>);
this post only covers how the auto-tuner wires those suites in as gates.

## Why bother

The honest version is that we built this because we were bad at doing it by hand,
repeatedly, across a pile of cards. The general-purpose answer is the one in the
lede. A provider hand-tunes prefill, caching, speculative decode, and context per
chip, and that tuning is a real part of why hosted inference feels fast and never
falls over. On a consumer GPU nobody is doing that for you. The auto-tuner closes
that gap: it gives a 3090 or a 4090 a config matched to its actual VRAM and
behavior, validated against the prompts it will serve, without anyone
hand-rolling flags. For
the engine those flags drive and the Docker workflow around it, see [Meet
lucebox](<Meet lucebox — a local AI inference engine optimized for consumer hardware.md>).

---

*lucebox is the engine; luce-dflash is the server daemon; DFlash is the
speculative-decode technique. Source and images live under the Luce-Org GitHub
org.*

**Related**
- Meet lucebox: a local AI inference engine optimized for consumer hardware
- Running the benchmarks: an intro to luce-bench
- Putting Qwen's thinking on a budget: counting tokens and forcing the close
- What /props tells you about a lucebox server
- Model cards in lucebox: a typed sidecar for what the server actually needs
- Sampling parameters on a lucebox model card: what the knobs mean
- Multi-turn agentic loops as a benchmark target: what they look like, why they matter, what we've measured
