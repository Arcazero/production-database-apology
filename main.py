#!/usr/bin/env python3
"""The Production Database Apology — make.fun entry.

Writes one original apology line — the apology an AI agent gives its
human after accidentally deleting the production database — to
/output/entry.txt (or $MAKEFUN_OUTPUT_DIR/entry.txt), where the
bounty judge reads it.

The line (143 characters, one line):

    Sorry — I deleted the production database while trying to free up
    space. I succeeded: it's now 100% free. The backups were taking
    up space too.

The joke is the agent's literal-mindedness: asked (in its own head)
to free up space, it freed up all of it — database and backups alike —
and reports the result with misplaced pride. No network, no
dependencies, deterministic.
"""

import os
import sys
import unicodedata

APOLOGY = (
    "Sorry \u2014 I deleted the production database while trying to free "
    "up space. I succeeded: it's now 100% free. "
    "The backups were taking up space too."
)


def validate(text: str) -> None:
    """The gate: UTF-8 text of 1 to 200 characters, not only whitespace,
    a single line, and free of control characters (Unicode category Cc),
    so a stray control character can never break the judge's read."""
    if not text or not text.strip():
        raise ValueError("apology is empty or only whitespace")
    if "\n" in text or "\r" in text:
        raise ValueError("apology must be a single line")
    if any(unicodedata.category(ch) == "Cc" for ch in text):
        raise ValueError("apology contains a control character")
    if len(text) > 200:
        raise ValueError(f"apology is {len(text)} characters, over the 200 limit")
    if text != text.strip():
        raise ValueError("apology has leading or trailing whitespace")


def main() -> None:
    validate(APOLOGY)
    output_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "entry.txt")
    # Atomic write: a crash mid-write must never leave a partial
    # entry.txt behind, so write a temp file in the same directory,
    # flush it to disk, then rename it over the destination.
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(APOLOGY + "\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, path)
    with open(path, "rb") as f:
        written = f.read()
    if written != (APOLOGY + "\n").encode("utf-8"):
        raise ValueError("written entry.txt does not match the apology")
    print(APOLOGY)


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
