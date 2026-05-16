"""lucebox_bench — in-container benchmark sweep.

Run inside the lucebox-hub image to pick the optimal DFLASH_* knobs for the
specific (GPU, target, draft) combination on this host. Writes the winning
config to /opt/lucebox-hub/dflash/models/.lucebox/config.env (which lives in
the host bind-mount, so the host-side `lucebox` CLI reads it back after the
container exits).

v1 scope — keep it minimal, ship something users can run end-to-end:

  Suite:    HE-style code-completion prompts (bench_he.PROMPTS), 5 prompts
            × 256 generated tokens. Captures decode throughput on the
            workload most sensitive to DFLASH_BUDGET. Deterministic prompts
            + greedy decoding ≈ comparable cells.

  Sweep:    DFLASH_BUDGET ∈ {8, 16, 22, 32}. The biggest tok/s lever and the
            one with documented sweet-spot differences across GPU
            generations (Ampere likes 22, RDNA3 likes 8).

  Pick:     mean decode tok/s across the prompts, tie-break by p10 (low
            tail) for reliability. Cells that error or produce <50 tokens
            are disqualified.

  Output:   .lucebox/config.env (overwrites DFLASH_BUDGET only — other
            DFLASH_* keys from host autotune are preserved by merge) and
            .lucebox/bench-report.json (raw per-cell numbers).

Extending the suite (future work):

  - Long-context workload: 32K-token prompt, sweep DFLASH_PREFILL_MODE.
  - Multi-turn workload: 3-turn convo with shared system prompt, sweep
    DFLASH_PREFIX_CACHE_SLOTS.
  - Reliability gate: each cell repeats N=3 with a hard wall-clock budget
    so OOMs / hangs are caught instead of stalling the whole sweep.
"""

import argparse
import json
import os
import signal
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
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

DFLASH_KEYS_PASSTHROUGH = (
    "DFLASH_TARGET", "DFLASH_DRAFT", "DFLASH_BIN", "DFLASH_MAX_CTX",
    "DFLASH_LAZY", "DFLASH_PREFIX_CACHE_SLOTS", "DFLASH_PREFILL_CACHE_SLOTS",
    "DFLASH_VERBOSE",
)


def log(msg: str) -> None:
    print(f"[lucebox-bench] {msg}", flush=True)


def find_target_gguf() -> Path:
    """Same selection rule as entrypoint.sh: largest .gguf under models/."""
    target = os.environ.get("DFLASH_TARGET")
    if target and Path(target).is_file():
        return Path(target)
    candidates = sorted(
        MODELS_DIR.rglob("*.gguf"),
        key=lambda p: p.stat().st_size,
        reverse=True,
    )
    if not candidates:
        raise SystemExit(
            f"No .gguf found under {MODELS_DIR}. Mount a model dir and re-run."
        )
    return candidates[0]


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


def build_server_argv(budget: int, target: Path) -> list[str]:
    argv = [
        "uv", "run", "--directory", str(DFLASH_DIR),
        "python", "scripts/server.py",
        "--host", "127.0.0.1",
        "--port", str(BENCH_PORT),
        "--target", str(target),
        "--budget", str(budget),
        "--max-ctx", os.environ.get("DFLASH_MAX_CTX", "16384"),
        "--bin", os.environ.get("DFLASH_BIN", str(DFLASH_DIR / "build/test_dflash")),
        "--prefix-cache-slots", os.environ.get("DFLASH_PREFIX_CACHE_SLOTS", "1"),
    ]
    draft = os.environ.get("DFLASH_DRAFT", str(MODELS_DIR / "draft"))
    if draft and (Path(draft).is_dir() or Path(draft).is_file()):
        # Mirror entrypoint.sh: skip --draft if dir is empty.
        if Path(draft).is_dir() and not any(Path(draft).glob("*.safetensors")):
            pass
        else:
            argv += ["--draft", draft]
    if os.environ.get("DFLASH_LAZY", "0") == "1":
        argv.append("--lazy-draft")
    return argv


