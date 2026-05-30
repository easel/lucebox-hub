# Auto-integration manifest

Repository: `Luce-Org/lucebox-hub`
Integration branch: `auto-integration`
Writable remote: `easel`
Upstream remote: `origin` / `Luce-Org`
Last refresh: `2026-05-30T09:00:39-04:00`
Current base: `origin/main` `c95dfcab`
Previous integration tip: `easel/auto-integration` `c6111ac0`
Latest integration tip before this refresh: `c6111ac0`

This branch is maintained as a reproducible patch stack over `origin/main`. This unattended run started from a clean primary checkout on `auto-integration`, verified GitHub/Claude/Codex auth with the real user credential home, fetched `origin` and `easel` separately, confirmed the current `easel/auto-integration` tip is already up to date with `origin/main`, fetched open PR refs, and rechecked all open non-draft PR heads by exact containment. The open non-draft set is unchanged from the prior refresh; no new includable PR heads landed during this pass.

The product-code stack remains unchanged from the prior refresh. Fresh direct-merge probes for every non-contained open non-draft PR still show old-layout MTP/scheduler/CMake conflict classes. This run reattempted direct worktree merges for #237, #221, #154, #153, #137, #135, #94, and #48. A tmux-driven Codex read-only pass on #221 completed and independently confirmed the existing assessment that #221 must be treated as a selective current-`server/` port after a #237-equivalent MTP foundation, not as a direct merge.

## Included in the current non-draft stack

| PR | Head branch | Head | State | Notes |
|---:|---|---:|---|---|
| #311 | `fix/prefix-cache-recurrent-state` | upstream `d0bdef72` merge | included through upstream | Prefix-cache/spec-decode fix is in `origin/main` and therefore carried by the stack base. |
| #310 | `feat-backend-activation-precision-policy-after-306` | `bf9f4b57` | included | Backend activation precision policy / graph tensor precision helpers are carried exactly. |
| #309 | `experiment-dflash-feature-dtype` | `ea6ac481` | included | Feature mirror dtype policy is carried exactly. |
| #308 | `fix/qwen-think-channel` | `9d4defe1` | included | Qwen3.6/Laguna think-mode reasoning is routed to `reasoning_content`; stack carries the replay HTTP stub harness and regression scenarios exactly. |
| #307 | `docs/why-this-exists-copy` | upstream `c95dfcab` merge | included through upstream | README “Why this exists” copy is in `origin/main`. |
| #306 | `refactor-server-layer-split-runtime` | `988fc933` | included | Shared layer-split runtime helper extraction is carried exactly. |
| #303 | `fix/harness-portable-run-dirs` | upstream `05b008a0` | included through upstream and stack | Harness portable run/cache dirs are in `origin/main`; stack compatibility docs/helpers remain carried. |
| #302 | `fix/harness-model-paths` | upstream | included through upstream | Harness model-path override behavior is in `origin/main`. |
| #301 | `fix/ddtree-test-harness` | upstream | included through upstream | DDTree test harness fixes are in `origin/main`. |
| #300 | `fix/sigterm-gpu-unload` | upstream | included through upstream | SIGTERM GPU-unload fix remains in upstream. |
| #299 | `feat/draft-swa-flag` | upstream | included through upstream | Draft SWA env/flag support remains in upstream. |
| #298 | `fix/gemma4-destructor-link` | upstream | included through upstream | Gemma4 destructor-link fix remains in upstream. |
| #292 | `feat-backend-ipc-payload-pipe-open` | upstream / `90bc52f` | included through upstream and stack | Backend IPC payload-pipe support is upstream and represented in carried stack history. |
| #297 | `feat-server-laguna-layer-split-adapter-v2` | `53dd1686` | included | Laguna target-layer-split adapter is carried exactly. |
| #295 | `fix-layer-split-sampling` | `a9aedf7d` | included | Target layer-split sampling support is carried exactly. |
| #294 | `feat/server-passthrough-proxy` | `48f6962d` | included | Passthrough proxy, keep-ratio curve, query survival checks, multimodal text extraction, and unit coverage are carried exactly. |
| #289 | `pipeline_moe` | `27bad6d3` | included | Pipelined hybrid Qwen35 MoE decode update is carried exactly. |
| #285 | `feat/lucebox-docker` | `3dffb306` | included | Refreshed Docker stack / `lucebox` CLI / harness / `luce-bench`, Bragi sweep docs, and autotune/sweep updates are carried exactly. |
| #276 | `fix/qwen36-claude-code-tool-calling` | `5e861b4d` | included | Qwen3.6-27B tool-calling fix for Claude-code Anthropic path is carried exactly. |
| #274 | `feat/pflash-drafter-ee7` | `8c1f37db` | included | Adaptive pFlash composition and effective-size admission/keep-ratio guard update are carried exactly. |
| #266 | `feat/harness-typed-adapters` | `17525eae` | included | Typed harness adapters and format-aware session-inject proxy are carried exactly. |
| #152 | `main` | `cf735bee` | included | Gemma 4 RTX 4090 backend helpers are carried exactly. |
| #142 | `xabicasa/dflash-safetensors-draft-fp16` | `f2fbf62f` | included | FP16 safetensors drafter support is carried exactly. |

