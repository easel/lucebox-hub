"""Heuristic autotune: VRAM tier → DflashRuntime defaults.

The recommended runtime is computed from HostFacts (VRAM, is_wsl) — stateless:
it takes HostFacts in and returns a fresh DflashRuntime. ``config.live_config``
applies it so ``lucebox print-serve-argv`` / ``docker_run`` bake conservative
DFLASH_* defaults into the serve command for the detected VRAM tier.

The empirical sweep + per-workload profiles (``lucebox autotune --sweep``)
live in a follow-up PR; this module keeps only the host-derived heuristic
that the serve path depends on.
"""

from __future__ import annotations

from lucebox.types import DflashRuntime, HostFacts


def _preset_approx_gb(preset: str) -> float:
    """Rough total VRAM footprint (model + draft) for the named preset.

    Used only to pick the right max_ctx tier when the preset is known.
    Returns 0.0 when the preset is unknown (caller should use tier defaults).
    """
    try:
        from lucebox.download import PRESETS
        p = PRESETS.get(preset)
        return float(p.approx_total_gb) if p is not None else 0.0
    except Exception:
        return 0.0


def runtime_from_host(host: HostFacts, preset: str = "") -> DflashRuntime:
    """Pick a conservative DflashRuntime that 'should work' on this VRAM tier.

    Tiers (NVIDIA, baseline = Qwen3.6-27B Q4_K_M ~18 GB total):
        <12 GB  — too small for 27B; pick min ctx as a floor so a fallback
                  start at least gets an error from the daemon rather than
                  a silent OOM.
        12-21   — fits but tight; cap ctx.
        22-31   — 24 GB-class consumer flagships (3090/4090/5090/5090-Laptop).
                  Default cap at 96 K (tq3_0, ~2 GB KV + ~18 GB model ≈ 20 GB).
                  For ≥20 GB models (gemma-4-31b at 21 GB, qwen3.6-moe at 22 GB)
                  the KV headroom shrinks to ~2-3 GB → cap at 32 K instead.
                  Confirmed on bragi (RTX 5090 Laptop, 23 GB VRAM) 2026-05-31:
                  Gemma4-31B starts at 32K but would OOM at 98K with tq3_0.
        32-47   — RTX 6000 Ada / A100 40 GB. Full 128 K.
        ≥48     — A100 80 GB / H100 / RTX 6000 Pro. Full 128 K.

    Prefix cache remains an explicit sweep tunable, but the automatic
    baseline keeps it off because tool prompts currently exercise a daemon
    snapshot path that is not reliable with prefix slots enabled.
    Empirically confirmed on bragi 2026-05-31: prefix_cache_slots=32
    caused -19pp regression on agent_recorded (23.1% vs 42.3% baseline).
    5 previously-passing cases regressed; 0 new cases unlocked. See
    docs/experiments/qwen3.6-27b-prefix-cache-regression-bragi-2026-05-31.md.

    On `lazy`: the C++ server requires `--prefill-drafter` (and `--draft`)
    to be set for `--lazy-draft` to take effect, and silently ignores it
    otherwise (`--lazy-draft ignored: requires both --prefill-drafter and
    --draft`). Since the heuristic path does NOT set `prefill_drafter`,
    we default `lazy=False` here — "what we say" matches "what runs".
    Users who explicitly opt in via config.toml will be warned at server
    startup that the flag is being dropped (see entrypoint.sh).
    """
    if host.vram_gb <= 0:
        return DflashRuntime()  # no VRAM signal — stick with class defaults

    if host.vram_gb < 12:
        return DflashRuntime(max_ctx=4096)
    if host.vram_gb < 22:
        return DflashRuntime(max_ctx=32768)
    if host.vram_gb < 32:
        # On 22-31 GB cards, model size matters. Models ≥20 GB (e.g. gemma-4-31b
        # at ~21 GB, qwen3.6-moe at ~22 GB) leave only ~2-3 GB for KV, limiting
        # practical max_ctx to ~32K even with tq3_0. Models <20 GB (e.g.
        # qwen3.6-27b at ~18 GB, laguna-xs.2 at ~21 GB with tq3_0 KV cliff) can
        # use up to 98K with tq3_0.
        # Note: Laguna's max_ctx cliff is a kernel path issue (not VRAM), handled
        # separately in config; the heuristic still gives 32K for Laguna to be safe.
        approx_gb = _preset_approx_gb(preset)
        if approx_gb >= 20.0:
            # Large model: ~2 GB headroom for KV → cap at 32K
            return DflashRuntime(
                budget=8, max_ctx=32768,
                cache_type_k="tq3_0", cache_type_v="tq3_0",
            )
        # tq3_0 is required at 98K on 23 GB cards: model (~18-19 GB) +
        # q8_0 KV cache at 98K (~5-6 GB) = 24-25 GB → OOM.
        # tq3_0 KV (~2 GB) leaves ~3 GB headroom. Confirmed on bragi
        # (RTX 5090 Laptop, 23 GB VRAM) 2026-05-30 — q8_0 timed out on
        # every 98K cell; all tq3_0 cells passed. See
        # docs/experiments/qwen3.6-27b-coding-agent-loop-sweep-bragi-2026-05-30.md
        if host.is_wsl:
            # Bumped from max_ctx=65536 → 98304 on 2026-05-30 after the
            # coding-agent-loop sweep on sindri proved 98K serves real
            # 90K-token agentic prompts with ~3 GB VRAM headroom and no
            # CUDA VMM failures. See
            # docs/experiments/gemma4-26b-coding-agent-loop-sweep-2026-05-30.md.
            # The original 65K cap cited unverified VMM failures —
            # bisect history showed no commit reproducing them.
            return DflashRuntime(
                budget=16, max_ctx=98304,
                cache_type_k="tq3_0", cache_type_v="tq3_0",
            )
        return DflashRuntime(
            max_ctx=98304,
            cache_type_k="tq3_0", cache_type_v="tq3_0",
        )
    if host.vram_gb < 48:
        return DflashRuntime(max_ctx=131072)
    return DflashRuntime(max_ctx=131072)
