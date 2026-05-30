# Auto-integration manifest

Repository: `Luce-Org/lucebox-hub`
Integration branch: `auto-integration`
Writable remote: `easel`
Upstream remote: `origin` / `Luce-Org`
Last refresh: 2026-05-30T03:30:16-04:00
Current base: `origin/main` `8782d07a`
Current integration tip before this refresh: `easel/auto-integration` `606db587`
Manifest refresh prepared in this run: this commit

This branch is maintained as a reproducible patch stack over `origin/main`. This unattended run started from a clean primary checkout on `auto-integration`, verified GitHub/Claude/Codex auth with the real user credential home, fetched `origin` and `easel` separately, confirmed `origin/main` was already included, then reconciled in `/tmp/luce-auto-cron-20260530-033059/stack`.

New in this refresh: no source PR head needed to be added to the stack. PR #312, which was integrated in the prior run, is now draft and is reclassified as draft/excluded while remaining present in stack history for dependency awareness. Fresh worktree probes were rerun for all eight non-draft PRs that are not ancestors of the stack, and a tmux-driven Codex salvage review was rerun for #237. The result remains: direct merge is blocked for old-layout/dependent MTP and scheduler PRs; #237 is feasible only as a current-layout selective port.

## Included in the current non-draft stack

| PR | Head branch | Head | State | Notes |
|---:|---|---:|---|---|
| #311 | `fix/prefix-cache-recurrent-state` | `c470446a` | included | Prefix-cache/spec-decode fix is carried: full-attention defaults for Qwen3.6 paths, draft feature-mirror resync after snapshot restore, and chunk-aligned prefix snapshots. |
| #310 | `feat-backend-activation-precision-policy-after-306` | `bf9f4b57` | included | Backend activation precision policy / graph tensor precision helpers are carried. |
| #309 | `experiment-dflash-feature-dtype` | `ea6ac481` | included | Feature mirror dtype policy is carried. |
| #307 | `docs/why-this-exists-copy` | `236fc2fd` | included | README “Why this exists” copy remains preserved. |
| #306 | `refactor-server-layer-split-runtime` | `988fc933` | included | Shared layer-split runtime helper extraction remains carried; #310 is stacked after it. |
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
| #285 | `feat/lucebox-docker` | `48fafe63` | included | Latest Docker stack / `lucebox` CLI / bench-profile / harness / `luce-bench` refresh is carried. |
| #276 | `fix/qwen36-claude-code-tool-calling` | `5e861b4d` | included | Qwen3.6-27B tool-calling fix for Claude-code Anthropic path is carried. |
| #274 | `feat/pflash-drafter-ee7` | `8c1f37d` | included | Latest adaptive pFlash composition plus effective-size admission/keep-ratio guard update is carried. |
| #266 | `feat/harness-typed-adapters` | `17525eae` | included | Typed harness adapters and format-aware session-inject proxy are carried. |
| #152 | `main` | `cf735bee` | included | Gemma 4 RTX 4090 backend helpers are carried. |
| #142 | `xabicasa/dflash-safetensors-draft-fp16` | `f2fbf62f` | included | FP16 safetensors drafter support is carried. |

## Validation run

This run performed:

