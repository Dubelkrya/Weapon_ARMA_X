"""Fetch the official vanilla Enforce-script snapshot without Workbench.

Arma Reforger publishes script sources in BohemiaInteractive/Arma-Reforger-Script-Diff.
For the currently validated game build we pin the exact official commit instead
of scraping mounted ``.c`` files through a Workbench plugin.

The checkout is raw external evidence and belongs under ``Imported`` (gitignored).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
from typing import Optional, Sequence


OFFICIAL_REPOSITORY = "https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff.git"
PINNED_GAME_VERSION = "1.8.0.13"
PINNED_COMMIT = "3d77cc212d5cda9922daf5f45635c7300d2d4cce"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
DEFAULT_DESTINATION = os.path.join(DEFAULT_REPO_ROOT, "Imported", "OfficialScriptDiff")


def _run(args, cwd=None) -> str:
    completed = subprocess.run(
        args,
        cwd=cwd,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


def _git(destination: str, *args: str) -> str:
    return _run(["git", "-C", destination, *args])


def _write_marker(destination: str) -> None:
    marker = {
        "source": "official_bohemia_script_diff",
        "repository": OFFICIAL_REPOSITORY,
        "game_version": PINNED_GAME_VERSION,
        "commit": PINNED_COMMIT,
    }
    with open(os.path.join(destination, "_wax_source.json"), "w", encoding="utf-8") as handle:
        json.dump(marker, handle, indent=2)
        handle.write("\n")


def ensure_checkout(destination: str = DEFAULT_DESTINATION) -> dict:
    destination = os.path.abspath(destination)
    git_dir = os.path.join(destination, ".git")

    if os.path.isdir(git_dir):
        dirty = _git(destination, "status", "--porcelain")
        # Ignore our own provenance marker if it is the only untracked file.
        dirty_rows = [
            row for row in dirty.splitlines()
            if row.strip() and not row.endswith("_wax_source.json")
        ]
        if dirty_rows:
            raise RuntimeError(
                "official script checkout has local changes; refusing to overwrite: "
                + "; ".join(dirty_rows[:8])
            )
        origin = _git(destination, "remote", "get-url", "origin")
        if origin.rstrip("/") != OFFICIAL_REPOSITORY.rstrip("/"):
            raise RuntimeError(
                f"unexpected origin for official script checkout: {origin}"
            )
    else:
        if os.path.exists(destination) and os.listdir(destination):
            raise RuntimeError(
                f"destination exists and is not an empty git checkout: {destination}"
            )
        os.makedirs(destination, exist_ok=True)
        _run(["git", "init", destination])
        _git(destination, "remote", "add", "origin", OFFICIAL_REPOSITORY)

    try:
        head = _git(destination, "rev-parse", "HEAD")
    except subprocess.CalledProcessError:
        head = ""

    if head != PINNED_COMMIT:
        _git(destination, "fetch", "--depth=1", "origin", PINNED_COMMIT)
        _git(destination, "checkout", "--detach", "FETCH_HEAD")
        head = _git(destination, "rev-parse", "HEAD")

    if head != PINNED_COMMIT:
        raise RuntimeError(
            f"official script checkout resolved to {head}, expected {PINNED_COMMIT}"
        )

    _write_marker(destination)
    return {
        "status": "ok",
        "destination": destination,
        "repository": OFFICIAL_REPOSITORY,
        "game_version": PINNED_GAME_VERSION,
        "commit": head,
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Fetch pinned official Arma Reforger script sources"
    )
    parser.add_argument("--destination", default=DEFAULT_DESTINATION)
    args = parser.parse_args(argv)
    result = ensure_checkout(args.destination)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
