# Auto-integration manifest

Repository: `Luce-Org/lucebox-hub`
Integration branch: `auto-integration`
Writable remote: `easel`
Upstream remote: `origin` / `Luce-Org`
Last refresh: `2026-05-30T11:43:11-04:00`
Current base: `origin/main` `c95dfcab`
Previous integration tip: `easel/auto-integration` `0a80d47f`
Latest product-code integration tip before this manifest refresh: `df0df5fe`

This branch is maintained as a reproducible patch stack over `origin/main`. This unattended run started from a clean primary checkout on `auto-integration`, verified GitHub/Claude/Codex auth with the real user credential home, fetched `origin` and `easel` separately, confirmed the current stack already matches `easel/auto-integration` and contains `origin/main`, fetched all open non-draft PR refs, and rechecked exact PR-head containment against the refreshed stack.

No product-code stack changes were made this run. The open non-draft exact-head set remains fully represented except for the same conflicted selective-port/superseded candidates listed below. All exact-head included PRs remain ancestors of the stack. The non-integrated PRs were freshly probed again in isolated worktrees from the current stack. Direct merge probes reconfirmed #94/#48/#137 as superseded or retarget-only, #221 as dependent on #237, #153/#154/#237 as MTP salvage candidates, and #135 as a separate scheduler salvage candidate. Claude read-only delegation for #305/#237 hit its turn limit without producing usable reports; tmux-driven Codex read-only reviews completed and reconfirmed #305 as a selective Laguna/common-MoE hybrid salvage candidate and #237 as a selective current-layout MTP foundation port rather than whole-PR merges.

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
| #289 | `pipeline_moe` | `caf2b112` | included | Carries pipelined hybrid Qwen35 MoE decode plus the sub-batch hybrid prefill FFN safety fix. |
| #285 | `feat/lucebox-docker` | `3dffb306` | included | Docker stack / `lucebox` CLI / harness / `luce-bench`, Bragi sweep docs, and autotune/sweep updates are carried exactly. |
| #276 | `fix/qwen36-claude-code-tool-calling` | `5e861b4d` | included | Qwen3.6-27B tool-calling fix for Claude-code Anthropic path is carried exactly. |
| #274 | `feat/pflash-drafter-ee7` | `8c1f37db` | included | Adaptive pFlash composition and effective-size admission/keep-ratio guard update are carried exactly. |
| #266 | `feat/harness-typed-adapters` | `17525eae` | included | Typed harness adapters and format-aware session-inject proxy are carried exactly. |
| #152 | `main` | `cf735bee` | included | Gemma 4 RTX 4090 backend helpers are carried exactly. |
| #142 | `xabicasa/dflash-safetensors-draft-fp16` | `f2fbf62f` | included | FP16 safetensors drafter support is carried exactly. |

## Validation run

This run performed:

- `date -Is` -> `2026-05-30T11:33:49-04:00` during preflight and `2026-05-30T11:43:11-04:00` for manifest refresh metadata.
- Primary checkout preflight: `git status --short` was clean; branch was `auto-integration`; remotes were `origin=https://github.com/Luce-Org/lucebox-hub` and `easel=https://github.com/easel/lucebox-hub`.
- Auth/tooling checks with real user credentials succeeded: `gh auth status`, `claude auth status --text`, and a harmless `codex --help` smoke check.
- `git fetch --prune origin` and `git fetch --prune easel` completed successfully.
- Open PR enumeration used `gh pr list --repo Luce-Org/lucebox-hub --state open --limit 200 --json ... --jq ...` and found 23 open non-draft PRs plus 7 draft/excluded PRs.
- Open non-draft PR refs were fetched individually to `refs/remotes/origin/pr/<n>`.
- Containment checks against the refreshed stack confirmed #310, #309, #308, #306, #297, #295, #294, #289, #285, #276, #274, #266, #152, and #142 are exact ancestors; #305, #237, #221, #154, #153, #137, #135, #94, and #48 are not ancestors and remain classified below. #311 and #307 remain included through `origin/main`.
- Worktree reconciliation at `/tmp/luce-auto-cron-20260530-113432` started from `easel/auto-integration` `0a80d47f`; `origin/main` `c95dfcab` was already contained, so the base merge was already up to date.
- Fresh direct-merge probes were run for #305, #237, #221, #154, #153, #137, #135, #94, and #48 from the current stack. Conflict paths are summarized below and detailed in `/tmp/luce-merge-20260530-113432-*.log` and `/tmp/luce-status-20260530-113432-*.txt`.
- Claude tmux read-only review attempts for #305 and #237 reached `--max-turns 8` without useful reports (`/tmp/luce-claude-20260530-113432-pr-305.txt`, `/tmp/luce-claude-20260530-113432-pr-237.txt`), so their conclusions were not used as evidence.
- Codex tmux read-only review for #305 completed a useful feasibility report at `/tmp/luce-codex-20260530-113432-pr-305.txt`, confirming whole-PR merge is not appropriate; the absent value is mainly Laguna hybrid MoE support and related common `moe_hybrid_*` helpers, while current IPC, layer-split, Gemma4, Qwen35MoE #289, precision-policy, CMake, and harness work must be preserved.
- Codex tmux read-only review for #237 completed a useful feasibility report at `/tmp/luce-codex-20260530-113432-pr-237.txt`, confirming native MTP value is absent and should be selectively ported into current `server/` paths while preserving remote-draft, pFlash, budget hooks, layer-split, native server, and Qwen35MoE changes.
- `git diff --check` passed on both the primary checkout and the stack worktree before this docs commit.
- `python3 -m py_compile server/test/test_stub_integration.py server/test/scripts/strip_gguf_to_tokenizer.py` passed.
- CUDA/CMake build status is unchanged from prior refreshes: local `/usr/bin/nvcc`/CMake fails during CUDA compiler identification with unsupported `sm_52` before project compilation, so the replay HTTP binary and pytest remain blocked in this environment until CUDA configure is fixed or the Docker CUDA toolchain gate is used.

