#!/usr/bin/env bash
# In-container ENTRYPOINT for lucebox-hub.
#
# Normal path: the host-side `lucebox` CLI has already populated every
# DFLASH_* env var from its detection / benchmark, so this script just
# resolves paths and execs uv run scripts/server.py.
#
# Fallback path: a user runs the image directly (`docker run --gpus all
# ghcr.io/luce-org/lucebox-hub:cuda13`) with no env-var prep. We then do a
# minimal VRAM-tiered autotune — same tiers as `lucebox configure`, kept in
# sync by hand. Anything more elaborate (driver-version probes, AMD paths,
# lspci fallbacks) belongs in the host CLI, not here.

set -euo pipefail

DFLASH_DIR="/opt/lucebox-hub/dflash"

info()  { printf '\033[1;34m[INFO]\033[0m  %s\n' "$*"; }
warn()  { printf '\033[1;33m[WARN]\033[0m  %s\n' "$*"; }
die()   { printf '\033[1;31m[ERROR]\033[0m %s\n' "$*" >&2; exit 1; }

# ── arg dispatch ───────────────────────────────────────────────────────────
# `serve` (default) — start the OpenAI-compatible server.
# `benchmark`        — run the in-container sweep (lucebox_bench.py). Eventually
#                      this becomes a thin shim that defers to `python -m
#                      lucebox benchmark`; for now keep the direct path so the
#                      legacy benchmark wiring keeps working.
# `shell`            — drop into bash inside the container (debug).
# `lucebox`          — dispatch to the Python CLI. Any subcommand
#                      `lucebox.sh` doesn't handle on the host arrives here
#                      (check, configure, pull, print-run, smoke, …).
# `python` or anything else
#                    — pass through to exec, so `docker run … python -m foo`
#                      still works for dev.
SUBCMD="${1:-serve}"
[ $# -gt 0 ] && shift || true

LUCEBOX_PKG="/opt/lucebox-hub"

case "$SUBCMD" in
    lucebox)
        exec uv run --directory "$LUCEBOX_PKG" python -m lucebox "$@"
        ;;
    benchmark)
        export DFLASH_DIR
        cd "$DFLASH_DIR"
        exec uv run --directory "$DFLASH_DIR" python scripts/lucebox_bench.py "$@"
        ;;
    shell)
        exec /bin/bash "$@"
        ;;
    serve|"")
        : # fall through to server startup below
        ;;
    *)
        die "Unknown entrypoint subcommand: $SUBCMD (expected: serve | benchmark | lucebox | shell)"
        ;;
esac

# ── detect ─────────────────────────────────────────────────────────────────
# nvidia-smi is always present here (--gpus all wires the driver in).
GPU_VRAM_GB=0
if command -v nvidia-smi &>/dev/null; then
    if mem_mib=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits 2>/dev/null \
                  | head -1) && [ -n "$mem_mib" ]; then
        GPU_VRAM_GB=$((mem_mib / 1024))
    fi
fi
GPU_COUNT=$(nvidia-smi -L 2>/dev/null | wc -l || echo 0)

# ── fallback autotune (only fills unset env) ───────────────────────────────
# Keep these tiers in lockstep with lucebox::autotune_env on the host. The
# divergence we accept is the lower-VRAM error tier — the host CLI refuses
# to start there with a clear message; here we just warn and let the server
# decide whether it can load.

if [ "$GPU_VRAM_GB" -gt 0 ]; then
    if [ "$GPU_VRAM_GB" -lt 12 ]; then
        : "${DFLASH_LAZY:=1}"
        : "${DFLASH_MAX_CTX:=4096}"
        warn "VRAM ${GPU_VRAM_GB} GB < 12 GB — 27B target unlikely to fit"
    elif [ "$GPU_VRAM_GB" -lt 22 ]; then
        : "${DFLASH_LAZY:=1}"
        : "${DFLASH_MAX_CTX:=32768}"
    elif [ "$GPU_VRAM_GB" -lt 32 ]; then
        : "${DFLASH_LAZY:=1}"
        : "${DFLASH_MAX_CTX:=114688}"
    elif [ "$GPU_VRAM_GB" -lt 48 ]; then
        : "${DFLASH_MAX_CTX:=131072}"
    else
        : "${DFLASH_PREFIX_CACHE_SLOTS:=4}"
        : "${DFLASH_MAX_CTX:=131072}"
    fi
fi

