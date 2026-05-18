"""lucebox_bench — in-container benchmark sweep.

Run inside the lucebox-hub image to pick the optimal DFLASH_* knobs for the
specific (GPU, target, draft) combination on this host. Writes the winning
config to /opt/lucebox-hub/dflash/models/.lucebox/config.env (which lives in
the host bind-mount, so the host-side `lucebox` CLI reads it back after the
container exits).

Profiles:

  quick:    Sweep DFLASH_BUDGET at the configured DFLASH_MAX_CTX. This is the
            fast smoke profile and preserves the v1 behavior.

  context:  Sweep DFLASH_MAX_CTX × DFLASH_BUDGET. Winner selection is
            context-first: choose the highest reliable context, then the
            fastest budget within that context. This is the profile to use
            when the goal is "serve the longest context that remains fast
            enough."

  full:     Same sweep as context, plus the standard post-winner validation
            suites (HTTP frontiers, graded capability, and agentic tools) unless the caller
            overrides --extra-suites.

Output:     .lucebox/config.env (overwrites DFLASH_BUDGET and
            DFLASH_MAX_CTX — other DFLASH_* keys from host autotune are
            preserved by merge) and
            .lucebox/bench-report.json (raw per-cell numbers).
"""

import argparse
import fnmatch
import json
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path

# bench_daemon's run() handles the streaming SSE protocol; we reuse it
# verbatim instead of re-implementing token counting / decode-window
# timing. Same module exposes the HE PROMPTS table.
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from bench_daemon import run as run_decode  # noqa: E402
from bench_he import PROMPTS  # noqa: E402

DFLASH_DIR = Path(os.environ.get("DFLASH_DIR", "/opt/lucebox-hub/dflash"))
MODELS_DIR = DFLASH_DIR / "models"
REPORT_DIR = MODELS_DIR / ".lucebox"
ENV_FILE = REPORT_DIR / "config.env"
REPORT_FILE = REPORT_DIR / "bench-report.json"

# Bind to a non-default port so we don't collide with anything the user
# already has running on 8080. The bench process is single-tenant.
BENCH_PORT = int(os.environ.get("LUCEBOX_BENCH_PORT", "8181"))
BENCH_URL = f"http://127.0.0.1:{BENCH_PORT}"

# Default sweep. Override via --budgets.
DEFAULT_BUDGETS = [8, 16, 22, 32]
DEFAULT_PROMPTS = 5     # subset of bench_he.PROMPTS for speed
DEFAULT_N_GEN = 256
DEFAULT_READY_TIMEOUT_S = 180
DEFAULT_CELL_TIMEOUT_S = 240
DEFAULT_FRONTIERS = "2048,4096,8192,16384"
STRESS_FRONTIERS = "512,2048,4096,8192"
DEFAULT_AGENTIC_REPEAT = 1
STRESS_AGENTIC_REPEAT = 5
DEFAULT_CTX_VALUES = [32768, 65536, 98304, 114688, 131072]
DEFAULT_MIN_CONTEXT_SPEED_RATIO = 0.85
DFLASH_KEYS_PASSTHROUGH = (
    "DFLASH_TARGET", "DFLASH_DRAFT", "DFLASH_BIN", "DFLASH_MAX_CTX",
    "DFLASH_LAZY", "DFLASH_PREFIX_CACHE_SLOTS", "DFLASH_PREFILL_CACHE_SLOTS",
    "DFLASH_VERBOSE",
)


def log(msg: str) -> None:
    print(f"[lucebox-bench] {msg}", flush=True)


@dataclass(frozen=True)
class SweepConfig:
    max_ctx: int
    budget: int
    lazy: bool
    prefix_cache_slots: int
    prefill_cache_slots: int
    kv: str
    prefill_mode: str
    prefill_keep_ratio: float
    prefill_threshold: int
    prefill_drafter: str = ""

    @property
    def cache_type_k(self) -> str:
        return "" if self.kv == "auto" else self.kv

    @property
    def cache_type_v(self) -> str:
        return "" if self.kv == "auto" else self.kv

    def report_fields(self) -> dict:
        out = asdict(self)
        out["cache_type_k"] = self.cache_type_k
        out["cache_type_v"] = self.cache_type_v
        return out


