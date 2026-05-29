# Auto-integration manifest

Repository: `Luce-Org/lucebox-hub`
Integration branch: `auto-integration`
Writable remote: `easel`
Upstream remote: `origin` / `Luce-Org`
Last refresh: 2026-05-29T09:42:47-04:00
Current base: `origin/main` `8782d07a`
Current integration tip before this refresh: `easel/auto-integration` `be7c2cc4`
Manifest refresh commit prepared in this run: this commit, if non-empty

This branch is maintained as a reproducible patch stack over `origin/main`. At
this run's start the primary checkout was clean, auth/tooling checks passed,
`origin` and `easel` were fetched separately, and `easel/auto-integration` was
already based on current `origin/main` (`0` behind / `434` ahead in the
reconciliation worktree before this manifest-only refresh). Open PR refs were
refreshed. No cleanly mergeable non-draft PR head advanced beyond the current
stack since the previous refresh. All direct-mergeable non-draft PRs remain
represented in the stack. The remaining non-draft PRs were freshly re-probed in
`/tmp/luce-auto-cron-20260529-092711`; they still require selective current-layout
ports or are superseded. A new delegated resolve attempt for #237 reached the
Claude max-turn limit without resolving the conflicted index, so the #237 probe
worktree was retained for manual/deeper-agent follow-up.

## Included in the current stack

| PR | Head branch | Head | State | Notes |
|---:|---|---:|---|---|
| #307 | `docs/why-this-exists-copy` | `236fc2fd` | included | Latest README “Why this exists” copy is merged. |
| #306 | `refactor-server-layer-split-runtime` | `988fc933` | included | Shared layer-split runtime helper extraction remains carried; it adds `server/src/common/layer_split_runtime.{h,cpp}` and rewires Gemma4, Laguna, and Qwen35 adapters. |
| #303 | `fix/harness-portable-run-dirs` | upstream `05b008a0` | included through upstream and stack | Harness portable run/cache directories and automatic client-install fallback are in `origin/main`; the stack preserved local compatibility docs and helpers. |
| #302 | `fix/harness-model-paths` | upstream | included through upstream | Harness launcher model-path override behavior and documentation are in `origin/main`. |
| #301 | `fix/ddtree-test-harness` | upstream | included through upstream | DDTree test harness fixes are in `origin/main`. |
| #300 | `fix/sigterm-gpu-unload` | upstream | included through upstream | SIGTERM GPU-unload fix remains in upstream. |
| #299 | `feat/draft-swa-flag` | upstream | included through upstream | Draft SWA env/flag support remains in upstream. |
| #298 | `fix/gemma4-destructor-link` | upstream | included through upstream | Gemma4 destructor-link fix remains in upstream. |
| #292 | `feat-backend-ipc-payload-pipe-open` | upstream / `90bc52f` | included through upstream and stack | Backend IPC payload-pipe support is upstream and still represented in the carried stack history. |
| #297 | `feat-server-laguna-layer-split-adapter-v2` | `53dd1686` | included | Laguna target-layer-split adapter remains carried. |
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

- `date -Is` -> `2026-05-29T09:26:28-04:00` for preflight; manifest timestamp
  refreshed at `2026-05-29T09:42:47-04:00`.
- Primary checkout preflight: `git status --short` was clean; branch was
  `auto-integration`; remotes were `origin=https://github.com/Luce-Org/lucebox-hub`
  and `easel=https://github.com/easel/lucebox-hub`.
- Auth/tooling checks with real user credentials succeeded: `gh auth status`,
  `claude auth status --text`, and Codex help smoke output.
- `git fetch --prune origin` and `git fetch --prune easel` completed successfully.
- Open PR enumeration used `gh pr list --repo Luce-Org/lucebox-hub --state open
  --limit 200 --json ... --jq ...` and found 27 open PRs total: 20 non-draft and
  7 draft/excluded.
- Fetched open non-draft PR refs explicitly: #307, #306, #297, #295, #294,
  #289, #285, #276, #274, #266, #237, #221, #154, #153, #152, #142, #137,
  #135, #94, and #48.
- Containment checks confirmed #307, #306, #297, #295, #294, #289, #285, #276,
  #274, #266, #152, and #142 are ancestors of `easel/auto-integration`; #237,
  #221, #154, #153, #137, #135, #94, and #48 are not.
- Reconciliation worktree `/tmp/luce-auto-cron-20260529-092711/reconcile` was
  created from `easel/auto-integration`; merging `origin/main` reported `Already
  up to date`.
- `git rev-list --left-right --count origin/main...HEAD` in the reconciliation
  worktree reported `0` behind and `434` ahead before the manifest-only refresh.
