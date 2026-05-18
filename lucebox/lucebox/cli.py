"""Typer app — the user-facing subcommands.

Layout follows the host wrapper's dispatch table. Anything `lucebox.sh`
doesn't intercept (everything outside the systemd surface) ends up here.

Subcommand inventory:
    check                  — readiness report
    configure              — write .lucebox/config.toml from heuristic autotune
    pull                   — docker pull the right variant
    print-run              — emit the docker-run command for the server
    print-serve-argv       — same, raw argv lines (consumed by lucebox.sh serve)
    benchmark              — sweep DFLASH_* knobs (stub for now)
    smoke                  — hit /v1/chat/completions on a running server (stub)
    download-models        — fetch target + draft via the container (stub)
"""

from __future__ import annotations

import sys
from datetime import UTC, datetime
from typing import Annotated

import typer
from rich.console import Console

from lucebox import __version__, docker_run, host_check
from lucebox import autotune as autotune_mod
from lucebox import config as config_mod
from lucebox import download as download_mod
from lucebox import smoke as smoke_mod
from lucebox.host_facts import from_env
from lucebox.types import AutotuneMeta, Config, Variant

app = typer.Typer(
    name="lucebox",
    help="Host CLI for the lucebox-hub container. Invoked by lucebox.sh.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


# ── helpers ────────────────────────────────────────────────────────────────

def _now() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _pick_variant_from_driver(driver_major: int, gpu_sm: str) -> Variant:
    # Mirrors lucebox.sh::pick_variant. Centralized so Python and bash agree.
    if gpu_sm == "110":
        return "cuda13"
    if driver_major >= 580:
        return "cuda13"
    if driver_major >= 525:
        return "cuda12"
    return "cuda13"


def _build_default_config() -> Config:
    """Build a fresh Config from current host facts + heuristic autotune."""
    host = from_env()
    variant = _pick_variant_from_driver(host.driver_major, host.gpu_sm)
    dflash = autotune_mod.runtime_from_host(host)
    return Config(
        variant=variant,
        dflash=dflash,
        host=host,
        autotune=AutotuneMeta(source="heuristic", timestamp=_now()),
    )


def _load_or_build() -> Config:
    cfg = config_mod.load()
    if cfg is not None:
        return cfg
    return _build_default_config()


# ── subcommands ────────────────────────────────────────────────────────────

@app.command()
def check() -> None:
    """Print a readiness report (driver, docker, CTK, RAM, VRAM, systemd)."""
    host = from_env()
    results = host_check.run_checks(host)
    worst = host_check.render(console, host, results)
    if worst == "fail":
        raise typer.Exit(code=1)


@app.command()
def configure(
    overwrite: Annotated[
        bool, typer.Option("--overwrite", "-o", help="Replace any existing config.toml")
    ] = False,
) -> None:
    """Pick CUDA variant + autotune defaults, write .lucebox/config.toml."""
    path = config_mod.default_config_path()
    if path.exists() and not overwrite:
        console.print(f"[yellow]{path} already exists — pass --overwrite to replace[/yellow]")
        raise typer.Exit(code=1)

    cfg = _build_default_config()
    written = config_mod.save(cfg, path)
    console.print(f"[green]Wrote[/green] {written}")
    console.print(f"  variant     [bold]{cfg.variant}[/bold]")
    console.print(f"  image       {cfg.image}:{cfg.variant}")
    console.print(f"  models      {cfg.models_dir}")
    console.print(f"  budget      {cfg.dflash.budget}")
    console.print(f"  max_ctx     {cfg.dflash.max_ctx}")
    console.print(f"  lazy_draft  {cfg.dflash.lazy}")
    console.print()
    console.print("Next:")
    console.print("  [dim]lucebox.sh pull[/dim]            # fetch the image")
    console.print("  [dim]lucebox.sh start[/dim]           # start via systemd")
    console.print("  [dim]lucebox.sh serve[/dim]           # foreground, no systemd")


@app.command()
def pull() -> None:
    """`docker pull` the image variant from config.toml."""
    cfg = _load_or_build()
    tag = f"{cfg.image}:{cfg.variant}"
    console.print(f"[bold]Pulling {tag}[/bold] (~14 GB; takes a while)…")
    rc = docker_run.docker_pull(tag)
    if rc != 0:
        raise typer.Exit(code=rc)


@app.command("print-run")
def print_run() -> None:
    """Print the docker-run command for the server (copy-pasteable)."""
    cfg = _load_or_build()
    spec = docker_run.server_run_spec(cfg)
    print(spec.printable())


@app.command("print-serve-argv")
def print_serve_argv() -> None:
    """Emit the server docker-run argv, one token per line.

    Consumed by lucebox.sh's `serve` subcommand and the systemd unit. Kept as
    a separate command from `print-run` so the bash side has a guaranteed
    machine-readable contract that's independent of the pretty formatter.
    """
    cfg = _load_or_build()
    spec = docker_run.server_run_spec(cfg)
    for tok in spec.argv():
        print(tok)


@app.command()
def benchmark() -> None:
    """Sweep DFLASH_* knobs inside the container, merge winner into config."""
    console.print("[yellow]benchmark not wired up in this build[/yellow]")
    console.print("Once landed it will spawn the bench container and merge the")
    console.print("optimal config back into .lucebox/config.toml. For now see")
    console.print("dflash/scripts/lucebox_bench.py.")
    raise typer.Exit(code=2)


@app.command()
def smoke(
    timeout: Annotated[float, typer.Option(help="Per-request timeout (seconds).")] = 60.0,
) -> None:
    """Hit /v1/chat/completions on the running server; report PASS/FAIL.

    Talks to the server container via the host docker bridge (port is mapped
    from cfg.port → 8080 inside). Pass criteria: HTTP 200 + ≥1 streamed
    content token within `timeout` seconds.
    """
    cfg = _load_or_build()
    result = smoke_mod.run(cfg, timeout_s=timeout)
    console.print(
        f"http={result.http_status}  tokens={result.n_tokens}  "
        f"wall={result.wall_s:.2f}s"
    )
    if result.ok:
        console.print("[green]PASS[/green]")
        return
    console.print(f"[red]FAIL[/red]  {result.error}")
    raise typer.Exit(code=1)


@app.command("download-models")
def download_models() -> None:
    """Fetch the default target + DFlash draft into the models dir.

    Streams `hf download` progress to the user. Resume-safe: re-running after
    an interrupted download picks up where it left off.
    """
    cfg = _load_or_build()
    pres = download_mod.DEFAULT_PRESET
    current = download_mod.status(cfg, pres)
    console.print(f"Models dir: [bold]{cfg.models_dir}[/bold]")
    console.print(f"  target ({pres.target_repo}/{pres.target_file}):"
                  f"  {'present' if current['target_present'] else 'will download'}")
    console.print(f"  draft  ({pres.draft_repo}):"
                  f"  {'present' if current['draft_present'] else 'will download'}")
    if current["target_present"] and current["draft_present"]:
        console.print("[green]Both present. Nothing to do.[/green]")
        return

    console.print(f"[bold]Downloading[/bold] (~{pres.approx_total_gb} GB total)…")
    rc = download_mod.download_preset(cfg, pres)
    if rc != 0:
        raise typer.Exit(code=rc)
    console.print("[green]Done.[/green]")


@app.command()
def version() -> None:
    """Print lucebox version."""
    print(__version__)


def main() -> None:
    """Module entrypoint — `python -m lucebox`."""
    try:
        app()
    except KeyboardInterrupt:
        console.print("\n[dim]interrupted[/dim]")
        sys.exit(130)


if __name__ == "__main__":
    main()
