# Auto-integration manifest

Repository: `Luce-Org/lucebox-hub`
Integration branch: `auto-integration`
Writable remote: `easel`
Upstream remote: `origin` / `Luce-Org`
Last refresh: 2026-05-29T20:14:26-04:00
Current base: `origin/main` `8782d07a`
Current integration tip before this refresh: `easel/auto-integration` `cd155cf0`
Manifest refresh and unresolved-PR probe update prepared in this run: this commit

This branch is maintained as a reproducible patch stack over `origin/main`. This unattended run started from a clean primary checkout on `auto-integration`, verified GitHub/Claude/Codex auth with the real user credential home, fetched `origin` and `easel` separately, reconciled a worktree from `easel/auto-integration`, confirmed `origin/main` was already included, and performed fresh direct-merge probing in `/tmp/luce-auto-cron-20260529-200529/probes/pr-*-probe` worktrees.

No new non-draft contributor PR head required a stack rewrite in this run. The current stack already contains the latest heads of #310, #309, #307, #306, #297, #295, #294, #289, #285, #276, #274, #266, #152, and #142. Fresh direct-merge probes for the remaining old-layout PRs still conflict. Claude was delegated through tmux to attempt a bounded #237 current-layout salvage port in `/tmp/luce-auto-cron-20260529-200529/probes/pr-237-salvage-claude`, but exited at `--max-turns 20` without producing the requested report or file changes. Codex was then delegated through tmux to inspect the #237 conflicted probe and produced a usable read-only report at `/tmp/luce-auto-cron-20260529-200529/probes/codex-pr237-current-report.txt`: direct merge is unsafe, but a manual current-layout MTP foundation port is feasible in staged slices.

## Included in the current stack

| PR | Head branch | Head | State | Notes |
|---:|---|---:|---|---|
| #310 | `feat-backend-activation-precision-policy-after-306` | `bf9f4b57` | included | Backend activation precision policy / graph tensor precision helpers are carried. |
| #309 | `experiment-dflash-feature-dtype` | `ea6ac481` | included | Feature mirror dtype policy is carried. |
| #307 | `docs/why-this-exists-copy` | `236fc2fd` | included | README “Why this exists” copy remains preserved. |
| #306 | `refactor-server-layer-split-runtime` | `988fc933` | included | Shared layer-split runtime helper extraction remains carried; #310 is stacked after it. |
| #303 | `fix/harness-portable-run-dirs` | upstream `05b008a0` | included through upstream and stack | Harness portable run/cache directories and automatic client-install fallback are in `origin/main`; stack compatibility docs/helpers remain carried. |
| #302 | `fix/harness-model-paths` | upstream | included through upstream | Harness launcher model-path override behavior and documentation are in `origin/main`. |
| #301 | `fix/ddtree-test-harness` | upstream | included through upstream | DDTree test harness fixes are in `origin/main`. |
| #300 | `fix/sigterm-gpu-unload` | upstream | included through upstream | SIGTERM GPU-unload fix remains in upstream. |
| #299 | `feat/draft-swa-flag` | upstream | included through upstream | Draft SWA env/flag support remains in upstream. |
| #298 | `fix/gemma4-destructor-link` | upstream | included through upstream | Gemma4 destructor-link fix remains in upstream. |
| #292 | `feat-backend-ipc-payload-pipe-open` | upstream / `90bc52f` | included through upstream and stack | Backend IPC payload-pipe support is upstream and still represented in carried stack history. |
| #297 | `feat-server-laguna-layer-split-adapter-v2` | `53dd1686` | included | Laguna target-layer-split adapter remains carried. |
| #295 | `fix-layer-split-sampling` | `a9aedf7d` | included | Target layer-split sampling support remains an ancestor of the stack. |
| #294 | `feat/server-passthrough-proxy` | `48f6962d` | included | Server passthrough proxy wiring, piecewise keep-ratio curve, query survival checks, multimodal last-user text extraction, curl cleanup, and unit coverage are carried. |
| #289 | `pipeline_moe` | `27bad6d3` | included | Pipelined hybrid Qwen35 MoE decode update plus sub-batch hybrid prefill FFN MMQ-bounds fix are carried. |
| #285 | `feat/lucebox-docker` | `9a6db60e` | included | Latest Docker stack / `lucebox` CLI / bench-profile / harness / `luce-bench` refresh is carried, including card-driven thinking-control and client-side thinking-budget updates; the branch also brings the Qwen3.6/Laguna reasoning-channel commits from draft #308. |
| #276 | `fix/qwen36-claude-code-tool-calling` | `5e861b4d` | included | Qwen3.6-27B tool-calling fix for Claude-code Anthropic path is carried. |
| #274 | `feat/pflash-drafter-ee7` | `8c1f37d` | included | Latest adaptive pFlash composition plus effective-size admission/keep-ratio guard update is carried. |
| #266 | `feat/harness-typed-adapters` | `17525eae` | included | Typed harness adapters and format-aware session-inject proxy are carried. |
| #152 | `main` | `cf735bee` | included | Gemma 4 RTX 4090 backend helpers are carried. |
| #142 | `xabicasa/dflash-safetensors-draft-fp16` | `f2fbf62f` | included | FP16 safetensors drafter support is carried. |

