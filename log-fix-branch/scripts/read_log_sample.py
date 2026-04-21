#!/usr/bin/env python3
"""
Read a compact sample from a local or SSH-reachable log source.

Accepted source formats:
  - /path/to/file.log
  - /path/to/log/dir
  - user@host:/path/to/file.log
  - ssh://user@host/path/to/file.log
"""

from __future__ import annotations

import argparse
import gzip
import re
import shlex
import subprocess
import sys
from collections import deque
from pathlib import Path
from typing import Iterable
from urllib.parse import urlparse


REMOTE_RE = re.compile(r"^(?P<host>[^:@/\s]+@[^:/\s]+):(?P<path>.+)$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="Local path or remote source")
    parser.add_argument("--lines", type=int, default=200, help="Number of lines to print")
    parser.add_argument(
        "--grep",
        help="Regex used to filter matching lines after sampling",
    )
    return parser.parse_args()


def classify_source(source: str) -> tuple[str, str, str | None]:
    if source.startswith("ssh://"):
        parsed = urlparse(source)
        host = parsed.netloc
        path = parsed.path
        if not host or not path:
            raise ValueError(f"Invalid SSH source: {source}")
        return "remote", path, host

    match = REMOTE_RE.match(source)
    if match:
        return "remote", match.group("path"), match.group("host")

    return "local", source, None


def tail_lines(lines: Iterable[str], count: int) -> list[str]:
    return list(deque(lines, maxlen=count))


def filter_lines(lines: list[str], pattern: str | None) -> list[str]:
    if not pattern:
        return lines

    regex = re.compile(pattern)
    matched = [line for line in lines if regex.search(line)]
    return matched or lines


def read_text_lines(path: Path) -> list[str]:
    opener = gzip.open if path.suffix == ".gz" else open
    mode = "rt"
    with opener(path, mode, encoding="utf-8", errors="replace") as handle:
        return list(handle)


def candidate_files(directory: Path) -> list[Path]:
    files = [
        path
        for path in directory.rglob("*")
        if path.is_file() and re.search(r"\.(log(\.\d+)?(\.gz)?|out|txt)$", path.name)
    ]
    if not files:
        files = [path for path in directory.rglob("*") if path.is_file()]
    files.sort(key=lambda item: item.stat().st_mtime, reverse=True)
    return files[:3]


def read_local(path_str: str, line_count: int, pattern: str | None) -> list[str]:
    path = Path(path_str).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Local path not found: {path}")

    if path.is_file():
        lines = tail_lines(read_text_lines(path), line_count)
        return filter_lines(lines, pattern)

    parts: list[str] = []
    per_file = max(20, line_count // 3)
    for file_path in candidate_files(path):
        lines = tail_lines(read_text_lines(file_path), per_file)
        lines = filter_lines(lines, pattern)
        if not lines:
            continue
        parts.append(f"===== {file_path} =====\n")
        parts.extend(lines)

    if not parts:
        raise FileNotFoundError(f"No readable log files found in directory: {path}")
    return tail_lines(parts, line_count + 20)


def build_remote_command(path: str, line_count: int, pattern: str | None) -> str:
    quoted_path = shlex.quote(path)
    quoted_lines = shlex.quote(str(line_count))
    filter_cmd = "tail -n \"$n\""
    if pattern:
        filter_cmd += f" | grep -E {shlex.quote(pattern)} || true"

    return f"""
set -e
p={quoted_path}
n={quoted_lines}
if [ -f "$p" ]; then
  case "$p" in
    *.gz) gzip -cd -- "$p" 2>/dev/null || zcat -- "$p" ;;
    *) cat -- "$p" ;;
  esac | {filter_cmd}
elif [ -d "$p" ]; then
  find "$p" -type f -print0 2>/dev/null | xargs -0 ls -1t 2>/dev/null | head -n 3 | while IFS= read -r f; do
    printf '===== %s =====\\n' "$f"
    case "$f" in
      *.gz) gzip -cd -- "$f" 2>/dev/null || zcat -- "$f" ;;
      *) cat -- "$f" ;;
    esac | {filter_cmd}
  done
else
  echo "Path not found: $p" >&2
  exit 2
fi
""".strip()


def read_remote(host: str, path: str, line_count: int, pattern: str | None) -> list[str]:
    command = build_remote_command(path, line_count, pattern)
    result = subprocess.run(
        ["ssh", host, command],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"ssh failed with code {result.returncode}")
    return result.stdout.splitlines(keepends=True)


def main() -> int:
    args = parse_args()
    try:
        source_type, path, host = classify_source(args.source)
        if source_type == "local":
            lines = read_local(path, args.lines, args.grep)
        else:
            assert host is not None
            lines = read_remote(host, path, args.lines, args.grep)
    except Exception as exc:  # noqa: BLE001
        print(str(exc), file=sys.stderr)
        return 1

    if not lines:
        print("No log lines found", file=sys.stderr)
        return 1

    sys.stdout.writelines(lines)
    if lines and not lines[-1].endswith("\n"):
        print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
