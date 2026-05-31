# Auto-integration manifest

Repository: `Luce-Org/lucebox-hub`
Integration branch: `auto-integration`
Writable remote: `easel`
Upstream remote: `origin` / `Luce-Org`
Last refresh: `2026-05-30T20:15:39-04:00`
Current base: `origin/main` `c95dfcab`
Previous integration tip: `easel/auto-integration` `5996a8ed`
Current integration tip before push: `5996a8ed`

This branch is maintained as a reproducible patch stack over `origin/main`. This unattended run started from a clean primary checkout on `auto-integration`, verified GitHub/Claude/Codex auth with the real user credential home, fetched `origin` and `easel` separately, fetched current PR heads, and rechecked exact PR-head containment against the current stack.

No product-code PR was newly integrated in this refresh: `origin/main` was already included in the stack and every currently included non-draft PR head was already an ancestor of `easel/auto-integration`. The open non-draft set still contains 24 PRs; 15 are exactly included and 9 remain non-ancestor conflict/selective-port candidates. This run reran direct merge probes for every still-non-integrated non-draft PR. Conflict classes remained unchanged from the prior audit, so no new external-agent delegation was warranted in this run.

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
| #285 | `feat/lucebox-docker` | `6ea9694a` | included | Docker stack / `lucebox` CLI / harness / `luce-bench`, Bragi sweep docs, autotune/sweep updates, shell harness tests, long-context grader coverage, and Bragi GPU-power-throttle experiment notes are carried exactly. |
| #276 | `fix/qwen36-claude-code-tool-calling` | `5e861b4d` | included | Qwen3.6-27B tool-calling fix for Claude-code Anthropic path is carried exactly. |
| #274 | `feat/pflash-drafter-ee7` | `8c1f37db` | included | Adaptive pFlash composition and effective-size admission/keep-ratio guard update are carried exactly. |
| #266 | `feat/harness-typed-adapters` | `17525eae` | included | Typed harness adapters and format-aware session-inject proxy are carried exactly. |
| #152 | `main` | `cf735bee` | included | Gemma 4 RTX 4090 backend helpers are carried exactly. |
| #142 | `xabicasa/dflash-safetensors-draft-fp16` | `f2fbf62f` | included | FP16 safetensors drafter support is carried exactly. |

Closed or upstreamed PRs still represented by the stack/base include #313 (closed, carried in stack history), #311, #307, #303, #302, #301, #300, #299, #298, and #292.

## Validation run

This run performed:

- `date -Is` -> `2026-05-30T20:15:39-04:00` during preflight.
- Primary checkout preflight: `git status --short` was clean on `auto-integration`; remotes were `origin=https://github.com/Luce-Org/lucebox-hub` and `easel=https://github.com/easel/lucebox-hub`.
- Auth/tooling checks with real user credentials succeeded: `gh auth status`, `claude auth status --text`, and a harmless `codex --help` smoke check.
- `git fetch --prune origin` and `git fetch --prune easel` completed successfully.
- Current open PR enumeration reported 24 non-draft PRs and 7 draft/excluded PRs.
- Explicit fetch of open PR heads succeeded for all current non-draft PRs.
- Exact-head containment showed #314, #310, #309, #308, #306, #297, #295, #294, #289, #285, #276, #274, #266, #152, and #142 were ancestors of the stack; #305, #237, #221, #154, #153, #137, #135, #94, and #48 remained non-ancestors.
- A reconcile worktree from `auto-integration` was created at `/tmp/luce-auto-cron-20260530-201608`; `git merge --no-edit origin/main` reported `Already up to date.`
- Probe worktrees were created from the current stack and direct-merge attempts were rerun for all still-non-integrated PRs; conflict file lists are recorded under `/tmp/luce-auto-cron-20260530-201608-logs/`.
- Direct merge probes remained conflicted: #305=29, #237=24, #221=23, #154=12, #153=10, #137=1, #135=3, #94=3, #48=1.
- No new external-agent delegation was run in this refresh because no PR heads changed and the conflict classes matched the prior tmux-driven #305 Claude/Codex audit and prior manual probe notes.
- Verification for this docs-only refresh: `git diff --check HEAD -- docs/auto-integration.md` passed before commit. No product build was run because the stack did not gain product-code changes in this run.

