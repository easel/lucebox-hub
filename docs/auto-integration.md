# Auto-integration manifest

Repository: `Luce-Org/lucebox-hub`
Integration branch: `auto-integration`
Writable remote: `easel`
Upstream remote: `origin` / `Luce-Org`
Last refresh: 2026-05-29T15:56:22-04:00
Current base: `origin/main` `8782d07a`
Current integration tip before this refresh: `easel/auto-integration` `28c01eff`
Manifest refresh commit prepared in this run: this commit

This branch is maintained as a reproducible patch stack over `origin/main`.
At this run's start the primary checkout was clean; GitHub, Claude Code, and
Codex auth/tooling checks passed using the real user credential home; and
`origin` and `easel` were fetched separately. Reconciliation was performed in
`/tmp/luce-auto-cron-20260529-155333/reconcile`, created from the fetched
writable remote tip; the primary checkout was not used for integration edits.

This refresh found one advanced non-draft contributor PR head: #285 moved from
`37b3fbd5` to `8b48ad85`. The branch was merged on top of the existing stack,
with manual conflict resolution in the server chat-template/reasoning-channel
unit-test area. The new #285 head carries the same Qwen3.6/Laguna think-mode
reasoning-channel commits that also appear in draft PR #308; because they are
now reachable through non-draft #285, they are included in the integration
stack. No external-agent delegation was needed for this small, localized
conflict.

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
| #285 | `feat/lucebox-docker` | `8b48ad85` | included | Latest Docker stack / `lucebox` CLI / bench-profile / harness / `luce-bench` refresh is carried; this run added the advanced Qwen3.6/Laguna reasoning-channel head (`db79a7db`, `f62b1ebb`). |
| #276 | `fix/qwen36-claude-code-tool-calling` | `5e861b4d` | included | Qwen3.6-27B tool-calling fix for Claude-code Anthropic path is carried. |
| #274 | `feat/pflash-drafter-ee7` | `8c1f37db` | included | Latest adaptive pFlash composition plus effective-size admission/keep-ratio guard update is carried. |
| #266 | `feat/harness-typed-adapters` | `17525eae` | included | Typed harness adapters and format-aware session-inject proxy are carried. |
| #152 | `main` | `cf735bee` | included | Gemma 4 RTX 4090 backend helpers are carried. |
| #142 | `xabicasa/dflash-safetensors-draft-fp16` | `f2fbf62f` | included | FP16 safetensors drafter support is carried. |

## Validation run

This run performed:

- `date -Is` -> `2026-05-29T15:52:51-04:00` for preflight and
  `2026-05-29T15:56:22-04:00` for this manifest refresh.
- Primary checkout preflight: `git status --short` was clean; branch was
  `auto-integration`; remotes were `origin=https://github.com/Luce-Org/lucebox-hub`
  and `easel=https://github.com/easel/lucebox-hub`.
- Auth/tooling checks with real user credentials succeeded: `gh auth status`,
  `claude auth status --text`, and a harmless `codex --help` smoke check.
- `git fetch --prune origin` and `git fetch --prune easel` completed successfully.
- Open PR enumeration used `gh pr list --repo Luce-Org/lucebox-hub --state open
  --limit 200 --json ... --jq ...` and found 30 open PRs total: 22 non-draft and
  8 draft/excluded.
- Open non-draft PR refs were fetched individually to `refs/remotes/origin/pr/<n>`.
- Containment checks confirmed #310, #309, #307, #306, #297, #295, #294, #289,
  #276, #274, #266, #152, and #142 were already ancestors of
  `easel/auto-integration`; #285 had advanced and was not yet included.
- Reconciliation worktree `/tmp/luce-auto-cron-20260529-155333/reconcile` was
  created from `easel/auto-integration`; merging `origin/main` reported
  `Already up to date`.
- Merging `origin/pr/285` conflicted in `server/src/server/chat_template.cpp`
  and `server/test/test_server_unit.cpp`. Manual resolution preserved the
  existing Qwen3 closed-think Jinja fallback and added #285's
  `PromptRenderResult.started_in_thinking` propagation and render-to-SSE
  reasoning-channel tests.
- Verification for this refresh:
  - `git diff --check` passed.
  - `python3 -m py_compile server/scripts/test_server_integration.py` passed.
  - `cmake -S server -B /tmp/luce-auto-cron-20260529-155333/build-server -DCMAKE_CUDA_ARCHITECTURES=86` was attempted and failed during local CUDA compiler identification with the known environment/toolchain blocker: `ptxas fatal : Value 'sm_52' is not defined for option 'gpu-name'`. This occurred before project compilation, matching prior runs.

## Pending / blocked-needs-human / selective-port candidates

