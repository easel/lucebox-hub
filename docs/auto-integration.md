# Auto-integration manifest

Repository: `Luce-Org/lucebox-hub`
Integration branch: `auto-integration`
Writable remote: `easel`
Upstream remote: `origin` / `Luce-Org`
Last refresh: 2026-05-30T06:06:00-04:00
Current base: `origin/main` `c95dfcab`
Previous integration tip: `easel/auto-integration` `77194cb9`
Latest integration tip before this refresh: `77194cb9`

This branch is maintained as a reproducible patch stack over `origin/main`. This unattended run started from a clean primary checkout on `auto-integration`, verified GitHub/Claude/Codex auth with the real user credential home, fetched `origin` and `easel` separately, checked the current `easel/auto-integration` tip in `/tmp/luce-auto-cron-20260530-055956`, confirmed it is already up to date with `origin/main`, and rechecked all open non-draft PR heads by exact containment.

New in this refresh: no open PR head or `origin/main` SHA changed since the previous refresh. The integration branch remains at `origin/main` `c95dfcab` plus the selected PR stack. Fresh direct-merge probes still show the same old-layout MTP/scheduler conflict set outside exact containment. A fresh tmux-driven Codex assessment produced a usable #135 selective-port plan; Claude reached its turn limit for #135 without a usable report.

## Included in the current non-draft stack

| PR | Head branch | Head | State | Notes |
|---:|---|---:|---|---|
| #311 | `fix/prefix-cache-recurrent-state` | upstream `d0bdef72` merge | included through upstream | Prefix-cache/spec-decode fix is now in `origin/main` and therefore carried by the stack base. |
| #310 | `feat-backend-activation-precision-policy-after-306` | `bf9f4b57` | included | Backend activation precision policy / graph tensor precision helpers are carried exactly. |
| #309 | `experiment-dflash-feature-dtype` | `ea6ac481` | included | Feature mirror dtype policy is carried exactly. |
| #307 | `docs/why-this-exists-copy` | upstream `c95dfcab` merge | included through upstream | README “Why this exists” copy is now in `origin/main` and therefore carried by the stack base. |
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
| #285 | `feat/lucebox-docker` | `3dffb306` | included | Refreshed Docker stack / `lucebox` CLI / harness / `luce-bench`, plus Bragi sweep docs and autotune/sweep updates, are carried exactly. |
| #276 | `fix/qwen36-claude-code-tool-calling` | `5e861b4d` | included | Qwen3.6-27B tool-calling fix for Claude-code Anthropic path is carried exactly. |
| #274 | `feat/pflash-drafter-ee7` | `8c1f37db` | included | Adaptive pFlash composition and effective-size admission/keep-ratio guard update are carried exactly. |
| #266 | `feat/harness-typed-adapters` | `17525eae` | included | Typed harness adapters and format-aware session-inject proxy are carried exactly. |
| #152 | `main` | `cf735bee` | included | Gemma 4 RTX 4090 backend helpers are carried exactly. |
| #142 | `xabicasa/dflash-safetensors-draft-fp16` | `f2fbf62f` | included | FP16 safetensors drafter support is carried exactly. |

## Validation run

This run performed:

- `date -Is` -> `2026-05-30T05:59:56-04:00` during preflight and `2026-05-30T06:06:00-04:00` for manifest refresh metadata.
- Primary checkout preflight: `git status --short` was clean; branch was `auto-integration`; remotes were `origin=https://github.com/Luce-Org/lucebox-hub` and `easel=https://github.com/easel/lucebox-hub`.
- Auth/tooling checks with real user credentials succeeded: `gh auth status`, `claude auth status --text`, and `codex --version`.
- `git fetch --prune origin` and `git fetch --prune easel` completed successfully.
- Open PR enumeration used `gh pr list --repo Luce-Org/lucebox-hub --state open --limit 200 --json ... --jq ...` and found 21 open non-draft PRs plus 9 draft/excluded PRs.
- Open non-draft PR refs were fetched individually to `refs/remotes/origin/pr/<n>`.
- Containment checks against `easel/auto-integration` confirmed #310, #309, #306, #297, #295, #294, #289, #285, #276, #274, #266, #152, and #142 are exact ancestors of the current integration stack; #237, #221, #154, #153, #137, #135, #94, and #48 are not ancestors and remain classified below. #311 and #307 remain included through `origin/main`.
- Reconciliation worktree `/tmp/luce-auto-cron-20260530-055956` was created from `easel/auto-integration`; `git merge --no-edit origin/main` reported `Already up to date`.
- Fresh probe worktrees attempted direct merges for #237, #221, #154, #153, #137, #135, #94, and #48. All eight still conflict in old-layout or dependent MTP/scheduler areas; worktrees are retained under `/tmp/luce-auto-cron-20260530-055956/probes/`.
- Fresh tmux-driven Claude delegation for #135 (`luce-pr135-claude-202605300559`) exited with `Error: Reached max turns (6)` and produced no usable feasibility summary.
- Fresh tmux-driven Codex delegation for #135 (`luce-pr135-codex-202605300602`) produced a usable feasibility summary at `/tmp/luce-auto-cron-20260530-055956/codex-pr135-assessment.txt`; no edits were accepted from the agent. Codex recommends a manual selective port using `HEAD` as spine: resolve `internal.h` first, then port `n_seqs`/4D cache/batched `target_feat` support into the current `qwen35_target_graph.cpp`, then transplant scheduler bucket/tagged-streaming/multi-slot/batch probe behavior into the current `test_dflash.cpp`.

