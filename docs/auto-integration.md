# Auto-integration manifest

Repository: `Luce-Org/lucebox-hub`
Integration branch: `auto-integration`
Writable remote: `easel`
Upstream remote: `origin` / `Luce-Org`
Last refresh: `2026-05-31T10:16:00-04:00`
Current base: `origin/main` `8305b6c2`
Previous integration tip: `easel/auto-integration` `a3ef342f`
Current integration source tip before this refresh: `a3ef342f`

This branch is maintained as a reproducible patch stack over `origin/main`. This unattended run started from a clean primary checkout on `auto-integration`, verified GitHub/Claude/Codex auth using the real user credential home, fetched `origin` and `easel` separately, fetched current non-draft PR heads, and checked exact PR-head containment against the stack tip.

The current stack contains 21 exact current open non-draft PR heads and carries selective salvage from three remaining non-ancestor PRs: #305's `DFLASH_EXPERT_BUDGET_PCT` cap for current Qwen35MoE dynamic expert placement, #237's common MTP interface/chain-runner/orchestrator foundation, and #135's capture-free `n_seqs` target-graph/cache plumbing, request-tagged daemon stream framing, and batched target-feature capture buffer plumbing for current qwen35 work. There are currently 27 open non-draft PRs and 8 draft/excluded PRs. The remaining 6 non-draft PRs are still old conflict/selective-port candidates by exact-head ancestry (#305, #237, #221, #154, #153, and #135), but #305, #237, and #135 are now partially represented beyond their already-carried broad themes. This refresh found no new non-draft PR heads and no upstream `origin/main` advance. Fresh direct-merge probes were rerun for all remaining non-ancestors on top of `a3ef342f`; conflict counts remained unchanged. A tmux-driven Codex attempt against #135 inspected the three conflicted current-layout files and started conflict-marker cleanup, but did not produce a usable narrow port or complete conflict resolution, so no source changes were promoted to the integration stack. The next safe #135 order remains: multi-cache-slot scaffolding, then scheduler state/introspection, then diagnostic-only batch probing before live copyback/target-step mutation.

## Included in the current non-draft stack

| PR | Head branch | Head | State | Notes |
|---:|---|---:|---|---|
| #322 | `status_html` | `7f8eb2e` | included | Adds real-time `/status` dashboard assets, SSE plumbing, server status registry, and inference observer callbacks; conflict with the #237 MTP hook in `model_backend.h` was resolved by preserving both callback types. |
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
| #285 | `feat/lucebox-docker` | `deb5adba` | included | Docker stack / `lucebox` CLI / harness / `luce-bench`, Bragi sweep docs, autotune/sweep updates, shell harness tests, long-context grader coverage, GPU-power-throttle notes, luce-bench grader fixes, think-vs-nothink baseline summary, and Forge grader tests are carried exactly. |
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