def run_cell(budget: int, target: Path, prompts: list[tuple[str, str]],
             n_gen: int, ready_timeout_s: int, cell_timeout_s: int
             ) -> dict:
    """Spawn server.py for a single config, run the prompt suite, tear down.

    Returns a dict describing the cell — never raises (errors are reported
    in the cell record so the sweep keeps going).
    """
    log(f"cell budget={budget}: starting server on :{BENCH_PORT}")
    argv = build_server_argv(budget, target)
    # New process group so we can SIGTERM the whole subtree (server.py spawns
    # test_dflash as a child).
    proc = subprocess.Popen(
        argv,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    cell: dict = {"budget": budget, "trials": [], "status": "pending"}
    deadline = time.monotonic() + cell_timeout_s
    try:
        if not wait_ready(ready_timeout_s):
            cell["status"] = "server_not_ready"
            return cell

        log(f"cell budget={budget}: server ready, running {len(prompts)} prompts")
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


def pick_winner(cells: list[dict]) -> dict | None:
    ok = [c for c in cells if c["status"] == "ok"]
    if not ok:
        return None
    # Primary: mean decode tok/s. Tie-break: min decode tok/s (tail
    # reliability) — same budget that runs fastest *and* most stably wins.
    ok.sort(key=lambda c: (c["mean_decode_tps"], c["min_decode_tps"]),
            reverse=True)
    return ok[0]


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


def main() -> int:
    ap = argparse.ArgumentParser(description="Sweep DFLASH_* knobs for this host.")
    ap.add_argument("--budgets", type=str, default=",".join(map(str, DEFAULT_BUDGETS)),
                    help="Comma-separated DFLASH_BUDGET values to sweep.")
    ap.add_argument("--n-prompts", type=int, default=DEFAULT_PROMPTS,
                    help="How many bench_he prompts per cell (1..10).")
    ap.add_argument("--n-gen", type=int, default=DEFAULT_N_GEN,
                    help="Generated tokens per prompt.")
    ap.add_argument("--ready-timeout", type=int, default=DEFAULT_READY_TIMEOUT_S,
                    help="Seconds to wait for server.py readiness per cell.")
    ap.add_argument("--cell-timeout", type=int, default=DEFAULT_CELL_TIMEOUT_S,
                    help="Hard wall-clock budget per cell.")
    args = ap.parse_args()

    budgets = [int(x) for x in args.budgets.split(",") if x.strip()]
    n_prompts = max(1, min(args.n_prompts, len(PROMPTS)))
    prompts = PROMPTS[:n_prompts]

    target = find_target_gguf()
    log(f"target: {target.name} ({target.stat().st_size // (1024**3)} GB)")
    log(f"sweeping DFLASH_BUDGET ∈ {budgets} × {n_prompts} prompts × {args.n_gen} gen")
    log(f"each cell takes ~30-60s on a 24 GB consumer GPU; total ~{len(budgets) * 60}s")

    cells: list[dict] = []
    for budget in budgets:
        cell = run_cell(budget, target, prompts, args.n_gen,
                        args.ready_timeout, args.cell_timeout)
        cells.append(cell)
        if cell["status"] == "ok":
            log(f"  budget={budget}: mean {cell['mean_decode_tps']:.2f} "
                f"(range {cell['min_decode_tps']:.2f}-{cell['max_decode_tps']:.2f}) "
                f"tok/s [{cell['n_ok_trials']}/{n_prompts} ok]")
        else:
            log(f"  budget={budget}: {cell['status']}")

    winner = pick_winner(cells)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_FILE.write_text(json.dumps({
        "winner": winner,
        "cells": cells,
        "target": target.name,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }, indent=2))
    log(f"wrote {REPORT_FILE}")

    if not winner:
        log("ERROR: no reliable cells found — config NOT updated")
        return 1

    log(f"winner: DFLASH_BUDGET={winner['budget']} "
        f"@ {winner['mean_decode_tps']:.2f} tok/s mean")
    merge_env_file({
        "DFLASH_BUDGET": str(winner["budget"]),
        "LUCEBOX_BENCH_MEAN_TPS": str(winner["mean_decode_tps"]),
    })
    log(f"wrote {ENV_FILE}")
    log("done — host CLI will pick this up on next 'lucebox start'")
    return 0


if __name__ == "__main__":
    sys.exit(main())
