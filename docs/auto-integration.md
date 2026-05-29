# Auto-integration manifest

Repository: `Luce-Org/lucebox-hub`
Integration branch: `auto-integration`
Writable remote: `easel`
Upstream remote: `origin` / `Luce-Org`
Last refresh: 2026-05-29T12:28:40-04:00
Current base: `origin/main` `8782d07a`
Previous integration tip: `easel/auto-integration` `2400aaf0`
Prepared integration tip before manifest commit: `d6ccd987`

This branch is maintained as a reproducible patch stack over `origin/main`.
This unattended run started from a clean primary checkout, verified GitHub / Claude / Codex auth using the real user home, fetched `origin` and `easel` separately, and reconciled in `/tmp/luce-auto-cron-20260529-122142/reconcile`.

## Included in the current stack

| PR | Head branch | Head | State | Notes |
|---:|---|---:|---|---|
| #309 | `experiment-dflash-feature-dtype` | `ad5ac25c` | included this run | Merged cleanly. Adds configurable DFlash feature-mirror storage dtype. A tmux-driven Claude review flagged a default-F32 host-round-trip regression; this stack adds integration fix `d6ccd987` to preserve the previous CUDA BF16→F32 path for default F32 mirrors. |
| #307 | `docs/why-this-exists-copy` | `236fc2fd` | included | README “Why this exists” copy remains preserved. |
| #306 | `refactor-server-layer-split-runtime` | `988fc933` | included | Shared layer-split runtime helper extraction remains carried. |
| #303 | `fix/harness-portable-run-dirs` | upstream `05b008a0` | included through upstream and stack | Harness portable run/cache directories and automatic client-install fallback are in `origin/main`; stack compatibility docs/helpers remain carried. |
| #302 | `fix/harness-model-paths` | upstream | included through upstream | Harness launcher model-path override behavior and documentation are in `origin/main`. |
| #301 | `fix/ddtree-test-harness` | upstream | included through upstream | DDTree test harness fixes are in `origin/main`. |
| #300 | `fix/sigterm-gpu-unload` | upstream | included through upstream | SIGTERM GPU-unload fix remains in upstream. |
| #299 | `feat/draft-swa-flag` | upstream | included through upstream | Draft SWA env/flag support remains in upstream. |
| #298 | `fix/gemma4-destructor-link` | upstream | included through upstream | Gemma4 destructor-link fix remains in upstream. |
| #292 | `feat-backend-ipc-payload-pipe-open` | upstream / `90bc52f` | included through upstream and stack | Backend IPC payload-pipe support is upstream and still represented in carried stack history. |
| #297 | `feat-server-laguna-layer-split-adapter-v2` | `53dd1686` | included | Laguna target-layer-split adapter remains carried. |
| #295 | `fix-layer-split-sampling` | `a9aedf7d` | included | Target layer-split sampling support remains an ancestor of the stack. |
| #294 | `feat/server-passthrough-proxy` | `48f6962d` | included | Server passthrough proxy wiring, piecewise keep-ratio curve, query survival checks, multimodal last-user text extraction, curl cleanup, and unit coverage are carried. |
| #289 | `pipeline_moe` | `27bad6d3` | included | Pipelined hybrid Qwen35 MoE decode update plus sub-batch hybrid prefill FFN MMQ-bounds fix are carried. |
| #285 | `feat/lucebox-docker` | `37b3fbd5` | included | Docker stack / `lucebox` CLI / bench-profile / harness / `luce-bench` refresh is carried. |
| #276 | `fix/qwen36-claude-code-tool-calling` | `5e861b4d` | included | Qwen3.6-27B tool-calling fix for Claude-code Anthropic path is carried. |
| #274 | `feat/pflash-drafter-ee7` | `8c1f37db` | included | Adaptive pFlash composition plus effective-size admission/keep-ratio guard update is carried. |
| #266 | `feat/harness-typed-adapters` | `17525eae` | included | Typed harness adapters and format-aware session-inject proxy are carried. |
| #152 | `main` | `cf735bee` | included | Gemma 4 RTX 4090 backend helpers are carried. |
| #142 | `xabicasa/dflash-safetensors-draft-fp16` | `f2fbf62f` | included | FP16 safetensors drafter support is carried. |

