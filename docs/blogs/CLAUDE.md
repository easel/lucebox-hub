# Writing posts in this folder

Voice and conventions for the lucebox/luce-bench blog posts. Read this before drafting or editing one.

## Voice

- **First-person lab notebook.** Lead with what we expected and what we found
  ("We expected the 192 GB Mac to have the edge. It didn't pan out."). A little
  personality is good; relentless neutrality is not.
- **Let the numbers carry it.** State results plainly. No hype verbs (beats,
  wins, dominates, crushes) — use *matched*, *edged*, *came out ahead*, *holds*.
- **Earn emphasis.** Don't tell the reader something is interesting; show it.

## Honesty / claims

- **Scope every claim to the benchmark.** ds4-eval-92 is one 92-question set. A
  lead on it means a model is good *at this*, not "better overall." Say so.
- **Credit the competition.** DeepSeek V4 is a strong model; a small model
  edging it on one eval is the story, not a verdict.
- **Lead with the durable result.** Footprint and speed (24 GB vs 192 GB, ~5x
  decode) are robust; a 3-point accuracy gap is benchmark- and seed-specific.
- **State caveats inline:** mode (think vs nothink), quant (Q4_K_M vs ~2-bit),
  single seed, decode-rate vs wall. Name the model size and quant when comparing.
- **nothink is Gemma 4's real mode** (think is within noise and ~10x slower).

## Anti-slop (run the `avoid-ai-writing` skill on every draft)

- **No em dashes in prose.** Use commas, periods, parentheses, or two sentences.
  (Em dashes are fine in *filenames* only — see below.)
- No "it's not X, it's Y" constructions. No compulsive rule-of-three. No bolded
  inline-header bullets or bold TL;DR labels (plain bullets).
- No CTA/marketing blocks. No `delve / leverage / seamless / robust / tapestry /
  realm`-type filler. Vary sentence length.
- After rewriting, do the skill's **second-pass audit**: re-read for survivors.

## Structure

A results post runs: short lede (finding stated once) → plain TL;DR → setup →
data table → "what the table says" analysis → honest takeaway → footer
(concise attribution) → **Related** list. Don't repeat methodology — point to
the hub posts. Vary paragraph length.

Two hub posts carry the shared material so results posts stay short:
- *Running the benchmarks* — luce-bench, ds4-eval provenance + antirez credit,
  the comparability rules, run commands.
- *Meet lucebox* — the engine, the Docker workflow.

Every post links both hubs (and siblings) in **Related**. Don't re-explain
ds4-eval provenance in a results post; link the hub and add only the deltas.

## Naming and references

- **lucebox** = the project/engine. **luce-dflash** = the server daemon.
  **DFlash** = the speculative-decode technique. **luce-bench** = the benchmark
  harness (ships in lucebox-hub, not a standalone repo).
- GitHub org is **Luce-Org**. Docker image: `ghcr.io/Luce-Org/lucebox-hub:cuda12`.
  Baselines: `Luce-Org/luce-bench-baselines`. Don't link a standalone
  `easel/luce-bench`.

## Files and links

- **Filename matches the H1**, with `: ` rendered as ` — ` (filesystem-safe;
  the H1 keeps the colon). Example: H1 `Foo: bar` → file `Foo — bar.md`.
- Cross-links are **relative**, angle-bracketed because filenames have spaces:
  `[text](<Other Post — subtitle.md>)`. Swap for real slugs at publish.
- After any rename, re-point every `](<...md>)` link and Related-list label.

## Data discipline

- Numbers come from committed runs in `Luce-Org/luce-bench-baselines`, produced
  by `scripts/run-baseline.sh`. Single seed unless stated. Don't ship a
  `_pending` cell.
- Report accuracy with wall (median) and decode tok/s. Decode rate is
  mode-independent and comparable; wall depends on token count.