def find_target_gguf() -> Path:
    """Same selection rule as entrypoint.sh: largest .gguf under models/."""
    target = os.environ.get("DFLASH_TARGET")
    if target and Path(target).is_file():
        return Path(target)
    preferred = sorted(_find_model_files("*Qwen3.6*Q4_K_M*.gguf"))
    if preferred:
        return preferred[0]
    candidates = sorted(
        _find_model_files("*.gguf"),
        key=lambda p: p.stat().st_size,
        reverse=True,
    )
    if not candidates:
        raise SystemExit(
            f"No .gguf found under {MODELS_DIR}. Mount a model dir and re-run."
        )
    return candidates[0]


def _find_model_files(pattern: str) -> list[Path]:
    out: list[Path] = []
    for root, _dirs, files in os.walk(MODELS_DIR, followlinks=True):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                out.append(Path(root) / name)
    return out


def find_draft_default() -> Path:
    env = os.environ.get("DFLASH_DRAFT")
    if env:
        return Path(env)
    for name in ("draft", "qwen3.6-27b-dflash", "Qwen3.6-27B-DFlash", "dflash"):
        cand = MODELS_DIR / name
        if cand.exists():
            return cand
    return MODELS_DIR / "draft"


def find_prefill_drafter_default() -> Path | None:
    env = os.environ.get("DFLASH_PREFILL_DRAFTER")
    if env:
        p = Path(env)
        return p if p.is_file() else None
    patterns = ("*Qwen3-0.6B*BF16*.gguf", "*Qwen3-0.6B*.gguf", "*0.6B*.gguf")
    for pattern in patterns:
        found = sorted(_find_model_files(pattern))
        if found:
            return found[0]
    return None


def wait_ready(timeout_s: int) -> bool:
    """Poll /v1/models until the server responds 200 or timeout elapses."""
    deadline = time.monotonic() + timeout_s
    while time.monotonic() < deadline:
        try:
            with urllib.request.urlopen(f"{BENCH_URL}/v1/models", timeout=2) as r:
                if r.status == 200:
                    return True
        except (urllib.error.URLError, ConnectionResetError, socket.timeout):
            pass
        time.sleep(1)
    return False


def build_server_argv(cfg: SweepConfig, target: Path) -> list[str]:
    argv = [
        "uv", "run", "--directory", str(DFLASH_DIR),
        "python", "scripts/server.py",
        "--host", "127.0.0.1",
        "--port", str(BENCH_PORT),
        "--target", str(target),
        "--budget", str(cfg.budget),
        "--max-ctx", str(cfg.max_ctx),
        "--bin", os.environ.get("DFLASH_BIN", str(DFLASH_DIR / "build/test_dflash")),
        "--prefix-cache-slots", str(cfg.prefix_cache_slots),
        "--prefill-cache-slots", str(cfg.prefill_cache_slots),
    ]
    draft = str(find_draft_default())
    if draft and (Path(draft).is_dir() or Path(draft).is_file()):
        # Mirror entrypoint.sh: skip --draft if dir is empty.
        if Path(draft).is_dir() and not any(
            next(Path(draft).rglob(pattern), None) is not None
            for pattern in ("dflash-draft-*.gguf", "*.gguf", "model.safetensors", "*.safetensors")
        ):
            pass
        else:
            argv += ["--draft", draft]
    if cfg.lazy:
        argv.append("--lazy-draft")
    if cfg.kv != "auto":
        argv += ["--cache-type-k", cfg.kv, "--cache-type-v", cfg.kv]
    if cfg.prefill_mode != "off":
        argv += [
            "--prefill-compression", cfg.prefill_mode,
            "--prefill-keep-ratio", str(cfg.prefill_keep_ratio),
            "--prefill-threshold", str(cfg.prefill_threshold),
            "--prefill-drafter", cfg.prefill_drafter,
        ]
    return argv


