#!/usr/bin/env python3
"""Repo-specific prose checks for docs/blogs.

This is intentionally narrower than a general prose linter. It catches the
failure modes that have already shown up in the lucebox blog drafts:

* prose em dashes
* recurring "AI slop" vocabulary and writer tics
* oversized Related sections

Vale can be run through --with-vale for style diagnostics, but these checks are
local policy. They should be deterministic, reviewable, and cheap enough to run
before every blog edit lands.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BLOG_DIR = ROOT / "docs" / "blogs"
BLOG_GLOB = "docs/blogs/*.md"
EXCLUDED = {"CLAUDE.md", ".gitignore"}


@dataclass(frozen=True)
class Finding:
    path: Path
    line: int
    rule: str
    severity: str
    message: str
    suggestion: str


@dataclass(frozen=True)
class Rule:
    rule_id: str
    severity: str
    pattern: re.Pattern[str]
    message: str
    suggestion: str


RULES = [
    Rule(
        "blog.em_dash",
        "error",
        re.compile("—"),
        "Avoid em dashes in prose.",
        "Use a comma, colon, parentheses, or a shorter sentence.",
    ),
    Rule(
        "blog.ai_tic.honest",
        "error",
        re.compile(r"\bhonest(?:ly)?\b|\bto be honest\b", re.IGNORECASE),
        "Avoid the honest/honestly tic.",
        "State the caveat directly.",
    ),
    Rule(
        "blog.ai_tic.interesting",
        "warning",
        re.compile(r"\binteresting(?:ly)?\b|\bwhat stands out\b", re.IGNORECASE),
        "Avoid reader-steering significance labels.",
        "Make the fact itself carry the significance.",
    ),
    Rule(
        "blog.ai_tic.worth",
        "warning",
        re.compile(
            r"\b(?:it is|it's|that is|that's)\s+worth\b"
            r"|\bworth\s+(?:noting|saying|flagging|holding|remembering|reading|checking|exploring)\b",
            re.IGNORECASE,
        ),
        "Avoid vague 'worth' endorsement language.",
        "Say why the detail matters.",
    ),
    Rule(
        "blog.ai_tic.empty_intensifier",
        "warning",
        re.compile(
            r"\b(?:real|actual|genuine|true)\s+"
            r"(?:accuracy|answer|benchmark|claim|compute|config|default|dial|engine|gain|"
            r"knob|mode|number|problem|quality|reason|result|score|speed|story|takeaway|"
            r"toggle|version)\b",
            re.IGNORECASE,
        ),
        "Avoid real/actual/genuine/true as abstract intensifiers.",
        "Name the contrast explicitly, or cut the intensifier.",
    ),
    Rule(
        "blog.ai_slop.generic_vocab",
        "error",
        re.compile(
            r"\b(?:delve|leverage|seamless|robust|pivotal|underscores|landscape|realm|"
            r"utilize|game[- ]changer|at its core|in conclusion|in summary|to summarize)\b",
            re.IGNORECASE,
        ),
        "Avoid generic AI-writing vocabulary.",
        "Replace it with the concrete mechanism, result, or constraint.",
    ),
]


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def markdown_files(paths: list[str], changed: bool) -> list[Path]:
    if paths:
        candidates = [Path(p) for p in paths]
    elif changed:
        candidates = changed_files()
    else:
        candidates = sorted(BLOG_DIR.glob("*.md"))

    files: list[Path] = []
    for candidate in candidates:
        path = candidate if candidate.is_absolute() else ROOT / candidate
        if path.is_dir():
            files.extend(sorted(path.glob("*.md")))
        elif path.match(BLOG_GLOB) or str(path).endswith(".md"):
            files.append(path)

    unique: dict[Path, None] = {}
    for path in files:
        if path.name in EXCLUDED:
            continue
        if BLOG_DIR not in path.parents:
            continue
        unique[path] = None
    return sorted(unique)


def changed_files() -> list[Path]:
    base = os.environ.get("DIFF_BASE")
    if base:
        args = ["git", "diff", "--name-only", "--diff-filter=ACMRTUXB", base, "--", "docs/blogs"]
    else:
        args = ["git", "diff", "--name-only", "--diff-filter=ACMRTUXB", "--", "docs/blogs"]
    proc = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        print(proc.stderr.strip(), file=sys.stderr)
        return []
    return [ROOT / line for line in proc.stdout.splitlines() if line.endswith(".md")]


def strip_noise(line: str) -> str:
    line = re.sub(r"`[^`]*`", "", line)
    line = re.sub(r"\]\(<[^>]+>\)", "](LINK)", line)
    line = re.sub(r"\]\([^)]+\)", "](LINK)", line)
    return line


def has_waiver(line: str, rule_id: str) -> bool:
    marker = "blog-prose: allow"
    if marker not in line:
        return False
    return rule_id in line or "all" in line


def scan_file(path: Path) -> list[Finding]:
    findings: list[Finding] = []
    in_fence = False
    related_count = 0
    in_related = False

    for n, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = raw_line.strip()
        if stripped.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue

        if stripped == "**Related**":
            in_related = True
            related_count = 0
            continue
        if in_related:
            if stripped.startswith("- "):
                related_count += 1
            elif stripped:
                if related_count > 5:
                    findings.append(
                        Finding(
                            path,
                            n - 1,
                            "blog.related.too_many",
                            "error",
                            f"Related section has {related_count} links; cap it at 5.",
                            "Keep only the closest methodology and sibling-result links.",
                        )
                    )
                in_related = False

        line = strip_noise(raw_line)
        for rule in RULES:
            if has_waiver(raw_line, rule.rule_id):
                continue
            if rule.pattern.search(line):
                findings.append(
                    Finding(path, n, rule.rule_id, rule.severity, rule.message, rule.suggestion)
                )

    if in_related and related_count > 5:
        findings.append(
            Finding(
                path,
                len(path.read_text(encoding="utf-8").splitlines()),
                "blog.related.too_many",
                "error",
                f"Related section has {related_count} links; cap it at 5.",
                "Keep only the closest methodology and sibling-result links.",
            )
        )

    return findings


def run_vale(paths: list[Path]) -> int:
    vale = shutil.which("vale")
    if not vale or not paths:
        if not vale:
            print("warning: vale is not on PATH; skipped Vale style checks", file=sys.stderr)
        return 0
    args = [vale, *[rel(p) for p in paths]]
    proc = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, check=False)
    if proc.stdout:
        print(proc.stdout.rstrip())
    if proc.stderr:
        print(proc.stderr.rstrip(), file=sys.stderr)
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Check lucebox blog prose policy.")
    parser.add_argument("paths", nargs="*", help="Markdown files or directories to scan.")
    parser.add_argument("--changed", action="store_true", help="Scan changed docs/blogs Markdown files.")
    parser.add_argument("--with-vale", action="store_true", help="Also run Vale with .vale.ini.")
    parser.add_argument(
        "--advisory",
        action="store_true",
        help="Print findings but exit 0. Useful while ratcheting the corpus down.",
    )
    args = parser.parse_args()

    files = markdown_files(args.paths, args.changed)
    vale_status = run_vale(files) if args.with_vale else 0

    findings: list[Finding] = []
    for path in files:
        findings.extend(scan_file(path))

    for item in findings:
        print(f"{rel(item.path)}:{item.line} [{item.severity}] {item.rule}")
        print(f"  rationale: {item.message}")
        print(f"  suggested edit: {item.suggestion}")

    if args.advisory:
        return 0
    if vale_status != 0 or findings:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
