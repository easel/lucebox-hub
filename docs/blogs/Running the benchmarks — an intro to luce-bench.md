# Running the benchmarks: an intro to luce-bench

*May 2026 · by Davide Ciffa and Erik LaBianca*

Every number in our model posts comes out of one tool: **luce-bench**, a small
harness that scores any OpenAI-compatible chat endpoint on the same cases, with
the same grader, under the same request rules. This post is the methodology
reference the results posts point back to: what the benchmarks are, where they
came from, and how to run them yourself. If you got here from one of the Gemma 4
26B posts, this is the protocol behind those numbers.

## What luce-bench is

luce-bench is the benchmark harness that ships in
[lucebox-hub](https://github.com/Luce-Org/lucebox-hub) (Apache-2.0). It scores any
OpenAI-compatible endpoint (local server, hosted gateway, anything that speaks the
OpenAI chat API) without pulling in the rest of the stack: one command, one set of
rules, comparable numbers across machines. Run it with `uvx luce-bench`.

## Where ds4-eval comes from

The reasoning benchmark we lean on most, `ds4-eval`, is not ours. It's the
92-question set embedded in [antirez/ds4](https://github.com/antirez/ds4),
Salvatore Sanfilippo's DeepSeek V4 Flash local inference engine, sitting right in
the engine's `ds4_eval.c` as an `eval_cases` table: 25 GPQA Diamond, 25
SuperGPQA, 25 AIME2025, and 17 COMPSEC questions, graded by a strict `Answer: X`
extract. Salvatore built both the engine and the eval in the open, MIT-licensed.
We ported the benchmark; we didn't write it.

ds4's eval is C, wired into ds4's own server. To score other stacks on the same
questions, we ported it into luce-bench's `ds4-eval` area as a faithful lift of
`ds4_eval.c`:

- The 92 cases are exported verbatim from the `eval_cases` table into a JSON
  fixture, so a future diff against upstream stays narrow.
- The graders mirror ds4's semantics: the permissive "find the `Answer:` marker,
  then take the next valid letter/integer" hunt for multiple-choice and AIME, and
  ds4's partial-credit line-range matching for COMPSEC. A strict pass requires
  the canonical `Answer: <X>` line; a mid-stream mention counts only as a
  semantic hint.
- `max_tokens` is pinned to **16000**, mirroring `ds4_eval.c`'s own default, a
  combined cap covering reasoning and reply.

## The areas

| Area | Cases | Grader | Source |
|---|---|---|---|
| `ds4-eval` | 92 (GPQA Diamond, SuperGPQA, AIME2025, COMPSEC) | strict `Answer: X` | [antirez/ds4](https://github.com/antirez/ds4) (MIT) |
| `code` | 10 (mid-function completion) | `ast.parse(prompt + completion)` | [openai/human-eval](https://github.com/openai/human-eval) (MIT) port |
| `longctx` | 6 (2k → 64k tokens) | `^Risk:` prefix check | own ports |
| `agent` | codex-style prompts + coding tasks | code-fence / json-tool / apply_patch detect | own ports |
| `forge` | 30 tool-calling scenarios | `error_type == None` | [antoinezambelli/forge](https://github.com/antoinezambelli/forge) (MIT) |

Upstream fixture licenses (all MIT) are reproduced in the package's `NOTICE`.

## The rules that keep numbers comparable

- *Send-nothing-explicit sampling.* luce-bench omits `temperature`, `top_p`, and
  the rest unless you set them, so each server applies its own defaults
  (model-card sampling, provider tuning). Forcing `temperature 0` everywhere would
  erase exactly the serving differences we want to measure.
- *Same `max_tokens`, server-side thinking split.* The 16000 cap goes on the wire
  identically; each server splits reasoning vs reply internally
  (`--think-max-tokens` on dflash, none on stock `ds4_server`). The wire protocol
  stays identical so cross-machine numbers stay honest.
- *Model auto-resolution.* With `--model default`, luce-bench queries
  `<base-url>/v1/models` and auto-picks when there's a single model; with several
  it lists them and makes you choose, so you never silently benchmark the wrong
  model.
- *Full payload per row.* Every result row carries `pass`, the full grader
  output, `wall_seconds`, `prompt_tokens`, `completion_tokens`, `content`,
  `reasoning_content`, `finish_reason`, and `timings` when the server surfaces
  them, enough to re-grade or debug after the fact.

## Running it

```bash
# one area against a local server
uvx luce-bench --area ds4-eval --base-url http://127.0.0.1:8080 --model dflash

# the full sweep (smoke, ds4-eval, code, longctx, agent, forge)
uvx luce-bench --areas all --name my-machine --base-url http://127.0.0.1:8080

# against a server exposing several models: list, then pick
uvx luce-bench --area ds4-eval --base-url http://host:1234 --model default   # prints the list
uvx luce-bench --area ds4-eval --base-url http://host:1234 --model gemma-4-26B-A4B-it-MLX-8bit

# against OpenRouter
export OPENROUTER_API_KEY=sk-or-...
uvx luce-bench --areas all --base-url https://openrouter.ai/api \
  --model google/gemma-4-26b-a4b-it --auth-env OPENROUTER_API_KEY
```

Add `--think` or `--no-think` to control the chat template's thinking mode
(otherwise the area's own default applies). A sweep writes per-area JSON plus a
`_summary.md` table under `./snapshots/<name>/`.

## Capturing baselines

The runs behind our posts live in
[Luce-Org/luce-bench-baselines](https://github.com/Luce-Org/luce-bench-baselines).
`scripts/run-baseline.sh` drives luce-bench via `uvx` and drops a snapshot into
the canonical `<host>-<gpu>-<label>-<date>/` directory, host and GPU
auto-detected, alongside a `/props` snapshot of the server config and a
re-runnable `command.sh`:

```bash
scripts/run-baseline.sh \
  --url http://localhost:8080 --api-model dflash \
  --label gemma4-26b-sweep --areas all
```

Baseline convention: runs are nothink by default (pass `--think` to flip). Diff
your own run against a published baseline with `luce-bench-report`.

---

*luce-bench is Apache-2.0; it redistributes MIT-licensed fixtures from
antirez/ds4, openai/human-eval, and antoinezambelli/forge (see `NOTICE`).
ds4-eval and the ds4 engine are the work of Salvatore Sanfilippo.*

**Related**
- Meet lucebox: a local AI inference engine optimized for consumer hardware
- Gemma 4 26B edges out DeepSeek V4 Flash (284B), at 5x the speed
- Gemma 4 26B across serving paths: a laptop GPU, a 3090 Ti, MLX, and OpenRouter
- Think vs nothink on Gemma 4: same accuracy, 10x the latency
- Every model we've run on ds4-eval-92
- Putting Qwen's thinking on a budget: counting tokens and forcing the close
- Qwen3.6 think vs nothink across providers: thinking helps, if you budget for it
- What /props tells you about a lucebox server
