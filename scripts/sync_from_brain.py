#!/usr/bin/env python3
"""Rewrite the Brain-owned sections of README.md from a checkout of the Brain.

The README is public and the Brain is private, so two whitelists sit between
them:

* SOURCES names every Brain file this script may open and the README section
  each one feeds. No other file in the Brain is read.
* Inside a whitelisted file, only the text between
  ``<!-- public-readme:<id>:start -->`` and ``<!-- public-readme:<id>:end -->``
  is used. Everything else in that file stays where it is.

In README.md each section sits between ``<!-- brain:<id>:start -->`` and
``<!-- brain:<id>:end -->``. Only those spans are rewritten; every other byte of
the file is left untouched.

Before anything is written, each block goes through the style rules (every em
dash, en dash and minus sign becomes a plain hyphen; invisible characters and
trailing spaces go) and a privacy check (no HTML comments, local paths, email
addresses, credentials, long digit runs, phone numbers, "do not publish" notes,
or links that are not public https). A failed check stops the run and names the
section, line and rule, never the text. Nothing this script prints comes from a
Brain file.

Usage:
    sync_from_brain.py BRAIN_DIR [--readme PATH] [--check] [--today YYYY-MM-DD]
    sync_from_brain.py --list-sources

Exit status: 0 when the README is in sync or was updated, 1 when --check finds
it out of date, 2 on any error (missing block or marker, failed check, bad path).
Standard library only.
"""

from __future__ import annotations

import argparse
import datetime as dt
import ipaddress
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_README = REPO_ROOT / "README.md"

# README section id -> the only Brain file, relative to the Brain root, that
# holds its public block. Listed in README order.
SOURCES: dict[str, str] = {
    "role": "cv/profile.md",
    "projects": "sources/github-public-repos.md",
    "education": "cv/profile.md",
    "community": "cv/cv-facts.md",
    "talks": "publications/speaking-and-events.md",
}

README_MARKER = re.compile(r"<!-- brain:([a-z0-9-]+):(start|end) -->")
BRAIN_MARKER = re.compile(r"<!-- public-readme:([a-z0-9-]+):(start|end) -->")

MAX_SOURCE_BYTES = 512 * 1024
MAX_BLOCK_CHARS = 12_000
MAX_BLOCK_LINES = 80

# Style: the profile uses plain hyphens only.
DASHES = "\u2010\u2011\u2012\u2013\u2014\u2015\u2212"
INVISIBLE = {
    "\u00a0": " ",  # no-break space
    "\u200b": "",  # zero-width space
    "\u200c": "",  # zero-width non-joiner
    "\u200d": "",  # zero-width joiner
    "\u2060": "",  # word joiner
    "\ufeff": "",  # byte-order mark
}
STYLE_TABLE = str.maketrans({**{c: "-" for c in DASHES}, **INVISIBLE})

# Privacy: any hit stops the run.
URL = re.compile(r"\b[a-zA-Z][a-zA-Z0-9+.-]*://[^\s<>()\[\]\"'`]+")
LINK_TARGET = re.compile(r"\]\(\s*<?([^)\s>]+)|\b(?:href|src)\s*=\s*[\"']([^\"']*)[\"']", re.I)
PRIVATE_SUFFIXES = (".local", ".lan", ".home", ".internal", ".intranet", ".corp", ".home.arpa", ".ts.net")
TEXT_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("html-comment", re.compile(r"<!--|-->")),
    ("local-path", re.compile(r"(?<![\w.-])(?:/home/|/Users/|/root/|/private/|/var/folders/|/mnt/|/media/|~/)|\b[A-Za-z]:\\")),
    ("email-address", re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")),
    (
        "credential",
        re.compile(
            r"gh[pousr]_[A-Za-z0-9]{20,}|github_pat_\w{20,}|\bA[KS]IA[0-9A-Z]{16}\b"
            r"|-----BEGIN [A-Z ]*PRIVATE KEY|\bxox[abposr]-[A-Za-z0-9-]{10,}"
            r"|\bsk-[A-Za-z0-9_-]{20,}|\bAIza[0-9A-Za-z_-]{35}\b|\beyJ[\w-]{10,}\.[\w-]{10,}\."
            r"|(?i:\b(?:password|passwd|api[_-]?key|secret|token)\s*[:=])"
        ),
    ),
    (
        "not-for-publication",
        re.compile(
            r"(?i)\b(?:do not publish|not for publication|no publicar|no se publica"
            r"|confidential|confidencial|internal only|uso interno)\b"
        ),
    ),
]
# Checked on the text with every URL removed, so URL ids do not trip them.
NUMBER_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("long-number", re.compile(r"\d{8,}")),
    ("phone-number", re.compile(r"\+\d{1,3}[\s().-]*\d(?:[\s().-]*\d){6,}")),
]