## Pending / blocked-needs-human / selective-port candidates

| PR | Head branch | Head | Current status | Probe result / next useful action |
|---:|---|---:|---|---|
| #305 | `layersplit_refactor` | `1de45e4d` | blocked-needs-human / selective-port | Fresh direct merge into the current #289/#306/#310 stack still conflicts broadly across README/spec/harness docs, backend IPC, backend precision, layer-split backend/adapters, Laguna/Qwen35/Qwen35MoE internals, and server tests. Claude read-only review hit the turn limit; Codex read-only review measured the whole PR as stale and not appropriate to merge. Unique work worth mining: Laguna hybrid MoE support with hot/cold expert placement, partial expert loading, `DFLASH_EXPERT_BUDGET_PCT`, hybrid prefill/decode, routing telemetry, post-request swap hooks, and possibly batched hybrid prefill / GPU-resident decode activations / cached hot-cold FFN graphs / gallocr reuse. Current selective-port paths: `server/src/laguna/*`, `server/src/common/moe_hybrid_*`, and `server/CMakeLists.txt`. Keep HEAD for shared/auto IPC, layer-split runtime and precision APIs, Gemma4 fixes, Qwen35MoE #289 normalized weights/cache cleanup/dummy routing/sub-batch/telemetry fixes, docs, harness, and CMake wiring; do not carry a Laguna sampled-request argmax regression. |
| #237 | `feat/dflash-mtp-foundation` | `02c6a6c4` | blocked-needs-human / human-scale server-layout port | Fresh probe still conflicts across old `dflash/` files and current `server/` files including CMake, backend factory, common MTP interfaces, Qwen35 graph/loader/backend, and tests. Claude read-only review hit the turn limit; Codex read-only review confirmed whole-PR merge is not appropriate. #237 carries absent native-heads MTP speculation (`--mtp-source`, `--mtp-gguf`, `--mtp-gamma`, chain/top-k modes), generic MTP interfaces/orchestrator/chain runner, Qwen35 MTP module/graph/loader, GGUF `nextn_predict_layers` auto-detect, target hidden capture, and MTP tests. Port into `server/src/common/mtp_*`, `server/src/common/gguf_metadata.h`, `server/src/common/{backend_factory,model_backend,dflash_target,step_graph,attn_masks}.h`, `server/src/qwen35/qwen35_mtp*`, current Qwen35 graph/loader/backend/daemon/target files, `server/src/server/server_main.cpp`, `server/CMakeLists.txt`, and `server/test/` without resurrecting `dflash/scripts/server.py` or replacing current remote-draft, pFlash, budget hooks, layer-split, native server, thinking-budget, or Qwen35MoE changes. |
| #221 | `feat/mtp-prefix-warm-ghost` | `05502974` | blocked-needs-human / dependent salvage-port | Fresh direct-merge probe still conflicts in old `dflash/` scripts/backend plus current MTP/common/prefix-cache/Qwen35 files and tests. Mine prefix-cache WARM behavior only after a current-layout #237-equivalent MTP foundation lands. |
| #154 | `xabicasa/dflash-mtp-speculative-loop` | `2f4ede79` | blocked-needs-human / dependency | Fresh probe conflicts in old `dflash/CMakeLists.txt`, MTP docs, CUDA/internal/Qwen35 graph/loader files, and MTP smoke/contract tests. Mine linear MTP decode semantics after current-layout Qwen35 MTP exists. |
| #153 | `xabicasa/dflash-mtp-integrated` | `e9b17cb1` | blocked-needs-human / dependency | Fresh probe conflicts in old `dflash/CMakeLists.txt`, MTP docs, CUDA/internal/Qwen35 graph/loader files, and MTP smoke/contract tests. Mine loader/graph/cache/test ideas after current-layout Qwen35 MTP exists. |
| #135 | `xabicasa/dflash-multi-request-scheduler-batched-target-step` | `561b0ac1` | blocked-needs-human / selective-port | Fresh direct probe conflicts in `server/src/internal.h`, `server/src/qwen35/qwen35_target_graph.cpp`, and `server/test/test_dflash.cpp`. Preserve current `ModelBackend::generate`, `DaemonIO::emit`, snapshot slots, current single-request `TargetCache`, and `build_target_step()` ABI; selectively port scheduler state and qwen35-only batched target helpers if still desired. |
| #137 | `xabicasa/dflash-build-cmake-sm89-bsa` | `297fc74e` | suggested-close/superseded | Fresh probe only conflicts on deleted old `dflash/CMakeLists.txt`; ask author to close or retarget to current `server/CMakeLists.txt` if anything remains. |
| #94 | `feat/dflash-qwen36-swa-draft` | `d2f9c9dd` | suggested-close/superseded | Fresh probe conflicts in current `server/src/draft/draft_graph.cpp`, `server/src/draft/draft_safetensors_loader.cpp`, and `server/src/internal.h`. Useful SWA/draft behavior is already present in current auto-integration (`DraftLayer::is_swa`, `DraftWeights::swa_window`, `--draft-swa-window`, `DFLASH27B_DRAFT_SWA_WINDOW`, qwen35 draft SWA propagation, and fixed bare-filename `config.json` lookup). Suggested close or author retarget with a minimal delta if still needed. |
| #48 | `fix/consumer-blackwell-auto-detect` | `858b84b6` | suggested-close/superseded | Fresh probe only conflicts on deleted old `dflash/CMakeLists.txt`; close or retarget to current `server/CMakeLists.txt` if still needed. |

