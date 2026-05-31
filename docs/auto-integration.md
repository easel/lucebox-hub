# Auto-integration manifest

Repository: `Luce-Org/lucebox-hub`
Integration branch: `auto-integration`
Writable remote: `easel`
Upstream remote: `origin` / `Luce-Org`
Last refresh: `2026-05-31T02:27:27-04:00`
Current base: `origin/main` `c95dfcab`
Previous integration tip: `easel/auto-integration` `cd7b9e80`
Current integration tip before push: `cd7b9e80`

This branch is maintained as a reproducible patch stack over `origin/main`. This unattended run started from a clean primary checkout on `auto-integration`, verified GitHub/Claude/Codex auth with the real user credential home, fetched `origin` and `easel` separately, fetched current PR heads, and rechecked exact PR-head containment against the current stack.

This run found `origin/main` unchanged and `easel/auto-integration` already at the previous manifest-only refresh. The open non-draft set still contains 27 PRs; 21 are included by exact head containment and 6 remain non-ancestor conflict/selective-port candidates. Fresh worktree probes reconfirmed the same conflict surfaces for #305, #237, #221, #154, #153, and #135. No PR head could be newly integrated as-is in this run, but a fresh tmux-driven Codex read-only audit produced a more concrete #237 current-layout salvage plan: start with single-GPU qwen35 native MTP chain mode only, explicitly gate it away from layer-split, pFlash-compressed requests, remote-draft IPC, restore paths, top-K/DDTree, and production `mtp_orchestrator` wiring.

## Included in the current non-draft stack

| PR | Head branch | Head | State | Notes |
|---:|---|---:|---|---|
| #317 | `docs/issue-102` | `7d3f873f` | included | Documents multi-GPU flags/env vars for PFlash/DFlash. The stack already had patch-equivalent README content, so the merge was resolved by retaining current README layout while making the PR head an exact ancestor. |
| #316 | `fix/issue-233` | `d28eb1fb` | included | Captures daemon stderr in `DflashClient` error messages by redirecting child stderr to stdout for both Windows and POSIX subprocess launches. |
| #315 | `codex/dflash-spec-tool-recovery` | `3ba401f0` | included | Recovers spec-decode agent stalls with env-gated tool-prefix floor injection, bounded residual stall/repetition guards, invalid draft-seed AR fallback, and the existing qwen35 empty-output / C2 `fa_window` AR fallbacks. |
| #314 | `fix/specdecode-empty-ar-fallback` | `f4a0d8b5` | included | Common empty-spec-decode fallback is carried: `ModelBackend` retries successful zero-token spec decode through forced AR for both generate and restore paths. Manual conflict resolution preserved existing qwen35 stall-recovery hints and pFlash C2 `fa_window` AR fallback behavior. |
| #310 | `feat-backend-activation-precision-policy-after-306` | `bf9f4b57` | included | Backend activation precision policy / graph tensor precision helpers are carried exactly. |
| #309 | `experiment-dflash-feature-dtype` | `ea6ac481` | included | Feature mirror dtype policy is carried exactly. |
| #308 | `fix/qwen-think-channel` | `9d4defe1` | included | Qwen3.6/Laguna think-mode reasoning is routed to `reasoning_content`; stack carries the replay HTTP stub harness and regression scenarios exactly. |
| #306 | `refactor-server-layer-split-runtime` | `988fc933` | included | Shared layer-split runtime helper extraction is carried exactly. |
| #297 | `feat-server-laguna-layer-split-adapter-v2` | `53dd1686` | included | Laguna target-layer-split adapter is carried exactly. |
| #295 | `fix-layer-split-sampling` | `a9aedf7d` | included | Target layer-split sampling support is carried exactly. |
| #294 | `feat/server-passthrough-proxy` | `48f6962d` | included | Passthrough proxy, keep-ratio curve, query survival checks, multimodal text extraction, and unit coverage are carried exactly. |
| #289 | `pipeline_moe` | `caf2b112` | included | Carries pipelined hybrid Qwen35 MoE decode plus the sub-batch hybrid prefill FFN safety fix. |
| #285 | `feat/lucebox-docker` | `4b4fd286` | included | Docker stack / `lucebox` CLI / harness / `luce-bench`, Bragi sweep docs, autotune/sweep updates, shell harness tests, long-context grader coverage, Bragi GPU-power-throttle experiment notes, and luce-bench grader fixes are carried exactly. |
| #276 | `fix/qwen36-claude-code-tool-calling` | `5e861b4d` | included | Qwen3.6-27B tool-calling fix for Claude-code Anthropic path is carried exactly. |
| #274 | `feat/pflash-drafter-ee7` | `8c1f37db` | included | Adaptive pFlash composition and effective-size admission/keep-ratio guard update are carried exactly. |
| #266 | `feat/harness-typed-adapters` | `17525eae` | included | Typed harness adapters and format-aware session-inject proxy are carried exactly. |
| #152 | `main` | `cf735bee` | included | Gemma 4 RTX 4090 backend helpers are carried exactly. |
| #142 | `xabicasa/dflash-safetensors-draft-fp16` | `f2fbf62f` | included | FP16 safetensors drafter support is carried exactly. |
| #137 | `xabicasa/dflash-build-cmake-sm89-bsa` | `297fc74e` | included / superseded | Merged by preserving deletion of the retired `dflash/CMakeLists.txt` path. Current `server/CMakeLists.txt` already handles user CUDA architectures and BSA defaults. |
| #94 | `feat/dflash-qwen36-swa-draft` | `d2f9c9dd` | included / superseded | Recorded with an `ours` merge because the current tree already has SWA draft support (`DraftLayer::is_swa`, `DraftWeights::swa_window`, safetensors SWA metadata parsing, SWA-aware draft masks, and GGUF SWA metadata support). |
| #48 | `fix/consumer-blackwell-auto-detect` | `858b84b6` | included / superseded | Merged by preserving deletion of the retired `dflash/CMakeLists.txt` path. Current `server/CMakeLists.txt` already conditionally handles Blackwell/CUDA-version flags. |