- `date -Is` -> `2026-05-30T03:30:16-04:00` during preflight.
- Primary checkout preflight: `git status --short` was clean; branch was `auto-integration`; remotes were `origin=https://github.com/Luce-Org/lucebox-hub` and `easel=https://github.com/easel/lucebox-hub`.
- Auth/tooling checks with real user credentials succeeded: `gh auth status`, `claude auth status --text`, and harmless `codex --version` smoke check.
- `git fetch --prune origin` and `git fetch --prune easel` completed successfully.
- Open PR enumeration used `gh pr list --repo Luce-Org/lucebox-hub --state open --limit 200 --json ... --jq ...` and found 32 open PRs total: 23 non-draft and 9 draft/excluded.
- Open non-draft PR refs were fetched individually to `refs/remotes/origin/pr/<n>`.
- Containment checks confirmed #311, #310, #309, #307, #306, #297, #295, #294, #289, #285, #276, #274, #266, #152, and #142 are ancestors of the current integration stack; #237, #221, #154, #153, #137, #135, #94, and #48 are not ancestors and remain classified below. PR #312 is also an ancestor but is now draft/excluded.
- `origin/main` remains included in `auto-integration`; merging `origin/main` in the reconciliation worktree reported `Already up to date.`
- Fresh probe worktrees attempted direct merges for the remaining non-integrated non-draft PRs. All eight still conflict in old-layout or dependent MTP/scheduler areas; logs are retained under `/tmp/luce-auto-cron-20260530-033059/probes/pr-*-merge.log`, status snapshots under `/tmp/luce-auto-cron-20260530-033059/probes/pr-*-status.txt`, and conflict-file lists under `/tmp/luce-auto-cron-20260530-033059/probes/pr-*-conflicts.txt`.
- Fresh tmux-driven Codex delegation for #237 (`luce-codex-237-20260530033126`) completed and wrote `/tmp/luce-auto-cron-20260530-033059/probes/codex-pr237-salvage-report.txt`. It recommends keeping #237 blocked for direct merge and salvaging it as a new current-layout integration task, starting with a narrow Qwen35 MTP foundation that is off by default plus focused orchestrator/Qwen35 smoke coverage.
- `git diff --check` passed in the reconciliation worktree.
- Targeted Python validation passed: `uv run --python 3.12 --with pytest pytest lucebox/tests luce-bench/tests -q` -> `362 passed in 25.73s`.
- CMake/CUDA configure was not rerun in this refresh because no source/build files changed; the previous run's local CUDA compiler-identification blocker remains the last C++ environment result (`ptxas fatal : Value 'sm_52' is not defined`).

## Pending / blocked-needs-human / selective-port candidates

| PR | Head branch | Head | Current status | Probe result / next useful action |
|---:|---|---:|---|---|
| #237 | `feat/dflash-mtp-foundation` | `02c6a6c4` | blocked-needs-human / human-scale server-layout port | Fresh direct-merge probe still conflicts across 24 old-layout and current server files, including deleted old `dflash/` server/backend files, current `server/CMakeLists.txt`, backend factory, MTP common files, Qwen35 loader/graph/backend/dflash target/MTP files, and tests. Fresh Codex salvage review says direct merge should stay blocked; viable path is a current-layout selective port: add MTP source/config and no-op interfaces first, then common MTP orchestrator tests, then Qwen35 loader/hidden-capture/backend behavior while preserving current remote draft, Qwen35-MoE, layer-split, PFlash/C2, and Gemma/Laguna paths. |
| #221 | `feat/mtp-prefix-warm-ghost` | `05502974` | blocked-needs-human / dependent salvage-port | Fresh direct-merge probe still conflicts in old `dflash/` scripts/backend plus current MTP/common/prefix-cache/Qwen35 files and tests. Mine prefix-cache WARM behavior only after a current-layout #237-equivalent MTP foundation lands. |
| #154 | `xabicasa/dflash-mtp-speculative-loop` | `2f4ede79` | blocked-needs-human / dependency | Fresh probe conflicts in old `dflash/CMakeLists.txt`, MTP docs, CUDA/internal/Qwen35 graph/loader files, and MTP smoke/contract tests. Mine linear MTP decode semantics after current-layout Qwen35 MTP exists. |
| #153 | `xabicasa/dflash-mtp-integrated` | `e9b17cb1` | blocked-needs-human / dependency | Fresh probe conflicts in old `dflash/CMakeLists.txt`, MTP docs, CUDA/internal/Qwen35 graph/loader files, and MTP smoke/contract tests. Mine loader/graph/cache/test ideas after current-layout Qwen35 MTP exists. |
| #135 | `xabicasa/dflash-multi-request-scheduler-batched-target-step` | `561b0ac1` | blocked-needs-human / selective-port | Fresh probe conflicts in `server/src/internal.h`, `server/src/qwen35/qwen35_target_graph.cpp`, and `server/test/test_dflash.cpp`. Prior and recent reviews found no small safe buildable slice: scheduler symbols are embedded in old monolithic harness code rather than current `common/daemon_loop` / `ModelBackend` / `Qwen35Backend`. |
| #137 | `xabicasa/dflash-build-cmake-sm89-bsa` | `297fc74e` | suggested-close/superseded | Fresh probe only conflicts on deleted old `dflash/CMakeLists.txt`; ask author to close or retarget to current `server/CMakeLists.txt` if anything remains. |
| #94 | `feat/dflash-qwen36-swa-draft` | `d2f9c9dd` | suggested-close/superseded | Fresh probe conflicts in current draft/internal files, but prior tmux-driven Codex report `/tmp/luce94-codex-2026-05-29-090910-report.txt` concluded the useful behavior is already present in current auto-integration. Suggested close or author retarget with a minimal delta if still needed. |
| #48 | `fix/consumer-blackwell-auto-detect` | `858b84b6` | suggested-close/superseded | Fresh probe only conflicts on deleted old `dflash/CMakeLists.txt`; close or retarget to current `server/CMakeLists.txt` if still needed. |