- Fresh direct merge probes from the current integration tip were created for
  #237, #221, #154, #153, #137, #135, #94, and #48. All still conflict in the
  file sets recorded below.
- New tmux-driven Claude feasibility delegation for #237 succeeded on retry at
  `/tmp/luce237b-20260529-092711-claude-report.txt`. It concluded #237 is a
  real MTP/NextN feature, not duplicated by the current stack, but direct merge
  is unsafe: most MTP additions can be re-pathed into `server/`, while true
  conflicts must union MoE/router and MTP fields/signatures and hand-port three
  relocated-file edits.
- A deeper tmux-driven Claude resolve attempt for #237 was attempted in
  `/tmp/luce-auto-cron-20260529-092711/pr-237-probe`, but exited with `Error:
  Reached max turns (30)` and left the merge unresolved. No changes were staged
  or committed from that probe.
- New tmux-driven Codex delegation for #135 produced a usable read-only report at
  `/tmp/luce135-20260529-092711-codex-report.txt`, confirming #135 remains a
  feasible but medium-sized selective port rather than a direct merge.
- Verification for this manifest-only refresh: `git diff --check -- docs/auto-integration.md`
  passed before commit. No project build was run because no contributor code changed.

## Pending / blocked-needs-human / selective-port candidates

| PR | Head branch | Head | Current status | Probe result / next useful action |
|---:|---|---:|---|---|
| #237 | `feat/dflash-mtp-foundation` | `02c6a6c4` | blocked-needs-human / salvage-port | Fresh probe worktree `/tmp/luce-auto-cron-20260529-092711/pr-237-probe` conflicts in old-layout `dflash/` server/backend files plus current `server/CMakeLists.txt`, common MTP files, Qwen35 loader/graph/backend/dflash target files, and tests. Claude feasibility report `/tmp/luce237b-20260529-092711-claude-report.txt` says this is a genuine, not-yet-duplicated MTP/NextN feature: re-path UA MTP files into `server/`, union-merge MoE/router and MTP fields/signatures, and hand-port relocated backend/server entry edits. A Claude resolve attempt reached max turns and did not finish; next step is a narrower staged manual port or multi-agent task split by conflict family. |
| #221 | `feat/mtp-prefix-warm-ghost` | `05502974` | blocked-needs-human / dependent salvage-port | Fresh probe worktree `/tmp/luce-auto-cron-20260529-092711/pr-221-probe` conflicts on old `dflash/` scripts/backend files, current common/Qwen35 MTP, metadata, prefix snapshot, graph, and tests, and brings old benchmark/results assets. Mine prefix-cache WARM behavior (`snapshot_head_kv`, `restore_head_kv`, `warm_head_kv_range`, `head_kv_warm_`), partial/range warm recovery, the NextN raw-`block_count` load-filter fix, dual-speculator routing ideas, and focused `test_prefix_cache_mtp.cpp` cases only after a PR-237-equivalent current-layout MTP foundation lands. Drop old qwen36 names, old Python server behavior, old inline snapshot storage, archived result payloads, and behavior already superseded by current `skip_park` / `cache_.last_tok` handling. |
| #154 | `xabicasa/dflash-mtp-speculative-loop` | `2f4ede79` | blocked-needs-human / dependency | Fresh probe worktree `/tmp/luce-auto-cron-20260529-092711/pr-154-probe` conflicts on old `dflash/CMakeLists.txt`, moved MTP docs/tests and `f16_convert.cu`, plus core Qwen35/internal target files. Mine linear MTP decode semantics after current-layout Qwen35 MTP exists. |
| #153 | `xabicasa/dflash-mtp-integrated` | `e9b17cb1` | blocked-needs-human / dependency | Fresh probe worktree `/tmp/luce-auto-cron-20260529-092711/pr-153-probe` conflicts on old CMake, moved MTP docs/tests and `f16_convert.cu`, and the same core Qwen35/internal target files. Mine loader/graph/cache/test ideas after current-layout Qwen35 MTP exists. |
| #135 | `xabicasa/dflash-multi-request-scheduler-batched-target-step` | `561b0ac1` | blocked-needs-human / selective-port | Fresh probe worktree `/tmp/luce-auto-cron-20260529-092711/pr-135-probe` conflicts in `server/src/internal.h`, `server/src/qwen35/qwen35_target_graph.cpp`, and `server/test/test_dflash.cpp`. Codex report `/tmp/luce135-20260529-092711-codex-report.txt` says the useful parts are scheduler semantics and batched target-step ideas; port targets are `ModelBackend`/daemon or HTTP request-slot APIs, qwen35 per-request cache/graph state, `graph_builders`/`step_graph` n-seq plumbing, and a resumable spec-decode state machine. Direct merge would regress current namespace, MoE, partial-cache, snapshot, and layer-split behavior. |
| #137 | `xabicasa/dflash-build-cmake-sm89-bsa` | `297fc74e` | suggested-close/superseded | Fresh probe worktree `/tmp/luce-auto-cron-20260529-092711/pr-137-probe` only conflicts on deleted old `dflash/CMakeLists.txt`. Ask author to close or retarget to current `server/CMakeLists.txt` if anything remains. |
| #94 | `feat/dflash-qwen36-swa-draft` | `d2f9c9dd` | suggested-close/superseded | Fresh probe worktree `/tmp/luce-auto-cron-20260529-092711/pr-94-probe` conflicts in `server/src/draft/draft_graph.cpp`, `draft_safetensors_loader.cpp`, and `server/src/internal.h`; prior tmux-driven Codex report `/tmp/luce94-codex-20260529-090910-report.txt` concluded the useful behavior is already present in current auto-integration: Qwen3.6 DFlash SWA metadata loading, bare-filename `config.json` lookup, and a stronger shared-runtime `causal_mask_swa` path. Ask author/maintainers to close unless they can identify an unported test case. |
| #48 | `fix/consumer-blackwell-auto-detect` | `858b84b6` | suggested-close/superseded | Fresh probe worktree `/tmp/luce-auto-cron-20260529-092711/pr-48-probe` only conflicts on deleted old `dflash/CMakeLists.txt`. Close or retarget to current `server/CMakeLists.txt` if still needed. |