## Attempted this run / pending blockers

Fresh direct-merge probes were run from the updated integration tip after #309. These PRs still require human-guided selective ports rather than direct merges:

| PR | Head branch | Head | Current status | Fresh probe result / next action |
|---:|---|---:|---|---|
| #237 | `feat/dflash-mtp-foundation` | `02c6a6c4` | blocked-needs-human / salvage-port | Probe worktree `/tmp/luce-auto-cron-20260529-122142/pr-237-probe` conflicts in old-layout `dflash/` files plus current `server/CMakeLists.txt`, common MTP files, Qwen35 loader/graph/backend/dflash target files, and tests. Prior usable Claude report `/tmp/luce237b-20260529-092711-claude-report.txt` says this is a genuine MTP/NextN feature. |
| #221 | `feat/mtp-prefix-warm-ghost` | `05502974` | blocked-needs-human / dependent salvage-port | Probe worktree `/tmp/luce-auto-cron-20260529-122142/pr-221-probe` conflicts on old `dflash/` scripts/backend files, current common/Qwen35 MTP, metadata, prefix snapshot, graph, and tests. Mine prefix-cache WARM behavior after a current-layout #237-equivalent lands. |
| #154 | `xabicasa/dflash-mtp-speculative-loop` | `2f4ede79` | blocked-needs-human / dependency | Probe worktree `/tmp/luce-auto-cron-20260529-122142/pr-154-probe` conflicts on old `dflash/CMakeLists.txt`, moved MTP docs/tests and `f16_convert.cu`, plus core Qwen35/internal target files. |
| #153 | `xabicasa/dflash-mtp-integrated` | `e9b17cb1` | blocked-needs-human / dependency | Probe worktree `/tmp/luce-auto-cron-20260529-122142/pr-153-probe` conflicts on old CMake, moved MTP docs/tests and `f16_convert.cu`, and core Qwen35/internal target files. |
| #135 | `xabicasa/dflash-multi-request-scheduler-batched-target-step` | `561b0ac1` | blocked-needs-human / selective-port | Probe worktree `/tmp/luce-auto-cron-20260529-122142/pr-135-probe` conflicts in `server/src/internal.h`, `server/src/qwen35/qwen35_target_graph.cpp`, and `server/test/test_dflash.cpp`. Prior Codex reports identify useful missing scheduler/cache-slot/batched-target-step behavior. |
| #137 | `xabicasa/dflash-build-cmake-sm89-bsa` | `297fc74e` | suggested-close/superseded | Probe worktree `/tmp/luce-auto-cron-20260529-122142/pr-137-probe` only conflicts on deleted old `dflash/CMakeLists.txt`; close or retarget to current `server/CMakeLists.txt` if anything remains. |
| #94 | `feat/dflash-qwen36-swa-draft` | `d2f9c9dd` | suggested-close/superseded | Probe worktree `/tmp/luce-auto-cron-20260529-122142/pr-94-probe` conflicts in draft graph/loader/internal files; prior Codex report `/tmp/luce94-codex-20260529-090910-report.txt` concluded useful behavior is already present. |
| #48 | `fix/consumer-blackwell-auto-detect` | `858b84b6` | suggested-close/superseded | Probe worktree `/tmp/luce-auto-cron-20260529-122142/pr-48-probe` only conflicts on deleted old `dflash/CMakeLists.txt`; close or retarget to current `server/CMakeLists.txt` if still needed. |

## Draft / excluded

Draft PRs remain outside the primary non-draft integration target except for dependency awareness: #308, #305, #304, #291, #290, #275, #249, and #193.

## Validation run

This run performed:

- `date -Is` -> `2026-05-29T12:21:42-04:00` for preflight.
- Primary checkout preflight: `git status --short` was clean; branch was `auto-integration`; remotes were `origin=https://github.com/Luce-Org/lucebox-hub` and `easel=https://github.com/easel/lucebox-hub`.
- Auth/tooling checks with real user credentials succeeded: `gh auth status`, `claude auth status --text`, and `codex --version`.
- `git fetch --prune origin` and `git fetch --prune easel` completed successfully.
- Open PR enumeration found 29 open PRs total: 21 non-draft and 8 draft/excluded.
- Fetched open non-draft PR refs explicitly: #309, #307, #306, #297, #295, #294, #289, #285, #276, #274, #266, #237, #221, #154, #153, #152, #142, #137, #135, #94, and #48.
- Containment checks confirmed only new #309 was a mergeable non-draft PR not already included among the direct-mergeable/current stack heads; #237, #221, #154, #153, #137, #135, #94, and #48 remained outside the stack for the reasons above.
- Reconciliation worktree `/tmp/luce-auto-cron-20260529-122142/reconcile` was created from `easel/auto-integration`; merging `origin/main` reported `Already up to date`; merging #309 succeeded with `ort`.
- Fresh direct merge probes from the updated integration tip were run for #237, #221, #154, #153, #137, #135, #94, and #48. All still conflict in the file sets recorded above.
- Tmux-driven Claude review of #309:
  - first run `/tmp/luce-auto-cron-20260529-122142/claude-pr309-review.txt` hit max turns without a report;
  - second run `/tmp/luce-auto-cron-20260529-122142/claude-pr309-review2.txt` produced a usable review and found one high-severity default-F32 performance regression. That regression was fixed in integration commit `d6ccd987`.
- Verification:
  - `git diff --check 2400aaf0..HEAD` passed before the manifest update.
  - `cmake -S server -B /tmp/luce-auto-cron-20260529-122142/server-build -DCMAKE_CUDA_ARCHITECTURES=89 -DDFLASH27B_FA_ALL_QUANTS=OFF -DDFLASH27B_BUILD_TESTS=ON` failed during CMake CUDA compiler identification because local `/usr/bin/nvcc` still invokes `ptxas -arch=sm_52`, which this environment rejects (`ptxas fatal: Value 'sm_52' is not defined for option 'gpu-name'`). This is the known local toolchain blocker before project compilation, not a project compile result.

## Retained worktrees / logs

The reconciliation worktree and conflicted probe worktrees were intentionally retained for audit/follow-up; safe cleanup would require resolving or discarding conflicted indexes in the probe worktrees:

- `/tmp/luce-auto-cron-20260529-122142/reconcile`
- `/tmp/luce-auto-cron-20260529-122142/pr-237-probe`
- `/tmp/luce-auto-cron-20260529-122142/pr-221-probe`
- `/tmp/luce-auto-cron-20260529-122142/pr-154-probe`
- `/tmp/luce-auto-cron-20260529-122142/pr-153-probe`
- `/tmp/luce-auto-cron-20260529-122142/pr-137-probe`
- `/tmp/luce-auto-cron-20260529-122142/pr-135-probe`
- `/tmp/luce-auto-cron-20260529-122142/pr-94-probe`
- `/tmp/luce-auto-cron-20260529-122142/pr-48-probe`

Fresh direct-merge probe logs were written under `/tmp/luce-auto-cron-20260529-122142/pr-*-merge.log`, with unmerged-file summaries under `/tmp/luce-auto-cron-20260529-122142/pr-*-unmerged.txt`.

## Notes

This run integrated the new non-draft contributor PR #309 and added one stack-local compatibility/performance fix for the default F32 feature mirror path. The next useful integration work remains a staged selective port of #237's MTP foundation into the current `server/` layout, then #221/#153/#154 MTP follow-ups, with #135 as a separate scheduler/batched-target selective port. #137 and #48 look like old `dflash/CMakeLists.txt` changes that should be closed or retargeted, and #94 appears largely superseded by current draft/SWA support.
