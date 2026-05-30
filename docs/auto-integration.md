# Auto-integration manifest

Repository: `Luce-Org/lucebox-hub`
Integration branch: `auto-integration`
Writable remote: `easel`
Upstream remote: `origin` / `Luce-Org`
Last refresh: `2026-05-30T16:29:56-04:00`
Current base: `origin/main` `c95dfcab`
Previous integration tip: `easel/auto-integration` `1344772e`
Current integration tip before push: `1344772e`

This branch is maintained as a reproducible patch stack over `origin/main`. This unattended run started from a clean primary checkout on `auto-integration`, verified GitHub/Claude/Codex auth with the real user credential home, fetched `origin` and `easel` separately, fetched current PR heads, and rechecked exact PR-head containment against the current stack.

No new contributor PR head was integrated in this refresh: all currently integrated non-draft PR heads were already ancestors of `easel/auto-integration`, and `origin/main` was already an ancestor of the stack. The run still recreated probe worktrees for all non-integrated non-draft PRs and refreshed the blocked/superseded evidence below.

## Included in the current non-draft stack

| PR | Head branch | Head | State | Notes |
|---:|---|---:|---|---|
| #314 | `fix/specdecode-empty-ar-fallback` | `38f92c48` | included | Qwen35 falls back to AR decode when spec-decode succeeds but produces an empty token vector. |
| #310 | `feat-backend-activation-precision-policy-after-306` | `bf9f4b57` | included | Backend activation precision policy / graph tensor precision helpers are carried exactly. |
| #309 | `experiment-dflash-feature-dtype` | `ea6ac481` | included | Feature mirror dtype policy is carried exactly. |
| #308 | `fix/qwen-think-channel` | `9d4defe1` | included | Qwen3.6/Laguna think-mode reasoning is routed to `reasoning_content`; stack carries the replay HTTP stub harness and regression scenarios exactly. |
| #306 | `refactor-server-layer-split-runtime` | `988fc933` | included | Shared layer-split runtime helper extraction is carried exactly. |
| #297 | `feat-server-laguna-layer-split-adapter-v2` | `53dd1686` | included | Laguna target-layer-split adapter is carried exactly. |
| #295 | `fix-layer-split-sampling` | `a9aedf7d` | included | Target layer-split sampling support is carried exactly. |
| #294 | `feat/server-passthrough-proxy` | `48f6962d` | included | Passthrough proxy, keep-ratio curve, query survival checks, multimodal text extraction, and unit coverage are carried exactly. |
| #289 | `pipeline_moe` | `caf2b112` | included | Carries pipelined hybrid Qwen35 MoE decode plus the sub-batch hybrid prefill FFN safety fix. |
| #285 | `feat/lucebox-docker` | `6ea9694a` | included | Docker stack / `lucebox` CLI / harness / `luce-bench`, Bragi sweep docs, autotune/sweep updates, shell harness tests, long-context grader coverage, and the latest Bragi GPU-power-throttle experiment notes are carried exactly. |
| #276 | `fix/qwen36-claude-code-tool-calling` | `5e861b4d` | included | Qwen3.6-27B tool-calling fix for Claude-code Anthropic path is carried exactly. |
| #274 | `feat/pflash-drafter-ee7` | `8c1f37db` | included | Adaptive pFlash composition and effective-size admission/keep-ratio guard update are carried exactly. |
| #266 | `feat/harness-typed-adapters` | `17525eae` | included | Typed harness adapters and format-aware session-inject proxy are carried exactly. |
| #152 | `main` | `cf735bee` | included | Gemma 4 RTX 4090 backend helpers are carried exactly. |
| #142 | `xabicasa/dflash-safetensors-draft-fp16` | `f2fbf62f` | included | FP16 safetensors drafter support is carried exactly. |

Closed or upstreamed PRs still represented by the stack/base include #313 (closed, carried in stack history), #311, #307, #303, #302, #301, #300, #299, #298, and #292.

## Validation run

This run performed:

- `date -Is` -> `2026-05-30T16:24:25-04:00` during preflight and `2026-05-30T16:29:56-04:00` for the manifest refresh.
- Primary checkout preflight: `git status --short` was clean on `auto-integration`; remotes were `origin=https://github.com/Luce-Org/lucebox-hub` and `easel=https://github.com/easel/lucebox-hub`.
- Auth/tooling checks with real user credentials succeeded: `gh auth status`, `claude auth status --text`, and `codex --version`.
- `git fetch --prune origin` and `git fetch --prune easel` completed successfully.
- Current open PR enumeration reported 24 non-draft PRs and 7 draft/excluded PRs.
- Explicit fetch of each open non-draft PR head succeeded. Exact-head containment showed #314, #310, #309, #308, #306, #297, #295, #294, #289, #285, #276, #274, #266, #152, and #142 were ancestors of the stack; #305, #237, #221, #154, #153, #137, #135, #94, and #48 remained non-ancestors.
- A reconcile worktree from `easel/auto-integration` was created at `/tmp/luce-auto-cron-20260530-162504`; `origin/main` was already an ancestor of the stack and `git merge --no-edit origin/main` reported `Already up to date.`
- Probe worktrees were created from the current stack and direct-merge attempts were rerun for all still-non-integrated PRs; conflict file lists are recorded under `/tmp/luce-auto-cron-20260530-162504-logs/`.
- Claude Code was run through tmux for fresh delegated assessments of #305 and #237. The first #305 attempt reached `max_turns`; the narrower rerun produced `/tmp/luce-auto-cron-20260530-162504-logs/claude-305b-report.txt`, and #237 produced `/tmp/luce-auto-cron-20260530-162504-logs/claude-237-report.txt`.
- Verification for this docs-only refresh: `git diff --check HEAD -- docs/auto-integration.md` and `git diff --check HEAD^..HEAD` passed after the manifest commit. No product build was run because the stack did not gain product-code changes in this run; previous local CUDA/CMake checks were blocked by unsupported `sm_52` compiler detection and missing populated `server/deps/llama.cpp` submodule headers in the worktree.

## Pending / blocked-needs-human / selective-port candidates

| PR | Head branch | Head | Current status | Probe result / next useful action |
|---:|---|---:|---|---|
| #305 | `layersplit_refactor` | `1de45e4d` | blocked-needs-human / human-scale refactor | Fresh direct merge still conflicts across 29 files: README/spec/harness docs, server CMake/scripts, backend IPC, backend precision, layer-split backend/adapters, Gemma4/Laguna/Qwen35/Qwen35MoE internals, and server tests. Fresh Claude tmux assessment concluded the PR collides with the already-carried MoE hybrid extraction and newer precision/payload/props infrastructure; no clean small port is safe unattended. The valuable gallocr/sub-batching perf delta should be manually re-ported onto the current canonical MoE common layer. |
| #237 | `feat/dflash-mtp-foundation` | `02c6a6c4` | blocked-needs-human / human-scale server-layout port | Fresh probe still conflicts across 24 old `dflash/` and current `server/` files including CMake, backend factory, common MTP interfaces, Qwen35 graph/loader/backend, and tests. Fresh Claude tmux assessment confirmed a staged selective port is required: discard old-layout `dflash/` paths, land additive MTP files under current `server/`, then hand-resolve build/backend/GGUF/graph/Qwen35 seams and verify `test_dflash` plus `test_common_mtp_orchestrator`; not safe for unattended merge/cherry-pick. |
| #221 | `feat/mtp-prefix-warm-ghost` | `05502974` | blocked-needs-human / dependent salvage-port | Fresh direct-merge probe still conflicts across 23 old `dflash/` scripts/backend plus current MTP/common/prefix-cache/Qwen35 files and tests. Mine prefix-cache WARM behavior only after a current-layout #237-equivalent MTP foundation lands. |
| #154 | `xabicasa/dflash-mtp-speculative-loop` | `2f4ede79` | blocked-needs-human / dependency | Fresh probe conflicts in 12 old/current MTP docs, `dflash/CMakeLists.txt`, CUDA/internal/Qwen35 graph/loader files, and MTP smoke/contract tests. Mine linear MTP decode semantics after current-layout Qwen35 MTP exists. |
| #153 | `xabicasa/dflash-mtp-integrated` | `e9b17cb1` | blocked-needs-human / dependency | Fresh probe conflicts in 10 old/current MTP docs, `dflash/CMakeLists.txt`, CUDA/internal/Qwen35 graph/loader files, and MTP smoke/contract tests. Mine loader/graph/cache/test ideas after current-layout Qwen35 MTP exists. |
| #135 | `xabicasa/dflash-multi-request-scheduler-batched-target-step` | `561b0ac1` | blocked-needs-human / selective-port | Fresh direct probe conflicts in `server/src/internal.h`, `server/src/qwen35/qwen35_target_graph.cpp`, and `server/test/test_dflash.cpp`. Preserve current `ModelBackend::generate`, `DaemonIO::emit`, snapshot slots, current single-request `TargetCache`, and `build_target_step()` ABI; selectively port scheduler state and qwen35-only batched target helpers if still desired. |
| #137 | `xabicasa/dflash-build-cmake-sm89-bsa` | `297fc74e` | suggested-close/superseded | Fresh probe still only conflicts on deleted old `dflash/CMakeLists.txt`; ask author to close or retarget to current `server/CMakeLists.txt` if anything remains. |
| #94 | `feat/dflash-qwen36-swa-draft` | `d2f9c9dd` | suggested-close/superseded | Fresh probe conflicts in current `server/src/draft/draft_graph.cpp`, `server/src/draft/draft_safetensors_loader.cpp`, and `server/src/internal.h`. Useful SWA/draft behavior is already present in current auto-integration; suggested close or author retarget with a minimal delta if still needed. |
| #48 | `fix/consumer-blackwell-auto-detect` | `858b84b6` | suggested-close/superseded | Fresh probe still only conflicts on deleted old `dflash/CMakeLists.txt`; close or retarget to current `server/CMakeLists.txt` if still needed. |

