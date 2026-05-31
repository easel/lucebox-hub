# Auto-integration manifest

Repository: `Luce-Org/lucebox-hub`
Integration branch: `auto-integration`
Writable remote: `easel`
Upstream remote: `origin` / `Luce-Org`
Last refresh: `2026-05-31T04:42:56-04:00`
Current base: `origin/main` `c95dfcab`
Previous integration tip: `easel/auto-integration` `01ce03d2`
Current integration tip before push: `01ce03d2`

This branch is maintained as a reproducible patch stack over `origin/main`. This unattended run started from a clean primary checkout on `auto-integration`, verified GitHub/Claude/Codex auth using the real user credential home, fetched `origin` and `easel` separately, fetched current non-draft PR heads, and checked exact PR-head containment against `easel/auto-integration`.

No ready PR head advanced since the prior pushed stack: the stack still contains 21 of 27 current non-draft contributor PR heads exactly; the same 5 old conflict/selective-port candidates plus one suggested-close branch remain non-ancestors (#305, #237, #221, #154, #153, and #135). `origin/main` was already included.

Fresh worktree probes were still performed for the 6 pre-existing non-ancestor candidates. A fresh tmux-driven Claude read-only attempt for #237 exited with `Error: Reached max turns (12)` and no useful report. A fresh tmux-driven Codex read-only attempt for #237 completed with a concise feasibility report after a large inspection transcript. Codex agreed that #237 should be ported in slices rather than direct-merged: build/file placement, factory/server CLI activation, common MTP abstraction, Qwen35 graph/target capture, Qwen35 backend runtime, and harness compatibility. Manual probe results still support the prior classification: #237 is the best MTP-foundation salvage starting point; #153/#154 depend on a current-layout #237-equivalent; #221 is broader/older and should be mined only after #237; #305 and #135 remain high-risk selective ports.

## Included in the current non-draft stack

| PR | Head branch | Head | State | Notes |
|---:|---|---:|---|---|
| #317 | `docs/issue-102` | `7d3f873f` | included | Documents multi-GPU flags/env vars for PFlash/DFlash. The stack already had patch-equivalent README content, so the merge was resolved by retaining current README layout while making the PR head an exact ancestor. |
| #316 | `fix/issue-233` | `d28eb1fb` | included | Captures daemon stderr in `DflashClient` error messages by redirecting child stderr to stdout for both Windows and POSIX subprocess launches. |
| #315 | `codex/dflash-spec-tool-recovery` | `3ba401f0` | included | Recovers spec-decode agent stalls with env-gated tool-prefix floor injection, bounded residual stall/repetition guards, invalid draft-seed AR fallback, and the existing qwen35 empty-output / C2 `fa_window` AR fallbacks. |
| #314 | `fix/specdecode-empty-ar-fallback` | `f4a0d8b5` | included | Common empty-spec-decode fallback is carried: `ModelBackend` retries successful zero-token spec decode through forced AR for both generate and restore paths. |
| #310 | `feat-backend-activation-precision-policy-after-306` | `bf9f4b57` | included | Backend activation precision policy / graph tensor precision helpers are carried exactly. |
| #309 | `experiment-dflash-feature-dtype` | `ea6ac481` | included | Feature mirror dtype policy is carried exactly. |
| #308 | `fix/qwen-think-channel` | `9d4defe1` | included | Qwen3.6/Laguna think-mode reasoning is routed to `reasoning_content`; stack carries the replay HTTP stub harness and regression scenarios exactly. |
| #306 | `refactor-server-layer-split-runtime` | `988fc933` | included | Shared layer-split runtime helper extraction is carried exactly. |
| #297 | `feat-server-laguna-layer-split-adapter-v2` | `53dd1686` | included | Laguna target-layer-split adapter is carried exactly. |
| #295 | `fix-layer-split-sampling` | `a9aedf7d` | included | Target layer-split sampling support is carried exactly. |
| #294 | `feat/server-passthrough-proxy` | `48f6962d` | included | Passthrough proxy, keep-ratio curve, query survival checks, multimodal text extraction, and unit coverage are carried exactly. |
| #289 | `pipeline_moe` | `caf2b112` | included | Carries pipelined hybrid Qwen35 MoE decode plus the sub-batch hybrid prefill FFN safety fix. |
| #285 | `feat/lucebox-docker` | `060492e4` | included | Docker stack / `lucebox` CLI / harness / `luce-bench`, Bragi sweep docs, autotune/sweep updates, shell harness tests, long-context grader coverage, Bragi GPU-power-throttle notes, luce-bench grader fixes, and Bragi think-vs-nothink baseline summary are carried exactly. |
| #276 | `fix/qwen36-claude-code-tool-calling` | `5e861b4d` | included | Qwen3.6-27B tool-calling fix for Claude-code Anthropic path is carried exactly. |
| #274 | `feat/pflash-drafter-ee7` | `8fc961b5` | included | Adaptive pFlash composition and effective-size admission/keep-ratio guard update are carried; the latest head adds an opt-in pFlash regime router (`PFLASH_ROUTER_ENABLE`) with standalone `test_regime_router` coverage. Conflict resolution preserved the stack's piecewise pFlash keep-ratio curve, session bandit override, upstream proxy config, and `DFLASH27B_DRAFT_SWA` env handling. |
| #266 | `feat/harness-typed-adapters` | `17525eae` | included | Typed harness adapters and format-aware session-inject proxy are carried exactly. |
| #152 | `main` | `cf735bee` | included | Gemma 4 RTX 4090 backend helpers are carried exactly. |
| #142 | `xabicasa/dflash-safetensors-draft-fp16` | `f2fbf62f` | included | FP16 safetensors drafter support is carried exactly. |
| #137 | `xabicasa/dflash-build-cmake-sm89-bsa` | `297fc74e` | included / superseded | Merged by preserving deletion of retired `dflash/CMakeLists.txt`; current `server/CMakeLists.txt` already handles user CUDA architectures and BSA defaults. |
| #94 | `feat/dflash-qwen36-swa-draft` | `d2f9c9dd` | included / superseded | Recorded with an `ours` merge because the current tree already has SWA draft support (`DraftLayer::is_swa`, `DraftWeights::swa_window`, safetensors SWA metadata parsing, SWA-aware draft masks, and GGUF SWA metadata support). |
| #48 | `fix/consumer-blackwell-auto-detect` | `858b84b6` | included / superseded | Merged by preserving deletion of retired `dflash/CMakeLists.txt`; current `server/CMakeLists.txt` already conditionally handles Blackwell/CUDA-version flags. |

Closed or upstreamed PRs still represented by the stack/base include #313 (closed, carried in stack history), #311, #307, #303, #302, #301, #300, #299, #298, and #292.

## Validation run

This run performed:

- `date -Is` -> `2026-05-31T04:33:29-04:00` during preflight and `2026-05-31T04:42:56-04:00` before manifest refresh.
- Primary checkout preflight: `git status --short` was clean on `auto-integration`; remotes were `origin=https://github.com/Luce-Org/lucebox-hub` and `easel=https://github.com/easel/lucebox-hub`.
- Auth/tooling checks with real user credentials succeeded: `gh auth status`, `claude auth status --text`, and Codex help smoke check.
- `git fetch --prune origin` and `git fetch --prune easel` completed successfully.
- Current open PR enumeration reported 27 non-draft PRs and 7 draft/excluded PRs.
- Explicit fetch of open non-draft PR heads succeeded for all current non-draft PRs.
- Exact-head containment showed #317, #316, #315, #314, #310, #309, #308, #306, #297, #295, #294, #289, #285, #276, #274, #266, #152, #142, #137, #94, and #48 were ancestors of `easel/auto-integration`; #305, #237, #221, #154, #153, and #135 were non-ancestors.
- A reconcile worktree from `easel/auto-integration` was created at `/tmp/luce-auto-cron-20260531-043408`; `origin/main` was already included.
- Fresh direct-merge probes on top of `01ce03d2` reconfirmed current conflict/status counts for the pre-existing remaining non-ancestor PRs: #305 (55 status entries), #237 (33), #221 (88), #154 (13), #153 (10), and #135 (3).
- Tmux-driven Claude read-only feasibility for #237 wrote `/tmp/luce-claude-20260531-043408-pr237-report.txt` but exited with max-turns before producing useful content.
- Tmux-driven Codex read-only feasibility for #237 wrote `/tmp/luce-codex-20260531-043408-pr237-report.txt` (739 KiB) and completed with a concise report recommending a sliced current-layout port.
- Validation for this documentation-only refresh: `git diff --check -- docs/auto-integration.md` passed.
- Final containment check confirmed `origin/main` and 21 included current PR heads are ancestors of `HEAD`; the remaining non-ancestor PRs are #305, #237, #221, #154, #153, and #135.

## Pending / blocked-needs-human / selective-port candidates

| PR | Head branch | Head | Current status | Probe result / next useful action |
|---:|---|---:|---|---|
| #305 | `layersplit_refactor` | `1de45e4d` | selective salvage only / human-scale | Fresh direct merge still conflicts across 29 files. `git cherry` still shows 21 patch-equivalent commits and 10 patch-unique commits covering common MoE hybrid extraction, routed FFN cached graphs, GPU-resident `act_cur` and async logits, Laguna hot/cold placement and `DFLASH_EXPERT_BUDGET_PCT`, dynamic placement logs/auto-placement, and no-sub-batch reused-`gallocr` behavior. Do not direct-merge; selectively port desired Laguna/common-MoE behavior into current `server/` layout while preserving current qwen35moe pipeline, Laguna layer-split adapter, backend precision policy, IPC payload transport, and harness/Docker layout. |
| #237 | `feat/dflash-mtp-foundation` | `02c6a6c4` | salvage-port candidate / human-scale server-layout port | Fresh probe still conflicts across 24 old `dflash/` and current `server/` files including CMake, backend factory, common MTP interfaces, Qwen35 graph/loader/backend, and tests. Current `HEAD` still lacks the #237 native MTP surface (`MtpSource`, `mtp-source`, `mtp-gguf`, `mtp_gamma`, `supports_mtp`) while #237 adds generic MTP interfaces/runner/orchestrator, Qwen35 MTP module files, hidden-state capture, server flags, and tests. Do not direct-merge; port as donor slices: generic `server/` MTP interface/runner/orchestrator and `test_common_mtp_orchestrator`, Qwen35 MTP module files, minimal target hidden-capture wiring, backend wiring, then current C++ server CLI flags. Preserve current remote draft IPC, empty-spec AR fallback, budget hooks, qwen35moe subclass hooks, and newer `model_backend.h` fields. |
| #135 | `xabicasa/dflash-multi-request-scheduler-batched-target-step` | `561b0ac1` | selective-port candidate / high risk | Fresh direct probe still conflicts in `server/src/internal.h`, `server/src/qwen35/qwen35_target_graph.cpp`, and `server/test/test_dflash.cpp`. The branch is one old-layout commit and should be salvaged as small current-layout slices: request/slot structs and tagged framing, aligned bucket scheduler protocol, batched cache/`n_seqs` graph plumbing, then batch probe/target step. Keep graph changes in `qwen35_target_graph.cpp`/`graph_builders.{h,cpp}`, port only scheduler-specific daemon pieces into `test_dflash.cpp`, and gate initial `n_seqs > 1` support away from tree mode, rollback capture, MoE routing, and unsupported cache shapes. |
| #154 | `xabicasa/dflash-mtp-speculative-loop` | `2f4ede79` | blocked-needs-human / dependency | Fresh probe conflicts in 12 old/current MTP docs, `dflash/CMakeLists.txt`, CUDA/internal/Qwen35 graph/loader files, and MTP smoke/contract tests. Mine linear MTP decode semantics after current-layout #237-equivalent Qwen35 MTP exists. |
| #153 | `xabicasa/dflash-mtp-integrated` | `e9b17cb1` | blocked-needs-human / dependency | Fresh probe conflicts in 10 old/current MTP docs, `dflash/CMakeLists.txt`, CUDA/internal/Qwen35 graph/loader files, and MTP smoke/contract tests. Mine loader/graph/cache/test ideas after current-layout #237-equivalent Qwen35 MTP exists. |

## Suggested close / superseded

| PR | Head branch | Head | Current status | Evidence / suggested action |
|---:|---|---:|---|---|
| #221 | `feat/mtp-prefix-warm-ghost` | `05502974` | superseded for direct integration; mine only after #237 | Fresh direct-merge probe still conflicts across 23 old/current files. The branch is older/broader than #237 and mixes early MTP, prefix-cache warm-hit, PFlash dispatcher/protocol, benches, and docs; #237 remains the better MTP foundation salvage base. |

## Draft / excluded

Draft PRs remain outside the primary non-draft integration target except for dependency awareness: #312, #304, #291, #290, #275, #249, and #193. Draft #312's backend IPC payload transport is related to already-carried IPC payload work, but remains draft/excluded. Draft #304 may touch compaction behavior and should be watched if it becomes ready.

## Retained worktrees / logs

This run retained the updated stack worktree, fresh conflicted probe worktrees, and agent transcripts for audit; earlier conflicted probe worktrees remain from prior runs because safe cleanup is left to a supervised pass:

- `/tmp/luce-auto-cron-20260531-043408` (manifest refresh worktree)
- `/tmp/luce-probe-20260531-043408-pr-305`
- `/tmp/luce-probe-20260531-043408-pr-237`
- `/tmp/luce-probe-20260531-043408-pr-221`
- `/tmp/luce-probe-20260531-043408-pr-154`
- `/tmp/luce-probe-20260531-043408-pr-153`
- `/tmp/luce-probe-20260531-043408-pr-135`
- `/tmp/luce-probe-20260531-043408-pr305-merge.log`
- `/tmp/luce-probe-20260531-043408-pr237-merge.log`
- `/tmp/luce-probe-20260531-043408-pr221-merge.log`
- `/tmp/luce-probe-20260531-043408-pr154-merge.log`
- `/tmp/luce-probe-20260531-043408-pr153-merge.log`
- `/tmp/luce-probe-20260531-043408-pr135-merge.log`
- `/tmp/luce-claude-20260531-043408-pr237-report.txt` (Claude max-turns failure)
- `/tmp/luce-codex-20260531-043408-pr237-report.txt` (large Codex inspection transcript with concise final recommendation)

Prior retained worktrees/logs for conflicted/superseded probes and earlier refreshes include `/tmp/luce-auto-cron-20260531-041107`, `/tmp/luce-probe-20260531-041107-pr-305`, `/tmp/luce-probe-20260531-041107-pr-237`, `/tmp/luce-probe-20260531-041107-pr-221`, `/tmp/luce-probe-20260531-041107-pr-154`, `/tmp/luce-probe-20260531-041107-pr-153`, `/tmp/luce-probe-20260531-041107-pr-135`, `/tmp/luce-claude-20260531-041107-pr237-report.txt`, `/tmp/luce-codex-20260531-041107-pr237-report.txt`, `/tmp/luce-pr274-merge-20260531-041107.log`, `/tmp/luce-auto-cron-20260531-035529`, `/tmp/luce-probe-20260531-035529-pr-305`, `/tmp/luce-probe-20260531-035529-pr-237`, `/tmp/luce-probe-20260531-035529-pr-221`, `/tmp/luce-probe-20260531-035529-pr-154`, `/tmp/luce-probe-20260531-035529-pr-153`, `/tmp/luce-probe-20260531-035529-pr-135`, `/tmp/luce-claude-20260531-035529-pr237-report.txt`, `/tmp/luce-codex-20260531-035529-pr135-report.txt`, and earlier `/tmp/luce-auto-cron-*` / `/tmp/luce-probe-*` audit worktrees.

## Notes

The next useful integration work is still a dedicated current-`server/` #237 MTP foundation selective port, starting with generic MTP interface/runner/orchestrator plus `test_common_mtp_orchestrator`, then Qwen35 native MTP module files, minimal target hidden-capture wiring, backend wiring, and current C++ server CLI flags. #153/#154 should be mined afterward for linear MTP decode semantics, and #221 only for any still-missing prefix-warm ideas. #305 is the other high-value human-scale port, but only as selective salvage of the 10 patch-unique commits after reconciling with current qwen35moe pipeline and Laguna layer-split code. Keep #135 as a separate scheduler/batched-target selective port split into small current-layout changes: request/slot structs and tagged framing, aligned bucket scheduler protocol, batched cache/`n_seqs` graph plumbing, then batch probe/target step, with early `n_seqs > 1` gated away from tree mode, rollback capture, MoE routing, and unsupported cache shapes. #137, #48, and #94 are now represented by superseding current-layout code and can be closed or retargeted only if authors can identify a minimal missing delta.
