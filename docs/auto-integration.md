# Auto-integration manifest

Repository: `Luce-Org/lucebox-hub`
Integration branch: `auto-integration`
Writable remote: `easel`
Upstream remote: `origin` / `Luce-Org`
Last refresh: 2026-05-29T12:55:47-04:00
Current base: `origin/main` `8782d07a`
Current integration tip before this refresh: `easel/auto-integration` `55244483`
Manifest refresh commit prepared in this run: this commit, if non-empty

This branch is maintained as a reproducible patch stack over `origin/main`. At
this run's start the primary checkout was clean, auth/tooling checks passed with
the real user credential home, and `origin` and `easel` were fetched separately.
This refresh found `easel/auto-integration` already carrying all currently
mergeable non-draft PR heads, including the latest #309 dFlash feature-mirror
dtype policy head `ea6ac481`. `origin/main` was unchanged, no included PR head
had advanced, and no stack code changes were required. Fresh direct-merge probes
for the remaining non-integrated non-draft PRs still conflicted in the same
conflict families, and a fresh tmux-driven Claude #237 salvage inspection again
hit its turn limit without a usable report.

## Included in the current stack

| PR | Head branch | Head | State | Notes |
|---:|---|---:|---|---|
| #309 | `experiment-dflash-feature-dtype` | `ea6ac481` | included | Latest dFlash feature mirror memory/dtype policy is carried. Conflict in `server/src/common/dflash_feature_ring.cpp` was resolved by keeping the integration GPU BF16-to-F32 CUDA path and applying #309's chunked BF16 host conversion for non-F32/non-BF16 storage. |
| #307 | `docs/why-this-exists-copy` | `236fc2fd` | included | README “Why this exists” copy remains preserved; the #285 README conflict was resolved in favor of this focused docs PR. |
| #306 | `refactor-server-layer-split-runtime` | `988fc933` | included | Shared layer-split runtime helper extraction remains carried. |
| #303 | `fix/harness-portable-run-dirs` | upstream `05b008a0` | included through upstream and stack | Harness portable run/cache directories and automatic client-install fallback are in `origin/main`; stack compatibility docs/helpers remain carried. |
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
| #285 | `feat/lucebox-docker` | `37b3fbd5` | included | Latest Docker stack / `lucebox` CLI / bench-profile / harness / `luce-bench` refresh is carried. Conflicts were resolved by preserving the integration-only native server CI dependency step, `.docker-build/` ignore, `std::algorithm` include needed by existing server code, and #307's README copy. |
| #276 | `fix/qwen36-claude-code-tool-calling` | `5e861b4d` | included | Qwen3.6-27B tool-calling fix for Claude-code Anthropic path is carried. |
| #274 | `feat/pflash-drafter-ee7` | `8c1f37db` | included | Latest adaptive pFlash composition plus effective-size admission/keep-ratio guard update is carried. Conflicts with #294's proxy path were resolved by applying the post-compression admission gate before upstream proxy forwarding and keeping both test groups. |
| #266 | `feat/harness-typed-adapters` | `17525eae` | included | Typed harness adapters and format-aware session-inject proxy are carried. |
| #152 | `main` | `cf735bee` | included | Gemma 4 RTX 4090 backend helpers are carried. |
| #142 | `xabicasa/dflash-safetensors-draft-fp16` | `f2fbf62f` | included | FP16 safetensors drafter support is carried. |

## Validation run

This run performed:

- `date -Is` -> `2026-05-29T12:55:47-04:00` for preflight.
- Primary checkout preflight: `git status --short` was clean; branch was
  `auto-integration`; remotes were `origin=https://github.com/Luce-Org/lucebox-hub`
  and `easel=https://github.com/easel/lucebox-hub`.
- Auth/tooling checks with real user credentials succeeded: `gh auth status`,
  `claude auth status --text`, and `codex --version` (`codex-cli 0.130.0`).
- `git fetch --prune origin` and `git fetch --prune easel` completed successfully.
- Open PR enumeration used `gh pr list --repo Luce-Org/lucebox-hub --state open
  --limit 200 --json ... --jq ...` and found 29 open PRs total: 21 non-draft and
  8 draft/excluded.
- Fetched open non-draft PR refs explicitly: #309, #307, #306, #297, #295, #294,
  #289, #285, #276, #274, #266, #237, #221, #154, #153, #152, #142, #137,
  #135, #94, and #48.