Closed or upstreamed PRs still represented by the stack/base include #313 (closed, carried in stack history), #311, #307, #303, #302, #301, #300, #299, #298, and #292.

## Validation run

This run performed:

- `date -Is` -> `2026-05-31T02:19:17-04:00` during preflight and `2026-05-31T02:27:27-04:00` before manifest refresh.
- Primary checkout preflight: `git status --short` was clean on `auto-integration`; remotes were `origin=https://github.com/Luce-Org/lucebox-hub` and `easel=https://github.com/easel/lucebox-hub`.
- Auth/tooling checks with real user credentials succeeded: `gh auth status`, `claude auth status --text`, and `codex --help`.
- `git fetch --prune origin` and `git fetch --prune easel` completed successfully.
- Current open PR enumeration reported 27 non-draft PRs and 7 draft/excluded PRs.
- Explicit fetch of open PR heads succeeded for all current non-draft PRs.
- Exact-head containment before reconciliation showed #317, #316, #315, #314, #310, #309, #308, #306, #297, #295, #294, #289, #285, #276, #274, #266, #152, #142, #137, #94, and #48 were ancestors of `easel/auto-integration`; #305, #237, #221, #154, #153, and #135 were non-ancestors.
- A reconcile worktree from `easel/auto-integration` was created at `/tmp/luce-auto-cron-20260531-022008`; `origin/main` was already included.
- Fresh direct-merge probes on top of `cd7b9e80` reconfirmed current conflict counts for all remaining non-ancestor PRs: #305 (29 files), #237 (24), #221 (23), #154 (12), #153 (10), and #135 (3).
- Tmux-driven Claude read-only feasibility for #237 exited with `Error: Reached max turns (12)` and produced no useful report.
- Tmux-driven Codex read-only feasibility for #237 completed and produced `/tmp/luce-codex-20260531-022008-pr237-report.txt`. It recommended a minimal current-layout port of single-GPU qwen35 native MTP chain mode only: add `MtpSource` / MTP args in `server/src/common/backend_factory.*`, explicit `--mtp-*` CLI validation in `server/src/server/server_main.cpp`, optional hidden-capture/MTP defaults in `server/src/common/dflash_target.h`, new common `mtp_interface` / `mtp_chain_runner`, gated hidden outputs in `step_graph`, `internal.h`, `graph_builders.cpp`, and `qwen35_target_graph.cpp`, qwen35 MTP loader/graph/module files, and `Qwen35Backend` wiring inside the current `generate()` flow while leaving `restore_and_generate()` on existing fallback paths.
- The Codex audit warned not to port PR #237's top-K/DDTree, production `mtp_orchestrator`, layer-split MTP, pFlash-compressed MTP, restore/disk-cache MTP, or external/Gemma4 MTP in the first salvage pass; MTP should be gated off when `fa_window_override != 0`, remote-draft IPC is active, layer-split is selected, or sampler logit processing is required.
- Containment check confirmed `origin/main` and 21 included PR heads are ancestors of `HEAD`; the remaining non-ancestor PRs are #305, #237, #221, #154, #153, and #135.
- `git diff --check` on the manifest-only change passed.

