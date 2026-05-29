# Auto-integration manifest

Repository: `Luce-Org/lucebox-hub`
Integration branch: `auto-integration`
Writable remote: `easel`
Upstream remote: `origin` / `Luce-Org`
Last refresh: 2026-05-29T13:47:52-04:00
Current base: `origin/main` `8782d07a`
Current integration tip before this refresh: `easel/auto-integration` `434389f4`
Manifest refresh commit prepared in this run: this commit, if non-empty

This branch is maintained as a reproducible patch stack over `origin/main`.
At this run's start the primary checkout was clean; GitHub, Claude Code, and
Codex auth/tooling checks passed using the real user credential home; and
`origin` and `easel` were fetched separately. The primary local checkout is
currently ahead/behind `easel/auto-integration`, so this run used a detached
worktree based on the fetched writable remote tip and treated the remote branch
as source of truth.

This refresh found no newly opened or advanced non-draft contributor PR heads
that were missing from the fetched `easel/auto-integration` tip. #309 and #310
are both already ancestors of the current integration branch. The branch still
contains the prior #310 manual conflict resolution in
`server/src/qwen35moe/qwen35moe_backend.cpp`, preserving the existing persistent
logits graph from the pipelined MoE decode path while adding #310's
backend-precision graph helpers for RMS norm/input/output-norm tensors. The
remaining non-integrated old PRs were re-probed from the updated tip and still
require selective ports or closure rather than direct merges.

## Included in the current stack

| PR | Head branch | Head | State | Notes |
|---:|---|---:|---|---|
| #310 | `feat-backend-activation-precision-policy-after-306` | `e73c2e3f` | included | Adds backend activation precision policy / graph tensor precision helpers to reduce layer-split activation memory. Conflict with the existing persistent Qwen35 MoE logits graph was previously resolved by combining both behaviors. |
| #309 | `experiment-dflash-feature-dtype` | `ea6ac481` | included before this run | Feature mirror dtype policy is already an ancestor of `easel/auto-integration`. |
| #307 | `docs/why-this-exists-copy` | `236fc2fd` | included | README “Why this exists” copy remains preserved; the #285 README conflict was resolved in favor of this focused docs PR. |
| #306 | `refactor-server-layer-split-runtime` | `988fc933` | included | Shared layer-split runtime helper extraction remains carried; #310 is stacked after it. |
| #303 | `fix/harness-portable-run-dirs` | upstream `05b008a0` | included through upstream and stack | Harness portable run/cache directories and automatic client-install fallback are in `origin/main`; stack compatibility docs/helpers remain carried. |
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
| #285 | `feat/lucebox-docker` | `37b3fbd5` | included | Latest Docker stack / `lucebox` CLI / bench-profile / harness / `luce-bench` refresh is carried. |
| #276 | `fix/qwen36-claude-code-tool-calling` | `5e861b4d` | included | Qwen3.6-27B tool-calling fix for Claude-code Anthropic path is carried. |
| #274 | `feat/pflash-drafter-ee7` | `8c1f37db` | included | Latest adaptive pFlash composition plus effective-size admission/keep-ratio guard update is carried. |
| #266 | `feat/harness-typed-adapters` | `17525eae` | included | Typed harness adapters and format-aware session-inject proxy are carried. |
| #152 | `main` | `cf735bee` | included | Gemma 4 RTX 4090 backend helpers are carried. |
| #142 | `xabicasa/dflash-safetensors-draft-fp16` | `f2fbf62f` | included | FP16 safetensors drafter support is carried. |

## Validation run

This run performed:

- `date -Is` -> `2026-05-29T13:46:59-04:00` for preflight and
  `2026-05-29T13:47:52-04:00` for the manifest refresh.
- Primary checkout preflight: `git status --short` was clean; branch was
  `auto-integration`; remotes were `origin=https://github.com/Luce-Org/lucebox-hub`
  and `easel=https://github.com/easel/lucebox-hub`.
- Auth/tooling checks with real user credentials succeeded: `gh auth status`,
  `claude auth status --text`, and `codex --version`.
- `git fetch --prune origin` and `git fetch --prune easel` completed successfully.
- Open PR enumeration used `gh pr list --repo Luce-Org/lucebox-hub --state open
  --limit 200 --json ... --jq ...` and found 30 open PRs total: 22 non-draft and
  8 draft/excluded.
- Fetched open non-draft PR refs explicitly: #310, #309, #307, #306, #297, #295,
  #294, #289, #285, #276, #274, #266, #237, #221, #154, #153, #152, #142, #137,
  #135, #94, and #48.