## Draft / excluded

Draft PRs remain outside the primary non-draft integration target except for dependency awareness: #312, #308, #305, #304, #291, #290, #275, #249, and #193. Draft #312's payload-transport work is already carried in stack history from the prior run; draft #308's current reasoning-channel changes are represented through non-draft #285's current head.

## Retained worktrees / logs

This run retained worktrees/logs for audit because probe worktrees contain conflicted indexes and safe cleanup is left to a supervised pass:

- `/tmp/luce-auto-cron-20260530-033059/stack`
- `/tmp/luce-auto-cron-20260530-033059/probes/pr-237-probe`
- `/tmp/luce-auto-cron-20260530-033059/probes/pr-221-probe`
- `/tmp/luce-auto-cron-20260530-033059/probes/pr-154-probe`
- `/tmp/luce-auto-cron-20260530-033059/probes/pr-153-probe`
- `/tmp/luce-auto-cron-20260530-033059/probes/pr-137-probe`
- `/tmp/luce-auto-cron-20260530-033059/probes/pr-135-probe`
- `/tmp/luce-auto-cron-20260530-033059/probes/pr-94-probe`
- `/tmp/luce-auto-cron-20260530-033059/probes/pr-48-probe`
- `/tmp/luce-auto-cron-20260530-033059/probes/pr-*-merge.log`
- `/tmp/luce-auto-cron-20260530-033059/probes/pr-*-status.txt`
- `/tmp/luce-auto-cron-20260530-033059/probes/pr-*-conflicts.txt`
- `/tmp/luce-auto-cron-20260530-033059/probes/codex-pr237-salvage-report.txt`
- `/tmp/luce-auto-cron-20260530-033059/probes/codex-pr237-pane.txt`

Useful prior probe/delegation artifacts remain for unresolved old-layout PRs:

- `/tmp/luce-auto-cron-20260530-012647/probes/codex-pr237-refresh-report.txt` (usable read-only #237 current-layout feasibility report)
- `/tmp/luce-auto-cron-20260529-220930/probes/codex-pr237-slice-report.txt` (usable read-only #237 current-layout slice report)
- `/tmp/luce-auto-cron-20260529-214904/probes/codex-pr237-current-report.txt` (usable read-only #237 current-layout feasibility report)
- `/tmp/luce-auto-cron-20260529-181411/codex-pr221-report.txt` (usable read-only #221 salvage report)
- `/tmp/luce-auto-cron-20260529-145519/codex-pr135-report.txt` (usable read-only #135 salvage note)
- `/tmp/luce-auto-cron-20260529-103040/codex-pr135-narrow-report.txt` (usable read-only #135 salvage plan)
- `/tmp/luce94-codex-2026-05-29-090910-report.txt` (usable read-only #94 superseded/close report)

## Notes

The next useful integration work is still concrete but manual: start a dedicated current-`server/` #237 port, not a direct merge. Add the interface/no-op surface first, then Qwen35 capture/rollback and common MTP tests, then follow with #221/#153/#154 MTP behavior after the foundation exists. Keep #135 as a separate scheduler/batched-target selective port that starts in `common/daemon_loop` / `ModelBackend` / `Qwen35Backend` APIs before any batched target graph changes. #137 and #48 look like old `dflash/CMakeLists.txt` changes that should be closed or retargeted, and #94 appears largely superseded by current draft/SWA support.