- Containment checks before reconciliation confirmed #309, #307, #306, #297,
  #295, #294, #289, #285, #276, #274, #266, #152, and #142 were ancestors of
  `easel/auto-integration`; #237, #221, #154, #153, #137, #135, #94, and #48
  were not ancestors.
- Reconciliation worktree `/tmp/luce-auto-cron-20260529-125618/reconcile` was
  created from `easel/auto-integration`; merging `origin/main` reported
  `Already up to date`.
- Merging #309 reported `Already up to date` because the latest #309 head was
  already an ancestor of `easel/auto-integration`.
- Fresh direct merge probes from the updated integration tip were created for
  #237, #221, #154, #153, #137, #135, #94, and #48. All still conflict in the
  file sets recorded below.
- Tmux-driven Claude delegation for #237 ran in session `luce237-125618` and
  wrote `/tmp/luce-auto-cron-20260529-125618/claude-pr237-report.txt`; it exited
  with `Error: Reached max turns (10)` and produced no usable salvage report.
- Verification for the manifest-only refresh included `git diff --check`, C++
  conflict-marker search, and targeted Python/YAML sanity checks. No CMake/CUDA
  rebuild was run because this refresh only changed the manifest; the known
  local CUDA toolkit/CMake compiler-identification blocker from prior runs
  remains relevant for full server builds (`ptxas fatal: Value 'sm_52' is not
  defined`).

## Pending / blocked-needs-human / selective-port candidates

| PR | Head branch | Head | Current status | Probe result / next useful action |
|---:|---|---:|---|---|
| #237 | `feat/dflash-mtp-foundation` | `02c6a6c4` | blocked-needs-human / salvage-port | Fresh probe worktree `/tmp/luce-auto-cron-20260529-125618/pr-237-probe` conflicts in old-layout `dflash/` server/backend files plus current `server/CMakeLists.txt`, common MTP files, Qwen35 loader/graph/backend/dflash target files, and tests. Fresh Claude delegation hit the turn limit without a usable report; prior usable Claude report `/tmp/luce237b-20260529-092711-claude-report.txt` says this is a genuine, not-yet-duplicated MTP/NextN feature. Next step remains a staged manual/multi-agent port by conflict family. |
| #221 | `feat/mtp-prefix-warm-ghost` | `05502974` | blocked-needs-human / dependent salvage-port | Fresh probe worktree `/tmp/luce-auto-cron-20260529-125618/pr-221-probe` conflicts on old `dflash/` scripts/backend files, current common/Qwen35 MTP, metadata, prefix snapshot, graph, and tests, and brings old benchmark/results assets. Mine prefix-cache WARM behavior after a current-layout #237-equivalent MTP foundation lands. |
| #154 | `xabicasa/dflash-mtp-speculative-loop` | `2f4ede79` | blocked-needs-human / dependency | Fresh probe worktree `/tmp/luce-auto-cron-20260529-125618/pr-154-probe` conflicts on old `dflash/CMakeLists.txt`, moved MTP docs/tests and `f16_convert.cu`, plus core Qwen35/internal target files. Mine linear MTP decode semantics after current-layout Qwen35 MTP exists. |
| #153 | `xabicasa/dflash-mtp-integrated` | `e9b17cb1` | blocked-needs-human / dependency | Fresh probe worktree `/tmp/luce-auto-cron-20260529-125618/pr-153-probe` conflicts on old CMake, moved MTP docs/tests and `f16_convert.cu`, and the same core Qwen35/internal target files. Mine loader/graph/cache/test ideas after current-layout Qwen35 MTP exists. |
| #135 | `xabicasa/dflash-multi-request-scheduler-batched-target-step` | `561b0ac1` | blocked-needs-human / selective-port | Fresh probe worktree `/tmp/luce-auto-cron-20260529-125618/pr-135-probe` conflicts in `server/src/internal.h`, `server/src/qwen35/qwen35_target_graph.cpp`, and `server/test/test_dflash.cpp`. Prior usable Codex reports confirm useful missing behavior: qwen35 multi-request scheduling with cache slots, daemon protocol hooks, fair quantum stepping, epoch checks, and batched target-step ideas. |
| #137 | `xabicasa/dflash-build-cmake-sm89-bsa` | `297fc74e` | suggested-close/superseded | Fresh probe worktree `/tmp/luce-auto-cron-20260529-125618/pr-137-probe` only conflicts on deleted old `dflash/CMakeLists.txt`. Ask author to close or retarget to current `server/CMakeLists.txt` if anything remains. |
| #94 | `feat/dflash-qwen36-swa-draft` | `d2f9c9dd` | suggested-close/superseded | Fresh probe worktree `/tmp/luce-auto-cron-20260529-125618/pr-94-probe` conflicts in `server/src/draft/draft_graph.cpp`, `draft_safetensors_loader.cpp`, and `server/src/internal.h`; prior tmux-driven Codex report `/tmp/luce94-codex-20260529-090910-report.txt` concluded the useful behavior is already present in current auto-integration. |
| #48 | `fix/consumer-blackwell-auto-detect` | `858b84b6` | suggested-close/superseded | Fresh probe worktree `/tmp/luce-auto-cron-20260529-125618/pr-48-probe` only conflicts on deleted old `dflash/CMakeLists.txt`. Close or retarget to current `server/CMakeLists.txt` if still needed. |

