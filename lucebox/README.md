# lucebox — host CLI for the lucebox-hub container

This package ships *inside* the `ghcr.io/luce-org/lucebox-hub` Docker image
and is invoked from the host via the [`lucebox.sh`](../lucebox.sh) wrapper:

    lucebox.sh check          # `docker run … lucebox check`
    lucebox.sh config get
    lucebox.sh print-run

The wrapper is the only thing that runs on the host; everything else (host
checks, TOML config, docker daemon calls, autotune + sweep, profile/smoke
diagnostics, model download) is Python in the container. Host facts (driver,
GPU, RAM, VRAM, systemd availability) are passed in via `LUCEBOX_HOST_*`
environment variables so the Python side doesn't reprobe. The agent-client
launchers land in a follow-up PR.

Subcommands are defined in [`lucebox/cli.py`](src/lucebox/cli.py). See the
top-level [README.md](../README.md) for the user-facing flow.