## Draft / excluded

Draft PRs remain outside the primary non-draft integration target except for dependency awareness: #312, #304, #291, #290, #275, #249, and #193. Draft #312's backend IPC payload transport is related to already-carried IPC payload work, but remains draft/excluded. Draft #304 may touch compaction behavior and should be watched if it becomes ready.

## Retained worktrees / logs

This run retained worktrees/logs for audit because probe worktrees contain conflicted indexes and safe cleanup is left to a supervised pass:

- `/tmp/luce-auto-cron-20260530-162504`
- `/tmp/luce-probe-20260530-162504-pr-305`
- `/tmp/luce-probe-20260530-162504-pr-237`
- `/tmp/luce-probe-20260530-162504-pr-221`
- `/tmp/luce-probe-20260530-162504-pr-154`
- `/tmp/luce-probe-20260530-162504-pr-153`
- `/tmp/luce-probe-20260530-162504-pr-137`
- `/tmp/luce-probe-20260530-162504-pr-135`
- `/tmp/luce-probe-20260530-162504-pr-94`
- `/tmp/luce-probe-20260530-162504-pr-48`
- Logs under `/tmp/luce-auto-cron-20260530-162504-logs/`, including `merge-*.log`, `status-*.txt`, `conflicts-*.txt`, and Claude tmux reports for #305/#237.

Earlier retained audit paths from prior runs include `/tmp/luce-auto-cron-20260530-161133`, `/tmp/luce-auto-cron-20260530-155251`, `/tmp/luce-auto-cron-20260530-153049`, `/tmp/luce-auto-cron-20260530-154010`, their corresponding probe worktrees, and logs.

## Notes

The next useful integration work remains a dedicated current-`server/` #237 MTP foundation selective port, with #221/#153/#154 mined afterward. #305 should be split or manually refactored in a supervised pass before inclusion; the safe shape is common MoE infrastructure with Qwen35MoE compatibility preserved, then Laguna hybrid behind an explicit opt-in gate while preserving device selection, backend factory layer-split selection, graph precision policy, and the current `TargetLoadPlan` partial loader. Keep #135 as a separate scheduler/batched-target selective port. #137 and #48 look like old `dflash/CMakeLists.txt` changes that should be closed or retargeted, and #94 appears largely superseded by current draft/SWA support.
