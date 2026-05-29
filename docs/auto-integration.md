# Auto-integration manifest

Repository: `Luce-Org/lucebox-hub`
Integration branch: `auto-integration`
Writable remote: `easel`
Upstream remote: `origin` / `Luce-Org`
Last refresh: 2026-05-29T02:11:21-04:00
Current base: `origin/main` `8782d07a`
Current integration tip before this refresh: `easel/auto-integration` `717f805e`
Manifest refresh commit prepared in this run: this commit

This branch is maintained as a reproducible patch stack over `origin/main`.
At this run's start `easel/auto-integration` was already based on current
`origin/main` (`0` behind / `393` ahead), so no base reconciliation merge was
needed. Open non-draft PR refs were refreshed, and all already-carried open
non-draft PR heads remain ancestors of the stack. The remaining non-draft PRs
were re-probed in fresh worktrees; #237 also received a fresh tmux-driven
Claude/Codex feasibility pass. The conflicted PRs still require selective
current-layout ports or closure/retarget decisions as recorded below.

## Included in the current stack

| PR | Head branch | Head | State | Notes |
|---:|---|---:|---|---|
| #303 | `fix/harness-portable-run-dirs` | upstream `05b008a0` | included through upstream and stack | Harness portable run/cache directories and automatic client-install fallback are in `origin/main`; the stack preserved local compatibility docs and helpers. |
| #302 | `fix/harness-model-paths` | upstream | included through upstream | Harness launcher model-path override behavior and documentation are in `origin/main`. |
| #301 | `fix/ddtree-test-harness` | upstream | included through upstream | DDTree test harness fixes are in `origin/main`. |
| #300 | `fix/sigterm-gpu-unload` | upstream | included through upstream | SIGTERM GPU-unload fix remains in upstream. |
| #299 | `feat/draft-swa-flag` | upstream | included through upstream | Draft SWA env/flag support remains in upstream. |
| #298 | `fix/gemma4-destructor-link` | upstream | included through upstream | Gemma4 destructor-link fix remains in upstream. |
| #292 | `feat-backend-ipc-payload-pipe-open` | upstream / `90bc52f` | included through upstream and stack | Backend IPC payload-pipe support is upstream and still represented in the carried stack history. |
| #297 | `feat-server-laguna-layer-split-adapter-v2` | `53dd1686` | included / draft at final check | Laguna target-layer-split adapter remains carried as an already-integrated draft dependency. |
| #295 | `fix-layer-split-sampling` | `a9aedf7d` | included | Target layer-split sampling support remains an ancestor of the stack. |
| #294 | `feat/server-passthrough-proxy` | `0883c2ef` | included | Server passthrough proxy wiring, piecewise keep-ratio curve, query survival checks, and unit coverage are carried. |
| #289 | `pipeline_moe` | `0ffab8a1` | included | Pipelined hybrid Qwen35 MoE decode update remains an ancestor of the stack. |
| #285 | `feat/lucebox-docker` | `09dc0bed` | included | Docker stack, `lucebox` CLI, bench/profile tooling, harness clients, `luce-bench`, and follow-up `model_info` download handling are carried. |
| #276 | `fix/qwen36-claude-code-tool-calling` | `5e861b4d` | included | Qwen3.6-27B tool-calling fix for Claude-code Anthropic path is carried. |
| #274 | `feat/pflash-drafter-ee7` | `e64a2b80` | included | Adaptive pFlash composition, EE7/drafter updates, docs, tests, and follow-up fixes are carried. |
| #266 | `feat/harness-typed-adapters` | `17525eae` | included | Typed harness adapters and format-aware session-inject proxy are carried. |
| #152 | `main` | `cf735bee` | included | Gemma 4 RTX 4090 backend helpers are carried. |
| #142 | `xabicasa/dflash-safetensors-draft-fp16` | `f2fbf62f` | included | FP16 safetensors drafter support is carried. |

## Validation run

This run performed:

- `date -Is` -> `2026-05-29T02:11:21-04:00`.
- Primary checkout preflight: `git status --short` was clean; branch was `auto-integration`; remotes were `origin=https://github.com/Luce-Org/lucebox-hub` and `easel=https://github.com/easel/lucebox-hub`.
- Auth/tooling checks with real user credentials succeeded: `gh auth status`, `claude auth status --text`, and `codex --version` (`codex-cli 0.130.0`).
- `git fetch --prune origin` and `git fetch --prune easel` completed successfully.
- Open PR enumeration used `gh pr list --repo Luce-Org/lucebox-hub --state open --limit 200 --json number,title,author,isDraft,headRefName,headRepositoryOwner,headRepository,baseRefName,mergeable,updatedAt,url --jq ...`.
- Fetched open non-draft PR refs explicitly: #295, #294, #289, #285, #276, #274, #266, #237, #221, #154, #153, #152, #142, #137, #135, #94, and #48.
- `git rev-list --left-right --count origin/main...easel/auto-integration` reported `0` behind and `393` ahead.
- `git merge-base --is-ancestor` checks pass for carried open non-draft PR refs: #295, #294, #289, #285, #276, #274, #266, #152, and #142.
- Reconciliation worktree `/tmp/luce-auto-cron-20260529-021121/reconcile` was created from `easel/auto-integration`; `origin/main` is already an ancestor and no base merge was required.
- Fresh direct merge probes from `easel/auto-integration` were created in `/tmp/luce-auto-cron-20260529-021121/` for #237, #221, #154, #153, #137, #135, #94, and #48. All still conflict in the conflict classes recorded below.
- Fresh delegation for #237: Claude Code ran in tmux session `luce237-20260529-021121-claude` and exited with `Error: Reached max turns (16)` without a usable report. Codex then ran in tmux session `luce237-20260529-021121-codex` and produced `/tmp/luce237-20260529-021121-codex-report.txt`; it made no edits and confirmed direct merge is unsafe because #237's backend creation, Qwen35 loading, target graph/capture plumbing, decode orchestration, server flags, and tests must be selectively ported into the current PFlash/MoE/layer-split/native-server layout.
- Verification after the manifest update: `git diff --check` passed in the reconciliation worktree. No build/test suite was run because this run changed only this manifest; conflicted probe worktrees are intentionally unbuildable until selective ports are authored.

## Pending / blocked-needs-human / selective-port candidates

| PR | Head branch | Head | Current status | Probe result / next useful action |
|---:|---|---:|---|---|
| #237 | `feat/dflash-mtp-foundation` | `02c6a6c4` | blocked-needs-human / salvage-port | Fresh probe worktree `/tmp/luce-auto-cron-20260529-021121/pr-237-probe` has old-layout delete/update conflicts in `dflash/scripts/server.py`, `dflash/src/common/backend_factory.cpp`, and `dflash/src/server/server_main.cpp`; file-location conflicts for MTP common/Qwen35 files and `server/test/test_common_mtp_orchestrator.cpp`; plus semantic conflicts in `server/CMakeLists.txt`, backend factory/model/step graph, qwen35 loader/graph/backend/dflash target, and `server/test/test_dflash.cpp`. Fresh Codex review says direct merge is unsafe; port first as a current-layout MTP foundation preserving current qwen35moe, layer-split, remote draft, PFlash, budget hooks, and MoE/router capture plumbing. |
| #221 | `feat/mtp-prefix-warm-ghost` | `05502974` | blocked-needs-human / dependent salvage-port | Fresh probe worktree `/tmp/luce-auto-cron-20260529-021121/pr-221-probe` conflicts on old `dflash/` scripts/backend files; `server/src/common/dflash_target.h`, `model_backend.h`, `step_graph.h`, `gguf_mmap.h`; MTP file-location paths; Qwen35 loader/graph/backend/dflash target areas; and `server/test/test_dflash.cpp` / MTP tests. Port #237-equivalent MTP foundation first, then mine #221 for prefix-cache MTP WARM behavior, snapshot/restore head KV, partial/range warm, warm-completion callback, dispatcher/PFlash protocol, and `server/test/test_prefix_cache_mtp.cpp` coverage. |
| #154 | `xabicasa/dflash-mtp-speculative-loop` | `2f4ede79` | blocked-needs-human / dependency | Fresh probe worktree `/tmp/luce-auto-cron-20260529-021121/pr-154-probe` conflicts on old `dflash/CMakeLists.txt`, file-location moves for MTP docs/tests and `f16_convert.cu`, plus semantic conflicts in `internal.h`, `gguf_target_loader.cpp`, `qwen35_target_graph.cpp`, and `test_dflash.cpp`. Mine linear MTP decode semantics after current-layout Qwen35 MTP exists. |
| #153 | `xabicasa/dflash-mtp-integrated` | `e9b17cb1` | blocked-needs-human / dependency | Fresh probe worktree `/tmp/luce-auto-cron-20260529-021121/pr-153-probe` conflicts on old CMake, moved MTP docs/tests and `f16_convert.cu`, and the same core Qwen35/internal target files. Mine loader/graph/cache/test ideas after current-layout Qwen35 MTP exists. |
| #135 | `xabicasa/dflash-multi-request-scheduler-batched-target-step` | `561b0ac1` | blocked-needs-human / selective-port | Fresh probe worktree `/tmp/luce-auto-cron-20260529-021121/pr-135-probe` has semantic conflicts in `server/src/internal.h`, `server/src/qwen35/qwen35_target_graph.cpp`, and `server/test/test_dflash.cpp`. Prior Codex analysis remains applicable: direct merge is unsafe; surviving behavior should be selectively ported as multi-request target cache slots, tagged stream protocol, native quantum scheduler commands, and batched target-step graph support into current daemon/backend/graph-builder boundaries while preserving TargetLoadPlan, partial layer cache allocation, MoE router capture, `last_token_logits_only`, rotated KV, extracted graph builders, and backend-level prefill/decode. |
| #137 | `xabicasa/dflash-build-cmake-sm89-bsa` | `297fc74e` | suggested-close/superseded | Fresh probe worktree `/tmp/luce-auto-cron-20260529-021121/pr-137-probe` only conflicts on deleted old `dflash/CMakeLists.txt`. Ask author to close or retarget to current `server/CMakeLists.txt` if anything remains. |
| #94 | `feat/dflash-qwen36-swa-draft` | `d2f9c9dd` | suggested-close/superseded | Fresh probe worktree `/tmp/luce-auto-cron-20260529-021121/pr-94-probe` conflicts in `server/src/draft/draft_graph.cpp`, `draft_safetensors_loader.cpp`, and `server/src/internal.h`; useful behavior appears absorbed by current draft/SWA support. Ask author/maintainers whether any remaining old-layout tests should be reauthored before close. |
| #48 | `fix/consumer-blackwell-auto-detect` | `858b84b6` | suggested-close/superseded | Fresh probe worktree `/tmp/luce-auto-cron-20260529-021121/pr-48-probe` only conflicts on deleted old `dflash/CMakeLists.txt`. Close or retarget to current `server/CMakeLists.txt` if still needed. |