: "${DFLASH_BIN:=$DFLASH_DIR/build/test_dflash}"
: "${DFLASH_HOST:=0.0.0.0}"
: "${DFLASH_PORT:=8080}"
: "${DFLASH_BUDGET:=22}"
: "${DFLASH_MAX_CTX:=16384}"
: "${DFLASH_LAZY:=0}"
: "${DFLASH_PREFIX_CACHE_SLOTS:=1}"
: "${DFLASH_PREFILL_CACHE_SLOTS:=0}"
: "${DFLASH_VERBOSE:=0}"
: "${DFLASH_TARGET:=}"
: "${DFLASH_DRAFT:=$DFLASH_DIR/models/draft}"
: "${DFLASH_PREFILL_MODE:=off}"
: "${DFLASH_PREFILL_KEEP:=0.05}"
: "${DFLASH_PREFILL_THRESHOLD:=32000}"
: "${DFLASH_PREFILL_DRAFTER:=}"

# ── auto-detect target ─────────────────────────────────────────────────────
# Largest .gguf wins (target ~16 GB vs ~1 GB drafter).
if [ -z "$DFLASH_TARGET" ] && [ -d "$DFLASH_DIR/models" ]; then
    DFLASH_TARGET=$(find "$DFLASH_DIR/models" -maxdepth 4 -type f -name '*.gguf' \
                      -printf '%s %p\n' 2>/dev/null \
                      | sort -nr | head -1 | awk '{ $1=""; sub(/^ /,""); print }')
fi

if [ -z "$DFLASH_TARGET" ] || [ ! -f "$DFLASH_TARGET" ]; then
    die "No target GGUF found. Mount a model dir: -v /host/models:/opt/lucebox-hub/dflash/models"
fi
[ -f "$DFLASH_BIN" ] || die "test_dflash binary missing at $DFLASH_BIN (image build failed?)"

# Draft: directory holding model.safetensors, or a direct .safetensors file.
DRAFT_ARG="$DFLASH_DRAFT"
if [ -d "$DFLASH_DRAFT" ]; then
    if ! ls "$DFLASH_DRAFT"/*.safetensors &>/dev/null; then
        warn "No .safetensors in draft dir $DFLASH_DRAFT — running without draft"
        DRAFT_ARG=""
    fi
elif [ -n "$DFLASH_DRAFT" ] && [ ! -f "$DFLASH_DRAFT" ]; then
    warn "Draft path $DFLASH_DRAFT not found — running without draft"
    DRAFT_ARG=""
fi

[ "$GPU_COUNT" -gt 1 ] && warn "${GPU_COUNT} GPUs detected — multi-GPU sharding is not auto-enabled (see server.py --target-gpus)"

# ── build + exec server.py ────────────────────────────────────────────────
CMD=(uv run --directory "$DFLASH_DIR" python scripts/server.py
     --host "$DFLASH_HOST"
     --port "$DFLASH_PORT"
     --target "$DFLASH_TARGET"
     --bin "$DFLASH_BIN"
     --budget "$DFLASH_BUDGET"
     --max-ctx "$DFLASH_MAX_CTX"
     --prefix-cache-slots "$DFLASH_PREFIX_CACHE_SLOTS"
     --prefill-cache-slots "$DFLASH_PREFILL_CACHE_SLOTS")

[ -n "$DRAFT_ARG" ]                && CMD+=(--draft "$DRAFT_ARG")
[ "$DFLASH_LAZY" = "1" ]           && CMD+=(--lazy-draft)
[ "$DFLASH_VERBOSE" = "1" ]        && CMD+=(--verbose-daemon)

if [ "$DFLASH_PREFILL_MODE" != "off" ]; then
    [ -n "$DFLASH_PREFILL_DRAFTER" ] || die "DFLASH_PREFILL_MODE=$DFLASH_PREFILL_MODE requires DFLASH_PREFILL_DRAFTER"
    [ -f "$DFLASH_PREFILL_DRAFTER" ] || die "Prefill drafter not found at $DFLASH_PREFILL_DRAFTER"
    CMD+=(--prefill-compression "$DFLASH_PREFILL_MODE"
          --prefill-keep-ratio "$DFLASH_PREFILL_KEEP"
          --prefill-threshold "$DFLASH_PREFILL_THRESHOLD"
          --prefill-drafter "$DFLASH_PREFILL_DRAFTER")
fi

info "lucebox-hub container starting (target=$(basename "$DFLASH_TARGET"), max_ctx=$DFLASH_MAX_CTX, budget=$DFLASH_BUDGET, lazy=$DFLASH_LAZY)"

cd "$DFLASH_DIR"
exec "${CMD[@]}"
