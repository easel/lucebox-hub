# Auto-integration manifest

Repository: `Luce-Org/lucebox-hub`
Integration branch: `auto-integration`
Writable remote: `easel`
Upstream remote: `origin` / `Luce-Org`
Last refresh: 2026-05-29T10:50:50-04:00
Current base: `origin/main` `8782d07a`
Current integration tip before this refresh: `easel/auto-integration` `8290ed4e`
Manifest refresh commit prepared in this run: this commit, if non-empty

This branch is maintained as a reproducible patch stack over `origin/main`. At
this run's start the primary checkout was clean, auth/tooling checks passed with
the real user credential home, and `origin` and `easel` were fetched separately.
`easel/auto-integration` was already based on current `origin/main` (`0` behind /
`438` ahead before reconciliation). One cleanly integrated PR head had advanced:
#285 (`feat/lucebox-docker`) moved from `09dc0bed` to `ccef4551`. The refresh
merged that PR head into the reconciliation worktree, resolving the only conflict
in `.github/workflows/ci.yml` by preserving the integration-only native server
`libcurl4-openssl-dev` install step while also adopting PR #285's pinned
`astral-sh/setup-uv` action SHA. Fresh direct-merge probes were then rerun for
all still-unintegrated non-draft PRs; their conflict classes are unchanged.

## Included in the current stack

| PR | Head branch | Head | State | Notes |
|---:|---|---:|---|---|
| #307 | `docs/why-this-exists-copy` | `236fc2fd` | included | Latest README “Why this exists” copy is merged. |
| #306 | `refactor-server-layer-split-runtime` | `988fc933` | included | Shared layer-split runtime helper extraction remains carried; it adds `server/src/common/layer_split_runtime.{h,cpp}` and rewires Gemma4, Laguna, and Qwen35 adapters. |
| #303 | `fix/harness-portable-run-dirs` | upstream `05b008a0` | included through upstream and stack | Harness portable run/cache directories and automatic client-install fallback are in `origin/main`; the stack preserved local compatibility docs and helpers. |
| #302 | `fix/harness-model-paths` | upstream | included through upstream | Harness launcher model-path override behavior and documentation are in `origin/main`. |
| #301 | `fix/ddtree-test-harness` | upstream | included through upstream | DDTree test harness fixes are in `origin/main`. |
| #300 | `fix/sigterm-gpu-unload` | upstream | included through upstream | SIGTERM GPU-unload fix remains in upstream. |
| #299 | `feat/draft-swa-flag` | upstream | included through upstream | Draft SWA env/flag support remains in upstream. |
| #298 | `fix/gemma4-destructor-link` | upstream | included through upstream | Gemma4 destructor-link fix remains in upstream. |
| #292 | `feat-backend-ipc-payload-pipe-open` | upstream / `90bc52f` | included through upstream and stack | Backend IPC payload-pipe support is upstream and still represented in the carried stack history. |
| #297 | `feat-server-laguna-layer-split-adapter-v2` | `53dd1686` | included | Laguna target-layer-split adapter remains carried. |
| #295 | `fix-layer-split-sampling` | `a9aedf7d` | included | Target layer-split sampling support remains an ancestor of the stack. |
| #294 | `feat/server-passthrough-proxy` | `48f6962d` | included | Server passthrough proxy wiring, piecewise keep-ratio curve, query survival checks, multimodal last-user text extraction, curl cleanup, and unit coverage are carried. |
| #289 | `pipeline_moe` | `27bad6d3` | included | Pipelined hybrid Qwen35 MoE decode update plus sub-batch hybrid prefill FFN MMQ-bounds fix are carried. |
| #285 | `feat/lucebox-docker` | `ccef4551` | included | Docker stack, `lucebox` CLI, bench/profile tooling, harness clients, `luce-bench`, reproducible uv sync defaults, pinned actions, sanitized tags, shell-wrapper mirroring, docs links, NOTICE copyright, and `areas.__all__` cleanup are carried. |
| #276 | `fix/qwen36-claude-code-tool-calling` | `5e861b4d` | included | Qwen3.6-27B tool-calling fix for Claude-code Anthropic path is carried. |
| #274 | `feat/pflash-drafter-ee7` | `e64a2b80` | included | Adaptive pFlash composition, EE7/drafter updates, docs, tests, and follow-up fixes are carried. |
| #266 | `feat/harness-typed-adapters` | `17525eae` | included | Typed harness adapters and format-aware session-inject proxy are carried. |
| #152 | `main` | `cf735bee` | included | Gemma 4 RTX 4090 backend helpers are carried. |
| #142 | `xabicasa/dflash-safetensors-draft-fp16` | `f2fbf62f` | included | FP16 safetensors drafter support is carried. |