## Validation run

This run performed:

- `date -Is` -> `2026-05-29T20:04:56-04:00` at preflight and `2026-05-29T20:14:26-04:00` for manifest refresh.
- Primary checkout preflight: `git status --short` was clean; branch was `auto-integration`; remotes were `origin=https://github.com/Luce-Org/lucebox-hub` and `easel=https://github.com/easel/lucebox-hub`.
- Auth/tooling checks with real user credentials succeeded: `gh auth status`, `claude auth status --text`, and harmless `codex --help`.
- `git fetch --prune origin` and `git fetch --prune easel` completed successfully.
- Open PR enumeration used `gh pr list --repo Luce-Org/lucebox-hub --state open --limit 200 --json ... --jq ...` and found 30 open PRs total: 22 non-draft and 8 draft/excluded.
- Open non-draft PR refs were fetched individually to `refs/remotes/origin/pr/<n>`.
- Containment checks confirmed #310, #309, #307, #306, #297, #295, #294, #289, #285, #276, #274, #266, #152, and #142 are ancestors of the current integration stack; #237, #221, #154, #153, #137, #135, #94, and #48 are not ancestors and remain classified below.
- `origin/main` remains included; merging `origin/main` into the reconciliation worktree reported `Already up to date`.
- Fresh probe worktrees attempted direct merges for every non-integrated non-draft PR. All eight still conflict in old-layout or dependent MTP/scheduler areas; logs are retained under `/tmp/luce-auto-cron-20260529-200529/probes/pr-*-merge.log`.
- Delegation check: Claude was launched through tmux for a bounded #237 salvage-port attempt and failed with `Error: Reached max turns (20)` in `/tmp/luce-auto-cron-20260529-200529/probes/claude-pr237-salvage-stdout.txt`, with no requested report and no repo file changes.
- Delegation check: Codex was launched through tmux for #237 in `/tmp/luce-auto-cron-20260529-200529/probes/pr-237-probe` and wrote `/tmp/luce-auto-cron-20260529-200529/probes/codex-pr237-current-report.txt`. The report says a minimal current-layout MTP foundation port is feasible only as a manual port, not as direct merge. Safe slices are: additive default-off API surface; PR-only MTP files under current `server/`; `gguf_contains_mtp_tensors()` / MTP source resolution ported into current `server/src/common/backend_factory.cpp`; native-server MTP CLI flags ported into current `server/src/server/server_main.cpp`; graph plumbing that keeps both MoE-router capture and MTP hidden capture; disabled-by-default Qwen35 MTP path; and `test_common_mtp_orchestrator` only after library compile success.
- Verification for the final manifest-only update: `git diff --check` passed. No code changed in this run, so the prior targeted `luce-bench` result (`108 passed in 1.64s` on the current #285 head) remains the latest code-test signal.

## Pending / blocked-needs-human / selective-port candidates

| PR | Head branch | Head | Current status | Probe result / next useful action |
|---:|---|---:|---|---|
| #237 | `feat/dflash-mtp-foundation` | `02c6a6c4` | blocked-needs-human / human-scale salvage-port | Fresh direct-merge probe still conflicts across deleted old `dflash/` server/backend files plus current `server/CMakeLists.txt`, backend factory, MTP common files, Qwen35 loader/graph/backend/dflash target/MTP files, and tests. Fresh Claude salvage attempt hit max turns without a report. Fresh tmux Codex report confirms direct merge is unsafe but provides a concrete staged manual port path: inert default-off API surface, PR-only MTP files in current `server/`, factory and native-server CLI ports, combined MoE-router + MTP hidden graph plumbing, disabled-by-default Qwen35 MTP, then tests. |
| #221 | `feat/mtp-prefix-warm-ghost` | `05502974` | blocked-needs-human / dependent salvage-port | Fresh direct-merge probe still conflicts in old `dflash/` scripts/backend plus current MTP/common/prefix-cache/Qwen35 files and tests. Prior Codex report says no small safe buildable prefix-warm slice should be extracted now: mine prefix-cache WARM behavior only after a current-layout #237-equivalent MTP foundation lands. |
| #154 | `xabicasa/dflash-mtp-speculative-loop` | `2f4ede79` | blocked-needs-human / dependency | Fresh probe conflicts in old `dflash/CMakeLists.txt`, MTP docs, CUDA/internal/Qwen35 graph/loader files, and MTP smoke/contract tests. Mine linear MTP decode semantics after current-layout Qwen35 MTP exists. |
| #153 | `xabicasa/dflash-mtp-integrated` | `e9b17cb1` | blocked-needs-human / dependency | Fresh probe conflicts in old `dflash/CMakeLists.txt`, MTP docs, CUDA/internal/Qwen35 graph/loader files, and MTP smoke/contract tests. Mine loader/graph/cache/test ideas after current-layout Qwen35 MTP exists. |
| #135 | `xabicasa/dflash-multi-request-scheduler-batched-target-step` | `561b0ac1` | blocked-needs-human / selective-port | Fresh probe conflicts in `server/src/internal.h`, `server/src/qwen35/qwen35_target_graph.cpp`, and `server/test/test_dflash.cpp`. Prior tmux Codex report confirms direct marker resolution is unsafe: the PR's old `dflash27b` graph/test implementation would overwrite current layer-split, MoE/qwen35moe, rotated-KV, prefix-snapshot, feature-mirror, `last_token_logits_only`, and helper extraction. Salvage batched scratch caches, `n_seqs` graph propagation, tagged stream frames, request commands, fair aligned-bucket scheduling, multiple qwen35 cache slots, and batched one-token target probes into current daemon/backend architecture with qwen35/qwen35moe/layer-split gates. |
| #137 | `xabicasa/dflash-build-cmake-sm89-bsa` | `297fc74e` | suggested-close/superseded | Fresh probe only conflicts on deleted old `dflash/CMakeLists.txt`; ask author to close or retarget to current `server/CMakeLists.txt` if anything remains. |
| #94 | `feat/dflash-qwen36-swa-draft` | `d2f9c9dd` | suggested-close/superseded | Fresh probe conflicts in current draft/internal files, but prior tmux-driven Codex report `/tmp/luce94-codex-2026-05-29-090910-report.txt` concluded the useful behavior is already present in current auto-integration. Suggested close or author retarget with a minimal delta if still needed. |
| #48 | `fix/consumer-blackwell-auto-detect` | `858b84b6` | suggested-close/superseded | Fresh probe only conflicts on deleted old `dflash/CMakeLists.txt`; close or retarget to current `server/CMakeLists.txt` if still needed. |

## Draft / excluded

Draft PRs remain outside the primary non-draft integration target except for dependency awareness: #308, #305, #304, #291, #290, #275, #249, and #193. Draft #308's current reasoning-channel changes are nevertheless included through non-draft #285's current head.

## Retained worktrees / logs

This run retained all worktrees/logs for audit because probe worktrees contain conflicted indexes and safe cleanup is left to a supervised pass:

- `/tmp/luce-auto-cron-20260529-200529/reconcile`
- `/tmp/luce-auto-cron-20260529-200529/probes/pr-237-probe`
- `/tmp/luce-auto-cron-20260529-200529/probes/pr-221-probe`
- `/tmp/luce-auto-cron-20260529-200529/probes/pr-154-probe`
- `/tmp/luce-auto-cron-20260529-200529/probes/pr-153-probe`
- `/tmp/luce-auto-cron-20260529-200529/probes/pr-137-probe`
- `/tmp/luce-auto-cron-20260529-200529/probes/pr-135-probe`
- `/tmp/luce-auto-cron-20260529-200529/probes/pr-94-probe`
- `/tmp/luce-auto-cron-20260529-200529/probes/pr-48-probe`
- `/tmp/luce-auto-cron-20260529-200529/probes/pr-237-salvage-claude`
- `/tmp/luce-auto-cron-20260529-200529/probes/pr-*-merge.log`
- `/tmp/luce-auto-cron-20260529-200529/probes/claude-pr237-salvage-stdout.txt` (Claude max-turns failure, no requested report)
- `/tmp/luce-auto-cron-20260529-200529/probes/codex-pr237-current-report.txt` (usable read-only #237 current-layout port report)

Useful prior probe/delegation artifacts remain for unresolved old-layout PRs:

- `/tmp/luce-auto-cron-20260529-193652/probes/codex-pr237-report.txt` (usable read-only #237 feasibility report)
- `/tmp/luce-auto-cron-20260529-181411/codex-pr221-report.txt` (usable read-only #221 salvage report)
- `/tmp/luce-auto-cron-20260529-175557/codex-pr237-report.txt` (usable read-only #237 salvage report)
- `/tmp/luce-auto-cron-20260529-164134/codex-pr237-salvage-report.txt` (usable read-only salvage audit)
- `/tmp/luce-auto-cron-20260529-145519/codex-pr135-report.txt` (usable read-only salvage note)
- `/tmp/luce-auto-cron-20260529-143520/codex-pr237-report.txt` (usable read-only salvage note)
- `/tmp/luce237b-20260529-092711-claude-report.txt` (usable read-only feasibility report)
- `/tmp/luce135-20260529-092711-codex-report.txt` (usable read-only feasibility report)
- `/tmp/luce-auto-cron-20260529-103040/codex-pr135-narrow-report.txt` (usable read-only salvage plan)
- `/tmp/luce221-codex-084947-report.txt` (usable read-only feasibility report)
- `/tmp/luce94-codex-2026-05-29-090910-report.txt` (usable read-only superseded/close report)

## Notes

The next useful integration work is now concrete: start a staged manual #237 current-layout MTP foundation port from a clean auto-integration worktree using the fresh Codex slice order, then attempt #221/#153/#154 MTP follow-ups after the foundation compiles. Keep #135 as a separate scheduler/batched-target selective port. #137 and #48 look like old `dflash/CMakeLists.txt` changes that should be closed or retargeted, and #94 appears largely superseded by current draft/SWA support.
