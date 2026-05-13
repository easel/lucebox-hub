# `/props` introspection endpoint plan

Status: design, not yet implemented. Target file: `dflash/scripts/server.py`. Models the design after `antirez/ds4` PR #81 (same llama-server `/props` convention, tailored to dflash's actual surface).

## Motivation

The dflash server currently exposes nothing comparable to vLLM `/metrics` or llama.cpp `/props`. `/health` returns liveness only; `/v1/models` returns context length and a Codex-specific capability blurb. There is no way for a client (or a future bench reader) to pull a single snapshot of "what is this server, what does it do, what state is it in."

The primary use case is **long-term benchmark comparison**: a `/props` capture stored alongside benchmark numbers should let a future reader reconstruct the Python-server-side configuration that produced them. Secondary uses are diagnostic — confirming KV types, FA window, pflash mode, and cache occupancy without inspecting CLI flags or env.

## Goals

- One read-only HTTP surface a client can `GET` to learn what this server is and what it does — context window, tokenizer, KV types, whether speculative decoding is live, whether pflash is on, cache occupancy, daemon liveness.
- Bench-time tombstone for the Python server configuration.
- Single helper for arch-gated capability booleans (`_capabilities(arch)`) so future `/v1/models` consumers can adopt it and stay aligned with `/props`. Today the helper is consumed only by `/props`; wiring it into the Codex `/v1/models` variant is a v2 follow-up (see "Known limitations").

## Non-goals (v1)

- **Prometheus-style metrics.** Counters, histograms, rates belong in a separate `/metrics` endpoint, designed separately.
- **Daemon build identity.** `/props` introspects the Python server. The C++ `test_dflash` daemon's commit/BSA flag/CUDA arch list is *not* surfaced. Bench reproducibility across daemon rebuilds remains the operator's responsibility; v2 may add a daemon `version` stdin handshake.
- **Per-endpoint parameter schemas.** Clients needing precise per-route accepted params should hit `/openapi.json`.

## Endpoint

`GET /props` → `application/json`. Public (same posture as `/health` and `/v1/models`). No `/v1/` prefix — matches llama.cpp's convention.

## Response shape

```json
{
  "server": {
    "name": "luce-dflash",
    "version": "0.1.0",
    "props_schema": 1
  },
  "model": {
    "id": "luce-dflash",
    "arch": "qwen35",
    "target_path": "/.../models/Qwen3.6-27B-Q4_K_M.gguf",
    "draft_path": "/.../models/draft/model.safetensors",
    "tokenizer_id": "Qwen/Qwen3.5-27B"
  },
  "runtime": {
    "max_ctx": 16384,
    "fa_window": 2048,
    "kv_cache_k": "q8_0",
    "kv_cache_v": "q8_0",
    "lazy_draft": false,
    "target_sharding": false
  },
  "reasoning": {
    "supported": true,
    "default_enabled": true
  },
  "speculative": {
    "enabled": true,
    "ddtree_budget": 22
  },
  "sampling": {
    "supports_temperature": true,
    "supports_top_p": true,
    "supports_top_k": true,
    "supports_frequency_penalty": true,
    "supports_seed": true
  },
  "pflash": {
    "enabled": true,
    "mode": "auto",
    "threshold": 32000,
    "keep_ratio": 0.05,
    "drafter_gguf": "/.../models/Qwen3-0.6B-BF16.gguf",
    "skip_park": false,
    "bsa_enabled": true,
    "bsa_alpha": 0.85,
    "lm_head_fix": false
  },
  "prefix_cache": {
    "capacity": 4,
    "in_use": 2,
    "lifetime_hits": 17
  },
  "full_cache": {
    "enabled": true,
    "capacity": 4,
    "in_use": 1,
    "disk_bytes": 73400320,
    "lifetime_hits": 3
  },
  "tool_replay": {
    "max_entries": 50000,
    "max_bytes": 67108864,
    "current_entries": 12,
    "current_bytes": 3142
  },
  "daemon": {
    "alive": true
  },
  "api": {
    "endpoints": [
      "GET /health",
      "GET /props",
      "GET /v1/models",
      "POST /v1/chat/completions",
      "POST /v1/messages",
      "POST /v1/responses"
    ]
  }
}
```

## Field rules

- All `*_path` fields are nullable — `null` when not applicable (e.g., `draft_path` on laguna).
- KV cache fields (`kv_cache_k`, `kv_cache_v`) reflect what the C++ daemon actually allocates after env precedence resolves — not what the user passed. Sourced from `_effective_kv_type()`, which mirrors the per-arch rules in `src/kv_quant.cpp` (qwen35) and `test/test_dflash.cpp` (laguna).
- `arch`-gated fields: `reasoning.supported`, `speculative.enabled`, presence of `draft_path` — all driven by `arch in _QWEN35_ARCHES`. `speculative` block is always emitted; `ddtree_budget` becomes `null` when `enabled: false`.
- `pflash` env knobs (`bsa_enabled`, `bsa_alpha`, `lm_head_fix`) read from the same env vars `main()` sets (`DFLASH_FP_USE_BSA`, `DFLASH_FP_ALPHA`, `DFLASH27B_LM_HEAD_FIX`) when pflash is on. These materially affect prefill behavior and belong in introspection. `bsa_alpha` parses via `_parse_optional_float()` and surfaces `None` (with a `log.warning`) for non-numeric values rather than raising at request time.
- `lifetime_hits` are real cumulative counters on the cache objects, not sums over surviving entries.
- `daemon.alive` is `daemon_proc.poll() is None`. No PID, no `bin_path`, no uptime.
- No `supported_request_parameters` field — clients hit `/openapi.json` for precise per-endpoint schemas.