- `date -Is` -> `2026-05-31T08:55:37-04:00` during preflight.
- `date -Is` -> `2026-05-31T09:06:53-04:00` for this manifest/code refresh.
- Primary checkout preflight: `git status --short` was clean on `auto-integration`; remotes were `origin=https://github.com/Luce-Org/lucebox-hub` and `easel=https://github.com/easel/lucebox-hub`.
- Auth/tooling checks with real user credentials succeeded: `gh auth status`, `claude auth status --text`, and `codex --version` (`codex-cli 0.130.0`).
- `git fetch --prune origin` and `git fetch --prune easel` completed successfully.
- Open PR enumeration reported 27 non-draft PRs and 8 draft/excluded PRs.
- Explicit fetch of all open non-draft PR heads succeeded.
- Exact-head containment before reconciliation showed #322, #319, #316, #315, #310, #309, #308, #306, #297, #295, #294, #289, #285, #276, #274, #266, #152, #142, #137, #94, and #48 were ancestors of `easel/auto-integration`; #305, #237, #221, #154, #153, and #135 were non-ancestors by exact PR-head ancestry.
- A reconcile worktree from `easel/auto-integration` was created at `/tmp/luce-auto-cron-20260531-0856`; `origin/main` was already up to date.
- Fresh direct-merge probes on top of `b69f2e14` reconfirmed current conflict/status counts for the remaining non-ancestor PRs: #305 (56 status entries), #237 (33), #221 (88), #154 (13), #153 (10), and #135 (3).
- Tmux-driven Claude delegation for the next #135 slice was started in `/tmp/luce-port-pr135-next-0856`; it exited with `Error: Reached max turns (12)` and no file changes.
- Tmux-driven Codex delegation in `/tmp/luce-port-pr135-codex-next-0856` identified a tiny safe #135 slice and produced a request-tagged stream framing patch in `server/test/test_dflash.cpp`: optional `REQ`/`REQUEST` daemon-line parsing, `--stream-tagged`/`--tagged-stream`, and token frames of `[-2, request_id, token]` while preserving legacy one-int streaming by default. Codex explicitly deferred batch cache copyback as still coupled to the unported multi-slot scheduler and batched target-feature layout.
- Validation for this refresh: `git diff --check` passed for the Codex draft diff and for the final stack diff. A standalone C++ parser smoke test compiled and ran the `REQ`/`REQUEST` prefix parser cases after an orchestrator fix to check `REQUEST` before the shorter `REQ` prefix. Full CMake validation was not rerun because this local checkout still lacks populated `server/deps/llama.cpp` and the known CUDA compiler-id `sm_52` toolchain blocker remains for full project configure.
- `date -Is` -> `2026-05-31T09:20:52-04:00` during this follow-up preflight; primary checkout was clean on `auto-integration` at `255f35f2` and auth/tooling checks again succeeded using the real user credential home.
- Fresh direct-merge probes on top of `255f35f2` reconfirmed current conflict/status counts for the remaining non-ancestor PRs: #305 (56 status entries), #237 (33), #221 (88), #154 (13), #153 (10), and #135 (3).
- Tmux-driven Claude delegation for the next #135 slice in `/tmp/luce-port-pr135-next-092139` produced an empty redirected report and no file changes before being stopped as stuck.
- Tmux-driven Codex delegation in the same worktree drafted and applied a narrow #135 target-feature capture slice in `server/src/internal.h` and `server/src/qwen35/qwen35_target_graph.cpp`: single-sequence target feature buffers keep their 2D layout, batched caches allocate `[features, cap, n_seqs]`, batched graph capture checks dimensions instead of rejecting capture outright, and feature-copy views iterate per sequence.
- Validation for the follow-up slice: `git diff --check` passed for the Codex draft diff and final stack diff. Full CMake validation was not rerun because `server/deps/llama.cpp/ggml/include/ggml.h` is still absent in this checkout and the known CUDA compiler-id `sm_52` toolchain blocker remains for full project configure.
- `date -Is` -> `2026-05-31T09:41:32-04:00` during this refresh preflight; primary checkout was clean on `auto-integration` at `067cc77f` and auth/tooling checks again succeeded using the real user credential home.
- `git fetch --prune origin` and `git fetch --prune easel` completed successfully. Current refs were `origin/main` `8305b6c2` and `easel/auto-integration` `067cc77f`.
- Open PR enumeration again reported 27 non-draft PRs and 9 draft/excluded PRs.
- Exact-head containment after explicit PR ref fetch showed the same 21 open non-draft PR heads included and the same 6 non-ancestor selective-port candidates: #305, #237, #221, #154, #153, and #135.
- A reconcile worktree from `easel/auto-integration` was created at `/tmp/luce-auto-cron-20260531-094212`; `origin/main` was already up to date.
- Fresh direct-merge probes on top of `067cc77f` reconfirmed current conflict/status counts for the remaining non-ancestor PRs: #305 (56 status entries), #237 (33), #221 (88), #154 (13), #153 (10), and #135 (3).
- Tmux-driven Claude no-edit review for #135 in `/tmp/luce-port-pr135-validate-20260531-094212` exited with `Error: Reached max turns (8)` and no file changes.
- Tmux-driven Codex no-edit review for #135 in the same worktree completed and reported that the already-ported #135 pieces cover batched cache/graph foundation, unsafe-mode guards, batched `target_feat` storage/copy, and tagged stream framing. It identified missing high-value slices as multi target-cache slots, native request scheduler, batched command path, batch cache copyback/validation, and multiplexed completion semantics.
- Validation for this docs-only refresh: `git diff --check` passed. Full CMake validation was not rerun because no source code changed in this refresh and the known missing `server/deps/llama.cpp` / CUDA compiler-id environment blockers remain.
- Post-push re-enumeration found #285 had advanced from `060492e4` to `deb5adba` while this run was in progress; draft #320 was no longer open. A fresh worktree `/tmp/luce-auto-cron-20260531-0950-pr285` merged the new #285 head cleanly on top of `eb6d964f`, adding Forge grader scoring changes and `luce-bench/tests/test_forge_grader.py`.
- Validation after the #285 fast-follow merge: `git diff --check` passed, host `python3 -m pytest luce-bench/tests/test_forge_grader.py` could not run because the host Python lacked pytest, and `uv run --project luce-bench --extra dev pytest luce-bench/tests/test_forge_grader.py` passed (`16 passed`).
- `date -Is` -> `2026-05-31T10:02:59-04:00` during this refresh preflight; primary checkout was clean on `auto-integration` at `a3ef342f` and auth/tooling checks succeeded using the real user credential home (`gh auth status`, `claude auth status --text`, `codex --version`).
- `git fetch --prune origin` and `git fetch --prune easel` completed successfully. Current refs remained `origin/main` `8305b6c2` and `easel/auto-integration` `a3ef342f`.
- Open PR enumeration reported 27 non-draft PRs and 8 draft/excluded PRs. Exact-head containment after explicit PR ref fetch showed the same 21 open non-draft PR heads included and the same 6 non-ancestor selective-port candidates: #305, #237, #221, #154, #153, and #135.
- A reconcile worktree from `easel/auto-integration` was created at `/tmp/luce-auto-cron-20260531-1003`; `origin/main` was already represented in the stack.
- Fresh direct-merge probes on top of `a3ef342f` reconfirmed current conflict/status counts for the remaining non-ancestor PRs: #305 (56 status entries), #237 (33), #221 (88), #154 (13), #153 (10), and #135 (3).
- Tmux-driven Codex delegation for #135 in `/tmp/luce-probe-20260531-1003-pr-135` inspected the remaining three conflicted files and attempted conflict-marker cleanup, but exited without a complete resolution or usable narrow port; `git status --short` still showed all three files unmerged and `git diff --check` reported leftover conflict markers in `server/test/test_dflash.cpp`. No source changes were promoted.
- Validation for this docs-only refresh: `git diff --check` passed. Full CMake validation was not rerun because no source code changed in this refresh and the known missing `server/deps/llama.cpp` / CUDA compiler-id environment blockers remain.

