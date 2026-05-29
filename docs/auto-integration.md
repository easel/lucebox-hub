# Auto-integration manifest

Repository: `Luce-Org/lucebox-hub`
Integration branch: `auto-integration`
Writable remote: `easel`
Upstream remote: `origin` / `Luce-Org`
Last refresh: 2026-05-29T05:46:07-04:00
Current base: `origin/main` `8782d07a`
Current integration tip before this refresh: `easel/auto-integration` `305d168f`
Manifest refresh commit prepared in this run: this commit, if non-empty

This branch is maintained as a reproducible patch stack over `origin/main`.
At this run's start the primary checkout was clean, `easel/auto-integration`
was already based on current `origin/main` (`0` behind / `413` ahead), and no
base reconciliation merge was needed. Open non-draft PR refs were refreshed.
No new non-draft contributor PR appeared since the previous refresh; #307 and
all currently direct-mergeable non-draft PRs already remain represented in the
stack. The remaining non-draft PRs were re-probed in fresh worktrees. They still
require selective current-layout ports or are superseded; no additional source
patch was safe to add automatically in this refresh.

## Included in the current stack

| PR | Head branch | Head | State | Notes |
|---:|---|---:|---|---|
| #307 | `docs/why-this-exists-copy` | `13dcf97b` | included | Sharpened README “Why this exists” copy remains merged; the PR head is an ancestor of the stack. |
| #303 | `fix/harness-portable-run-dirs` | upstream `05b008a0` | included through upstream and stack | Harness portable run/cache directories and automatic client-install fallback are in `origin/main`; the stack preserved local compatibility docs and helpers. |
| #302 | `fix/harness-model-paths` | upstream | included through upstream | Harness launcher model-path override behavior and documentation are in `origin/main`. |
| #301 | `fix/ddtree-test-harness` | upstream | included through upstream | DDTree test harness fixes are in `origin/main`. |
| #300 | `fix/sigterm-gpu-unload` | upstream | included through upstream | SIGTERM GPU-unload fix remains in upstream. |
| #299 | `feat/draft-swa-flag` | upstream | included through upstream | Draft SWA env/flag support remains in upstream. |
| #298 | `fix/gemma4-destructor-link` | upstream | included through upstream | Gemma4 destructor-link fix remains in upstream. |
| #292 | `feat-backend-ipc-payload-pipe-open` | upstream / `90bc52f` | included through upstream and stack | Backend IPC payload-pipe support is upstream and still represented in the carried stack history. |
| #297 | `feat-server-laguna-layer-split-adapter-v2` | `53dd1686` | included / draft at final check | Laguna target-layer-split adapter remains carried as an already-integrated draft dependency. |
| #295 | `fix-layer-split-sampling` | `a9aedf7d` | included | Target layer-split sampling support remains an ancestor of the stack. |
| #294 | `feat/server-passthrough-proxy` | `48f6962d` | included | Server passthrough proxy wiring, piecewise keep-ratio curve, query survival checks, multimodal last-user text extraction, curl cleanup, and unit coverage are carried. |
| #289 | `pipeline_moe` | `27bad6d3` | included | Pipelined hybrid Qwen35 MoE decode update plus sub-batch hybrid prefill FFN MMQ-bounds fix are carried. |
| #285 | `feat/lucebox-docker` | `09dc0bed` | included | Docker stack, `lucebox` CLI, bench/profile tooling, harness clients, `luce-bench`, and follow-up `model_info` download handling are carried. |
| #276 | `fix/qwen36-claude-code-tool-calling` | `5e861b4d` | included | Qwen3.6-27B tool-calling fix for Claude-code Anthropic path is carried. |
| #274 | `feat/pflash-drafter-ee7` | `e64a2b80` | included | Adaptive pFlash composition, EE7/drafter updates, docs, tests, and follow-up fixes are carried. |
| #266 | `feat/harness-typed-adapters` | `17525eae` | included | Typed harness adapters and format-aware session-inject proxy are carried. |
| #152 | `main` | `cf735bee` | included | Gemma 4 RTX 4090 backend helpers are carried. |
| #142 | `xabicasa/dflash-safetensors-draft-fp16` | `f2fbf62f` | included | FP16 safetensors drafter support is carried. |

## Validation run

This run performed:

- `date -Is` -> `2026-05-29T05:46:07-04:00` for preflight.
- Primary checkout preflight: `git status --short` was clean; branch was
  `auto-integration`; remotes were `origin=https://github.com/Luce-Org/lucebox-hub`
  and `easel=https://github.com/easel/lucebox-hub`.
- Auth/tooling checks with real user credentials succeeded: `gh auth status`,
  `claude auth status --text`, and Codex help smoke output.
- `git fetch --prune origin` and `git fetch --prune easel` completed successfully.
- Open PR enumeration used `gh pr list --repo Luce-Org/lucebox-hub --state open
  --limit 200 --json ... --jq ...` and found 27 open PRs total, 18 non-draft and
  9 draft/excluded.
- Fetched open non-draft PR refs explicitly: #307, #295, #294, #289, #285, #276,
  #274, #266, #237, #221, #154, #153, #152, #142, #137, #135, #94, and #48.
- `git rev-list --left-right --count origin/main...easel/auto-integration`
  reported `0` behind and `413` ahead at the start of this refresh.
- `git merge-base --is-ancestor` checks pass for carried open non-draft PR refs:
  #307, #295, #294, #289, #285, #276, #274, #266, #152, and #142.
- Reconciliation worktree `/tmp/luce-auto-cron-20260529-054636` was created from
  `easel/auto-integration`; merging `origin/main` reported `Already up to date`.
- Fresh direct merge probes from the current integration tip were created for
  #237, #221, #154, #153, #137, #135, #94, and #48. All still conflict in the
  classes recorded below.
- Claude delegation for #237 via tmux produced only `Error: Reached max turns (8)`
  and no usable report; this was treated as failed delegation, not evidence.
- Codex delegation for #237 via tmux produced `/tmp/luce237-20260529-054636-codex-report.txt`.
  It confirmed no small automatic merge is safe and identified missing current-layout
  behavior: remote draft IPC, layer-split adapters, `qwen35moe`, current native
  server CLI/properties, PFlash C2 fallback, thinking-budget hooks, accept-rate
  telemetry, snapshot restore behavior, and Lucebox/container MTP knob exposure.
- Manifest-only validation: `git diff --check -- docs/auto-integration.md` passed.

## Pending / blocked-needs-human / selective-port candidates