## Pending / blocked-needs-human / selective-port candidates

| PR | Head branch | Head | Current status | Probe result / next useful action |
|---:|---|---:|---|---|
| #305 | `layersplit_refactor` | `1de45e4d` | selective salvage only / human-scale | Fresh direct merge still conflicts across 29 files. Prior delegated audit reconfirmed first 21 PR commits are patch-equivalent/already absorbed; the 10 patch-unique commits cover common MoE hybrid extraction, routed FFN cached graphs, GPU-resident `act_cur` and async logits, Laguna hot/cold placement and `DFLASH_EXPERT_BUDGET_PCT`, and no-sub-batch reused-`gallocr` behavior. Recent Claude/Codex attempts did not yield a better automated port. Do not direct-merge; selectively port desired Laguna/common-MoE behavior into current `server/` layout while preserving current qwen35moe pipeline, Laguna layer-split adapter, backend precision policy, IPC payload transport, and harness/Docker layout. |
| #237 | `feat/dflash-mtp-foundation` | `02c6a6c4` | salvage-port candidate / human-scale server-layout port | Fresh probe still conflicts across 24 old `dflash/` and current `server/` files including CMake, backend factory, common MTP interfaces, Qwen35 graph/loader/backend, and tests. This run's Codex audit refined the first salvage slice: port only single-GPU qwen35 native MTP chain mode behind explicit/auto MTP flags; add `MtpSource` / MTP args, CLI validation, optional hidden-capture defaults, common `mtp_interface` / `mtp_chain_runner`, qwen35 MTP loader/graph/module files, gated hidden graph outputs, and `Qwen35Backend::generate()` integration. Keep `restore_and_generate()` on existing fallback paths and explicitly gate MTP away from layer-split, pFlash `fa_window_override`, remote-draft IPC, sampler logit processing, top-K/DDTree, production `mtp_orchestrator`, and external/Gemma4 MTP. |
| #135 | `xabicasa/dflash-multi-request-scheduler-batched-target-step` | `561b0ac1` | selective-port candidate / high risk | Fresh direct probe still conflicts in `server/src/internal.h`, `server/src/qwen35/qwen35_target_graph.cpp`, and `server/test/test_dflash.cpp`. Current `TargetCache` remains single-cache/slot oriented and qwen35 target graph still has internal `n_seqs = 1` assumptions. This run's Claude/Codex attempts did not produce a usable automated port report. Split any salvage into smaller current-layout changes: cache slots/ownership, tagged framing, scheduler protocol, then batched target step. |
| #154 | `xabicasa/dflash-mtp-speculative-loop` | `2f4ede79` | blocked-needs-human / dependency | Fresh probe conflicts in 12 old/current MTP docs, `dflash/CMakeLists.txt`, CUDA/internal/Qwen35 graph/loader files, and MTP smoke/contract tests. Mine linear MTP decode semantics after current-layout #237-equivalent Qwen35 MTP exists. |
| #153 | `xabicasa/dflash-mtp-integrated` | `e9b17cb1` | blocked-needs-human / dependency | Fresh probe conflicts in 10 old/current MTP docs, `dflash/CMakeLists.txt`, CUDA/internal/Qwen35 graph/loader files, and MTP smoke/contract tests. Mine loader/graph/cache/test ideas after current-layout #237-equivalent Qwen35 MTP exists. |

## Suggested close / superseded