## Draft / excluded

Draft PRs remain outside the primary non-draft integration target except for dependency awareness: #312, #304, #291, #290, #275, #249, and #193. Draft #312's backend IPC payload transport is new since recent runs and related to already-carried IPC payload work, but remains draft/excluded. Draft #304 may touch compaction behavior and should be watched if it becomes ready.

## Retained worktrees / logs

This run retained worktrees/logs for audit because probe worktrees contain conflicted indexes and safe cleanup is left to a supervised pass:

- `/tmp/luce-auto-cron-20260530-113432`
- `/tmp/luce-probe-20260530-113432-pr-305`
- `/tmp/luce-probe-20260530-113432-pr-237`
- `/tmp/luce-probe-20260530-113432-pr-221`
- `/tmp/luce-probe-20260530-113432-pr-154`
- `/tmp/luce-probe-20260530-113432-pr-153`
- `/tmp/luce-probe-20260530-113432-pr-137`
- `/tmp/luce-probe-20260530-113432-pr-135`
- `/tmp/luce-probe-20260530-113432-pr-94`
- `/tmp/luce-probe-20260530-113432-pr-48`
- `/tmp/luce-merge-20260530-113432-305.log`
- `/tmp/luce-merge-20260530-113432-237.log`
- `/tmp/luce-merge-20260530-113432-221.log`
- `/tmp/luce-merge-20260530-113432-154.log`
- `/tmp/luce-merge-20260530-113432-153.log`
- `/tmp/luce-merge-20260530-113432-137.log`
- `/tmp/luce-merge-20260530-113432-135.log`
- `/tmp/luce-merge-20260530-113432-94.log`
- `/tmp/luce-merge-20260530-113432-48.log`
- External-agent logs: `/tmp/luce-claude-20260530-113432-pr-305.txt`, `/tmp/luce-claude-20260530-113432-pr-237.txt`, `/tmp/luce-codex-20260530-113432-pr-305.txt`, `/tmp/luce-codex-20260530-113432-pr-237.txt`.

## Notes

The next useful integration work remains two dedicated selective ports: first, a current-`server/` #237 MTP foundation port; second, a #305 Laguna/common-MoE hybrid port that preserves the current #289 Qwen35MoE path and #306/#310 layer-split/precision APIs. Keep #135 as a separate scheduler/batched-target selective port. #137 and #48 look like old `dflash/CMakeLists.txt` changes that should be closed or retargeted, and #94 appears largely superseded by current draft/SWA support. The #308 replay HTTP stub harness gives a useful CPU-only validation pattern for future API/wire-format fixes once the local CUDA configure blocker is bypassed or the deterministic Docker CUDA path is used.
