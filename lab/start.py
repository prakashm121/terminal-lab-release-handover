#!/usr/bin/env python3
"""
Tech Lab 2: Start Script (start.py)
Initializes a fresh, isolated workspace under lab-work/attempt-N.
GUARANTEE: Never overwrites any existing attempt directory!
"""

import os
import sys
import shutil
from datetime import datetime, timezone
from pathlib import Path

def main():
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    lab_data_dir = repo_root / "lab" / "data"
    work_dir = repo_root / "lab-work"

    if not lab_data_dir.is_dir():
        print(f"ERROR: Fixture directory not found at {lab_data_dir}", file=sys.stderr)
        sys.exit(1)

    work_dir.mkdir(parents=True, exist_ok=True)

    # Find the next unused attempt number
    attempt_num = 1
    while (work_dir / f"attempt-{attempt_num}").exists():
        attempt_num += 1

    target_dir = work_dir / f"attempt-{attempt_num}"
    target_dir.mkdir(parents=True, exist_ok=True)

    # Copy initial fixture files into the attempt directory
    shutil.copy2(lab_data_dir / "build.log", target_dir / "build.log")
    shutil.copy2(lab_data_dir / "tickets.txt", target_dir / "tickets.txt")
    shutil.copy2(lab_data_dir / "config-v1.env", target_dir / "config-v1.env")
    shutil.copy2(lab_data_dir / "config-v2.env", target_dir / "config-v2.env")
    shutil.copy2(lab_data_dir / "handover.md.template", target_dir / "handover.md")
    shutil.copy2(lab_data_dir / "config-v2.env", target_dir / "config-fixed.env")

    # Create sandbox scratchpad
    sandbox_dir = target_dir / "sandbox"
    sandbox_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(lab_data_dir / "tickets.txt", sandbox_dir / "tickets_copy.txt")

    # Write attempt metadata
    meta_file = target_dir / ".attempt_meta"
    with open(meta_file, "w", encoding="utf-8") as f:
        f.write(f"ATTEMPT={attempt_num}\n")
        f.write(f"CREATED_AT={datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n")
        f.write(f"REPO_ROOT={repo_root}\n")

    print("==================================================================")
    print(f"  [SUCCESS] Initialized fresh lab workspace: attempt-{attempt_num}")
    print("==================================================================")
    print("")
    print(f"  Workspace path:")
    print(f"    {target_dir}")
    print("")
    print("  To begin working, run:")
    print(f"    cd lab-work/attempt-{attempt_num}")
    print("")
    print("  To test your progress at any time, run:")
    print("    python ../../lab/check.py   (or: ../../lab/check.sh)")
    print("")
    print(f"  Previous attempts are preserved intact in {work_dir}.")
    print("==================================================================")

if __name__ == "__main__":
    main()