## Pending / blocked-needs-human / selective-port candidates

| PR | Head branch | Head | Current status | Probe result / next useful action |
|---:|---|---:|---|---|
| #305 | `layersplit_refactor` | `1de45e4d` | blocked-needs-human / human-scale selective port | Fresh direct merge still conflicts across 29 files: README/spec/harness docs, server CMake/scripts, backend IPC, backend precision, layer-split backend/adapters, Gemma4/Laguna/Qwen35/Qwen35MoE internals, and server tests. Prior Claude hit the turn limit; prior Codex completed a no-edit audit and found the first 21 PR commits patch-equivalent to already-carried stack changes. Mine the remaining common MoE hybrid extraction, Laguna hybrid hot/cold expert placement and `DFLASH_EXPERT_BUDGET_PCT`, Qwen35MoE routed-FFN/GPU-resident/cached-graph/async-logits work, and the no-sub-batch reused-`gallocr` optimization. Preserve current sampling gates, `layer_split_runtime`, #310 activation precision policy, shared IPC payload transport, Qwen35/Gemma4 snapshot/restore and AR decode behavior, rich props metadata, and current harness/luce-bench/lucebox/Docker layout. |
| #237 | `feat/dflash-mtp-foundation` | `02c6a6c4` | blocked-needs-human / human-scale server-layout port | Fresh probe still conflicts across 24 old `dflash/` and current `server/` files including CMake, backend factory, common MTP interfaces, Qwen35 graph/loader/backend, and tests. Port old `dflash/scripts/server.py` and `dflash/src/server/server_main.cpp` CLI/config semantics into current `server/src/server/server_main.cpp`; merge `MtpSource`, native/external MTP GGUF detection, and config assignment into current backend factory without regressing remote-draft, Qwen35MoE, layer-split, or PFlash helpers; combine current MoE router captures with MTP hidden captures in `step_graph` / graph builders; preserve `set_fa_window` while adding MTP hidden accessors; hand-merge Qwen35 `init`, `generate`, `restore_and_generate`, `do_prefill`, prefix-cache restore, and MTP helpers; then build `dflash_common`, `dflash_server`, `test_dflash`, and `test_common_mtp_orchestrator` and run non-MTP, PFlash, remote-draft, Qwen35MoE, prefix-cache, and native/external MTP runtime smoke tests. |
| #221 | `feat/mtp-prefix-warm-ghost` | `05502974` | blocked-needs-human / dependent salvage-port | Fresh direct-merge probe still conflicts across 23 old `dflash/` scripts/backend plus current MTP/common/prefix-cache/Qwen35 files and tests. Mine prefix-cache WARM behavior only after a current-layout #237-equivalent MTP foundation lands. |
| #154 | `xabicasa/dflash-mtp-speculative-loop` | `2f4ede79` | blocked-needs-human / dependency | Fresh probe conflicts in 12 old/current MTP docs, `dflash/CMakeLists.txt`, CUDA/internal/Qwen35 graph/loader files, and MTP smoke/contract tests. Mine linear MTP decode semantics after current-layout Qwen35 MTP exists. |
| #153 | `xabicasa/dflash-mtp-integrated` | `e9b17cb1` | blocked-needs-human / dependency | Fresh probe conflicts in 10 old/current MTP docs, `dflash/CMakeLists.txt`, CUDA/internal/Qwen35 graph/loader files, and MTP smoke/contract tests. Mine loader/graph/cache/test ideas after current-layout Qwen35 MTP exists. |
| #135 | `xabicasa/dflash-multi-request-scheduler-batched-target-step` | `561b0ac1` | blocked-needs-human / selective-port | Fresh direct probe still conflicts in `server/src/internal.h`, `server/src/qwen35/qwen35_target_graph.cpp`, and `server/test/test_dflash.cpp`. Preserve current `is_eos_tok`, `TargetLoadPlan`, partial/layer-split load/cache allocation, dynamic capture layers, Qwen35MoE/router/precision paths, last-token-only logits, drafter arch handling, sampler/PFlash/feature-mirror/EOS behavior, and current generic daemon backend abstractions. Mine only the scheduler slot/request model, `START`/`CONTINUE` protocol, aligned same-position bucket selection, tagged stream frames, `QwenGraphInputs::n_seqs`, batched single-token target graph support, batch-vs-single validation, copyback validation, and lifecycle signal semantics (`-4`) behind Qwen35-only feature gates before widening support. |
| #137 | `xabicasa/dflash-build-cmake-sm89-bsa` | `297fc74e` | suggested-close/superseded | Fresh probe still only conflicts on deleted old `dflash/CMakeLists.txt`; ask author to close or retarget to current `server/CMakeLists.txt` if anything remains. |
| #94 | `feat/dflash-qwen36-swa-draft` | `d2f9c9dd` | suggested-close/superseded | Fresh probe conflicts in current `server/src/draft/draft_graph.cpp`, `server/src/draft/draft_safetensors_loader.cpp`, and `server/src/internal.h`. Useful SWA/draft behavior is already present in current auto-integration; suggested close or author retarget with a minimal delta if still needed. |
| #48 | `fix/consumer-blackwell-auto-detect` | `858b84b6` | suggested-close/superseded | Fresh probe still only conflicts on deleted old `dflash/CMakeLists.txt`; close or retarget to current `server/CMakeLists.txt` if still needed. |