## Draft / excluded

Draft PRs remain outside the primary non-draft integration target except for
dependency awareness: #308, #305, #304, #291, #290, #275, #249, and #193.

## Retained worktrees / logs

The reconciliation worktree and conflicted probe worktrees were intentionally
retained for audit/follow-up; safe cleanup would require resolving or discarding
conflicted indexes in the probe worktrees:

- `/tmp/luce-auto-cron-20260529-125618/reconcile`
- `/tmp/luce-auto-cron-20260529-125618/pr-237-probe`
- `/tmp/luce-auto-cron-20260529-125618/pr-221-probe`
- `/tmp/luce-auto-cron-20260529-125618/pr-154-probe`
- `/tmp/luce-auto-cron-20260529-125618/pr-153-probe`
- `/tmp/luce-auto-cron-20260529-125618/pr-137-probe`
- `/tmp/luce-auto-cron-20260529-125618/pr-135-probe`
- `/tmp/luce-auto-cron-20260529-125618/pr-94-probe`
- `/tmp/luce-auto-cron-20260529-125618/pr-48-probe`
- `/tmp/luce-auto-cron-20260529-125618`

Fresh direct-merge probe logs were written under `/tmp/luce-auto-cron-20260529-125618/pr-*-merge.log`, with unmerged-file summaries under `/tmp/luce-auto-cron-20260529-125618/pr-*-unmerged.txt`.
Delegation reports from recent runs that remain useful:

- `/tmp/luce237b-20260529-092711-claude-report.txt` (usable read-only feasibility report)
- `/tmp/luce237resolve-20260529-092711-claude-report.txt` (failed: max turns; unresolved index retained)
- `/tmp/luce-auto-cron-20260529-101411/claude-pr237-report.txt` (failed: max turns)
- `/tmp/luce-auto-cron-20260529-103040/claude-pr237-narrow-report.txt` (failed: blank/zero-byte stuck tmux run)
- `/tmp/luce-auto-cron-20260529-120701/claude-pr237-report.txt` (failed: max turns)
- `/tmp/luce-auto-cron-20260529-125618/claude-pr237-report.txt` (failed: max turns)
- `/tmp/luce135-20260529-092711-codex-report.txt` (usable read-only feasibility report)
- `/tmp/luce-auto-cron-20260529-101411/codex-pr135-report.txt` (partial transcript only; stopped before final summary)
- `/tmp/luce-auto-cron-20260529-103040/codex-pr135-narrow-report.txt` (usable read-only salvage plan)
- `/tmp/luce221-084809-claude-report.txt` (failed: max turns)
- `/tmp/luce221-codex-084947-report.txt` (usable read-only feasibility report)
- `/tmp/luce94-codex-20260529-090910-report.txt` (usable read-only superseded/close report)

## Notes

This refresh made no stack code changes and re-confirmed that all mergeable
non-draft PR heads are already included. The next useful integration work
remains a staged selective port of #237's MTP foundation into the current
`server/` layout, then #221/#153/#154 MTP follow-ups, with #135 as a separate
scheduler/batched-target selective port. #137 and #48 look like old
`dflash/CMakeLists.txt` changes that should be closed or retargeted, and #94
appears largely superseded by current draft/SWA support.
