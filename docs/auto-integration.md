# Auto-integration manifest

Repository: `Luce-Org/lucebox-hub`
Integration branch: `auto-integration`
Writable remote: `easel`
Upstream remote: `origin` / `Luce-Org`
Last refresh: `2026-05-31T07:08:04-04:00`
Current base: `origin/main` `8305b6c2`
Previous integration tip: `easel/auto-integration` `c4ac87a5`
Current integration tip before push: `e97aca57`

This branch is maintained as a reproducible patch stack over `origin/main`. This unattended run started from a clean primary checkout on `auto-integration`, verified GitHub/Claude/Codex auth using the real user credential home, fetched `origin` and `easel` separately, fetched current non-draft PR heads, and checked exact PR-head containment against the stack tip.

The current stack still contains 20 exact current open non-draft PR heads and carries selective salvage from two remaining non-ancestor PRs: #305's `DFLASH_EXPERT_BUDGET_PCT` cap for current Qwen35MoE dynamic expert placement, and #135's capture-free `n_seqs` target-graph/cache plumbing for current qwen35 prefill-only probe work. There are currently 26 open non-draft PRs and 8 draft/excluded PRs. The remaining 6 non-draft PRs are still old conflict/selective-port candidates by exact-head ancestry (#305, #237, #221, #154, #153, and #135), but #305 and #135 are now partially represented beyond their already-carried broad themes. This refresh found no new ready non-draft PR heads to add; fresh worktree probes were run for all remaining non-ancestors. Claude port delegation for #135 reached max turns without changes; tmux-driven Codex then implemented the minimal two-file #135 slice and reported it as prefill-only, capture-free plumbing with runtime validation still required before scheduler/copyback follow-up.

## Included in the current non-draft stack

| PR | Head branch | Head | State | Notes |
|---:|---|---:|---|---|
| #319 | `codex/pr314-restore-default` | `a079a4b1` | included | Adds default empty-spec-decode retry through backend wrapper methods so successful zero-token speculative paths retry once via AR decode while preserving timing/metadata. |
| #316 | `fix/issue-233` | `d28eb1fb` | included | Captures daemon stderr in `DflashClient` error messages by redirecting child stderr to stdout for both Windows and POSIX subprocess launches. |
| #315 | `codex/dflash-spec-tool-recovery` | `3ba401f0` | included | Recovers spec-decode agent stalls with env-gated tool-prefix floor injection, bounded residual stall/repetition guards, invalid draft-seed AR fallback, and qwen35 empty-output / C2 `fa_window` AR fallbacks. |
| #310 | `feat-backend-activation-precision-policy-after-306` | `bf9f4b57` | included | Backend activation precision policy / graph tensor precision helpers are carried exactly. |
| #309 | `experiment-dflash-feature-dtype` | `ea6ac481` | included | Feature mirror dtype policy is carried exactly. |
| #308 | `fix/qwen-think-channel` | `9d4defe1` | included | Qwen3.6/Laguna think-mode reasoning is routed to `reasoning_content`; stack carries the replay HTTP stub harness and regression scenarios exactly. |
| #306 | `refactor-server-layer-split-runtime` | `988fc933` | included | Shared layer-split runtime helper extraction is carried exactly. |
| #297 | `feat-server-laguna-layer-split-adapter-v2` | `53dd1686` | included | Laguna target-layer-split adapter is carried exactly. |
| #295 | `fix-layer-split-sampling` | `a9aedf7d` | included | Target layer-split sampling support is carried exactly. |
| #294 | `feat/server-passthrough-proxy` | `48f6962d` | included | Passthrough proxy, keep-ratio curve, query survival checks, multimodal text extraction, and unit coverage are carried exactly. |
| #289 | `pipeline_moe` | `caf2b112` | included | Carries pipelined hybrid Qwen35 MoE decode plus the sub-batch hybrid prefill FFN safety fix. |
| #285 | `feat/lucebox-docker` | `060492e4` | included | Docker stack / `lucebox` CLI / harness / `luce-bench`, Bragi sweep docs, autotune/sweep updates, shell harness tests, long-context grader coverage, GPU-power-throttle notes, luce-bench grader fixes, and think-vs-nothink baseline summary are carried exactly. |
| #276 | `fix/qwen36-claude-code-tool-calling` | `5e861b4d` | included | Qwen3.6-27B tool-calling fix for Claude-code Anthropic path is carried exactly. |
| #274 | `feat/pflash-drafter-ee7` | `8fc961b5` | included | Adaptive pFlash composition, effective-size admission/keep-ratio guard, and opt-in pFlash regime router are carried with current stack conflict resolutions preserved. |
| #266 | `feat/harness-typed-adapters` | `17525eae` | included | Typed harness adapters and format-aware session-inject proxy are carried exactly. |
| #152 | `main` | `cf735bee` | included | Gemma 4 RTX 4090 backend helpers are carried exactly. |
| #142 | `xabicasa/dflash-safetensors-draft-fp16` | `f2fbf62f` | included | FP16 safetensors drafter support is carried exactly. |
| #137 | `xabicasa/dflash-build-cmake-sm89-bsa` | `297fc74e` | included / superseded | Merged by preserving deletion of retired `dflash/CMakeLists.txt`; current `server/CMakeLists.txt` already handles user CUDA architectures and BSA defaults. |
| #94 | `feat/dflash-qwen36-swa-draft` | `d2f9c9dd` | included / superseded | Recorded with an `ours` merge because the current tree already has SWA draft support (`DraftLayer::is_swa`, `DraftWeights::swa_window`, safetensors SWA metadata parsing, SWA-aware draft masks, and GGUF SWA metadata support). |
| #48 | `fix/consumer-blackwell-auto-detect` | `858b84b6` | included / superseded | Merged by preserving deletion of retired `dflash/CMakeLists.txt`; current `server/CMakeLists.txt` already conditionally handles Blackwell/CUDA-version flags. |