## Validation run

This run performed:

- `date -Is` -> `2026-05-29T10:50:50-04:00` for preflight.
- Primary checkout preflight: `git status --short` was clean; branch was
  `auto-integration`; remotes were `origin=https://github.com/Luce-Org/lucebox-hub`
  and `easel=https://github.com/easel/lucebox-hub`.
- Auth/tooling checks with real user credentials succeeded: `gh auth status`,
  `claude auth status --text`, and Codex version smoke output (`codex-cli 0.130.0`).
- `git fetch --prune origin` and `git fetch --prune easel` completed successfully.
- Open PR enumeration used `gh pr list --repo Luce-Org/lucebox-hub --state open
  --limit 200 --json ... --jq ...` and found 27 open PRs total: 20 non-draft and
  7 draft/excluded.
- Fetched open non-draft PR refs explicitly: #307, #306, #297, #295, #294,
  #289, #285, #276, #274, #266, #237, #221, #154, #153, #152, #142, #137,
  #135, #94, and #48.
- Containment checks before reconciliation confirmed #307, #306, #297, #295,
  #294, #289, #276, #274, #266, #152, and #142 were ancestors of
  `easel/auto-integration`; #285 had advanced to `ccef4551` and was not yet an
  ancestor; #237, #221, #154, #153, #137, #135, #94, and #48 were not ancestors.
- Reconciliation worktree `/tmp/luce-auto-cron-20260529-105050/reconcile` was
  created from `easel/auto-integration`; merging `origin/main` reported `Already
  up to date`.
- Merging `origin/pr/285` conflicted only in `.github/workflows/ci.yml`. The
  resolution kept the integration branch's native server dependency install step
  and PR #285's pinned `astral-sh/setup-uv@caf0cab7a618c569241d31dcd442f54681755d39 # v3`.
  The merge commit is `a0a40dc6` before this manifest update.
- Fresh direct merge probes from the updated integration tip were created for
  #237, #221, #154, #153, #137, #135, #94, and #48. All still conflict in the
  file sets recorded below.
- Verification for the PR #285 update and manifest refresh:
  - `git diff --check easel/auto-integration..HEAD` passed.
  - `python3 -m py_compile harness/src/harness/clients/_common.py harness/src/harness/clients/hermes.py harness/src/harness/clients/openclaw.py harness/src/harness/clients/pi.py luce-bench/src/lucebench/areas/__init__.py` passed.
  - YAML parsing with `python3`/PyYAML passed for `.github/workflows/ci.yml`,
    `.github/workflows/docker.yml`, and `.github/workflows/release-luce-bench.yml`.
  - Conflict-marker search over files changed in this run found no markers.
- No CUDA/server build was run in this cycle; the meaningful code delta was the
  PR #285 docker/harness/CI follow-up plus the manifest.

## Pending / blocked-needs-human / selective-port candidates

