# Auto-integration manifest

Repository: `Luce-Org/lucebox-hub`
Integration branch: `auto-integration`
Writable remote: `easel`
Upstream remote: `origin` / `Luce-Org`
Last refresh: `2026-05-30T22:21:48-04:00`
Current base: `origin/main` `c95dfcab`
Previous integration tip: `easel/auto-integration` `fa9c9797`
Current integration tip before push: `fa9c9797`

This branch is maintained as a reproducible patch stack over `origin/main`. This unattended run started from a clean primary checkout on `auto-integration`, verified GitHub/Claude/Codex auth with the real user credential home, fetched `origin` and `easel` separately, fetched current PR heads, and rechecked exact PR-head containment against the current stack.

This refresh found no new non-draft PR heads beyond the already-pushed stack. `origin/main` was already included. The open non-draft set contains 25 PRs; 16 are included by exact head containment and 9 remain non-ancestor conflict/selective-port or superseded candidates. Fresh direct-merge probes for all 9 non-ancestor PRs still conflict in the same broad classes recorded below.

## Included in the current non-draft stack

| PR | Head branch | Head | State | Notes |
|---:|---|---:|---|---|
| #315 | `codex/dflash-spec-tool-recovery` | `6c8db53f` | included | Recovers spec-decode agent stalls with env-gated tool-prefix floor injection while preserving existing qwen35 empty-output AR fallback and the C2 `fa_window` AR fallback. |
| #314 | `fix/specdecode-empty-ar-fallback` | `38f92c48` | included | Qwen35 falls back to AR decode when spec-decode succeeds but produces an empty token vector. |
| #310 | `feat-backend-activation-precision-policy-after-306` | `bf9f4b57` | included | Backend activation precision policy / graph tensor precision helpers are carried exactly. |
| #309 | `experiment-dflash-feature-dtype` | `ea6ac481` | included | Feature mirror dtype policy is carried exactly. |
| #308 | `fix/qwen-think-channel` | `9d4defe1` | included | Qwen3.6/Laguna think-mode reasoning is routed to `reasoning_content`; stack carries the replay HTTP stub harness and regression scenarios exactly. |
| #306 | `refactor-server-layer-split-runtime` | `988fc933` | included | Shared layer-split runtime helper extraction is carried exactly. |
| #297 | `feat-server-laguna-layer-split-adapter-v2` | `53dd1686` | included | Laguna target-layer-split adapter is carried exactly. |
| #295 | `fix-layer-split-sampling` | `a9aedf7d` | included | Target layer-split sampling support is carried exactly. |
| #294 | `feat/server-passthrough-proxy` | `48f6962d` | included | Passthrough proxy, keep-ratio curve, query survival checks, multimodal text extraction, and unit coverage are carried exactly. |
| #289 | `pipeline_moe` | `caf2b112` | included | Carries pipelined hybrid Qwen35 MoE decode plus the sub-batch hybrid prefill FFN safety fix. |
| #285 | `feat/lucebox-docker` | `4b4fd286` | included | Docker stack / `lucebox` CLI / harness / `luce-bench`, Bragi sweep docs, autotune/sweep updates, shell harness tests, long-context grader coverage, Bragi GPU-power-throttle experiment notes, and the latest luce-bench grader fixes for `call:<verb>{}` agent/tool emissions and HumanEval trailing garbage trimming are carried exactly. |
| #276 | `fix/qwen36-claude-code-tool-calling` | `5e861b4d` | included | Qwen3.6-27B tool-calling fix for Claude-code Anthropic path is carried exactly. |
| #274 | `feat/pflash-drafter-ee7` | `8c1f37db` | included | Adaptive pFlash composition and effective-size admission/keep-ratio guard update are carried exactly. |
| #266 | `feat/harness-typed-adapters` | `17525eae` | included | Typed harness adapters and format-aware session-inject proxy are carried exactly. |
| #152 | `main` | `cf735bee` | included | Gemma 4 RTX 4090 backend helpers are carried exactly. |
| #142 | `xabicasa/dflash-safetensors-draft-fp16` | `f2fbf62f` | included | FP16 safetensors drafter support is carried exactly. |

Closed or upstreamed PRs still represented by the stack/base include #313 (closed, carried in stack history), #311, #307, #303, #302, #301, #300, #299, #298, and #292.

## Validation run

This run performed:

- `date -Is` -> `2026-05-30T22:20:18-04:00` during preflight.
- Primary checkout preflight: `git status --short` was clean on `auto-integration`; remotes were `origin=https://github.com/Luce-Org/lucebox-hub` and `easel=https://github.com/easel/lucebox-hub`.
- Auth/tooling checks with real user credentials succeeded: `gh auth status`, `claude auth status --text`, and a harmless `codex --help` smoke check.
- `git fetch --prune origin` and `git fetch --prune easel` completed successfully.
- Current open PR enumeration reported 25 non-draft PRs and 7 draft/excluded PRs.
- Explicit fetch of open PR heads succeeded for all current non-draft PRs.
- Exact-head containment before reconciliation showed #315, #314, #310, #309, #308, #306, #297, #295, #294, #289, #285, #276, #274, #266, #152, and #142 were ancestors of the stack; #305, #237, #221, #154, #153, #137, #135, #94, and #48 were non-ancestors.
- A reconcile worktree from `easel/auto-integration` was created at `/tmp/luce-auto-cron-20260530-222119`; `origin/main` was already included.
- No contributor PR head merged this run because all ready PR heads were either already exact ancestors or remained conflicting/superseded candidates.
- Fresh direct-merge probes were created for all 9 remaining non-ancestor non-draft PRs from stack commit `fa9c9797`; all still conflicted: #305 (29 conflicted files), #237 (24), #221 (23), #154 (12), #153 (10), #137 (1 old `dflash/CMakeLists.txt`), #135 (3), #94 (3), and #48 (1 old `dflash/CMakeLists.txt`).
- Verification for the unchanged code stack: `git diff --check` passed. No targeted runtime tests were rerun because this run made only a manifest refresh after confirming no code/PR-head delta since the previous verified push.

## Pending / blocked-needs-human / selective-port candidates

| PR | Head branch | Head | Current status | Probe result / next useful action |
|---:|---|---:|---|---|
| #305 | `layersplit_refactor` | `1de45e4d` | selective salvage only / human-scale | Fresh direct merge still conflicts across 29 files. Prior delegated audit reconfirmed first 21 PR commits are patch-equivalent/already absorbed; the 10 patch-unique commits cover common MoE hybrid extraction, routed FFN cached graphs, GPU-resident `act_cur` and async logits, Laguna hot/cold placement and `DFLASH_EXPERT_BUDGET_PCT`, and no-sub-batch reused-`gallocr` behavior. Do not direct-merge; selectively port desired Laguna/common-MoE behavior into current `server/` layout while preserving current qwen35moe pipeline, Laguna layer-split adapter, backend precision policy, IPC payload transport, and harness/Docker layout. |
| #237 | `feat/dflash-mtp-foundation` | `02c6a6c4` | salvage-port candidate / human-scale server-layout port | Fresh probe still conflicts across 24 old `dflash/` and current `server/` files including CMake, backend factory, common MTP interfaces, Qwen35 graph/loader/backend, and tests. Prior delegated audit reconfirmed no newly direct-portable minimal subset; port old CLI/config semantics into current `server/src/server/server_main.cpp`; merge `MtpSource`, native/external MTP GGUF detection, backend factory assignment, MTP hidden captures, and Qwen35 helpers without regressing remote-draft, Qwen35MoE, layer-split, or PFlash helpers. |
| #135 | `xabicasa/dflash-multi-request-scheduler-batched-target-step` | `561b0ac1` | selective-port candidate / high risk | Fresh direct probe still conflicts in `server/src/internal.h`, `server/src/qwen35/qwen35_target_graph.cpp`, and `server/test/test_dflash.cpp`. Prior delegated audit found no current hits for `SCHED_BATCH_*`, `SCHED_STEP`, `LIST_REQUESTS`, `--target-cache-slots`, `--stream-tagged`, `PendingQuantum`, or `ActiveDaemonSlot`; current `TargetCache` remains single-cache/slot oriented and qwen35 target graph still has internal `n_seqs = 1` assumptions. Split any salvage into smaller current-layout changes: cache slots/ownership, tagged framing, scheduler protocol, then batched target step. |
| #154 | `xabicasa/dflash-mtp-speculative-loop` | `2f4ede79` | blocked-needs-human / dependency | Fresh probe conflicts in 12 old/current MTP docs, `dflash/CMakeLists.txt`, CUDA/internal/Qwen35 graph/loader files, and MTP smoke/contract tests. Mine linear MTP decode semantics after current-layout #237-equivalent Qwen35 MTP exists. |
| #153 | `xabicasa/dflash-mtp-integrated` | `e9b17cb1` | blocked-needs-human / dependency | Fresh probe conflicts in 10 old/current MTP docs, `dflash/CMakeLists.txt`, CUDA/internal/Qwen35 graph/loader files, and MTP smoke/contract tests. Mine loader/graph/cache/test ideas after current-layout #237-equivalent Qwen35 MTP exists. |

## Suggested close / superseded