## Draft / excluded

Draft PRs remain outside the primary non-draft integration target except for
dependency awareness: #305, #304, #291, #290, #275, #249, and #193.

## Retained worktrees / logs

The conflicted probe worktrees were intentionally retained for manual follow-up
because safe cleanup would require resolving or discarding conflicted indexes:

- `/tmp/luce-auto-cron-20260529-092711/reconcile`
- `/tmp/luce-auto-cron-20260529-092711/pr-237-probe`
- `/tmp/luce-auto-cron-20260529-092711/pr-221-probe`
- `/tmp/luce-auto-cron-20260529-092711/pr-154-probe`
- `/tmp/luce-auto-cron-20260529-092711/pr-153-probe`
- `/tmp/luce-auto-cron-20260529-092711/pr-137-probe`
- `/tmp/luce-auto-cron-20260529-092711/pr-135-probe`
- `/tmp/luce-auto-cron-20260529-092711/pr-94-probe`
- `/tmp/luce-auto-cron-20260529-092711/pr-48-probe`
- `/tmp/luce-auto-cron-20260529-092711`

Fresh direct-merge probe logs were written under `/tmp/luce-auto-cron-20260529-092711/pr-*-merge.log`.
Delegation reports from recent/current runs:

- `/tmp/luce237-20260529-070359-claude-report.txt` (failed: max turns)
- `/tmp/luce237-20260529-070359-codex-report.txt` (usable read-only feasibility report)
- `/tmp/luce237-20260529-092711-claude-report.txt` (failed: max turns)
- `/tmp/luce237b-20260529-092711-claude-report.txt` (usable read-only feasibility report)
- `/tmp/luce237resolve-20260529-092711-claude-report.txt` (failed: max turns; unresolved index retained)
- `/tmp/luce135-20260529-072338-codex-report.txt` (usable read-only feasibility report)
- `/tmp/luce135-20260529-092711-codex-report.txt` (usable read-only feasibility report)
- `/tmp/luce221-084809-claude-report.txt` (failed: max turns)
- `/tmp/luce221-codex-084947-report.txt` (usable read-only feasibility report)
- `/tmp/luce94-codex-20260529-090910-report.txt` (usable read-only superseded/close report)

## Notes

No contributor code changed in this refresh; the stack was already up to date
with `origin/main` and all cleanly integrated non-draft PR heads. The next useful
integration work remains a staged selective port of #237's MTP foundation into
the current `server/` layout, split by conflict family: first land the re-pathed
MTP files, then union-merge MoE/router and MTP fields/signatures, then hand-port
relocated backend/server entry edits and build-gate. After that, mine #221's
WARM-cache/head-KV/range-warm, NextN load-filter, and dispatcher/routing
behavior plus #153/#154's native/integrated MTP semantics. #135 is a separate
current-layout selective port that should be split into request-slot APIs,
qwen35 batched one-token target-step support, scheduler fairness/cancel tests,
backend decode slots, and opt-in scheduler APIs. #137 and #48 look like old
`dflash/CMakeLists.txt` changes that should be closed or retargeted, and #94
appears largely superseded by current draft/SWA support.