## Source-of-truth helpers

Single module-level constant for endpoint list, single function for arch-aware capabilities:

```python
_API_ENDPOINTS: list[str] = [
    "GET /health",
    "GET /props",
    "GET /v1/models",
    "POST /v1/chat/completions",
    "POST /v1/messages",
    "POST /v1/responses",
]
# Keep in sync with the @app.{get,post} decorators in build_app().
# Drift is caught by test_props_endpoints_match_app_routes.

def _capabilities(arch: str) -> dict:
    qwen = arch in _QWEN35_ARCHES
    return {
        "reasoning_supported": qwen,
        "speculative_supported": qwen,
        "tools_supported": qwen,
    }
```

`/props` consumes `_capabilities(arch)`. The Codex variant of `/v1/models` (`server.py:754-771`) currently keeps its existing hardcoded fields and does **not** call `_capabilities` — wiring it through is tracked under "Known limitations" because the Codex schema requires non-empty `supported_reasoning_levels` and `default_reasoning_level`, and gating those on `arch="laguna"` needs validation against a real Codex client first. Standard `/v1/models` is unchanged — no `meta` block contamination of the Codex payload.

## Versioning

```python
import tomllib

_PYPROJECT = Path(__file__).resolve().parent.parent / "pyproject.toml"

def _resolve_server_version() -> str:
    # Source: dflash/pyproject.toml [project] version. Reflects the
    # declared workspace version; bump on releases.
    try:
        with _PYPROJECT.open("rb") as f:
            return tomllib.load(f)["project"]["version"]
    except (OSError, KeyError):
        # File missing or shape unexpected — common case before the
        # workspace pyproject is committed. Silent fallback.
        return "0.0.0+unknown"
    except tomllib.TOMLDecodeError as exc:
        # File present but malformed — that's a real config bug worth
        # surfacing, not a silent fallback case.
        log.warning("could not parse %s for server version: %s", _PYPROJECT, exc)
        return "0.0.0+unknown"

SERVER_VERSION = _resolve_server_version()

PROPS_SCHEMA = 1
# Bump only on breaking changes to /props output:
#   - field renamed
#   - field removed
#   - existing field's semantics change (units, nullability, type)
# Do NOT bump for additive changes (new fields, new sections).
```

`tomllib` is stdlib in Python 3.11+, which the project pins. `importlib.metadata` is *not* used because `dflash/pyproject.toml` declares `[tool.uv] package = false` — the project is never installed as a wheel and `importlib.metadata.version("lucebox-dflash")` would always raise `PackageNotFoundError`.

## Concurrency

- `tool_replay` reads `current_entries` and `current_bytes` under no lock — `ToolMemory` doesn't carry one. The two reads happen consecutively under the GIL; a mutation between them can tear the pair, which is acceptable for an introspection endpoint (call out in a comment at the `stats()` site).
- `prefix_cache` and `full_cache` slot/hit reads are lockless (single-threaded mutation under `daemon_lock`). A `/props` call landing mid-eviction may report a transiently inconsistent slot count; same posture as above.
- `daemon.alive` is a plain `poll()` — already lockless elsewhere.

## Adjacent code changes

| File | Change |
|---|---|
| `server.py` | New `@app.get("/props")` route; `_resolve_server_version`, `_capabilities(arch)`, `_effective_kv_type(axis, arch)`, `_pflash_props`, `_parse_optional_float` helpers; `_API_ENDPOINTS` constant; `SERVER_VERSION`, `PROPS_SCHEMA` constants. `tomllib` and `fastapi.routing.APIRoute` imports added. |
| `prefix_cache.py` | `stats()` and `full_stats()` methods on `PrefixCache`; cumulative `_lifetime_hits` (incremented on every successful `lookup()`) and `_full_lifetime_hits` (incremented on every successful `lookup_full()`) counters; `_full_disk_bytes_snapshot` refreshed on every full-cache mutation (`confirm_full_snap`, `_retire_full_entry`, `rehydrate_full_cache`, missing-file pop in `lookup_full`) so `/props` never has to `stat()` cache files. |
| `tool_memory.py` | `stats()` method returning `{max_entries, max_bytes, current_entries, current_bytes}` with no mutex (cross-field tear accepted, comment documents it). |
| `server.py` (KV resolution) | `_effective_kv_type(axis, arch)` mirrors the per-arch precedence in `src/kv_quant.cpp::resolve_kv_types()` (qwen35: default Q4_0, legacy `_KV_F16`/`_KV_Q4`/`_KV_TQ3` last-wins, per-axis `_KV_K`/`_KV_V` overrides legacy) and the laguna path in `test/test_dflash.cpp` (default Q8_0, reads only `_KV_K`). Distinct from `_resolve_kv_k_type()` which remains the prefix-cache hash salt. |