| PR | Head branch | Head | Current status | Evidence / suggested action |
|---:|---|---:|---|---|
| #221 | `feat/mtp-prefix-warm-ghost` | `05502974` | superseded for direct integration; mine only after #237 | Fresh direct-merge probe still conflicts across 23 old/current files. Prior delegated audit found 12 non-equivalent commits, but the branch is older/broader than #237 and mixes early MTP, prefix-cache warm-hit, PFlash dispatcher/protocol, benches, and docs; #237 is the better MTP foundation salvage base. |
| #137 | `xabicasa/dflash-build-cmake-sm89-bsa` | `297fc74e` | suggested-close/superseded | Fresh probe conflicts only on deleted old `dflash/CMakeLists.txt`. Prior delegated audit confirmed current `server/CMakeLists.txt` already honors `DFLASH27B_USER_CUDA_ARCHITECTURES`, applies resolved CUDA arches to `dflash_common`, and keeps `DFLASH27B_ENABLE_BSA` on except explicit HIP Phase 1. |
| #94 | `feat/dflash-qwen36-swa-draft` | `d2f9c9dd` | suggested-close/superseded | Fresh probe conflicts in current draft/internal files. Prior delegated audit confirmed current tree has `DraftLayer::is_swa`, `DraftWeights::swa_window`, bare-filename config fallback, safetensors `sliding_window`/`layer_types` parsing, SWA-aware draft graph masks, and GGUF SWA metadata support. |
| #48 | `fix/consumer-blackwell-auto-detect` | `858b84b6` | suggested-close/superseded | Fresh probe conflicts only on deleted old `dflash/CMakeLists.txt`. Prior delegated audit confirmed current `server/CMakeLists.txt` conditionally adds CUDA `120`/`110`/`121` by CUDA version and sets `GGML_CUDA_BLACKWELL_CONSUMER` from resolved 12x arches. |

## Draft / excluded

Draft PRs remain outside the primary non-draft integration target except for dependency awareness: #312, #304, #291, #290, #275, #249, and #193. Draft #312's backend IPC payload transport is related to already-carried IPC payload work, but remains draft/excluded. Draft #304 may touch compaction behavior and should be watched if it becomes ready.

## Retained worktrees / logs

This run retained the updated stack worktree and fresh conflicted probe logs for audit; earlier conflicted probe worktrees remain from prior runs because safe cleanup is left to a supervised pass:

- `/tmp/luce-auto-cron-20260530-222119`
- Fresh conflicted probe worktrees: `/tmp/luce-probe-20260530-222119-pr-305`, `/tmp/luce-probe-20260530-222119-pr-237`, `/tmp/luce-probe-20260530-222119-pr-221`, `/tmp/luce-probe-20260530-222119-pr-154`, `/tmp/luce-probe-20260530-222119-pr-153`, `/tmp/luce-probe-20260530-222119-pr-137`, `/tmp/luce-probe-20260530-222119-pr-135`, `/tmp/luce-probe-20260530-222119-pr-94`, and `/tmp/luce-probe-20260530-222119-pr-48`.
- Fresh logs under `/tmp/luce-auto-cron-20260530-222119-logs/`, including `merge-*.log`, `status-*.txt`, and `conflicts-*.txt`.

Prior retained worktrees/logs for conflicted/superseded probes and earlier refreshes include `/tmp/luce-auto-cron-20260530-220557`, `/tmp/luce-auto-cron-20260530-215157`, `/tmp/luce-auto-cron-20260530-212604`, `/tmp/luce-auto-cron-20260530-210747`, `/tmp/luce-auto-cron-20260530-204620`, `/tmp/luce-auto-cron-20260530-203020`, `/tmp/luce-auto-cron-20260530-201608`, `/tmp/luce-auto-cron-20260530-200216`, `/tmp/luce-auto-cron-20260530-194121`, `/tmp/luce-auto-cron-20260530-192047`, `/tmp/luce-auto-cron-20260530-184231`, `/tmp/luce-auto-cron-20260530-181103`, `/tmp/luce-auto-cron-20260530-175155`, `/tmp/luce-auto-cron-20260530-173141`, `/tmp/luce-auto-cron-20260530-171420`, `/tmp/luce-auto-cron-20260530-165724`, `/tmp/luce-auto-cron-20260530-164341`, `/tmp/luce-auto-cron-20260530-162504`, `/tmp/luce-auto-cron-20260530-161133`, `/tmp/luce-auto-cron-20260530-155251`, `/tmp/luce-auto-cron-20260530-153049`, `/tmp/luce-auto-cron-20260530-154010`, their corresponding probe worktrees, and logs.

## Notes

The next useful integration work remains a dedicated current-`server/` #237 MTP foundation selective port, with #153/#154 mined afterward and #221 mined only for any still-missing prefix-warm ideas. #305 is the other high-value human-scale port, but only as selective salvage of the 10 patch-unique commits after reconciling with current qwen35moe pipeline and Laguna layer-split code. Keep #135 as a separate scheduler/batched-target selective port split into small current-layout PRs. #137, #48, and #94 look superseded and should be closed or retargeted only if authors can identify a minimal missing delta.