## Validation run

This run performed:

- `date -Is` -> `2026-05-30T08:57:11-04:00` during preflight and `2026-05-30T09:00:39-04:00` for manifest refresh metadata.
- Primary checkout preflight: `git status --short` was clean; branch was `auto-integration`; remotes were `origin=https://github.com/Luce-Org/lucebox-hub` and `easel=https://github.com/easel/lucebox-hub`.
- Auth/tooling checks with real user credentials succeeded: `gh auth status`, `claude auth status --text`, and a harmless `codex --version` check (`codex-cli 0.130.0`).
- `git fetch --prune origin` and `git fetch --prune easel` completed successfully.
- Open PR enumeration used `gh pr list --repo Luce-Org/lucebox-hub --state open --limit 200 --json ... --jq ...` and found 22 open non-draft PRs plus 8 draft/excluded PRs.
- Open non-draft PR refs were fetched individually to `refs/remotes/origin/pr/<n>`.
- Containment checks against `easel/auto-integration` `c6111ac0` confirmed #310, #309, #308, #306, #297, #295, #294, #289, #285, #276, #274, #266, #152, and #142 are exact ancestors; #237, #221, #154, #153, #137, #135, #94, and #48 are not ancestors and remain classified below. #311 and #307 remain included through `origin/main`.
- The current `auto-integration`/`easel/auto-integration` tip `c6111ac0` is already based on `origin/main` `c95dfcab`; merging `origin/main` in the reconciliation worktree reported “Already up to date.”
- Fresh probe worktrees attempted direct merges for #237, #221, #154, #153, #137, #135, #94, and #48 from the refreshed integration head. All eight still conflict in old-layout or dependent MTP/scheduler/CMake areas; worktrees are retained under `/tmp/luce-probe-20260530-085751-pr-*`.
- Delegation: `/home/linuxbrew/.linuxbrew/bin/tmux` launched a read-only Codex #221 feasibility pass with `HOME=/home/erik`; it completed and wrote `/tmp/luce-codex-20260530-085751-221-report.txt`, confirming direct merge is unsafe and listing a current-layout selective-port plan.
- `git diff --check` passed on the metadata-only update.
- `python3 -m py_compile server/test/test_stub_integration.py server/test/scripts/strip_gguf_to_tokenizer.py` passed.
- CUDA/CMake build status is unchanged from the prior refresh: local `/usr/bin/nvcc`/CMake fails during CUDA compiler identification with unsupported `sm_52` before project compilation, so the replay HTTP binary and pytest remain blocked in this environment until CUDA configure is fixed or the Docker CUDA toolchain gate is used.

## Pending / blocked-needs-human / selective-port candidates