def run_cell(cfg: SweepConfig, target: Path, prompts: list[tuple[str, str]],
             n_gen: int, ready_timeout_s: int, cell_timeout_s: int
             ) -> dict:
    """Spawn server.py for a single config, run the prompt suite, tear down.

    Returns a dict describing the cell — never raises (errors are reported
    in the cell record so the sweep keeps going).
    """
    log(
        f"cell ctx={cfg.max_ctx} budget={cfg.budget} lazy={int(cfg.lazy)} "
        f"prefix={cfg.prefix_cache_slots} kv={cfg.kv} pflash={cfg.prefill_mode}: "
        f"starting server on :{BENCH_PORT}"
    )
    argv = build_server_argv(cfg, target)
    # New process group so we can SIGTERM the whole subtree (server.py spawns
    # test_dflash as a child).
    proc = subprocess.Popen(
        argv,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    cell: dict = {**cfg.report_fields(), "trials": [], "status": "pending"}
    deadline = time.monotonic() + cell_timeout_s
    try:
        if not wait_ready(ready_timeout_s):
            cell["status"] = "server_not_ready"
            return cell

        log(
            f"cell ctx={cfg.max_ctx} budget={cfg.budget} lazy={int(cfg.lazy)} "
            f"prefix={cfg.prefix_cache_slots} kv={cfg.kv} pflash={cfg.prefill_mode}: "
            f"server ready, running {len(prompts)} prompts"
        )
        for name, text in prompts:
            if time.monotonic() > deadline:
                cell["status"] = "cell_timeout"
                return cell
            try:
                n_tok, wall_s, decode_s = run_decode(BENCH_URL, text, n_gen)
            except Exception as e:
                cell["trials"].append({"prompt": name, "error": str(e)})
                continue
            dec_tps = (n_tok - 1) / decode_s if decode_s > 0 and n_tok > 1 else 0.0
            cell["trials"].append({
                "prompt": name, "n_tok": n_tok,
                "wall_s": round(wall_s, 3),
                "decode_s": round(decode_s, 3),
                "decode_tps": round(dec_tps, 2),
            })
            log(f"  {name:26s}  n_tok={n_tok:4d}  decode={dec_tps:7.2f} tok/s")

        # Reliability gate: <50 tokens or zero successful trials = disqualify.
        ok_trials = [t for t in cell["trials"]
                     if "decode_tps" in t and t["n_tok"] >= 50]
        if not ok_trials:
            cell["status"] = "no_valid_trials"
            return cell
        cell["status"] = "ok"
        tps = sorted(t["decode_tps"] for t in ok_trials)
        cell["mean_decode_tps"] = round(sum(tps) / len(tps), 2)
        cell["p10_decode_tps"] = tps[max(0, len(tps) // 10)]
        cell["min_decode_tps"] = tps[0]
        cell["max_decode_tps"] = tps[-1]
        cell["n_ok_trials"] = len(ok_trials)
    finally:
        # Kill the process group; server.py installs no SIGTERM handler, so a
        # plain TERM should fall through and bring down test_dflash too.
        try:
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait(timeout=5)
        except ProcessLookupError:
            pass
    return cell


def rank_candidates(
    cells: list[dict],
    *,
    profile: str = "quick",
    min_context_speed_ratio: float = DEFAULT_MIN_CONTEXT_SPEED_RATIO,
) -> list[dict]:
    ok = [c for c in cells if c["status"] == "ok"]
    if not ok:
        return []
    if profile in {"context", "full", "stress"}:
        fastest = max(float(c["mean_decode_tps"]) for c in ok)
        speed_floor = fastest * min_context_speed_ratio
        viable = [c for c in ok if float(c["mean_decode_tps"]) >= speed_floor] or ok
        # Context-first: highest reliable max_ctx that stays near the fastest
        # candidate, then best mean and tail decode inside that context.
        viable.sort(
            key=lambda c: (int(c["max_ctx"]), c["mean_decode_tps"], c["min_decode_tps"]),
            reverse=True,
        )
        return viable
    # Quick profile: primary speed, tie-break by max_ctx then tail reliability.
    ok.sort(
        key=lambda c: (c["mean_decode_tps"], int(c["max_ctx"]), c["min_decode_tps"]),
        reverse=True,
    )
    return ok


def pick_winner(
    cells: list[dict],
    *,
    profile: str = "quick",
    min_context_speed_ratio: float = DEFAULT_MIN_CONTEXT_SPEED_RATIO,
) -> dict | None:
    ranked = rank_candidates(
        cells,
        profile=profile,
        min_context_speed_ratio=min_context_speed_ratio,
    )
    return ranked[0] if ranked else None


def candidate_summary(candidate: dict) -> dict:
    keys = (
        "max_ctx", "budget", "lazy", "prefix_cache_slots", "prefill_cache_slots",
        "kv", "prefill_mode", "prefill_keep_ratio", "prefill_threshold",
        "prefill_drafter", "cache_type_k", "cache_type_v", "mean_decode_tps",
        "min_decode_tps",
    )
    return {key: candidate.get(key) for key in keys if key in candidate}


def run_extra_suites(
    cfg: SweepConfig,
    target: Path,
    suites: list[str],
    ready_timeout_s: int,
    frontiers: str,
    agentic_repeat: int,
) -> list[dict]:
    """Run optional post-optimizer suites against the winning config."""
    if not suites:
        return []
    argv = build_server_argv(cfg, target)
    results: list[dict] = []
    for suite in suites:
        suite = suite.strip()
        if not suite:
            continue
        if suite in {"http-frontiers", "ds4-frontiers"}:
            suite_name = "http-frontiers"
            out_json = REPORT_DIR / "bench-http-frontiers.json"
            out_csv = REPORT_DIR / "bench-http-frontiers.csv"
            cmd = [
                sys.executable, str(SCRIPT_DIR / "bench_http_frontiers.py"),
                "--url", BENCH_URL,
                "--frontiers", frontiers,
                "--gen-tokens", "64",
                "--json-out", str(out_json),
                "--csv-out", str(out_csv),
            ]
        elif suite == "capability":
            suite_name = suite
            out_json = REPORT_DIR / "bench-capability.json"
            trace = REPORT_DIR / "bench-capability-trace.txt"
            cmd = [
                sys.executable, str(SCRIPT_DIR / "bench_http_capability.py"),
                "--url", BENCH_URL,
                "--json-out", str(out_json),
                "--trace", str(trace),
            ]
        elif suite == "agentic-tools":
            suite_name = suite
            out_json = REPORT_DIR / "bench-agentic-tools.json"
            cmd = [
                sys.executable, str(SCRIPT_DIR / "bench_agentic_tools.py"),
                "--url", BENCH_URL,
                "--repeat", str(agentic_repeat),
                "--json-out", str(out_json),
            ]
        else:
            results.append({"suite": suite, "status": "unknown_suite"})
            continue

        log(f"extra suite {suite_name}: starting winner server on :{BENCH_PORT}")
        proc = subprocess.Popen(
            argv,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        try:
            if not wait_ready(ready_timeout_s):
                results.append({"suite": suite_name, "status": "server_not_ready"})
                continue
            log(f"extra suite {suite_name}: running")
            t0 = time.monotonic()
            rc = subprocess.call(cmd)
            results.append({
                "suite": suite_name,
                "status": "ok" if rc == 0 else "failed",
                "returncode": rc,
                "wall_s": round(time.monotonic() - t0, 3),
                "report": str(out_json),
            })
        finally:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait(timeout=5)
            except ProcessLookupError:
                pass
    return results


def merge_env_file(updates: dict[str, str]) -> None:
    """Read-modify-write config.env, preserving non-DFLASH lines."""
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    existing: dict[str, str] = {}
    header: list[str] = []
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            if not line or line.startswith("#"):
                header.append(line)
                continue
            if "=" in line:
                k, v = line.split("=", 1)
                existing[k.strip()] = v.strip()
    existing.update(updates)

    lines = list(header)
    lines.append(f"# Updated by lucebox_bench at {time.strftime('%Y-%m-%dT%H:%M:%S')}")
    for k, v in existing.items():
        lines.append(f"{k}={v}")
    ENV_FILE.write_text("\n".join(lines) + "\n")


def parse_int_list(value: str) -> list[int]:
    return [int(x) for x in value.split(",") if x.strip()]


def parse_float_list(value: str) -> list[float]:
    return [float(x) for x in value.split(",") if x.strip()]


def parse_str_list(value: str) -> list[str]:
    return [x.strip() for x in value.split(",") if x.strip()]


def parse_bool_list(value: str, current: bool) -> list[bool]:
    if not value:
        return [current]
    out: list[bool] = []
    for raw in parse_str_list(value):
        lowered = raw.lower()
        if lowered in {"1", "true", "yes", "on", "lazy"}:
            out.append(True)
        elif lowered in {"0", "false", "no", "off", "eager"}:
            out.append(False)
        else:
            raise SystemExit(f"Invalid boolean sweep value: {raw!r}")
    return out


def current_kv_value() -> str:
    cache_type_k = os.environ.get("DFLASH_CACHE_TYPE_K", "")
    cache_type_v = os.environ.get("DFLASH_CACHE_TYPE_V", "")
    if cache_type_k and cache_type_k == cache_type_v:
        return cache_type_k
    return "auto"


def context_values_for_profile(profile: str, explicit_values: str) -> list[int]:
    configured = int(os.environ.get("DFLASH_MAX_CTX", "16384"))
    if explicit_values:
        return parse_int_list(explicit_values)
    if profile == "quick":
        return [configured]
    values = [v for v in DEFAULT_CTX_VALUES if v <= configured]
    if configured not in values:
        values.append(configured)
    return sorted(set(values))


def sweep_configs(args) -> list[SweepConfig]:
    current_lazy = os.environ.get("DFLASH_LAZY", "0") == "1"
    current_prefix = int(os.environ.get("DFLASH_PREFIX_CACHE_SLOTS", "1"))
    current_prefill_slots = int(os.environ.get("DFLASH_PREFILL_CACHE_SLOTS", "0"))
    current_prefill_mode = os.environ.get("DFLASH_PREFILL_MODE", "off")
    current_prefill_keep = float(os.environ.get("DFLASH_PREFILL_KEEP", "0.05"))
    current_prefill_threshold = int(os.environ.get("DFLASH_PREFILL_THRESHOLD", "32000"))
    current_kv = current_kv_value()

    budgets = parse_int_list(args.budgets)
    ctx_values = context_values_for_profile(args.profile, args.ctx_values)
    lazy_values = parse_bool_list(args.lazy_values, current_lazy)
    prefix_values = (
        parse_int_list(args.prefix_cache_slots_values)
        if args.prefix_cache_slots_values else [current_prefix]
    )
    prefill_slot_values = (
        parse_int_list(args.prefill_cache_slots_values)
        if args.prefill_cache_slots_values else [current_prefill_slots]
    )
    kv_values = parse_str_list(args.kv_values) if args.kv_values else [current_kv]
    prefill_modes = (
        parse_str_list(args.prefill_modes)
        if args.prefill_modes else [current_prefill_mode]
    )
    prefill_keep_ratios = (
        parse_float_list(args.prefill_keep_ratios)
        if args.prefill_keep_ratios else [current_prefill_keep]
    )
    prefill_thresholds = (
        parse_int_list(args.prefill_thresholds)
        if args.prefill_thresholds else [current_prefill_threshold]
    )
    prefill_drafter = args.prefill_drafter or os.environ.get("DFLASH_PREFILL_DRAFTER", "")
    if any(mode != "off" for mode in prefill_modes):
        if not prefill_drafter:
            found = find_prefill_drafter_default()
            if found is not None:
                prefill_drafter = str(found)
        if not prefill_drafter or not Path(prefill_drafter).is_file():
            raise SystemExit(
                "PFlash sweep requested but no prefill drafter GGUF was found. "
                "Pass --prefill-drafter or set DFLASH_PREFILL_DRAFTER."
            )

    configs: list[SweepConfig] = []
    for max_ctx in ctx_values:
        for budget in budgets:
            for lazy in lazy_values:
                for prefix_slots in prefix_values:
                    for prefill_slots in prefill_slot_values:
                        for kv in kv_values:
                            for prefill_mode in prefill_modes:
                                if prefill_mode == "off":
                                    configs.append(SweepConfig(
                                        max_ctx=max_ctx,
                                        budget=budget,
                                        lazy=lazy,
                                        prefix_cache_slots=prefix_slots,
                                        prefill_cache_slots=prefill_slots,
                                        kv=kv,
                                        prefill_mode="off",
                                        prefill_keep_ratio=current_prefill_keep,
                                        prefill_threshold=current_prefill_threshold,
                                    ))
                                    continue
                                for keep_ratio in prefill_keep_ratios:
                                    for threshold in prefill_thresholds:
                                        configs.append(SweepConfig(
                                            max_ctx=max_ctx,
                                            budget=budget,
                                            lazy=lazy,
                                            prefix_cache_slots=prefix_slots,
                                            prefill_cache_slots=prefill_slots,
                                            kv=kv,
                                            prefill_mode=prefill_mode,
                                            prefill_keep_ratio=keep_ratio,
                                            prefill_threshold=threshold,
                                            prefill_drafter=prefill_drafter,
                                        ))
    return configs


def config_from_winner(winner: dict) -> SweepConfig:
    kv = str(winner.get("kv", ""))
    if not kv:
        cache_type_k = str(winner.get("cache_type_k", ""))
        cache_type_v = str(winner.get("cache_type_v", ""))
        kv = cache_type_k if cache_type_k and cache_type_k == cache_type_v else "auto"
    return SweepConfig(
        max_ctx=int(winner["max_ctx"]),
        budget=int(winner["budget"]),
        lazy=bool(winner.get("lazy", False)),
        prefix_cache_slots=int(winner.get("prefix_cache_slots", 1)),
        prefill_cache_slots=int(winner.get("prefill_cache_slots", 0)),
        kv=kv,
        prefill_mode=str(winner.get("prefill_mode", "off")),
        prefill_keep_ratio=float(winner.get("prefill_keep_ratio", 0.05)),
        prefill_threshold=int(winner.get("prefill_threshold", 32000)),
        prefill_drafter=str(winner.get("prefill_drafter", "")),
    )


def main() -> int:
    ap = argparse.ArgumentParser(description="Sweep DFLASH_* knobs for this host.")
    ap.add_argument("--profile", choices=("quick", "context", "full", "stress"), default="quick",
                    help="quick=speed at configured ctx; context=maximize ctx then speed; "
                         "full=context plus validation suites; "
                         "stress=full with warmed capability, agentic, and frontier gates.")
    ap.add_argument("--budgets", type=str, default=",".join(map(str, DEFAULT_BUDGETS)),
                    help="Comma-separated DFLASH_BUDGET values to sweep.")
    ap.add_argument("--ctx-values", type=str, default="",
                    help="Comma-separated DFLASH_MAX_CTX values to sweep. "
                         "Default: configured ctx for quick; tiered values up to configured ctx "
                         "for context/full.")
    ap.add_argument("--min-context-speed-ratio", type=float,
                    default=DEFAULT_MIN_CONTEXT_SPEED_RATIO,
                    help="For context/full, keep only candidates at least this fraction "
                         "of the fastest reliable cell before maximizing context.")
    ap.add_argument("--lazy-values", type=str, default="",
                    help="Comma-separated lazy-draft values to sweep: 0,1. "
                         "Default: configured DFLASH_LAZY only.")
    ap.add_argument("--prefix-cache-slots-values", type=str, default="",
                    help="Comma-separated --prefix-cache-slots values. "
                         "Default: configured DFLASH_PREFIX_CACHE_SLOTS only.")
    ap.add_argument("--prefill-cache-slots-values", type=str, default="",
                    help="Comma-separated --prefill-cache-slots values. "
                         "Default: configured DFLASH_PREFILL_CACHE_SLOTS only.")
    ap.add_argument("--kv-values", type=str, default="",
                    help="Comma-separated KV modes: auto,f16,q4_0,q4_1,q5_0,q5_1,q8_0,tq3_0.")
    ap.add_argument("--prefill-modes", type=str, default="",
                    help="Comma-separated PFlash modes: off,auto,always. "
                         "Default: configured DFLASH_PREFILL_MODE only.")
    ap.add_argument("--prefill-keep-ratios", type=str, default="",
                    help="Comma-separated PFlash keep ratios. Default: configured value.")
    ap.add_argument("--prefill-thresholds", type=str, default="",
                    help="Comma-separated PFlash auto thresholds. Default: configured value.")
    ap.add_argument("--prefill-drafter", type=str, default="",
                    help="PFlash drafter GGUF path for non-off prefill modes.")
    ap.add_argument("--allow-extra-suite-failures", action="store_true",
                    help="Write the winning config even if post-winner validation suites fail.")
    ap.add_argument("--n-prompts", type=int, default=DEFAULT_PROMPTS,
                    help="How many bench_he prompts per cell (1..10).")
    ap.add_argument("--n-gen", type=int, default=DEFAULT_N_GEN,
                    help="Generated tokens per prompt.")
    ap.add_argument("--ready-timeout", type=int, default=DEFAULT_READY_TIMEOUT_S,
                    help="Seconds to wait for server.py readiness per cell.")
    ap.add_argument("--cell-timeout", type=int, default=DEFAULT_CELL_TIMEOUT_S,
                    help="Hard wall-clock budget per cell.")
    ap.add_argument("--extra-suites", type=str, default="",
                    help="Comma-separated post-optimizer suites: http-frontiers,capability,agentic-tools.")
    ap.add_argument("--frontiers", type=str, default=DEFAULT_FRONTIERS,
                    help="Frontiers for the http-frontiers extra suite.")
    ap.add_argument("--agentic-repeat", type=int, default=DEFAULT_AGENTIC_REPEAT,
                    help="Repeats per prompt for the agentic-tools extra suite.")
    args = ap.parse_args()

    configs = sweep_configs(args)
    n_prompts = max(1, min(args.n_prompts, len(PROMPTS)))
    prompts = PROMPTS[:n_prompts]
    extra_suites = [s.strip() for s in args.extra_suites.split(",") if s.strip()]
    if args.profile in {"full", "stress"} and not extra_suites:
        extra_suites = ["http-frontiers", "capability", "agentic-tools"]
    if args.profile == "stress":
        if args.agentic_repeat == DEFAULT_AGENTIC_REPEAT:
            args.agentic_repeat = STRESS_AGENTIC_REPEAT
        if args.frontiers == DEFAULT_FRONTIERS:
            args.frontiers = STRESS_FRONTIERS

    target = find_target_gguf()
    log(f"target: {target.name} ({target.stat().st_size // (1024**3)} GB)")
    log(f"profile={args.profile} speed_floor={args.min_context_speed_ratio:.0%}")
    log(f"sweeping {len(configs)} configs × {n_prompts} prompts × {args.n_gen} gen")
    log(f"each cell takes ~30-60s on a 24 GB consumer GPU; total ~{len(configs) * 60}s")

    cells: list[dict] = []
    for cfg in configs:
        cell = run_cell(cfg, target, prompts, args.n_gen,
                        args.ready_timeout, args.cell_timeout)
        cells.append(cell)
        if cell["status"] == "ok":
            log(f"  ctx={cfg.max_ctx} budget={cfg.budget} lazy={int(cfg.lazy)} "
                f"prefix={cfg.prefix_cache_slots} kv={cfg.kv} pflash={cfg.prefill_mode}: "
                f"mean {cell['mean_decode_tps']:.2f} "
                f"(range {cell['min_decode_tps']:.2f}-{cell['max_decode_tps']:.2f}) "
                f"tok/s [{cell['n_ok_trials']}/{n_prompts} ok]")
        else:
            log(f"  ctx={cfg.max_ctx} budget={cfg.budget} lazy={int(cfg.lazy)} "
                f"prefix={cfg.prefix_cache_slots} kv={cfg.kv} pflash={cfg.prefill_mode}: "
                f"{cell['status']}")

    ranked_candidates = rank_candidates(
        cells,
        profile=args.profile,
        min_context_speed_ratio=args.min_context_speed_ratio,
    )
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    winner = ranked_candidates[0] if ranked_candidates else None
    extra_results: list[dict] = []
    candidate_validations: list[dict] = []
    if winner and extra_suites:
        winner = None
        for candidate in ranked_candidates:
            candidate_cfg = config_from_winner(candidate)
            extra_results = run_extra_suites(
                candidate_cfg, target, extra_suites,
                args.ready_timeout, args.frontiers, args.agentic_repeat)
            failed_extras = [r for r in extra_results if r.get("status") != "ok"]
            candidate_validations.append({
                "candidate": candidate_summary(candidate),
                "extra_suites": extra_results,
                "accepted": not failed_extras or args.allow_extra_suite_failures,
            })
            if not failed_extras or args.allow_extra_suite_failures:
                winner = candidate
                break
            log(
                "candidate rejected by extra suites: "
                f"ctx={candidate.get('max_ctx')} budget={candidate.get('budget')} "
                f"prefix={candidate.get('prefix_cache_slots')} kv={candidate.get('kv')} "
                f"pflash={candidate.get('prefill_mode')} failures={failed_extras}"
            )

    REPORT_FILE.write_text(json.dumps({
        "winner": winner,
        "cells": cells,
        "extra_suites": extra_results,
        "candidate_validations": candidate_validations,
        "ranked_candidates": [candidate_summary(c) for c in ranked_candidates],
        "profile": args.profile,
        "configs": [cfg.report_fields() for cfg in configs],
        "min_context_speed_ratio": args.min_context_speed_ratio,
        "target": target.name,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }, indent=2))
    log(f"wrote {REPORT_FILE}")

    if not winner:
        if ranked_candidates and extra_suites:
            log("ERROR: no ranked candidates passed extra suites — config NOT updated")
        else:
            log("ERROR: no reliable cells found — config NOT updated")
        return 1

    log(f"winner: DFLASH_BUDGET={winner['budget']} "
        f"DFLASH_MAX_CTX={winner['max_ctx']} "
        f"DFLASH_LAZY={int(bool(winner.get('lazy')))} "
        f"PREFIX_CACHE_SLOTS={winner.get('prefix_cache_slots')} "
        f"KV={winner.get('kv')} "
        f"PFLASH={winner.get('prefill_mode')} "
        f"@ {winner['mean_decode_tps']:.2f} tok/s mean")
    merge_env_file({
        "DFLASH_BUDGET": str(winner["budget"]),
        "DFLASH_MAX_CTX": str(winner["max_ctx"]),
        "DFLASH_LAZY": "1" if winner.get("lazy") else "0",
        "DFLASH_PREFIX_CACHE_SLOTS": str(winner.get("prefix_cache_slots", 1)),
        "DFLASH_PREFILL_CACHE_SLOTS": str(winner.get("prefill_cache_slots", 0)),
        "DFLASH_CACHE_TYPE_K": str(winner.get("cache_type_k", "")),
        "DFLASH_CACHE_TYPE_V": str(winner.get("cache_type_v", "")),
        "DFLASH_PREFILL_MODE": str(winner.get("prefill_mode", "off")),
        "DFLASH_PREFILL_KEEP": str(winner.get("prefill_keep_ratio", 0.05)),
        "DFLASH_PREFILL_THRESHOLD": str(winner.get("prefill_threshold", 32000)),
        "DFLASH_PREFILL_DRAFTER": str(winner.get("prefill_drafter", "")),
        "LUCEBOX_BENCH_MEAN_TPS": str(winner["mean_decode_tps"]),
    })
    log(f"wrote {ENV_FILE}")
    log("done — host CLI will pick this up on next 'lucebox start'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