## Draft / excluded

Draft PRs remain outside the primary non-draft integration target except for
dependency awareness: #304, #297, #291, #290, #275, #249, and #193. #297 is
still carried as an already-integrated draft dependency.

## Retained worktrees / logs

The conflicted probe worktrees were intentionally retained for manual follow-up
because safe cleanup would require resolving or discarding conflicted indexes:

- `/tmp/luce-auto-cron-20260529-021121/pr-237-probe`
- `/tmp/luce-auto-cron-20260529-021121/pr-221-probe`
- `/tmp/luce-auto-cron-20260529-021121/pr-154-probe`
- `/tmp/luce-auto-cron-20260529-021121/pr-153-probe`
- `/tmp/luce-auto-cron-20260529-021121/pr-137-probe`
- `/tmp/luce-auto-cron-20260529-021121/pr-135-probe`
- `/tmp/luce-auto-cron-20260529-021121/pr-94-probe`
- `/tmp/luce-auto-cron-20260529-021121/pr-48-probe`

The clean reconciliation worktree `/tmp/luce-auto-cron-20260529-021121/reconcile`
was also left in place to avoid worktree force-deletion in an unattended run.

Agent reports/logs retained:

- `/tmp/luce237-20260529-021121-claude-report.txt` (Claude Code max-turns without usable report for #237)
- `/tmp/luce237-20260529-021121-codex-report.txt` (fresh Codex selective-port feasibility report for #237)
- Prior run reports remain useful: `/tmp/luce135-20260529-015226-codex-report.txt`, `/tmp/luce237-luce-auto-cron-20260529-011930-codex-report.txt`, and `/tmp/luce135-20260529-010054-codex-report.txt`.

## Notes

No new non-draft PR head required direct integration in this refresh; the branch
already included all current non-draft PRs that are safe direct-stack ancestors.
The next useful work remains a human-reviewed selective port of #237's MTP
foundation into the current `server/` layout. After that, mine #221's
WARM-cache/dispatcher behavior and #153/#154's native/integrated MTP semantics.
#135 remains a separate selective current-layout port focused on scheduler/cache
slots, tagged streams, and batched target-step support. #137 and #48 look like
old `dflash/CMakeLists.txt` changes that should be closed or retargeted, and
#94 appears largely superseded by current draft/SWA support.
