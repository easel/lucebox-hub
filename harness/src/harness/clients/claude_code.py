"""Launch Claude Code pointed at a Lucebox server.

The env contract is the same one ``harness/clients/run_claude_code.sh`` uses:

    ANTHROPIC_BASE_URL          → Lucebox /v1 base (Anthropic-Messages compat)
    ANTHROPIC_API_KEY           → any token; Lucebox doesn't gate
    CLAUDE_CODE_API_BASE_URL    → some Claude Code versions read this instead
    CLAUDE_CODE_DISABLE_*       → telemetry + nonessential traffic off
    CLAUDE_CODE_DISABLE_NONSTREAMING_FALLBACK → prevent the client from
                                  falling back to a non-streaming code path
                                  that older Lucebox builds don't speak

Two invocation modes:
  - **interactive** (default): exec claude with an empty argv, user gets the
    full TUI. The ``lucebox claude`` host subcommand calls this.
  - **print** (test mode): ``--print --output-format json`` for the harness
    ``run_claude_code.sh`` compatibility-check flow.

Stdlib only.
"""

from __future__ import annotations

import os

from harness.clients._common import (
    DEFAULT_API_KEY,
    build_base_parser,
    exec_client,
    find_bin,
    run_main,
)


def claude_env(
    base_url: str,
    *,
    api_key: str = DEFAULT_API_KEY,
    extra_env: dict[str, str] | None = None,
) -> dict[str, str]:
    """Compose the env dict that points Claude Code at a Lucebox server.

    Returns a fresh dict to merge over os.environ — callers control whether
    to inherit, sanitize, or replace the parent environment.
    """
    env: dict[str, str] = {
        "ANTHROPIC_API_KEY": api_key,
        "ANTHROPIC_BASE_URL": base_url.rstrip("/"),
        "CLAUDE_CODE_API_BASE_URL": base_url.rstrip("/"),
        # Older Claude Code versions occasionally retry a non-streaming
        # request when the streaming endpoint returns an unexpected shape.
        # That path isn't well-tested against Lucebox; force-disable so
        # any incompatibility surfaces in the streaming path where we test.
        "CLAUDE_CODE_DISABLE_NONSTREAMING_FALLBACK": "1",
        # Privacy/telemetry off — both for the test harness (deterministic
        # runs) and for user-facing `lucebox claude` (running a local model).
        "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
        "CLAUDE_CODE_DISABLE_TELEMETRY": "1",
    }
    if extra_env:
        env.update(extra_env)
    return env


def find_claude_bin() -> str:
    """Locate the `claude` binary via the shared resolver.

    Search order (from ``_common.find_bin``):
      1. $CLAUDE_BIN env var (explicit override)
      2. $PATH (typical dev install)
      3. Test-box convention: $CLIENT_WORK_DIR/clients/claude_code/npm/bin/claude

    Note: ``find_bin`` requires the resolved path to be an executable regular
    file (vs. the prior bare ``Path.exists()``), so a $CLAUDE_BIN pointing at
    a directory or non-executable now fails fast at resolution rather than
    at exec time.
    """
    return find_bin(
        "claude",
        env_var="CLAUDE_BIN",
        work_dir_hint="clients/claude_code/npm/bin/claude",
    )


def launch(
    *,
    base_url: str,
    model: str = "luce-dflash",
    api_key: str = DEFAULT_API_KEY,
    prompt: str | None = None,
    timeout: int | None = None,
    extra_args: list[str] | None = None,
    interactive: bool = True,
) -> int:
    """Run Claude Code against the given Lucebox server.

    Args:
        base_url: Lucebox HTTP base, e.g. ``http://localhost:8080``.
        model: Model ID to advertise to Claude Code.
        api_key: Bearer token for ANTHROPIC_API_KEY. Lucebox doesn't gate;
            any non-empty string works.
        prompt: For non-interactive use — pass a prompt to ``claude --print``.
            Ignored when ``interactive=True``.
        timeout: Wrap in ``timeout`` (seconds) for non-interactive runs.
            Ignored in interactive mode.
        extra_args: Extra argv to forward to claude.
        interactive: True → TUI mode (default). False → `--print` mode for
            the harness compat-check pattern.

    Returns:
        claude's exit code.
    """
    claude = find_claude_bin()
    env = {**os.environ, **claude_env(base_url, api_key=api_key)}
    argv: list[str] = [claude]

    if interactive:
        # Claude Code's TUI honors `--model` at startup; without it the
        # user gets whichever default model the CLI shipped with, even
        # though they passed --model on the host wrapper. Mirror the
        # non-interactive flag so the model selection is consistent
        # across both modes.
        argv += ["--model", model]
        if extra_args:
            argv += extra_args
        # Inherit stdin/out/err so the TUI works. No timeout in interactive mode.
        return exec_client(argv, env, interactive=True)

    # Non-interactive: matches `harness/clients/run_claude_code.sh` flags.
    if prompt is None:
        raise ValueError("non-interactive mode requires prompt=...")
    argv += [
        "--print",
        "--output-format", "json",
        "--model", model,
        "--permission-mode", "dontAsk",
        "--no-session-persistence",
    ]
    if extra_args:
        argv += extra_args
    argv += [prompt]

    return exec_client(argv, env, interactive=False, timeout=timeout)


def main() -> int:
    """`harness-claude-code` console script — small CLI for ad-hoc use.

    The full TUI flow goes through ``lucebox claude`` (interactive). The
    harness ``run_claude_code.sh`` calls in test (--print) mode. This main
    is a thin wrapper for either."""
    parser = build_base_parser("harness-claude-code")
    args, extra = parser.parse_known_args()

    return run_main(
        lambda: launch(
            base_url=args.base_url,
            model=args.model,
            api_key=args.api_key,
            prompt=args.prompt,
            timeout=args.timeout,
            extra_args=extra or None,
            interactive=args.prompt is None,
        ),
        prog="harness-claude-code",
    )


if __name__ == "__main__":
    raise SystemExit(main())