## Pending / blocked-needs-human / selective-port candidates

| PR | Head branch | Head | Current status | Probe result / next useful action |
|---:|---|---:|---|---|
| #305 | `layersplit_refactor` | `1de45e4d` | partial selective salvage / human-scale | Fresh direct merge still conflicts heavily (56 status entries) and Codex review reconfirmed direct merge would regress large current stack areas. This run ported the small `DFLASH_EXPERT_BUDGET_PCT` control-plane cap into current Qwen35MoE dynamic expert placement. Much of the broad PR is already represented by current layer-split runtime, Qwen35MoE hybrid machinery, IPC payload/feature range streaming, backend precision fallback, safetensors config validation, SWA flags, and server signal handling. Remaining high-value slices: Qwen35MoE gallocr reuse / remove `kFfnSafeBatch`; larger Laguna hot/cold MoE hybrid prefill/dynamic placement only if Laguna XS.2 residency remains a target. |
| #237 | `feat/dflash-mtp-foundation` | `02c6a6c4` | partial selective salvage / human-scale server-layout port | Fresh probe still conflicts across old `dflash/` and current `server/` files. The stack already carries the first common-only slice: MTP module interfaces, generic chain runner/orchestrator, default backend/target hooks, CMake wiring, and a common orchestrator regression test. This run attempted the next Qwen35 runtime slice: Claude stalled with an empty report/no changes, while Codex drafted a large current-layout port of `qwen35_mtp*` plus `gguf_metadata.h`. The draft remains uncommitted pending populated ggml/gguf deps or CI-backed compile validation. Remaining #237 work: validate/adapt Qwen35 MTP module, graph, loader, hidden-capture attachment, backend/server CLI wiring, native metadata handling, and current-layout end-to-end smoke/contract tests. |
| #135 | `xabicasa/dflash-multi-request-scheduler-batched-target-step` | `561b0ac1` | partial selective salvage / high risk | Fresh direct probe still conflicts only in `server/src/internal.h`, `server/src/qwen35/qwen35_target_graph.cpp`, and `server/test/test_dflash.cpp`. Prior runs ported defaulted `n_seqs` graph/cache parameters, prefill-only batched cache allocation, qwen35 attention/DeltaNet shape plumbing, guards rejecting rollback capture, tree parent IDs, MoE-router capture, and last-token-only logits for `n_seqs > 1`, plus request-tagged daemon stream framing and target-feature capture for matching batched caches. This run's Codex attempt on the conflicted probe inspected those same three files and partially cleaned `qwen35_target_graph.cpp` markers, but left unresolved conflicts in all three files and many `test_dflash.cpp` markers, so nothing was promoted. The next #135 order remains: multi-cache-slot scaffolding (`--target-cache-slots`, slot selection, and `LIST_TARGET_CACHE_SLOTS`), scheduler state/introspection (`DaemonRequestState`, `LIST_REQUESTS`, `CANCEL`, non-batched `SCHED_STEP`/`SCHED_DRAIN`), then diagnostic-only batch probing (`build_target_batch_probe_step` and cache-copy helpers) before live `SCHED_BATCH_TARGET_STEP`/copyback. Remaining unique semantics also include CUDA widening rollback, TQ3 rotation cleanup, and debug/EOS controls. Runtime validation of the batched probe is still needed before enabling scheduler/copyback paths. |
| #154 | `xabicasa/dflash-mtp-speculative-loop` | `2f4ede79` | blocked-needs-human / dependency | Fresh probe conflicts in old/current MTP docs, `dflash/CMakeLists.txt`, CUDA/internal/Qwen35 graph/loader files, and MTP smoke/contract tests. Mine linear MTP decode semantics only after a current-layout #237-equivalent Qwen35 MTP foundation exists. |
| #153 | `xabicasa/dflash-mtp-integrated` | `e9b17cb1` | blocked-needs-human / dependency | Fresh probe conflicts in old/current MTP docs, `dflash/CMakeLists.txt`, CUDA/internal/Qwen35 graph/loader files, and MTP smoke/contract tests. Mine loader/graph/cache/test ideas after current-layout #237-equivalent Qwen35 MTP exists. |