- Containment checks before reconciliation confirmed #310, #309, #307, #306,
  #297, #295, #294, #289, #285, #276, #274, #266, #152, and #142 were ancestors
  of `easel/auto-integration`; #237, #221, #154, #153, #137, #135, #94, and
  #48 were not ancestors.
- Reconciliation worktree `/tmp/luce-auto-cron-20260529-134752/reconcile` was
  created from `easel/auto-integration`; merging `origin/main` reported
  `Already up to date`.
- No open non-draft PR head had advanced beyond the fetched integration tip, so
  no code merge or conflict resolution was required in the reconciliation
  worktree.
- Fresh direct merge probes from the updated integration tip were created for
  #237, #221, #154, #153, #137, #135, #94, and #48. All still conflict in the
  file sets recorded below.
- Verification for the manifest-only refresh:
  - `git diff --check easel/auto-integration..HEAD` passed for this run's new
    range after the manifest update.
  - `git diff --check origin/main..HEAD` still reports pre-existing stack
    whitespace warnings in `luce-bench/src/lucebench/fixtures/forge_eval/scenarios/_model_quality.py`,
    `luce-bench/src/lucebench/fixtures/forge_eval/scenarios/_stateful_model_quality.py`,
    and `scripts/docker_build_env.sh`.
  - `python3 -m py_compile` via an inline Python driver passed for the harness
    client modules and `luce-bench/src/lucebench/areas/__init__.py`.
  - `cmake -S server -B /tmp/luce-auto-cron-20260529-134752/server-build -DCMAKE_BUILD_TYPE=Release -DCMAKE_CUDA_ARCHITECTURES=89 -DDFLASH27B_TESTS=ON`
    failed during CUDA compiler identification before project compilation with
    the known local toolkit/CMake blocker: `ptxas fatal : Value 'sm_52' is not
    defined for option 'gpu-name'`. Consequently `test_server_unit` could not be
    built or run locally in this WSL environment.

## Pending / blocked-needs-human / selective-port candidates

| PR | Head branch | Head | Current status | Probe result / next useful action |
|---:|---|---:|---|---|
| #237 | `feat/dflash-mtp-foundation` | `02c6a6c4` | blocked-needs-human / salvage-port | Fresh probe worktree `/tmp/luce-auto-cron-20260529-134752/pr-237-probe` conflicts in old-layout `dflash/` server/backend files plus current `server/CMakeLists.txt`, common MTP files, Qwen35 loader/graph/backend/dflash target files, and tests. Prior usable Claude report `/tmp/luce237b-20260529-092711-claude-report.txt` says this is a genuine, not-yet-duplicated MTP/NextN feature. Next step remains a staged manual/multi-agent port by conflict family. |
| #221 | `feat/mtp-prefix-warm-ghost` | `05502974` | blocked-needs-human / dependent salvage-port | Fresh probe worktree `/tmp/luce-auto-cron-20260529-134752/pr-221-probe` conflicts on old `dflash/` scripts/backend files, current common/Qwen35 MTP, metadata, prefix snapshot, graph, and tests, and brings old benchmark/results assets. Mine prefix-cache WARM behavior after a current-layout #237-equivalent MTP foundation lands. |
| #154 | `xabicasa/dflash-mtp-speculative-loop` | `2f4ede79` | blocked-needs-human / dependency | Fresh probe worktree `/tmp/luce-auto-cron-20260529-134752/pr-154-probe` conflicts on old `dflash/CMakeLists.txt`, moved MTP docs/tests and `f16_convert.cu`, plus core Qwen35/internal target files. Mine linear MTP decode semantics after current-layout Qwen35 MTP exists. |
| #153 | `xabicasa/dflash-mtp-integrated` | `e9b17cb1` | blocked-needs-human / dependency | Fresh probe worktree `/tmp/luce-auto-cron-20260529-134752/pr-153-probe` conflicts on old CMake, moved MTP docs/tests and `f16_convert.cu`, and the same core Qwen35/internal target files. Mine loader/graph/cache/test ideas after current-layout Qwen35 MTP exists. |
| #135 | `xabicasa/dflash-multi-request-scheduler-batched-target-step` | `561b0ac1` | blocked-needs-human / selective-port | Fresh probe worktree `/tmp/luce-auto-cron-20260529-134752/pr-135-probe` conflicts in `server/src/internal.h`, `server/src/qwen35/qwen35_target_graph.cpp`, and `server/test/test_dflash.cpp`. Prior usable Codex reports confirm useful missing behavior: qwen35 multi-request scheduling with cache slots, daemon protocol hooks, fair quantum stepping, epoch checks, and batched target-step ideas. |
| #137 | `xabicasa/dflash-build-cmake-sm89-bsa` | `297fc74e` | suggested-close/superseded | Fresh probe worktree `/tmp/luce-auto-cron-20260529-134752/pr-137-probe` only conflicts on deleted old `dflash/CMakeLists.txt`. Ask author to close or retarget to current `server/CMakeLists.txt` if anything remains. |
| #94 | `feat/dflash-qwen36-swa-draft` | `d2f9c9dd` | suggested-close/superseded | Fresh probe worktree `/tmp/luce-auto-cron-20260529-134752/pr-94-probe` conflicts in `server/src/draft/draft_graph.cpp`, `draft_safetensors_loader.cpp`, and `server/src/internal.h`; prior tmux-driven Codex report `/tmp/luce94-codex-20260529-090910-report.txt` concluded the useful behavior is already present in current auto-integration. |
| #48 | `fix/consumer-blackwell-auto-detect` | `858b84b6` | suggested-close/superseded | Fresh probe worktree `/tmp/luce-auto-cron-20260529-134752/pr-48-probe` only conflicts on deleted old `dflash/CMakeLists.txt`. Close or retarget to current `server/CMakeLists.txt` if still needed. |