| PR | Head branch | Head | Current status | Probe result / next useful action |
|---:|---|---:|---|---|
| #237 | `feat/dflash-mtp-foundation` | `02c6a6c4` | blocked-needs-human / salvage-port | Fresh probe worktree `/tmp/luce-auto-cron-20260529-105050/pr-237-probe` conflicts in old-layout `dflash/` server/backend files plus current `server/CMakeLists.txt`, common MTP files, Qwen35 loader/graph/backend/dflash target files, and tests. Prior usable Claude report `/tmp/luce237b-20260529-092711-claude-report.txt` says this is a genuine, not-yet-duplicated MTP/NextN feature: re-path UA MTP files into `server/`, union-merge MoE/router and MTP fields/signatures, and hand-port relocated backend/server entry edits. Next step is a narrower staged manual port or multi-agent task split by conflict family. |
| #221 | `feat/mtp-prefix-warm-ghost` | `05502974` | blocked-needs-human / dependent salvage-port | Fresh probe worktree `/tmp/luce-auto-cron-20260529-105050/pr-221-probe` conflicts on old `dflash/` scripts/backend files, current common/Qwen35 MTP, metadata, prefix snapshot, graph, and tests, and brings old benchmark/results assets. Mine prefix-cache WARM behavior (`snapshot_head_kv`, `restore_head_kv`, `warm_head_kv_range`, `head_kv_warm_`), partial/range warm recovery, the NextN raw-`block_count` load-filter fix, dual-speculator routing ideas, and focused `test_prefix_cache_mtp.cpp` cases only after a PR-237-equivalent current-layout MTP foundation lands. |
| #154 | `xabicasa/dflash-mtp-speculative-loop` | `2f4ede79` | blocked-needs-human / dependency | Fresh probe worktree `/tmp/luce-auto-cron-20260529-105050/pr-154-probe` conflicts on old `dflash/CMakeLists.txt`, moved MTP docs/tests and `f16_convert.cu`, plus core Qwen35/internal target files. Mine linear MTP decode semantics after current-layout Qwen35 MTP exists. |
| #153 | `xabicasa/dflash-mtp-integrated` | `e9b17cb1` | blocked-needs-human / dependency | Fresh probe worktree `/tmp/luce-auto-cron-20260529-105050/pr-153-probe` conflicts on old CMake, moved MTP docs/tests and `f16_convert.cu`, and the same core Qwen35/internal target files. Mine loader/graph/cache/test ideas after current-layout Qwen35 MTP exists. |
| #135 | `xabicasa/dflash-multi-request-scheduler-batched-target-step` | `561b0ac1` | blocked-needs-human / selective-port | Fresh probe worktree `/tmp/luce-auto-cron-20260529-105050/pr-135-probe` conflicts in `server/src/internal.h`, `server/src/qwen35/qwen35_target_graph.cpp`, and `server/test/test_dflash.cpp`. Prior usable Codex reports confirm useful missing behavior: qwen35 multi-request scheduling with cache slots, `REQ`/`SLOT`/`START`/`CONTINUE`/`CANCEL`/`LIST_REQUESTS`, fair quantum stepping, epoch checks, daemon tagged stream framing, and batched target-step ideas. Port by adding a small multi-slot owner in `Qwen35Backend`, defaulting `target_cache_slots` to 1, adding daemon protocol hooks in `common/daemon_loop` or backend command handling, then porting batched target graph support while preserving current partial-cache/layer-split/MoE/TurboQuant behavior. |
| #137 | `xabicasa/dflash-build-cmake-sm89-bsa` | `297fc74e` | suggested-close/superseded | Fresh probe worktree `/tmp/luce-auto-cron-20260529-105050/pr-137-probe` only conflicts on deleted old `dflash/CMakeLists.txt`. Ask author to close or retarget to current `server/CMakeLists.txt` if anything remains. |
| #94 | `feat/dflash-qwen36-swa-draft` | `d2f9c9dd` | suggested-close/superseded | Fresh probe worktree `/tmp/luce-auto-cron-20260529-105050/pr-94-probe` conflicts in `server/src/draft/draft_graph.cpp`, `draft_safetensors_loader.cpp`, and `server/src/internal.h`; prior tmux-driven Codex report `/tmp/luce94-codex-20260529-090910-report.txt` concluded the useful behavior is already present in current auto-integration: Qwen3.6 DFlash SWA metadata loading, bare-filename `config.json` lookup, and a stronger shared-runtime `causal_mask_swa` path. Ask author/maintainers to close unless they can identify an unported test case. |
| #48 | `fix/consumer-blackwell-auto-detect` | `858b84b6` | suggested-close/superseded | Fresh probe worktree `/tmp/luce-auto-cron-20260529-105050/pr-48-probe` only conflicts on deleted old `dflash/CMakeLists.txt`. Close or retarget to current `server/CMakeLists.txt` if still needed. |

