"""Heuristic autotune: VRAM tier → DflashRuntime defaults.

Same tiers as the legacy bash autotune lived in `start_server.sh`. Kept in
one place here so the benchmark optimizer and the on-the-fly `configure`
both share the same rules.

The benchmark optimizer overrides specific fields (today: `budget`) via
`merge_benchmark_winner`. Heuristic tiers fill everything; benchmark refines.
"""

from __future__ import annotations

from dataclasses import replace

from lucebox.types import DflashRuntime, HostFacts


def runtime_from_host(host: HostFacts) -> DflashRuntime:
    """Pick a conservative DflashRuntime that 'should work' on this VRAM tier.

    Tiers (NVIDIA, target = Qwen3.6-27B Q4_K_M ~16 GB + DFlash draft ~3.3 GB):
        <12 GB  — too small for 27B; pick min ctx and lazy draft as a floor
                  so a fallback start at least gets an error from the daemon
                  rather than a silent OOM.
        12-21   — fits but tight; cap ctx, keep draft lazy.
        22-31   — 24 GB-class consumer flagships (3090/4090/5090/5090-Laptop).
                  ctx ≈112 K with TQ3_0 KV (auto-enabled by server.py).
        32-47   — RTX 6000 Ada / A100 40 GB. Full 128 K.
        ≥48     — A100 80 GB / H100 / RTX 6000 Pro. Full 128 K + 4 prefix slots.
    """
    if host.vram_gb <= 0:
        return DflashRuntime()  # no VRAM signal — stick with class defaults

    if host.vram_gb < 12:
        return DflashRuntime(lazy=True, max_ctx=4096)
    if host.vram_gb < 22:
        return DflashRuntime(lazy=True, max_ctx=32768)
    if host.vram_gb < 32:
        return DflashRuntime(lazy=True, max_ctx=114688)
    if host.vram_gb < 48:
        return DflashRuntime(max_ctx=131072)
    return DflashRuntime(max_ctx=131072, prefix_cache_slots=4)


def merge_benchmark_winner(base: DflashRuntime, *, budget: int) -> DflashRuntime:
    """Apply benchmark-discovered overrides on top of the heuristic baseline.

    For v1 the optimizer only sweeps DFLASH_BUDGET; this signature grows as
    we add more knobs to the sweep (prefill mode, prefix slots).
    """
    return replace(base, budget=budget)
