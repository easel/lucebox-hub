# Auto-integration manifest

Repository: `Luce-Org/lucebox-hub`
Integration branch: `auto-integration`
Writable remote: `easel`
Upstream remote: `origin` / `Luce-Org`
Last refresh: `2026-05-31T05:35:31-04:00`
Current base: `origin/main` `8305b6c2`
Previous integration tip: `easel/auto-integration` `d7d0b9c9`
Current integration tip before push: `83a2965b`

This branch is maintained as a reproducible patch stack over `origin/main`. This unattended run started from a clean primary checkout on `auto-integration`, verified GitHub/Claude/Codex auth using the real user credential home, fetched `origin` and `easel` separately, fetched current non-draft PR heads, and checked exact PR-head containment against the stack tip.

This refresh merged ready PR #319 into the integration stack, resolving the qwen35moe conflict by preserving the current `generate_impl` / `restore_and_generate_impl` wrapper semantics while adding the common empty-spec-decode AR retry fallback. There are currently 26 open non-draft PRs and 7 draft/excluded PRs. The stack contains 20 of the 26 current open non-draft PR heads exactly; the same 6 old conflict/selective-port candidates remain non-ancestors (#305, #237, #221, #154, #153, and #135). Fresh worktree probes and tmux-driven agent attempts were run again for the remaining candidates before retaining their blocked/selective-port status.

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

- `date -Is` -> `2026-05-31T05:31:21-04:00` during preflight.
- Primary checkout preflight: `git status --short` was clean on `auto-integration`; remotes were `origin=https://github.com/Luce-Org/lucebox-hub` and `easel=https://github.com/easel/lucebox-hub`.
- Auth/tooling checks with real user credentials succeeded: `gh auth status`, `claude auth status --text`, and Codex help smoke check.
- `git fetch --prune origin` and `git fetch --prune easel` completed successfully.
- Current open PR enumeration reported 26 non-draft PRs and 7 draft/excluded PRs.
- Explicit fetch of all open non-draft PR heads succeeded.
- Exact-head containment before reconciliation showed #316, #315, #310, #309, #308, #306, #297, #295, #294, #289, #285, #276, #274, #266, #152, #142, #137, #94, and #48 were ancestors of `easel/auto-integration`; #319, #305, #237, #221, #154, #153, and #135 were non-ancestors.
- A reconcile worktree from `easel/auto-integration` was created at `/tmp/luce-auto-cron-20260531-053202`; `origin/main` was already an ancestor of `easel/auto-integration`.
- PR #319 was merged in the reconcile worktree; the only conflicts were `server/src/qwen35moe/qwen35moe_backend.cpp` and `.h`, resolved by keeping current virtual method names (`generate_impl` / `restore_and_generate_impl`) and current MoE-hybrid predicate (`target_weights().moe_hybrid`) while adopting the backend-level empty-spec retry wrapper changes.
- Fresh direct-merge probes on top of `83a2965b` reconfirmed current conflict/status counts for the pre-existing remaining non-ancestor PRs: #305 (large multi-area conflict set), #237 (33 status entries), #221 (old-layout MTP/prefix-cache conflict set), #154 (13), #153 (10), and #135 (3).
- Tmux-driven Claude read-only attempts for #135 and #305 produced empty redirected reports and blank panes, so the sessions were stopped and not used as evidence.
- Tmux-driven Codex read-only review for #135 produced a large transcript at `/tmp/luce-codex-135-053202.txt` but was stopped after streaming conflicted file excerpts without a final recommendation; manual inspection still confirms #135 remains a small but high-risk scheduler/target-graph selective port rather than a direct merge.
- Validation for this refresh: `git diff --check` passed before committing the #319 conflict resolution; `cmake -S server -B /tmp/luce-auto-cron-20260531-053202-build -DCMAKE_BUILD_TYPE=Release -DCMAKE_CUDA_ARCHITECTURES=89` was attempted but the local CUDA compiler-id step failed before project configure with the known `ptxas fatal: Value 'sm_52' is not defined` environment/toolchain blocker; post-doc `git diff --check` and conflict-marker scans are listed in the final run report.

## Pending / blocked-needs-human / selective-port candidates