## Pending / blocked-needs-human / selective-port candidates

| PR | Head branch | Head | Current status | Probe result / next useful action |
|---:|---|---:|---|---|
| #237 | `feat/dflash-mtp-foundation` | `02c6a6c4` | blocked-needs-human / human-scale server-layout port | Fresh direct-merge probe still conflicts across old `dflash/` files and current `server/` files including CMake, backend factory, common MTP interfaces, Qwen35 graph/loader/backend, and tests. Direct merge is not viable; selective port remains feasible: port MTP source/config routing, interfaces/runner, Qwen35 MTP graph/loader, hidden capture accessors, GGUF `nextn_predict_layers`, and non-GPU orchestrator tests while preserving current MoE, layer-split, remote-draft, pFlash/C2, budget, and native server behavior. |
| #221 | `feat/mtp-prefix-warm-ghost` | `05502974` | blocked-needs-human / dependent salvage-port | Fresh direct-merge probe still conflicts in old `dflash/` scripts/backend plus current MTP/common/prefix-cache/Qwen35 files and tests. Mine prefix-cache WARM behavior only after a current-layout #237-equivalent MTP foundation lands. |
| #154 | `xabicasa/dflash-mtp-speculative-loop` | `2f4ede79` | blocked-needs-human / dependency | Fresh probe conflicts in old `dflash/CMakeLists.txt`, MTP docs, CUDA/internal/Qwen35 graph/loader files, and MTP smoke/contract tests. Mine linear MTP decode semantics after current-layout Qwen35 MTP exists. |
| #153 | `xabicasa/dflash-mtp-integrated` | `e9b17cb1` | blocked-needs-human / dependency | Fresh probe conflicts in old `dflash/CMakeLists.txt`, MTP docs, CUDA/internal/Qwen35 graph/loader files, and MTP smoke/contract tests. Mine loader/graph/cache/test ideas after current-layout Qwen35 MTP exists. |
| #135 | `xabicasa/dflash-multi-request-scheduler-batched-target-step` | `561b0ac1` | blocked-needs-human / selective-port | Fresh direct probe conflicts in `server/src/internal.h`, `server/src/qwen35/qwen35_target_graph.cpp`, and `server/test/test_dflash.cpp`. Fresh Codex assessment says salvage is plausible but manual: use current `HEAD` as spine, preserve current partial-cache/runtime hparams/MoE/layer-split/common namespace behavior, port PR batching (`n_seqs`, 4D cache views, batched `target_feat`) into Qwen35 graph code, then transplant scheduler bucket, tagged streaming, target cache slot, synthetic prompt, batch probe/commit, and debug flag behavior into current tests/server flow. Direct merge remains unsafe. |
| #137 | `xabicasa/dflash-build-cmake-sm89-bsa` | `297fc74e` | suggested-close/superseded | Fresh probe only conflicts on deleted old `dflash/CMakeLists.txt`; ask author to close or retarget to current `server/CMakeLists.txt` if anything remains. |
| #94 | `feat/dflash-qwen36-swa-draft` | `d2f9c9dd` | suggested-close/superseded | Fresh probe conflicts in current draft/internal files; prior review found the useful SWA/draft behavior is already present in current auto-integration. Suggested close or author retarget with a minimal delta if still needed. |
| #48 | `fix/consumer-blackwell-auto-detect` | `858b84b6` | suggested-close/superseded | Fresh probe only conflicts on deleted old `dflash/CMakeLists.txt`; close or retarget to current `server/CMakeLists.txt` if still needed. |

## Draft / excluded

Draft PRs remain outside the primary non-draft integration target except for dependency awareness: #312, #308, #305, #304, #291, #290, #275, #249, and #193. Draft #312’s backend IPC payload transport appears related to already-carried IPC payload work but remains draft/excluded. Draft #308’s reasoning-channel work is represented through current #285 stack history where applicable.

## Retained worktrees / logs

This run retained worktrees/logs for audit because probe worktrees contain conflicted indexes and safe cleanup is left to a supervised pass:

- `/tmp/luce-auto-cron-20260530-055956`
- `/tmp/luce-auto-cron-20260530-055956/probes/pr-237-probe`
- `/tmp/luce-auto-cron-20260530-055956/probes/pr-221-probe`
- `/tmp/luce-auto-cron-20260530-055956/probes/pr-154-probe`
- `/tmp/luce-auto-cron-20260530-055956/probes/pr-153-probe`
- `/tmp/luce-auto-cron-20260530-055956/probes/pr-137-probe`
- `/tmp/luce-auto-cron-20260530-055956/probes/pr-135-probe`
- `/tmp/luce-auto-cron-20260530-055956/probes/pr-94-probe`
- `/tmp/luce-auto-cron-20260530-055956/probes/pr-48-probe`
- `/tmp/luce-auto-cron-20260530-055956/claude-pr135-assessment.txt`
- `/tmp/luce-auto-cron-20260530-055956/codex-pr135-assessment.txt`

## Notes

The next useful integration work remains a dedicated current-`server/` #237 port, not a direct merge. Add the interface/no-op surface first, then Qwen35 capture/rollback and common MTP tests, then follow with #221/#153/#154 MTP behavior after the foundation exists. Keep #135 as a separate scheduler/batched-target selective port; the fresh Codex plan suggests starting with `internal.h`, then Qwen35 batched tensor/cache shape support, then scheduler/tagged-streaming/multi-slot behavior in the current server/test flow. #137 and #48 look like old `dflash/CMakeLists.txt` changes that should be closed or retargeted, and #94 appears largely superseded by current draft/SWA support.
