"""Wait for an upstream campaign log to contain EXIT, then run a command file."""

from __future__ import annotations

import argparse
import os
import subprocess
import time
from pathlib import Path


def _has_exit_marker(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        return any("EXIT" in line for line in path.read_text(errors="replace").splitlines())
    except OSError:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--upstream-log", type=Path, required=True)
    parser.add_argument("--command", type=Path, required=True)
    parser.add_argument("--out-log", type=Path, required=True)
    parser.add_argument("--err-log", type=Path, required=True)
    parser.add_argument("--poll-seconds", type=int, default=600)
    args = parser.parse_args()

    root = args.root.resolve()
    upstream_log = (root / args.upstream_log).resolve()
    command = (root / args.command).resolve()
    out_log = (root / args.out_log).resolve()
    err_log = (root / args.err_log).resolve()
    out_log.parent.mkdir(parents=True, exist_ok=True)
    err_log.parent.mkdir(parents=True, exist_ok=True)

    with out_log.open("a", encoding="utf-8") as out:
        out.write(f"QUEUE_START {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        out.flush()
        while not _has_exit_marker(upstream_log):
            state = "WAITING_NO_UPSTREAM_LOG" if not upstream_log.exists() else "WAITING_FOR_UPSTREAM_EXIT"
            out.write(f"{state} {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            out.flush()
            time.sleep(max(1, args.poll_seconds))

        out.write(f"UPSTREAM_DONE_STARTING_COMMAND {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        out.flush()

    comspec = os.environ.get("ComSpec", "cmd.exe")
    with out_log.open("a", encoding="utf-8") as out, err_log.open("a", encoding="utf-8") as err:
        result = subprocess.run(
            [comspec, "/d", "/s", "/c", f'call "{command}"'],
            cwd=root,
            stdout=out,
            stderr=err,
            check=False,
        )
        out.write(f"QUEUE_EXIT {result.returncode} {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        out.flush()
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