Closed, upstreamed, or no-longer-open PRs still represented by the stack/base include #317, #314, #313, #311, #307, #303, #302, #301, #300, #299, #298, and #292.

## Validation run

This run performed:

- `date -Is` -> `2026-05-31T06:48:32-04:00` during preflight.
- `date -Is` -> `2026-05-31T07:08:04-04:00` for the manifest/source refresh.
- Primary checkout preflight: `git status --short` was clean on `auto-integration`; remotes were `origin=https://github.com/Luce-Org/lucebox-hub` and `easel=https://github.com/easel/lucebox-hub`.
- Auth/tooling checks with real user credentials succeeded: `gh auth status`, `claude auth status --text`, and `codex --version` (`codex-cli 0.130.0`).
- `git fetch --prune origin` and `git fetch --prune easel` completed successfully.
- Current open PR enumeration reported 26 non-draft PRs and 8 draft/excluded PRs.
- Explicit fetch of all open non-draft PR heads succeeded.
- Exact-head containment before reconciliation showed #319, #316, #315, #310, #309, #308, #306, #297, #295, #294, #289, #285, #276, #274, #266, #152, #142, #137, #94, and #48 were ancestors of `easel/auto-integration`; #305, #237, #221, #154, #153, and #135 were non-ancestors by exact PR-head ancestry.
- A reconcile worktree from `easel/auto-integration` was created at `/tmp/luce-auto-cron-20260531-064912`; `origin/main` was already up to date.
- Fresh direct-merge probes on top of `c4ac87a5` reconfirmed current conflict/status counts for the remaining non-ancestor PRs: #305 (55 status entries), #237 (33), #221 (88), #154 (13), #153 (10), and #135 (3).
- Tmux-driven Claude read-only review of #135 reached max turns without a useful report (`/tmp/luce-claude-pr135-064912.txt`); tmux-driven Codex read-only review completed and identified a small manual salvage slice: capture-free qwen35 `n_seqs` target graph/cache plumbing while leaving scheduler/copyback commands out (`/tmp/luce-codex-pr135-064912.txt`).
- Tmux-driven Claude port delegation for #135 reached max turns without file changes (`/tmp/luce-claude-pr135-port-064912.txt`); tmux-driven Codex implemented the minimal two-file port in `/tmp/luce-port-pr135-batched-probe-064912` and it was cherry-picked into the stack as `e97aca57`.
- Validation for this source/doc refresh: `git diff --check`, conflict-marker scan of the touched qwen35 source/header, and CMake configure attempt. CMake failed during CUDA compiler identification because local nvcc/CMake selected unsupported `sm_52` before project compilation (`ptxas fatal: Value 'sm_52' is not defined`), matching the known local toolchain blocker; compiled tests/runtime batched-probe validation were not run.