## Draft / excluded

Draft PRs remain outside the primary non-draft integration target except for
dependency awareness: #308, #305, #304, #291, #290, #275, #249, and #193.

## Retained worktrees / logs

The reconciliation worktree and conflicted probe worktrees were intentionally
retained for audit/follow-up; safe cleanup would require resolving or discarding
conflicted indexes in the probe worktrees:

- `/tmp/luce-auto-cron-20260529-134752/reconcile`
- `/tmp/luce-auto-cron-20260529-134752/pr-237-probe`
- `/tmp/luce-auto-cron-20260529-134752/pr-221-probe`
- `/tmp/luce-auto-cron-20260529-134752/pr-154-probe`
- `/tmp/luce-auto-cron-20260529-134752/pr-153-probe`
- `/tmp/luce-auto-cron-20260529-134752/pr-137-probe`
- `/tmp/luce-auto-cron-20260529-134752/pr-135-probe`
- `/tmp/luce-auto-cron-20260529-134752/pr-94-probe`
- `/tmp/luce-auto-cron-20260529-134752/pr-48-probe`
- `/tmp/luce-auto-cron-20260529-134752`

Fresh direct-merge probe logs were written under `/tmp/luce-auto-cron-20260529-134752/pr-*-merge.log`, with unmerged-file summaries under `/tmp/luce-auto-cron-20260529-134752/pr-*-unmerged.txt`.
Useful prior delegation reports remain:

- `/tmp/luce237b-20260529-092711-claude-report.txt` (usable read-only feasibility report)
- `/tmp/luce237resolve-20260529-092711-claude-report.txt` (failed: max turns; unresolved index retained)
- `/tmp/luce-auto-cron-20260529-101411/claude-pr237-report.txt` (failed: max turns)
- `/tmp/luce-auto-cron-20260529-103040/claude-pr237-narrow-report.txt` (failed: blank/zero-byte stuck tmux run)
- `/tmp/luce-auto-cron-20260529-120701/claude-pr237-report.txt` (failed: max turns)
- `/tmp/luce135-20260529-092711-codex-report.txt` (usable read-only feasibility report)
- `/tmp/luce-auto-cron-20260529-101411/codex-pr135-report.txt` (partial transcript only; stopped before final summary)
- `/tmp/luce-auto-cron-20260529-103040/codex-pr135-narrow-report.txt` (usable read-only salvage plan)
- `/tmp/luce221-084809-claude-report.txt` (failed: max turns)
- `/tmp/luce221-codex-084947-report.txt` (usable read-only feasibility report)
- `/tmp/luce94-codex-20260529-090910-report.txt` (usable read-only superseded/close report)

## Notes

This refresh integrated #310 and re-confirmed the remaining direct-merge
conflicts. The next useful integration work remains a staged selective port of
#237's MTP foundation into the current `server/` layout, then #221/#153/#154
MTP follow-ups, with #135 as a separate scheduler/batched-target selective port.
#137 and #48 look like old `dflash/CMakeLists.txt` changes that should be closed
or retargeted, and #94 appears largely superseded by current draft/SWA support.