| PR | Head branch | Head | Current status | Probe result / next useful action |
|---:|---|---:|---|---|
| #305 | `layersplit_refactor` | `1de45e4d` | selective salvage only / human-scale | Fresh direct merge still conflicts heavily. Prior Codex review found the first 21 PR commits patch-equivalent in `HEAD`, leaving 10 unique MoE/Laguna hybrid-prefill commits. Selectively port only current-layout MoE/Laguna hybrid-prefill work while preserving current layer-split runtime, IPC payload transport, backend precision, force-AR/spec-decode telemetry, CPU sampling, snapshot logits, CMake/test wiring, qwen35moe pipeline, Laguna adapter, Docker/harness layout. |
| #237 | `feat/dflash-mtp-foundation` | `02c6a6c4` | salvage-port candidate / human-scale server-layout port | Fresh probe still conflicts across old `dflash/` and current `server/` files. Claude read-only review confirms direct merge is not viable: clean added files still require current-layout base hooks (`supports_mtp`, `mtp`, `dflash_target`, `last_hidden`, chain restore/capture, tree verify, etc.). Port order: MTP interface/metadata headers, base virtuals, `mtp_chain_runner`, `mtp_orchestrator`, Qwen35 MTP module/graph/loader, current CMake wiring, then tests. |
| #135 | `xabicasa/dflash-multi-request-scheduler-batched-target-step` | `561b0ac1` | selective-port candidate / high risk | Fresh direct probe still conflicts only in `server/src/internal.h`, `server/src/qwen35/qwen35_target_graph.cpp`, and `server/test/test_dflash.cpp`, but the donor branch is one old-layout commit embedded in a broad historical tree move. Manual/Codex-aided review shows the unique semantics are request/slot structs and tagged framing, aligned bucket scheduler protocol, batched cache/`n_seqs` graph plumbing, batched target argmax, copyback validation, and test daemon wiring. Port as small slices, gating initial `n_seqs > 1` away from tree mode, rollback capture, MoE routing, and unsupported cache shapes. |
| #154 | `xabicasa/dflash-mtp-speculative-loop` | `2f4ede79` | blocked-needs-human / dependency | Fresh probe conflicts in old/current MTP docs, `dflash/CMakeLists.txt`, CUDA/internal/Qwen35 graph/loader files, and MTP smoke/contract tests. Mine linear MTP decode semantics only after a current-layout #237-equivalent Qwen35 MTP foundation exists. |
| #153 | `xabicasa/dflash-mtp-integrated` | `e9b17cb1` | blocked-needs-human / dependency | Fresh probe conflicts in old/current MTP docs, `dflash/CMakeLists.txt`, CUDA/internal/Qwen35 graph/loader files, and MTP smoke/contract tests. Mine loader/graph/cache/test ideas after current-layout #237-equivalent Qwen35 MTP exists. |

## Suggested close / superseded

| PR | Head branch | Head | Current status | Evidence / suggested action |
|---:|---|---:|---|---|
| #221 | `feat/mtp-prefix-warm-ghost` | `05502974` | superseded for direct integration; mine only after #237 | Fresh direct-merge probe still conflicts across old/current files. The branch is older/broader than #237 and mixes early MTP, prefix-cache warm-hit, PFlash dispatcher/protocol, benches, and docs; #237 remains the better MTP foundation salvage base. |

## Draft / excluded

Draft PRs remain outside the primary non-draft integration target except for dependency awareness: #312, #304, #291, #290, #275, #249, and #193. Draft #312's backend IPC payload transport is related to already-carried IPC payload work, but remains draft/excluded. Draft #304 may touch compaction behavior and should be watched if it becomes ready.

## Retained worktrees / logs

This run retained the updated stack worktree, conflicted probe worktrees, and agent transcripts for audit; earlier conflicted probe worktrees remain from prior runs because safe cleanup is left to a supervised pass:

- `/tmp/luce-auto-cron-20260531-053202` (#319 merge/docs worktree)
- `/tmp/luce-auto-cron-20260531-053202-pr-305`
- `/tmp/luce-auto-cron-20260531-053202-pr-237`
- `/tmp/luce-auto-cron-20260531-053202-pr-221`
- `/tmp/luce-auto-cron-20260531-053202-pr-154`
- `/tmp/luce-auto-cron-20260531-053202-pr-153`
- `/tmp/luce-auto-cron-20260531-053202-pr-135`
- `/tmp/luce-claude-135-053202.txt` (empty, unusable)
- `/tmp/luce-claude-305-053202.txt` (empty, unusable)
- `/tmp/luce-codex-135-053202.txt` (large transcript, no final recommendation)
- `/tmp/luce-auto-cron-20260531-051332` (previous manifest/base-refresh worktree)
- `/tmp/luce-probe-20260531-051332-pr-305`
- `/tmp/luce-probe-20260531-051332-pr-237`
- `/tmp/luce-probe-20260531-051332-pr-221`
- `/tmp/luce-probe-20260531-051332-pr-154`
- `/tmp/luce-probe-20260531-051332-pr-153`
- `/tmp/luce-probe-20260531-051332-pr-135`
- `/tmp/luce-claude-20260531-051332-pr237-report.txt` (max-turns, unusable)
- `/tmp/luce-claude-20260531-051332-pr237b-report.txt` (usable read-only #237 feasibility)
- `/tmp/luce-codex-20260531-051332-pr135-report.txt` (interrupted before final recommendation)

## Notes

The next useful integration work is a dedicated selective port, not another direct merge. Highest-value candidates are #237 current-`server/` MTP foundation and #305's 10 unique MoE/Laguna tail commits. For #237, start with generic MTP interface/runner/orchestrator plus `test_common_mtp_orchestrator`, then Qwen35 native MTP module files, minimal target hidden-capture wiring, backend wiring, and current C++ server CLI flags. For #305, port the common MoE extraction and Laguna hybrid-prefill features in small slices while preserving current IPC/layer-split/runtime/test wiring. #153/#154 should be mined afterward for linear MTP decode semantics, and #221 only for any still-missing prefix-warm ideas. Keep #135 as a separate scheduler/batched-target selective port split into small current-layout changes: request/slot structs and tagged framing, aligned bucket scheduler protocol, batched cache/`n_seqs` graph plumbing, then batch probe/target step, with early `n_seqs > 1` gated away from tree mode, rollback capture, MoE routing, and unsupported cache shapes. #137, #48, and #94 are represented by superseding current-layout code and can be closed or retargeted only if authors can identify a minimal missing delta.
