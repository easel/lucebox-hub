# Auto-integration manifest

Repository: `Luce-Org/lucebox-hub`
Integration branch: `auto-integration`
Writable remote: `easel`
Upstream remote: `origin` / `Luce-Org`
Last refresh: `2026-05-30T13:46:55-04:00`
Current base: `origin/main` `c95dfcab`
Previous integration tip: `easel/auto-integration` `1a00f25d`
Latest product-code integration tip before this manifest refresh: `8fc6a081`

This branch is maintained as a reproducible patch stack over `origin/main`. This unattended run started from a clean primary checkout on `auto-integration`, verified GitHub/Claude/Codex auth with the real user credential home, fetched `origin` and `easel` separately, fetched current PR heads, and rechecked exact PR-head containment against the current stack. `HEAD` and `easel/auto-integration` were already identical at `1a00f25d`, and the stack already contains `origin/main` `c95dfcab`.

No product-code stack changes were available in this run. The open non-draft set contains 23 PRs (#310, #309, #308, #306, #305, #297, #295, #294, #289, #285, #276, #274, #266, #237, #221, #154, #153, #152, #142, #137, #135, #94, #48). Exact-head included PRs remain ancestors of the stack. The non-integrated PRs were probed again in isolated worktrees from the current stack. Direct merge probes reconfirmed #94/#48/#137 as superseded or retarget-only, #221 as dependent on #237, #153/#154/#237 as MTP salvage candidates, #305 as a Laguna/common-MoE hybrid salvage candidate, and #135 as a separate scheduler salvage candidate. A Codex tmux read-only delegation for #305 completed and produced a concrete selective-port plan: port only the generic `server/src/common/moe_hybrid_*` infrastructure plus an opt-in Laguna hybrid path, while preserving current backend IPC, activation precision, layer-split runtime, Qwen35, and Qwen35MoE behavior. A Claude tmux read-only delegation for #135 reached the configured max-turn limit without a usable report.

## Included in the current non-draft stack

| PR | Head branch | Head | State | Notes |
|---:|---|---:|---|---|
| #310 | `feat-backend-activation-precision-policy-after-306` | `bf9f4b57` | included | Backend activation precision policy / graph tensor precision helpers are carried exactly. |
| #309 | `experiment-dflash-feature-dtype` | `ea6ac481` | included | Feature mirror dtype policy is carried exactly. |
| #308 | `fix/qwen-think-channel` | `9d4defe1` | included | Qwen3.6/Laguna think-mode reasoning is routed to `reasoning_content`; stack carries the replay HTTP stub harness and regression scenarios exactly. |
| #306 | `refactor-server-layer-split-runtime` | `988fc933` | included | Shared layer-split runtime helper extraction is carried exactly. |
| #297 | `feat-server-laguna-layer-split-adapter-v2` | `53dd1686` | included | Laguna target-layer-split adapter is carried exactly. |
| #295 | `fix-layer-split-sampling` | `a9aedf7d` | included | Target layer-split sampling support is carried exactly. |
| #294 | `feat/server-passthrough-proxy` | `48f6962d` | included | Passthrough proxy, keep-ratio curve, query survival checks, multimodal text extraction, and unit coverage are carried exactly. |
| #289 | `pipeline_moe` | `caf2b112` | included | Carries pipelined hybrid Qwen35 MoE decode plus the sub-batch hybrid prefill FFN safety fix. |
| #285 | `feat/lucebox-docker` | `3dffb306` | included | Docker stack / `lucebox` CLI / harness / `luce-bench`, Bragi sweep docs, and autotune/sweep updates are carried exactly. |
| #276 | `fix/qwen36-claude-code-tool-calling` | `5e861b4d` | included | Qwen3.6-27B tool-calling fix for Claude-code Anthropic path is carried exactly. |
| #274 | `feat/pflash-drafter-ee7` | `8c1f37db` | included | Adaptive pFlash composition and effective-size admission/keep-ratio guard update are carried exactly. |
| #266 | `feat/harness-typed-adapters` | `17525eae` | included | Typed harness adapters and format-aware session-inject proxy are carried exactly. |
| #152 | `main` | `cf735bee` | included | Gemma 4 RTX 4090 backend helpers are carried exactly. |
| #142 | `xabicasa/dflash-safetensors-draft-fp16` | `f2fbf62f` | included | FP16 safetensors drafter support is carried exactly. |

Closed or upstreamed PRs still represented by the stack/base include #313 (closed, carried in stack history), #311, #307, #303, #302, #301, #300, #299, #298, and #292.

## Validation run

This run performed:

- `date -Is` -> `2026-05-30T13:38:36-04:00` during preflight and `2026-05-30T13:46:55-04:00` for this manifest refresh.
- Primary checkout preflight: `git status --porcelain=v1` was clean; branch was `auto-integration`; remotes were `origin=https://github.com/Luce-Org/lucebox-hub` and `easel=https://github.com/easel/lucebox-hub`.
- Auth/tooling checks with real user credentials succeeded: `gh auth status`, `claude auth status --text`, and `codex --version` (`codex-cli 0.130.0`).
- `git fetch --prune origin` and `git fetch --prune easel` completed successfully.
- Current open PR enumeration reported 23 non-draft PRs and 7 draft/excluded PRs.
- Explicit fetch of each open PR head succeeded. Exact-head containment against the refreshed `auto-integration` tip confirmed #310, #309, #308, #306, #297, #295, #294, #289, #285, #276, #274, #266, #152, and #142 as ancestors; #305, #237, #221, #154, #153, #137, #135, #94, and #48 remain non-ancestors and stay in the blocked/salvage buckets below.
- A reconcile worktree from `easel/auto-integration` was created at `/tmp/luce-auto-cron-20260530-133925`; merging `origin/main` reported no source-code merge work, but the worktree immediately showed 21 modified binary/LFS asset paths after checkout/merge (`assets/...`, `harness/assets/hero.png`, `server/test/fixtures/qwen3.6-tokenizer.gguf`, etc.). The primary checkout stayed clean, so no product-code update was taken from that worktree.
- Probe worktrees were created from the current stack and direct-merge attempts were run for all non-integrated PRs; conflict file lists are recorded under `/tmp/luce-auto-cron-20260530-133925-logs/`.
- Delegation: Codex tmux read-only review for #305 completed and recommended a selective Laguna hybrid/common-MoE port only. Claude tmux read-only review for #135 exited with `Error: Reached max turns (6)` and no usable report.
- `git diff --check -- docs/auto-integration.md` passed for this manifest-only change.
- No product-code tests or builds were rerun because no product-code changes were made; the local CUDA/CMake blocker from prior runs remains unchanged and still prevents full replay HTTP / pytest validation in this environment.

## Pending / blocked-needs-human / selective-port candidates

| PR | Head branch | Head | Current status | Probe result / next useful action |
|---:|---|---:|---|---|
| #305 | `layersplit_refactor` | `1de45e4d` | blocked-needs-human / selective-port | Fresh direct merge still conflicts broadly across README/spec/harness docs, backend IPC, backend precision, layer-split backend/adapters, Laguna/Qwen35/Qwen35MoE internals, and server tests. Codex delegation recommends porting only the Laguna hybrid hot/cold expert work: add `server/src/common/moe_hybrid_*` infrastructure (`MoeHybridConfig`, `MoeLayerDesc`, placement/routing/storage/FFN/swap symbols), add opt-in Laguna hybrid symbols (`init_hybrid_mode`, `generate_hybrid`, `hybrid_forward_one_token`, `maybe_post_request_swap`, `build_laguna_layer_prefn_step`, `DFLASH_EXPERT_BUDGET_PCT`), and prefer a new `load_target_gguf_laguna_hybrid_partial(...)`. Preserve current `ggml_backend_cuda_init(args_.device.gpu)`, backend IPC shared-payload work, activation precision policy, `supports_cpu_sampling`, `compute_target_split_projection`, prefill logits, `LagunaLayerSplitAdapter`, and current #289 Qwen35MoE sub-batch safety behavior. |
| #237 | `feat/dflash-mtp-foundation` | `02c6a6c4` | blocked-needs-human / human-scale server-layout port | Fresh probe still conflicts across old `dflash/` files and current `server/` files including CMake, backend factory, common MTP interfaces, Qwen35 graph/loader/backend, and tests. Native MTP is still absent from the live stack and should be selectively ported into current `server/` layout: `common/gguf_metadata.h`, `common/mtp_interface.h`, `common/mtp_chain_runner.*`, `common/mtp_orchestrator.*`, `qwen35/qwen35_mtp*`, `qwen35/qwen35_mtp_graph*`, `qwen35/qwen35_mtp_loader.cpp`, and MTP tests. |
| #221 | `feat/mtp-prefix-warm-ghost` | `05502974` | blocked-needs-human / dependent salvage-port | Fresh direct-merge probe still conflicts in old `dflash/` scripts/backend plus current MTP/common/prefix-cache/Qwen35 files and tests. Mine prefix-cache WARM behavior only after a current-layout #237-equivalent MTP foundation lands. |
| #154 | `xabicasa/dflash-mtp-speculative-loop` | `2f4ede79` | blocked-needs-human / dependency | Fresh probe conflicts in old `dflash/CMakeLists.txt`, MTP docs, CUDA/internal/Qwen35 graph/loader files, and MTP smoke/contract tests. Mine linear MTP decode semantics after current-layout Qwen35 MTP exists. |
| #153 | `xabicasa/dflash-mtp-integrated` | `e9b17cb1` | blocked-needs-human / dependency | Fresh probe conflicts in old `dflash/CMakeLists.txt`, MTP docs, CUDA/internal/Qwen35 graph/loader files, and MTP smoke/contract tests. Mine loader/graph/cache/test ideas after current-layout Qwen35 MTP exists. |
| #135 | `xabicasa/dflash-multi-request-scheduler-batched-target-step` | `561b0ac1` | blocked-needs-human / selective-port | Fresh direct probe conflicts in `server/src/internal.h`, `server/src/qwen35/qwen35_target_graph.cpp`, and `server/test/test_dflash.cpp`. Preserve current `ModelBackend::generate`, `DaemonIO::emit`, snapshot slots, current single-request `TargetCache`, and `build_target_step()` ABI; selectively port scheduler state and qwen35-only batched target helpers if still desired. A Claude read-only analysis attempt hit the configured turn limit. |
| #137 | `xabicasa/dflash-build-cmake-sm89-bsa` | `297fc74e` | suggested-close/superseded | Fresh probe only conflicts on deleted old `dflash/CMakeLists.txt`; ask author to close or retarget to current `server/CMakeLists.txt` if anything remains. |
| #94 | `feat/dflash-qwen36-swa-draft` | `d2f9c9dd` | suggested-close/superseded | Fresh probe conflicts in current `server/src/draft/draft_graph.cpp`, `server/src/draft/draft_safetensors_loader.cpp`, and `server/src/internal.h`. Useful SWA/draft behavior is already present in current auto-integration (`DraftLayer::is_swa`, `DraftWeights::swa_window`, `--draft-swa-window`, `DFLASH27B_DRAFT_SWA_WINDOW`, qwen35 draft SWA propagation, and fixed bare-filename `config.json` lookup). Suggested close or author retarget with a minimal delta if still needed. |
| #48 | `fix/consumer-blackwell-auto-detect` | `858b84b6` | suggested-close/superseded | Fresh probe only conflicts on deleted old `dflash/CMakeLists.txt`; close or retarget to current `server/CMakeLists.txt` if still needed. |

## Draft / excluded

Draft PRs remain outside the primary non-draft integration target except for dependency awareness: #312, #304, #291, #290, #275, #249, and #193. Draft #312's backend IPC payload transport is related to already-carried IPC payload work, but remains draft/excluded. Draft #304 may touch compaction behavior and should be watched if it becomes ready.

## Retained worktrees / logs

This run retained worktrees/logs for audit because probe worktrees contain conflicted indexes and safe cleanup is left to a supervised pass:

- `/tmp/luce-auto-cron-20260530-133925`
- `/tmp/luce-probe-20260530-133925-pr-305`
- `/tmp/luce-probe-20260530-133925-pr-237`
- `/tmp/luce-probe-20260530-133925-pr-221`
- `/tmp/luce-probe-20260530-133925-pr-154`
- `/tmp/luce-probe-20260530-133925-pr-153`
- `/tmp/luce-probe-20260530-133925-pr-137`
- `/tmp/luce-probe-20260530-133925-pr-135`
- `/tmp/luce-probe-20260530-133925-pr-94`
- `/tmp/luce-probe-20260530-133925-pr-48`
- Logs under `/tmp/luce-auto-cron-20260530-133925-logs/`, including `merge-*.log`, `status-*.txt`, `conflicts-*.txt`, `luce-codex-305-20260530-133925.capture3.txt`, and `luce-claude-135-20260530-133925.capture.txt`.

## Notes

The next useful integration work remains two dedicated selective ports: first, a current-`server/` #237 MTP foundation port; second, the #305 Laguna/common-MoE hybrid port following Codex's narrower plan while preserving current #289 Qwen35MoE and #306/#310 layer-split/precision APIs. Keep #135 as a separate scheduler/batched-target selective port. #137 and #48 look like old `dflash/CMakeLists.txt` changes that should be closed or retargeted, and #94 appears largely superseded by current draft/SWA support.