## Draft / excluded

Draft PRs remain outside the primary non-draft integration target except for
dependency awareness: #305, #304, #291, #290, #275, #249, and #193.

## Retained worktrees / logs

The conflicted probe worktrees were intentionally retained for manual follow-up
because safe cleanup would require resolving or discarding conflicted indexes:

- `/tmp/luce-auto-cron-20260529-105050/reconcile`
- `/tmp/luce-auto-cron-20260529-105050/pr-237-probe`
- `/tmp/luce-auto-cron-20260529-105050/pr-221-probe`
- `/tmp/luce-auto-cron-20260529-105050/pr-154-probe`
- `/tmp/luce-auto-cron-20260529-105050/pr-153-probe`
- `/tmp/luce-auto-cron-20260529-105050/pr-137-probe`
- `/tmp/luce-auto-cron-20260529-105050/pr-135-probe`
- `/tmp/luce-auto-cron-20260529-105050/pr-94-probe`
- `/tmp/luce-auto-cron-20260529-105050/pr-48-probe`
- `/tmp/luce-auto-cron-20260529-105050`

Fresh direct-merge probe logs were written under `/tmp/luce-auto-cron-20260529-105050/pr-*-merge.log`, with unmerged-file summaries under `/tmp/luce-auto-cron-20260529-105050/pr-*-unmerged.txt`.
Delegation reports from recent runs that remain useful:

- `/tmp/luce237b-20260529-092711-claude-report.txt` (usable read-only feasibility report)
- `/tmp/luce237resolve-20260529-092711-claude-report.txt` (failed: max turns; unresolved index retained)
- `/tmp/luce-auto-cron-20260529-101411/claude-pr237-report.txt` (failed: max turns)
- `/tmp/luce-auto-cron-20260529-103040/claude-pr237-narrow-report.txt` (failed: blank/zero-byte stuck tmux run)
- `/tmp/luce135-20260529-092711-codex-report.txt` (usable read-only feasibility report)
- `/tmp/luce-auto-cron-20260529-101411/codex-pr135-report.txt` (partial transcript only; stopped before final summary)
- `/tmp/luce-auto-cron-20260529-103040/codex-pr135-narrow-report.txt` (usable read-only salvage plan)
- `/tmp/luce221-084809-claude-report.txt` (failed: max turns)
- `/tmp/luce221-codex-084947-report.txt` (usable read-only feasibility report)
- `/tmp/luce94-codex-20260529-090910-report.txt` (usable read-only superseded/close report)

## Notes

This refresh integrated the newly advanced #285 head and preserved stack semantics
with `origin/main` first, then carried contributor PRs and integration-only fixes.
The next useful integration work remains a staged selective port of #237's MTP
foundation into the current `server/` layout, split by conflict family: first
land the re-pathed MTP files, then union-merge MoE/router and MTP fields/signatures,
then hand-port relocated backend/server entry edits and build-gate. After that,
mine #221's WARM-cache/head-KV/range-warm, NextN load-filter, and dispatcher/routing
behavior plus #153/#154's native/integrated MTP semantics. #135 is a separate
current-layout selective port that should be split into request-slot APIs, qwen35
batched one-token target-step support, scheduler fairness/cancel tests, backend
decode slots, and opt-in scheduler APIs. #137 and #48 look like old
`dflash/CMakeLists.txt` changes that should be closed or retargeted, and #94
appears largely superseded by current draft/SWA support.