## Pending / blocked-needs-human / selective-port candidates

| PR | Head branch | Head | Current status | Probe result / next useful action |
|---:|---|---:|---|---|
| #305 | `layersplit_refactor` | `1de45e4d` | partial selective salvage / human-scale | Fresh direct merge still conflicts heavily (55 status entries) and Codex review reconfirmed direct merge would regress large current stack areas. This run ported the small `DFLASH_EXPERT_BUDGET_PCT` control-plane cap into current Qwen35MoE dynamic expert placement. Much of the broad PR is already represented by current layer-split runtime, Qwen35MoE hybrid machinery, IPC payload/feature range streaming, backend precision fallback, safetensors config validation, SWA flags, and server signal handling. Remaining high-value slices: Qwen35MoE gallocr reuse / remove `kFfnSafeBatch`; larger Laguna hot/cold MoE hybrid prefill/dynamic placement only if Laguna XS.2 residency remains a target. |
| #237 | `feat/dflash-mtp-foundation` | `02c6a6c4` | salvage-port candidate / human-scale server-layout port | Fresh probe still conflicts across old `dflash/` and current `server/` files. Prior Claude read-only review confirms direct merge is not viable: clean added files still require current-layout base hooks (`supports_mtp`, `mtp`, `dflash_target`, `last_hidden`, chain restore/capture, tree verify, etc.). Port order: MTP interface/metadata headers, base virtuals, `mtp_chain_runner`, `mtp_orchestrator`, Qwen35 MTP module/graph/loader, current CMake wiring, then tests. |
| #135 | `xabicasa/dflash-multi-request-scheduler-batched-target-step` | `561b0ac1` | partial selective salvage / high risk | Fresh direct probe still conflicts only in `server/src/internal.h`, `server/src/qwen35/qwen35_target_graph.cpp`, and `server/test/test_dflash.cpp`. This run ported the smallest current-layout slice: defaulted `n_seqs` graph/cache parameters, prefill-only batched cache allocation, qwen35 attention/DeltaNet shape plumbing, and guards rejecting rollback capture, tree parent IDs, MoE-router capture, target feature capture, q-tail capture, and last-token-only logits for `n_seqs > 1`. Remaining unique semantics to port in later slices: request/slot structs and tagged framing, aligned bucket scheduler protocol, batch cache validation/copyback, batched target argmax command path, CUDA widening rollback, TQ3 rotation cleanup, and debug/EOS controls. Runtime validation of the batched probe is still needed before enabling scheduler/copyback paths. |
| #154 | `xabicasa/dflash-mtp-speculative-loop` | `2f4ede79` | blocked-needs-human / dependency | Fresh probe conflicts in old/current MTP docs, `dflash/CMakeLists.txt`, CUDA/internal/Qwen35 graph/loader files, and MTP smoke/contract tests. Mine linear MTP decode semantics only after a current-layout #237-equivalent Qwen35 MTP foundation exists. |
| #153 | `xabicasa/dflash-mtp-integrated` | `e9b17cb1` | blocked-needs-human / dependency | Fresh probe conflicts in old/current MTP docs, `dflash/CMakeLists.txt`, CUDA/internal/Qwen35 graph/loader files, and MTP smoke/contract tests. Mine loader/graph/cache/test ideas after current-layout #237-equivalent Qwen35 MTP exists. |