## Draft / excluded

Draft PRs remain outside the primary non-draft integration target except for dependency awareness: #312, #304, #291, #290, #275, #249, and #193. Draft #312's backend IPC payload transport is related to already-carried IPC payload work, but remains draft/excluded. Draft #304 may touch compaction behavior and should be watched if it becomes ready.

## Retained worktrees / logs

This run retained worktrees/logs for audit because probe worktrees contain conflicted indexes and safe cleanup is left to a supervised pass:

- `/tmp/luce-auto-cron-20260530-201608`
- `/tmp/luce-probe-20260530-201608-pr-305`
- `/tmp/luce-probe-20260530-201608-pr-237`
- `/tmp/luce-probe-20260530-201608-pr-221`
- `/tmp/luce-probe-20260530-201608-pr-154`
- `/tmp/luce-probe-20260530-201608-pr-153`
- `/tmp/luce-probe-20260530-201608-pr-137`
- `/tmp/luce-probe-20260530-201608-pr-135`
- `/tmp/luce-probe-20260530-201608-pr-94`
- `/tmp/luce-probe-20260530-201608-pr-48`
- Logs under `/tmp/luce-auto-cron-20260530-201608-logs/`, including `merge-*.log`, `status-*.txt`, and `conflicts-*.txt`.

Earlier retained audit paths from prior runs include `/tmp/luce-auto-cron-20260530-200216`, `/tmp/luce-auto-cron-20260530-194121`, `/tmp/luce-auto-cron-20260530-192047`, `/tmp/luce-auto-cron-20260530-184231`, `/tmp/luce-auto-cron-20260530-181103`, `/tmp/luce-auto-cron-20260530-175155`, `/tmp/luce-auto-cron-20260530-173141`, `/tmp/luce-auto-cron-20260530-171420`, `/tmp/luce-auto-cron-20260530-165724`, `/tmp/luce-auto-cron-20260530-164341`, `/tmp/luce-auto-cron-20260530-162504`, `/tmp/luce-auto-cron-20260530-161133`, `/tmp/luce-auto-cron-20260530-155251`, `/tmp/luce-auto-cron-20260530-153049`, `/tmp/luce-auto-cron-20260530-154010`, their corresponding probe worktrees, and logs.

## Notes

The next useful integration work remains a dedicated current-`server/` #237 MTP foundation selective port, with #221/#153/#154 mined afterward. #305 is now the other high-value human-scale port: first extract common MoE hybrid infrastructure into current Qwen35MoE without changing Laguna, then port the Qwen35MoE routed-FFN/GPU-resident/reused-`gallocr` optimizations, then add Laguna hybrid behind an opt-in gate while preserving device selection, backend factory layer-split selection, graph precision policy, and the current `TargetLoadPlan` partial loader. Keep #135 as a separate scheduler/batched-target selective port. #137 and #48 look like old `dflash/CMakeLists.txt` changes that should be closed or retargeted, and #94 appears largely superseded by current draft/SWA support.