| PR | Head branch | Head | Current status | Probe result / next useful action |
|---:|---|---:|---|---|
| #237 | `feat/dflash-mtp-foundation` | `02c6a6c4` | blocked-needs-human / salvage-port | Still not an ancestor. Prior probes conflict in old-layout `dflash/` server/backend files plus current `server/CMakeLists.txt`, common MTP files, Qwen35 loader/graph/backend/dflash target files, and tests. Prior usable Codex reports confirm valuable missing runtime behavior: generic MTP abstractions, Qwen3.6 NextN/native-head support, `--mtp-source`/`--mtp-gguf`/`--mtp-gamma`/`--mtp-draft-topk`, MTP tensor auto-detect, head-KV warming, hidden/pre-norm capture, accept-prefix-plus-bonus chain verification, and KV rollback via `restore_kv_at_chain`. |
| #221 | `feat/mtp-prefix-warm-ghost` | `05502974` | blocked-needs-human / dependent salvage-port | Still not an ancestor. Mine prefix-cache WARM behavior after a current-layout #237-equivalent MTP foundation lands. |
| #154 | `xabicasa/dflash-mtp-speculative-loop` | `2f4ede79` | blocked-needs-human / dependency | Still not an ancestor. Mine linear MTP decode semantics after current-layout Qwen35 MTP exists. |
| #153 | `xabicasa/dflash-mtp-integrated` | `e9b17cb1` | blocked-needs-human / dependency | Still not an ancestor. Mine loader/graph/cache/test ideas after current-layout Qwen35 MTP exists. |
| #135 | `xabicasa/dflash-multi-request-scheduler-batched-target-step` | `561b0ac1` | blocked-needs-human / selective-port | Still not an ancestor. Prior Codex report says direct merge would regress current layer-split/MoE/TQ3/KV/snapshot/HIP behavior; salvage tagged stream frames, request commands, fair aligned-bucket scheduling, multiple qwen35 cache slots, and batched one-token target probes into current daemon/backend architecture. |
| #137 | `xabicasa/dflash-build-cmake-sm89-bsa` | `297fc74e` | suggested-close/superseded | Still not an ancestor. Prior probe only conflicted on deleted old `dflash/CMakeLists.txt`; ask author to close or retarget to current `server/CMakeLists.txt` if anything remains. |
| #94 | `feat/dflash-qwen36-swa-draft` | `d2f9c9dd` | suggested-close/superseded | Still not an ancestor. Prior tmux-driven Codex report `/tmp/luce94-codex-20260529-090910-report.txt` concluded the useful behavior is already present in current auto-integration. |
| #48 | `fix/consumer-blackwell-auto-detect` | `858b84b6` | suggested-close/superseded | Still not an ancestor. Prior probe only conflicted on deleted old `dflash/CMakeLists.txt`; close or retarget to current `server/CMakeLists.txt` if still needed. |

## Draft / excluded

Draft PRs remain outside the primary non-draft integration target except for
dependency awareness: #308, #305, #304, #291, #290, #275, #249, and #193.
Draft #308's current reasoning-channel changes are nevertheless included through
non-draft #285's advanced head.

## Retained worktrees / logs

The reconciliation worktree and build/configure log were intentionally retained
for audit/follow-up:

- `/tmp/luce-auto-cron-20260529-155333/reconcile`
- `/tmp/luce-auto-cron-20260529-155333/build-server`
- `/tmp/luce-auto-cron-20260529-155333/cmake-configure.log`
- `/tmp/luce-auto-cron-20260529-155333`

Useful prior probe/delegation artifacts remain for unresolved old-layout PRs:

- `/tmp/luce-auto-cron-20260529-153853/pr-237-probe`
- `/tmp/luce-auto-cron-20260529-153853/pr-221-probe`
- `/tmp/luce-auto-cron-20260529-153853/pr-154-probe`
- `/tmp/luce-auto-cron-20260529-153853/pr-153-probe`
- `/tmp/luce-auto-cron-20260529-153853/pr-137-probe`
- `/tmp/luce-auto-cron-20260529-153853/pr-135-probe`
- `/tmp/luce-auto-cron-20260529-153853/pr-94-probe`
- `/tmp/luce-auto-cron-20260529-153853/pr-48-probe`
- `/tmp/luce-auto-cron-20260529-145519/codex-pr135-report.txt` (usable read-only salvage note)
- `/tmp/luce-auto-cron-20260529-143520/codex-pr237-report.txt` (usable read-only salvage note)
- `/tmp/luce237b-20260529-092711-claude-report.txt` (usable read-only feasibility report)
- `/tmp/luce135-20260529-092711-codex-report.txt` (usable read-only feasibility report)
- `/tmp/luce-auto-cron-20260529-103040/codex-pr135-narrow-report.txt` (usable read-only salvage plan)
- `/tmp/luce221-codex-084947-report.txt` (usable read-only feasibility report)
- `/tmp/luce94-codex-20260529-090910-report.txt` (usable read-only superseded/close report)

## Notes

The next useful integration work remains a staged selective port of #237's MTP
foundation into the current `server/` layout, then #221/#153/#154 MTP follow-ups,
with #135 as a separate scheduler/batched-target selective port into the current
daemon/backend architecture. #137 and #48 look like old `dflash/CMakeLists.txt`
changes that should be closed or retargeted, and #94 appears largely superseded
by current draft/SWA support.
