"""Client launchers — start a Lucebox server, point a real client at it.

Each module here exposes a `launch()` function that handles the
client-specific env config + binary exec, alongside the shell wrappers
under ``harness/clients/run_*.sh`` that handle the server lifecycle.

The split: shell wrappers own the server start/stop + log-dir setup;
these Python modules own the client-side env + argv. ``lucebox <client>``
subcommands (e.g. ``lucebox claude``) call these directly.
"""

# Re-export submodules so callers (and mypy) can resolve
# ``from harness.clients import claude_code`` without the submodule
# needing to be force-loaded by an earlier import.
from . import claude_code, codex, hermes, openclaw, opencode, pi

__all__ = ["claude_code", "codex", "hermes", "openclaw", "opencode", "pi"]