## Tests (mock-only baseline pass; no daemon required)

17 tests in `dflash/scripts/test_server.py` cover the endpoint and its supporting helpers.

`/props` endpoint shape:

| Test | What it verifies |
|---|---|
| `test_props_endpoint_shape` | All top-level keys present; JSON parses; `props_schema == 1` |
| `test_props_version_reads_pyproject` | `SERVER_VERSION` is a non-empty string; if not the fallback, looks semver-ish |
| `test_props_version_falls_back_when_pyproject_missing` | Renaming the pyproject path produces `"0.0.0+unknown"` |
| `test_props_arch_qwen35` | qwen35 → `reasoning.supported`, `speculative.enabled`, `speculative.ddtree_budget == 22`, `draft_path` populated |
| `test_props_arch_laguna` | laguna → `reasoning.supported == false`, `speculative.enabled == false`, `ddtree_budget is None`, `draft_path is None` |
| `test_props_pflash_disabled` | `prefill_cfg=None` → `pflash.enabled == false`, optional pflash fields are `null` |
| `test_props_pflash_enabled` | Reflects threshold, keep_ratio, drafter_gguf, and `DFLASH_FP_USE_BSA` / `DFLASH_FP_ALPHA` env state |
| `test_props_target_sharding_disables_caches` | `extra_daemon_args` containing `--target-gpus` → `prefix_cache.capacity == 0`, `full_cache.enabled == false` |
| `test_props_endpoints_match_app_routes` | Diffs `_API_ENDPOINTS` against actual FastAPI routes (excluding `/openapi.json`, `/docs`, `/redoc`) — drift detector |

Helper unit tests:

| Test | What it verifies |
|---|---|
| `test_capabilities_arch_gated` | `_capabilities("qwen35")` vs `_capabilities("laguna")` return correct booleans |
| `test_effective_kv_type_qwen35_defaults` | With all KV env vars unset, qwen35 K and V both resolve to `q4_0` (matches C++ default) |
| `test_effective_kv_type_qwen35_per_axis_override` | `_KV_TQ3=1` + `_KV_V=q4_0` → K is `tq3_0`, V is `q4_0` (per-axis override beats legacy) |
| `test_effective_kv_type_laguna_ignores_legacy_and_v` | Laguna ignores `_KV_TQ3` and `_KV_V`; only `_KV_K` matters; default `q8_0` |
| `test_prefix_cache_stats_disabled` | A disabled `PrefixCache` reports `capacity=0, in_use=0, lifetime_hits=0` |
| `test_prefix_cache_lifetime_hits_increments` | Repeated `lookup()` hits increment `_lifetime_hits`; counter survives eviction |
| `test_full_cache_disk_bytes_snapshot_updates_on_mutation` | `confirm_full_snap` and `_retire_full_entry` refresh `disk_bytes` without `stat()` on read |
| `test_tool_memory_stats` | Empty `ToolMemory` reports zero counters; after `remember()`, current_entries and current_bytes reflect the inserted block |

## Known limitations / v2 candidates

1. **No daemon build identity.** A `/props` capture pins Python-server config but not C++ daemon commit. Two `/props` outputs with the same `server.version` can still come from differently-built daemons. v2: stdin-protocol `version` handshake that returns commit + BSA flag + CUDA arch list.
2. **No request-rate / latency / token-throughput metrics.** v2 `/metrics`.
3. **No per-endpoint param schemas.** Clients hit `/openapi.json`.
4. **`server.version` requires manual `pyproject.toml` bumps.** Release-hygiene problem, not a `/props` problem. Working-tree edits between releases will report whatever version the file says.
5. **Codex `/v1/models` variant doesn't yet call `_capabilities(arch)`.** The helper exists and `/props` consumes it; the Codex payload (`server.py:754-771`) keeps its hardcoded `default_reasoning_level` / `supported_reasoning_levels` because gating those on `arch="laguna"` needs validation against a real Codex client (the schema may require non-empty values). Drift between `/props` and the Codex payload remains possible until this is wired through.

## Prior art

- `antirez/ds4` PR #81 — single-binary C server, same `/props` convention. Cleanly demonstrates the "single runtime-config struct + shared constants between request path and introspection" pattern. Source for several conventions adopted here: hand-curated endpoint list with sync comment, lock-where-it-matters concurrency, toggle-state tests, no `pid`/`uptime`/`bin_path`.
- `llama.cpp` `llama-server` `/props` — convention for endpoint name and "single JSON document describing the live server."