| PR | Head branch | Head | Current status | Probe result / next useful action |
|---:|---|---:|---|---|
| #237 | `feat/dflash-mtp-foundation` | `02c6a6c4` | blocked-needs-human / salvage-port | Fresh probe worktree `/tmp/luce-auto-cron-20260529-054636/pr-237-probe` conflicts in old-layout `dflash/` server/backend files plus current `server/CMakeLists.txt`, common MTP files, Qwen35 loader/graph/backend/dflash target files, and tests. Codex confirmed a small automatic merge is unsafe. Port old `dflash/src/*` behavior into current `server/src/*`, add MTP GGUF/source selection in the current backend factory/server CLI, union StepGraph graph-builder hidden capture with MoE/router capture, preserve current PFlash/remote-draft/layer-split/`qwen35moe` paths, expose Lucebox/container MTP knobs, add `test_common_mtp_orchestrator`, and fix unresolved review comments before inclusion. |
| #221 | `feat/mtp-prefix-warm-ghost` | `05502974` | blocked-needs-human / dependent salvage-port | Fresh probe worktree `/tmp/luce-auto-cron-20260529-054636/pr-221-probe` conflicts on old `dflash/` scripts/backend files, current common/Qwen35 MTP, metadata, prefix snapshot, graph, and tests, and brings old benchmark/results assets. It depends on a PR-237-equivalent MTP foundation first; then mine WARM and partial/range prefix-cache restore, NextN head block handling, argmax OOB fix, request dispatcher, PFlash drafter protocol, `skip_park`, and tests. |
| #154 | `xabicasa/dflash-mtp-speculative-loop` | `2f4ede79` | blocked-needs-human / dependency | Fresh probe worktree `/tmp/luce-auto-cron-20260529-054636/pr-154-probe` conflicts on old `dflash/CMakeLists.txt`, moved MTP docs/tests and `f16_convert.cu`, plus core Qwen35/internal target files. Mine linear MTP decode semantics after current-layout Qwen35 MTP exists. |
| #153 | `xabicasa/dflash-mtp-integrated` | `e9b17cb1` | blocked-needs-human / dependency | Fresh probe worktree `/tmp/luce-auto-cron-20260529-054636/pr-153-probe` conflicts on old CMake, moved MTP docs/tests and `f16_convert.cu`, and the same core Qwen35/internal target files. Mine loader/graph/cache/test ideas after current-layout Qwen35 MTP exists. |
| #135 | `xabicasa/dflash-multi-request-scheduler-batched-target-step` | `561b0ac1` | blocked-needs-human / selective-port | Fresh probe worktree `/tmp/luce-auto-cron-20260529-054636/pr-135-probe` conflicts in `server/src/internal.h`, `server/src/qwen35/qwen35_target_graph.cpp`, and `server/test/test_dflash.cpp`. Port scheduler commands, same-`cur_pos` batching, batch-probe copy-in/copy-back validation, and tagged stream behavior into current daemon/graph-builder APIs with focused tests. |
| #137 | `xabicasa/dflash-build-cmake-sm89-bsa` | `297fc74e` | suggested-close/superseded | Fresh probe worktree `/tmp/luce-auto-cron-20260529-054636/pr-137-probe` only conflicts on deleted old `dflash/CMakeLists.txt`. Ask author to close or retarget to current `server/CMakeLists.txt` if anything remains. |
| #94 | `feat/dflash-qwen36-swa-draft` | `d2f9c9dd` | suggested-close/superseded | Fresh probe worktree `/tmp/luce-auto-cron-20260529-054636/pr-94-probe` conflicts in `server/src/draft/draft_graph.cpp`, `draft_safetensors_loader.cpp`, and `server/src/internal.h`; useful behavior appears absorbed by current draft/SWA support. Ask author/maintainers whether any remaining old-layout tests should be reauthored before close. |
| #48 | `fix/consumer-blackwell-auto-detect` | `858b84b6` | suggested-close/superseded | Fresh probe worktree `/tmp/luce-auto-cron-20260529-054636/pr-48-probe` only conflicts on deleted old `dflash/CMakeLists.txt`. Close or retarget to current `server/CMakeLists.txt` if still needed. |

## Draft / excluded

Draft PRs remain outside the primary non-draft integration target except for
dependency awareness: #306, #305, #304, #297, #291, #290, #275, #249, and #193.
#297 is still carried as an already-integrated draft dependency. #306, #305, and
#304 remain newer draft refs and were excluded from the non-draft target.

## Retained worktrees / logs

The conflicted probe worktrees were intentionally retained for manual follow-up
because safe cleanup would require resolving or discarding conflicted indexes:

- `/tmp/luce-auto-cron-20260529-054636/pr-237-probe`
- `/tmp/luce-auto-cron-20260529-054636/pr-221-probe`
- `/tmp/luce-auto-cron-20260529-054636/pr-154-probe`
- `/tmp/luce-auto-cron-20260529-054636/pr-153-probe`
- `/tmp/luce-auto-cron-20260529-054636/pr-137-probe`
- `/tmp/luce-auto-cron-20260529-054636/pr-135-probe`
- `/tmp/luce-auto-cron-20260529-054636/pr-94-probe`
- `/tmp/luce-auto-cron-20260529-054636/pr-48-probe`
- `/tmp/luce-auto-cron-20260529-054636`

Fresh direct-merge probe logs were written under `/tmp/luce-auto-cron-20260529-054636/pr-*-merge.log`.
Delegation reports from this run:

- `/tmp/luce237-20260529-054636-claude-report.txt` (failed: max turns)
- `/tmp/luce237-20260529-054636-codex-report.txt` (usable feasibility report)

## Notes

No new source integration was safe in this refresh. The next useful work remains
a human-reviewed selective port of #237's MTP foundation into the current
`server/` layout. After that, mine #221's WARM-cache/head-KV/dispatcher behavior
and #153/#154's native/integrated MTP semantics. #135 remains a separate
selective current-layout port focused on multi-sequence target-cache tensors,
scheduler/cache slots, tagged request streams, and batched target-step support.
#137 and #48 look like old `dflash/CMakeLists.txt` changes that should be closed
or retargeted, and #94 appears largely superseded by current draft/SWA support.