MONTHS = {m: i for i, m in enumerate(("jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"), 1)}
TALK_DATE = re.compile(
    r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(\d{1,2})(?:\s*-\s*(\d{1,2}))?,\s*(\d{4})"
)


class SyncError(Exception):
    """A problem that stops the sync. Messages never quote Brain content."""


def find_blocks(text: str, marker: re.Pattern[str], where: str) -> dict[str, tuple[int, int]]:
    """Map each block id to the line indexes of its start and end markers."""
    spans: dict[str, tuple[int, int]] = {}
    open_id: str | None = None
    open_at = 0
    for index, line in enumerate(text.split("\n")):
        match = marker.fullmatch(line.strip())
        if not match:
            continue
        block_id, kind = match.groups()
        if kind == "start":
            if open_id is not None:
                raise SyncError(f"{where}: block '{block_id}' starts inside block '{open_id}'")
            if block_id in spans:
                raise SyncError(f"{where}: block '{block_id}' appears more than once")
            open_id, open_at = block_id, index
        else:
            if open_id != block_id:
                raise SyncError(f"{where}: block '{block_id}' ends without a matching start")
            spans[block_id] = (open_at, index)
            open_id = None
    if open_id is not None:
        raise SyncError(f"{where}: block '{open_id}' is never closed")
    return spans


def read_source(root: Path, rel: str) -> str:
    """Read one whitelisted Brain file. The only place the Brain is opened."""
    if Path(rel).is_absolute() or ".." in Path(rel).parts:
        raise SyncError(f"{rel}: whitelist entries must be plain relative paths")
    path = root / rel
    if not path.exists():
        raise SyncError(f"{rel}: not found in the Brain checkout")
    if path.is_symlink() or path.resolve() != path:
        raise SyncError(f"{rel}: reached through a symlink; refusing to follow it")
    if not path.is_file():
        raise SyncError(f"{rel}: not a regular file")
    data = path.read_bytes()
    if len(data) > MAX_SOURCE_BYTES:
        raise SyncError(f"{rel}: larger than {MAX_SOURCE_BYTES} bytes")
    try:
        return data.decode("utf-8").replace("\r\n", "\n")
    except UnicodeDecodeError:
        raise SyncError(f"{rel}: not valid UTF-8") from None


def apply_style(text: str) -> str:
    """Normalize a block: plain hyphens, no invisible characters, no trailing spaces."""
    lines = [line.rstrip() for line in text.translate(STYLE_TABLE).split("\n")]
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


def style_violations(text: str) -> list[str]:
    """Characters the style rules forbid, as code points (never the text)."""
    return sorted({f"U+{ord(c):04X}" for c in text if c in DASHES or c in INVISIBLE})


def _link_problem(target: str) -> str | None:
    if target.startswith("#"):
        return None
    parts = urlsplit(target)
    if parts.scheme.lower() != "https":
        return "non-https-link"
    host = (parts.hostname or "").lower()
    if parts.username or parts.password:
        return "credential"
    if not host or "." not in host or host == "localhost" or host.endswith(PRIVATE_SUFFIXES):
        return "private-host"
    try:
        ipaddress.ip_address(host)
    except ValueError:
        return None
    return "private-host"


def privacy_violations(text: str) -> list[tuple[int, str]]:
    """(line number within the block, rule) for every privacy hit."""
    hits: set[tuple[int, str]] = set()
    for number, line in enumerate(text.split("\n"), 1):
        for rule, pattern in TEXT_RULES:
            if pattern.search(line):
                hits.add((number, rule))
        for url in URL.findall(line):
            problem = _link_problem(url.rstrip(".,;:!?*_"))
            if problem:
                hits.add((number, problem))
        for match in LINK_TARGET.finditer(line):
            problem = _link_problem(match.group(1) or match.group(2) or "")
            if problem:
                hits.add((number, problem))
        without_urls = URL.sub(" ", line)
        for rule, pattern in NUMBER_RULES:
            if pattern.search(without_urls):
                hits.add((number, rule))
    return sorted(hits)


def enforce(section: str, raw: str) -> str:
    """Apply the style rules, then refuse anything that fails the privacy check."""
    text = apply_style(raw)
    if not text:
        raise SyncError(f"section '{section}': the Brain block is empty")
    if len(text) > MAX_BLOCK_CHARS or text.count("\n") + 1 > MAX_BLOCK_LINES:
        raise SyncError(f"section '{section}': the Brain block is larger than the limit")
    leftover = style_violations(text)
    if leftover:
        raise SyncError(f"section '{section}': forbidden characters remain: {', '.join(leftover)}")
    problems = privacy_violations(text)
    if problems:
        detail = "; ".join(f"line {line}: {rule}" for line, rule in problems)
        raise SyncError(f"section '{section}': privacy check failed ({detail})")
    return text