## Suggested close / superseded

| PR | Head branch | Head | Current status | Evidence / suggested action |
|---:|---|---:|---|---|
| #221 | `feat/mtp-prefix-warm-ghost` | `05502974` | superseded for direct integration; mine only after #237 | Fresh direct-merge probe still conflicts across old/current files. The branch is older/broader than #237 and mixes early MTP, prefix-cache warm-hit, PFlash dispatcher/protocol, benches, and docs; #237 remains the better MTP foundation salvage base. |

## Draft / excluded

Draft PRs remain outside the primary non-draft integration target except for dependency awareness: #321, #312, #304, #291, #290, #275, #249, and #193. Draft #321 is a mixed-backend target layer-split runtime follow-up and should be watched if it becomes ready. Draft #312's backend IPC payload transport is related to already-carried IPC payload work, but remains draft/excluded. Draft #304 may touch compaction behavior and should be watched if it becomes ready.

## Retained worktrees / logs

This run retained the updated stack worktree, conflicted probe worktrees, and agent transcripts for audit; earlier conflicted probe worktrees remain from prior runs because safe cleanup is left to a supervised pass:

- `/tmp/luce-auto-cron-20260531-1003` (current docs-only refresh worktree)
- `/tmp/luce-probe-20260531-1003-pr-305`
- `/tmp/luce-probe-20260531-1003-pr-237`
- `/tmp/luce-probe-20260531-1003-pr-221`
- `/tmp/luce-probe-20260531-1003-pr-154`
- `/tmp/luce-probe-20260531-1003-pr-153`
- `/tmp/luce-probe-20260531-1003-pr-135` (Codex attempted #135 conflict-resolution/narrow-port here; still conflicted)
- `/tmp/luce-codex-pr135-20260531-1003.txt` (orchestrator-written summary of the Codex attempt)

- `/tmp/luce-auto-cron-20260531-0950-pr285` (fast-follow #285 advanced-head merge worktree)

- `/tmp/luce-auto-cron-20260531-094212` (current docs-only refresh worktree)
- `/tmp/luce-probe-20260531-094212-pr-305`
- `/tmp/luce-probe-20260531-094212-pr-237`
- `/tmp/luce-probe-20260531-094212-pr-221`
- `/tmp/luce-probe-20260531-094212-pr-154`
- `/tmp/luce-probe-20260531-094212-pr-153`
- `/tmp/luce-probe-20260531-094212-pr-135`
- `/tmp/luce-port-pr135-validate-20260531-094212` (Claude/Codex no-edit #135 remaining-slice review worktree)
- `/tmp/luce-claude-pr135-validate-20260531-094212.txt` (Claude max-turns/no report)
- `/tmp/luce-codex-pr135-validate-20260531-094212.txt` (usable Codex review transcript)

- `/tmp/luce-auto-cron-20260531-092139` (current code/manifest refresh worktree)
- `/tmp/luce-probe-092139-pr-305`
- `/tmp/luce-probe-092139-pr-237`
- `/tmp/luce-probe-092139-pr-221`
- `/tmp/luce-probe-092139-pr-154`
- `/tmp/luce-probe-092139-pr-153`
- `/tmp/luce-probe-092139-pr-135`
- `/tmp/luce-port-pr135-next-092139` (Claude/Codex #135 target-feature capture slice worktree; Claude empty/stuck, Codex produced patch)
- `/tmp/luce-claude-pr135-092139.txt`
- `/tmp/luce-codex-pr135-092139.txt`

- `/tmp/luce-auto-cron-20260531-0856` (current code/manifest refresh worktree)
- `/tmp/luce-probe-0856-pr-305`
- `/tmp/luce-probe-0856-pr-237`
- `/tmp/luce-probe-0856-pr-221`
- `/tmp/luce-probe-0856-pr-154`
- `/tmp/luce-probe-0856-pr-153`
- `/tmp/luce-probe-0856-pr-135`
- `/tmp/luce-port-pr135-next-0856` (Claude #135 next-slice attempt; max-turns/no changes)
- `/tmp/luce-claude-pr135-next-0856.txt`
- `/tmp/luce-port-pr135-codex-next-0856` (Codex #135 tagged-stream slice source worktree)
- `/tmp/luce-codex-pr135-next-0856.txt`
- `/tmp/luce-auto-cron-20260531-073539` (source/doc refresh worktree)
- `/tmp/luce-probe-luce-auto-cron-20260531-073539-pr-305`
- `/tmp/luce-probe-luce-auto-cron-20260531-073539-pr-237`
- `/tmp/luce-probe-luce-auto-cron-20260531-073539-pr-221`
- `/tmp/luce-probe-luce-auto-cron-20260531-073539-pr-154`
- `/tmp/luce-probe-luce-auto-cron-20260531-073539-pr-153`
- `/tmp/luce-probe-luce-auto-cron-20260531-073539-pr-135`
- `/tmp/luce-port-pr237-foundation-20260531-073539` (successful #237 common MTP foundation selective-port worktree)
- `/tmp/luce-claude-pr237-luce-port-pr237-foundation-20260531-073539.txt` (empty Claude port report/no changes)
- `/tmp/luce-codex-pr237-luce-port-pr237-foundation-20260531-073539.txt` (usable port transcript)
- `/tmp/test_common_mtp_orchestrator_manual` (manual narrow test binary built with temporary `ggml` stubs)
- `/tmp/test_common_mtp_orchestrator_stack_post322` (manual narrow post-#322 test binary built with temporary `ggml` stubs)
- `/tmp/luce-auto-cron-20260531-064912` and its probe/log set from the previous #135 selective-port refresh
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

The next useful integration work remains a dedicated selective port, not another direct merge. Highest-value candidates are now: (1) continue #237 using the retained `/tmp/luce-port-pr237-qwen-mtp-20260531-083154` draft only after populating `server/deps/llama.cpp` or otherwise obtaining CI-backed compile evidence for the Qwen35 MTP module/graph/loader slice; (2) #135 runtime validation for the already-ported batched target-graph, request-tagged stream framing, and target-feature capture slices, then multi-cache-slot scaffolding, scheduler state/introspection, and diagnostic-only batch probing before live copyback/target-step mutation; (3) #305's Qwen35MoE gallocr reuse / `kFfnSafeBatch` removal; and (4) #305's larger Laguna hot/cold MoE hybrid path if Laguna XS.2 residency is still desired. #153/#154 should be mined after #237 has current-layout Qwen35 runtime wiring for linear MTP decode semantics, and #221 only for any still-missing prefix-warm ideas. #137, #48, and #94 are represented by superseding current-layout code and can be closed or retargeted only if authors can identify a minimal missing delta.