| PR | Head branch | Head | Current status | Probe result / next useful action |
|---:|---|---:|---|---|
| #237 | `feat/dflash-mtp-foundation` | `02c6a6c4` | blocked-needs-human / human-scale server-layout port | Fresh probe still conflicts across old `dflash/` files and current `server/` files including CMake, backend factory, common MTP interfaces, Qwen35 graph/loader/backend, and tests. Prior tmux Codex inspection confirmed direct merge is unsafe because wholesale acceptance would regress newer remote-draft, pFlash/C2, qwen35moe, thinking-budget, prefix-cache, and layer-split behavior. Direct merge is not viable; selective port remains feasible: port MTP source/config routing, interfaces/runner, Qwen35 MTP graph/loader, hidden capture accessors, GGUF `nextn_predict_layers`, and non-GPU orchestrator tests while preserving current MoE, layer-split, remote-draft, pFlash/C2, budget, native server behavior, and #308's replay stub harness. |
| #221 | `feat/mtp-prefix-warm-ghost` | `05502974` | blocked-needs-human / dependent salvage-port | Fresh direct-merge probe still conflicts in old `dflash/` scripts/backend plus current MTP/common/prefix-cache/Qwen35 files and tests. This run's tmux Codex read-only review concluded direct conflict resolution is unsafe: PR #221 targets old paths/namespaces and older MTP contracts, overlaps the #237 foundation, and risks losing current thinking-budget, tool-call hint, pFlash FA-window, remote draft IPC, scratch release, 64-slot snapshot, snapshot serialization, and MoE routing behavior. Mine prefix-cache WARM behavior only after a current-layout #237-equivalent MTP foundation lands. |
| #154 | `xabicasa/dflash-mtp-speculative-loop` | `2f4ede79` | blocked-needs-human / dependency | Fresh probe conflicts in old `dflash/CMakeLists.txt`, MTP docs, CUDA/internal/Qwen35 graph/loader files, and MTP smoke/contract tests. Mine linear MTP decode semantics after current-layout Qwen35 MTP exists. |
| #153 | `xabicasa/dflash-mtp-integrated` | `e9b17cb1` | blocked-needs-human / dependency | Fresh probe conflicts in old `dflash/CMakeLists.txt`, MTP docs, CUDA/internal/Qwen35 graph/loader files, and MTP smoke/contract tests. Mine loader/graph/cache/test ideas after current-layout Qwen35 MTP exists. |
| #135 | `xabicasa/dflash-multi-request-scheduler-batched-target-step` | `561b0ac1` | blocked-needs-human / selective-port | Fresh direct probe conflicts in `server/src/internal.h`, `server/src/qwen35/qwen35_target_graph.cpp`, and `server/test/test_dflash.cpp`. Prior Codex read-only tmux inspection confirmed direct resolution is unsafe: taking PR files would resurrect the obsolete `dflash/` monolith, while keeping current deletion makes the PR a no-op. Preserve `ModelBackend::generate`, `DaemonIO::emit`, snapshot slots, current single-request `TargetCache`, and `build_target_step()` ABI. Selectively port scheduler state, qwen35-only batched target scratch/cache-copy helpers, a narrow batched target graph builder, and current-layout tests for bucket selection and batched-vs-single target-step comparison. |
| #137 | `xabicasa/dflash-build-cmake-sm89-bsa` | `297fc74e` | suggested-close/superseded | Fresh probe only conflicts on deleted old `dflash/CMakeLists.txt`; ask author to close or retarget to current `server/CMakeLists.txt` if anything remains. |
| #94 | `feat/dflash-qwen36-swa-draft` | `d2f9c9dd` | suggested-close/superseded | Fresh probe conflicts in current `server/src/draft/draft_graph.cpp`, `server/src/draft/draft_safetensors_loader.cpp`, and `server/src/internal.h`. Manual inspection from prior passes found the useful SWA/draft behavior is already present in current auto-integration (`DraftLayer::is_swa`, `DraftWeights::swa_window`, `--draft-swa-window`, `DFLASH27B_DRAFT_SWA_WINDOW`, qwen35 draft SWA propagation, and fixed bare-filename `config.json` lookup). Suggested close or author retarget with a minimal delta if still needed. |
| #48 | `fix/consumer-blackwell-auto-detect` | `858b84b6` | suggested-close/superseded | Fresh probe only conflicts on deleted old `dflash/CMakeLists.txt`; close or retarget to current `server/CMakeLists.txt` if still needed. |

## Draft / excluded

Draft PRs remain outside the primary non-draft integration target except for dependency awareness: #312, #305, #304, #291, #290, #275, #249, and #193. Draft #312's backend IPC payload transport appears related to already-carried IPC payload work but remains draft/excluded. Draft #305 may touch layer-split/MoE refactor areas already represented by #306/#310 and should be watched if it becomes ready.

## Retained worktrees / logs

This run retained worktrees/logs for audit because probe worktrees contain conflicted indexes and safe cleanup is left to a supervised pass:

- `/tmp/luce-auto-cron-20260530-085751`
- `/tmp/luce-probe-20260530-085751-pr-237`
- `/tmp/luce-probe-20260530-085751-pr-221`
- `/tmp/luce-probe-20260530-085751-pr-154`
- `/tmp/luce-probe-20260530-085751-pr-153`
- `/tmp/luce-probe-20260530-085751-pr-137`
- `/tmp/luce-probe-20260530-085751-pr-135`
- `/tmp/luce-probe-20260530-085751-pr-94`
- `/tmp/luce-probe-20260530-085751-pr-48`
- `/tmp/luce-merge-20260530-085751-237.log`
- `/tmp/luce-merge-20260530-085751-221.log`
- `/tmp/luce-merge-20260530-085751-154.log`
- `/tmp/luce-merge-20260530-085751-153.log`
- `/tmp/luce-merge-20260530-085751-137.log`
- `/tmp/luce-merge-20260530-085751-135.log`
- `/tmp/luce-merge-20260530-085751-94.log`
- `/tmp/luce-merge-20260530-085751-48.log`
- `/tmp/luce-codex-20260530-085751-221-report.txt` (usable read-only selective-port report)

## Notes

The next useful integration work remains a dedicated current-`server/` #237 port, not a direct merge. Add the interface/no-op surface first, then Qwen35 capture/rollback and common MTP tests, then follow with #221/#153/#154 MTP behavior after the foundation exists. Keep #135 as a separate scheduler/batched-target selective port. #137 and #48 look like old `dflash/CMakeLists.txt` changes that should be closed or retargeted, and #94 appears largely superseded by current draft/SWA support. The #308 replay HTTP stub harness gives a useful CPU-only validation pattern for future API/wire-format fixes once the local CUDA configure blocker is bypassed or the deterministic Docker CUDA path is used.