def load_blocks(brain_root: Path) -> tuple[dict[str, str], list[str]]:
    """Read the public block of every section from its whitelisted file."""
    try:
        root = brain_root.resolve(strict=True)
    except (FileNotFoundError, RuntimeError):
        raise SyncError("the Brain directory does not exist") from None
    if not root.is_dir():
        raise SyncError("the Brain path is not a directory")

    wanted: dict[str, list[str]] = {}
    for section, rel in SOURCES.items():
        wanted.setdefault(rel, []).append(section)

    blocks: dict[str, str] = {}
    warnings: list[str] = []
    for rel, sections in wanted.items():
        text = read_source(root, rel)
        spans = find_blocks(text, BRAIN_MARKER, rel)
        lines = text.split("\n")
        for section in sections:
            if section not in spans:
                raise SyncError(f"{rel}: no public-readme block for section '{section}'")
            start, end = spans[section]
            blocks[section] = enforce(section, "\n".join(lines[start + 1 : end]))
        for extra in sorted(set(spans) - set(sections)):
            warnings.append(f"{rel}: public-readme block '{extra}' is not mapped to a README section and was ignored")
    return {section: blocks[section] for section in SOURCES}, warnings


def render(readme: str, blocks: dict[str, str]) -> tuple[str, list[str]]:
    """Replace the text between each pair of README markers; return (text, changed sections)."""
    spans = find_blocks(readme, README_MARKER, "README.md")
    unknown = sorted(set(spans) - set(SOURCES))
    if unknown:
        raise SyncError(f"README.md: markers for unknown sections: {', '.join(unknown)}")
    missing = [section for section in SOURCES if section not in spans]
    if missing:
        raise SyncError(f"README.md: no markers for sections: {', '.join(missing)}")

    lines = readme.split("\n")
    out: list[str] = []
    changed: list[str] = []
    position = 0
    for section, (start, end) in sorted(spans.items(), key=lambda item: item[1][0]):
        new = blocks[section].split("\n")
        if lines[start + 1 : end] != new:
            changed.append(section)
        out.extend(lines[position : start + 1])
        out.extend(new)
        position = end
    out.extend(lines[position:])
    return "\n".join(out), [section for section in SOURCES if section in changed]


def stale_upcoming(talks: str, today: dt.date) -> list[str]:
    """Warn about talks still listed under "Upcoming" whose last day has passed."""
    warnings: list[str] = []
    in_upcoming = False
    item = 0
    for line in talks.split("\n"):
        if line.startswith("#"):
            in_upcoming = line.lstrip("#").strip().lower().startswith("upcoming")
            continue
        if not (in_upcoming and line.startswith("- ")):
            continue
        item += 1
        match = TALK_DATE.search(line)
        if not match:
            continue
        month, first, last, year = match.groups()
        try:
            ends = dt.date(int(year), MONTHS[month.lower()], int(last or first))
        except ValueError:
            continue
        if ends < today:
            warnings.append(
                f"talks: upcoming item {item} ended on {ends.isoformat()}; move it to the past list in the Brain"
            )
    return warnings


def _emit_warning(message: str) -> None:
    prefix = "::warning title=Brain sync::" if os.environ.get("GITHUB_ACTIONS") == "true" else "warning: "
    print(prefix + message, file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Sync the Brain-owned sections of README.md.")
    parser.add_argument("brain_dir", nargs="?", type=Path, help="path to a checkout of the Brain")
    parser.add_argument("--readme", type=Path, default=DEFAULT_README, help="README to update (default: the repo README)")
    parser.add_argument("--check", action="store_true", help="exit 1 if the README would change; write nothing")
    parser.add_argument("--today", type=dt.date.fromisoformat, help="date for the stale-talk warning (default: today)")
    parser.add_argument("--list-sources", action="store_true", help="print the whitelisted Brain files and exit")
    args = parser.parse_args(argv)

    if args.list_sources:
        for rel in sorted(set(SOURCES.values())):
            print(rel)
        return 0
    if args.brain_dir is None:
        parser.error("BRAIN_DIR is required")

    try:
        blocks, warnings = load_blocks(args.brain_dir)
        try:
            current = args.readme.read_bytes().decode("utf-8")
        except FileNotFoundError:
            raise SyncError(f"{args.readme}: not found") from None
        except UnicodeDecodeError:
            raise SyncError(f"{args.readme}: not valid UTF-8") from None
        updated, changed = render(current, blocks)
    except SyncError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2

    if "talks" in blocks:
        warnings += stale_upcoming(blocks["talks"], args.today or dt.date.today())
    for message in warnings:
        _emit_warning(message)

    verb = "would update" if args.check else "updated"
    for section in SOURCES:
        print(f"{section}: {verb if section in changed else 'in sync'} ({SOURCES[section]})")
    if not changed:
        print("README.md is in sync with the Brain.")
        return 0
    if args.check:
        print("README.md is out of date; run without --check to update it.", file=sys.stderr)
        return 1
    args.readme.write_bytes(updated.encode("utf-8"))
    print(f"README.md updated: {', '.join(changed)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