| PR | Head branch | Head | Current status | Evidence / suggested action |
|---:|---|---:|---|---|
| #221 | `feat/mtp-prefix-warm-ghost` | `05502974` | superseded for direct integration; mine only after #237 | Fresh direct-merge probe still conflicts across 23 old/current files. Prior delegated audit found 12 non-equivalent commits, but the branch is older/broader than #237 and mixes early MTP, prefix-cache warm-hit, PFlash dispatcher/protocol, benches, and docs; #237 is the better MTP foundation salvage base. |

## Draft / excluded

Draft PRs remain outside the primary non-draft integration target except for dependency awareness: #312, #304, #291, #290, #275, #249, and #193. Draft #312's backend IPC payload transport is related to already-carried IPC payload work, but remains draft/excluded. Draft #304 may touch compaction behavior and should be watched if it becomes ready.

## Retained worktrees / logs

This run retained the updated stack worktree, fresh conflicted probe worktrees, and agent transcripts for audit; earlier conflicted probe worktrees remain from prior runs because safe cleanup is left to a supervised pass:

- `/tmp/luce-auto-cron-20260531-022008` (manifest-only refresh worktree)
- `/tmp/luce-probe-20260531-022008-pr-305`
- `/tmp/luce-probe-20260531-022008-pr-237`
- `/tmp/luce-probe-20260531-022008-pr-221`
- `/tmp/luce-probe-20260531-022008-pr-154`
- `/tmp/luce-probe-20260531-022008-pr-153`
- `/tmp/luce-probe-20260531-022008-pr-135`
- `/tmp/luce-claude-20260531-022008-pr237-report.txt` (Claude max-turns failure report)
- `/tmp/luce-codex-20260531-022008-pr237-report.txt` (Codex #237 salvage plan transcript)

Prior retained worktrees/logs for conflicted/superseded probes and earlier refreshes include `/tmp/luce-auto-cron-20260531-020218`, `/tmp/luce-probe-20260531-020218-pr-305`, `/tmp/luce-probe-20260531-020218-pr-237`, `/tmp/luce-probe-20260531-020218-pr-221`, `/tmp/luce-probe-20260531-020218-pr-154`, `/tmp/luce-probe-20260531-020218-pr-153`, `/tmp/luce-probe-20260531-020218-pr-135`, `/tmp/luce-auto-cron-20260531-014341`, `/tmp/luce-probe-20260531-014341-pr-305`, `/tmp/luce-probe-20260531-014341-pr-237`, `/tmp/luce-probe-20260531-014341-pr-221`, `/tmp/luce-probe-20260531-014341-pr-154`, `/tmp/luce-probe-20260531-014341-pr-153`, `/tmp/luce-probe-20260531-014341-pr-135`, `/tmp/luce-auto-cron-20260531-012821`, `/tmp/luce-probe-20260531-012821-pr-305`, `/tmp/luce-probe-20260531-012821-pr-237`, `/tmp/luce-probe-20260531-012821-pr-221`, `/tmp/luce-probe-20260531-012821-pr-154`, `/tmp/luce-probe-20260531-012821-pr-153`, `/tmp/luce-probe-20260531-012821-pr-135`, `/tmp/luce-auto-cron-20260531-010104`, `/tmp/luce-auto-cron-20260531-002924`, `/tmp/luce-auto-cron-20260531-000900`, `/tmp/luce-auto-cron-20260530-235000`, `/tmp/luce-auto-cron-20260530-232125`, and earlier `/tmp/luce-auto-cron-*` / `/tmp/luce-probe-*` audit worktrees.

## Notes

The next useful integration work is now a dedicated current-`server/` #237 MTP foundation selective port, starting with only single-GPU qwen35 native MTP chain mode and the guardrails captured above; #153/#154 should be mined afterward for linear MTP decode semantics, and #221 only for any still-missing prefix-warm ideas. #305 is the other high-value human-scale port, but only as selective salvage of the 10 patch-unique commits after reconciling with current qwen35moe pipeline and Laguna layer-split code. Keep #135 as a separate scheduler/batched-target selective port split into small current-layout changes: cache slots/ownership, tagged framing, scheduler protocol, then batched target step. #137, #48, and #94 are now represented by superseding current-layout code and can be closed or retargeted only if authors can identify a minimal missing delta.