## Suggested close / superseded

| PR | Head branch | Head | Current status | Evidence / suggested action |
|---:|---|---:|---|---|
| #221 | `feat/mtp-prefix-warm-ghost` | `05502974` | superseded for direct integration; mine only after #237 | Fresh direct-merge probe still conflicts across old/current files. The branch is older/broader than #237 and mixes early MTP, prefix-cache warm-hit, PFlash dispatcher/protocol, benches, and docs; #237 remains the better MTP foundation salvage base. |

## Draft / excluded

Draft PRs remain outside the primary non-draft integration target except for dependency awareness: #320, #312, #304, #291, #290, #275, #249, and #193. Draft #320 is an easel branch for plain-text tool-call synthesis and is conflicting against main; watch it but exclude while draft. Draft #312's backend IPC payload transport is related to already-carried IPC payload work, but remains draft/excluded. Draft #304 may touch compaction behavior and should be watched if it becomes ready.

## Retained worktrees / logs

This run retained the updated stack worktree, conflicted probe worktrees, and agent transcripts for audit; earlier conflicted probe worktrees remain from prior runs because safe cleanup is left to a supervised pass:

- `/tmp/luce-auto-cron-20260531-064912` (source/doc refresh worktree)
- `/tmp/luce-probe-luce-auto-cron-20260531-064912-pr-305`
- `/tmp/luce-probe-luce-auto-cron-20260531-064912-pr-237`
- `/tmp/luce-probe-luce-auto-cron-20260531-064912-pr-221`
- `/tmp/luce-probe-luce-auto-cron-20260531-064912-pr-154`
- `/tmp/luce-probe-luce-auto-cron-20260531-064912-pr-153`
- `/tmp/luce-probe-luce-auto-cron-20260531-064912-pr-135`
- `/tmp/luce-port-pr135-batched-probe-064912` (successful #135 selective-port worktree)
- `/tmp/luce-claude-pr135-064912.txt` (max-turns with no useful read-only report)
- `/tmp/luce-codex-pr135-064912.txt` (usable read-only feasibility review)
- `/tmp/luce-claude-pr135-port-064912.txt` (max-turns with no file changes)
- `/tmp/luce-codex-pr135-port-064912.txt` (usable port transcript)
- `/tmp/luce-build-pr135-064912` (failed local CMake configure due CUDA compiler-id `sm_52` toolchain issue)
- `/tmp/luce-auto-cron-20260531-063024` and its probe/log set from the previous #305 PCT refresh
- `/tmp/luce-auto-cron-20260531-060921` and its probe/log set from the previous refresh
- `/tmp/luce-auto-cron-20260531-051332` and its probe/log set from the previous #237/#135 feasibility refresh

## Notes

The next useful integration work is a dedicated selective port, not another direct merge. Highest-value candidates are now: (1) #305's Qwen35MoE gallocr reuse / `kFfnSafeBatch` removal; (2) #237 current-`server/` MTP foundation; (3) #135 runtime validation for the newly ported batched target-graph probe, followed by request/slot tagged framing and scheduler/copyback slices if validation passes; and (4) #305's larger Laguna hot/cold MoE hybrid path if Laguna XS.2 residency is still desired. For #237, start with generic MTP interface/runner/orchestrator plus `test_common_mtp_orchestrator`, then Qwen35 native MTP module files, minimal target hidden-capture wiring, backend wiring, and current C++ server CLI flags. #153/#154 should be mined afterward for linear MTP decode semantics, and #221 only for any still-missing prefix-warm ideas. #137, #48, and #94 are represented by superseding current-layout code and can be closed or retargeted only if authors can identify a minimal missing delta.
