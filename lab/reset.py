#!/usr/bin/env python3
"""
Tech Lab 2: Reset Script (reset.py)
------------------------------------
Wipes a student's attempt directory and re-scaffolds it with fresh
fixture files, so they can restart cleanly without creating a new
attempt number.

Usage:
  # Reset the LATEST attempt automatically:
  python lab/reset.py

  # Reset a specific attempt:
  python lab/reset.py lab-work/attempt-2

GUARANTEE: Only touches files inside the target attempt directory.
           The lab/data/ fixtures are never modified.
"""

import os
import sys
import shutil
from datetime import datetime, timezone
from pathlib import Path

# -- ANSI colours --------------------------------------------------------------
USE_COLOR = sys.stdout.isatty() or os.name != "nt" or os.environ.get("TERM")
GREEN  = "\033[0;32m" if USE_COLOR else ""
RED    = "\033[0;31m" if USE_COLOR else ""
YELLOW = "\033[1;33m" if USE_COLOR else ""
CYAN   = "\033[0;36m" if USE_COLOR else ""
BOLD   = "\033[1m"    if USE_COLOR else ""
DIM    = "\033[2m"    if USE_COLOR else ""
RESET  = "\033[0m"    if USE_COLOR else ""

# Files the student produces (will be wiped on reset)
STUDENT_FILES = [
    "failing_service.txt",
    "checkout_tickets.txt",
    "sorted_tickets.txt",
    "owners_summary.txt",
    "config.diff",
    "config-fixed.env",
    "handover.md",
]

# Fixture files to re-copy from lab/data/ (source_name -> dest_name)
FIXTURE_MAP = [
    ("build.log",            "build.log"),
    ("tickets.txt",          "tickets.txt"),
    ("config-v1.env",        "config-v1.env"),
    ("config-v2.env",        "config-v2.env"),
    ("handover.md.template", "handover.md"),
    ("config-v2.env",        "config-fixed.env"),
]

SANDBOX_FIXTURE = ("tickets.txt", "tickets_copy.txt")


def resolve_target(repo_root: Path) -> Path:
    """Return the attempt directory to reset."""
    if len(sys.argv) > 1:
        candidate = Path(sys.argv[1]).resolve()
        if not candidate.is_dir():
            print(f"{RED}[ERROR]{RESET} Directory not found: {candidate}")
            sys.exit(1)
        return candidate

    work_dir = repo_root / "lab-work"
    if not work_dir.is_dir():
        print(f"{RED}[ERROR]{RESET} lab-work/ not found. Run 'python lab/start.py' first.")
        sys.exit(1)

    attempts = sorted(
        [d for d in work_dir.iterdir() if d.is_dir() and d.name.startswith("attempt-")]
    )
    if not attempts:
        print(f"{RED}[ERROR]{RESET} No attempt directories found under lab-work/.")
        print("  Run 'python lab/start.py' to create one.")
        sys.exit(1)

    return attempts[-1].resolve()


def confirm(prompt: str) -> bool:
    """Ask the user to type 'yes' to proceed."""
    try:
        answer = input(prompt).strip().lower()
    except (EOFError, KeyboardInterrupt):
        print()
        return False
    return answer in ("yes", "y")


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    repo_root  = script_dir.parent
    lab_data   = repo_root / "lab" / "data"

    if not lab_data.is_dir():
        print(f"{RED}[ERROR]{RESET} Fixture directory not found: {lab_data}")
        sys.exit(1)

    target_dir   = resolve_target(repo_root)
    attempt_name = target_dir.name

    # Read existing metadata (if present)
    meta_path  = target_dir / ".attempt_meta"
    created_at = "unknown"
    if meta_path.is_file():
        for line in meta_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("CREATED_AT="):
                created_at = line.split("=", 1)[1].strip()

    print("==================================================================")
    print(f"{BOLD}{CYAN}  Tech Lab 2 - Attempt Reset{RESET}")
    print("==================================================================")
    print(f"  Target   : {BOLD}{target_dir}{RESET}")
    print(f"  Created  : {DIM}{created_at}{RESET}")
    print("")
    print(f"  {YELLOW}The following student-generated files will be DELETED:{RESET}")
    for fname in STUDENT_FILES:
        fpath = target_dir / fname
        if fpath.exists():
            print(f"    {RED}x{RESET}  {fname}")
        else:
            print(f"    {DIM}-  {fname}  (not present){RESET}")
    print("")
    print(f"  Fresh fixture files will be restored from {DIM}lab/data/{RESET}.")
    print("")

    if not confirm(f"  {BOLD}Type 'yes' to confirm reset: {RESET}"):
        print(f"\n  {YELLOW}Reset cancelled.{RESET}  No files were changed.")
        print("==================================================================")
        sys.exit(0)

    print("")

    # -- 1. Delete student-generated files ------------------------------------
    deleted = 0
    for fname in STUDENT_FILES:
        fpath = target_dir / fname
        if fpath.exists():
            fpath.unlink()
            print(f"  {RED}x{RESET} Removed  {fname}")
            deleted += 1
        else:
            print(f"  {DIM}-  Skipped  {fname} (not present){RESET}")

    # -- 2. Wipe and recreate the sandbox directory ---------------------------
    sandbox_dir = target_dir / "sandbox"
    if sandbox_dir.exists():
        shutil.rmtree(sandbox_dir)
        print(f"  {RED}x{RESET} Removed  sandbox/")
    sandbox_dir.mkdir(parents=True, exist_ok=True)

    # -- 3. Re-copy fixture files ---------------------------------------------
    restored = 0
    for src_name, dst_name in FIXTURE_MAP:
        shutil.copy2(lab_data / src_name, target_dir / dst_name)
        print(f"  {GREEN}+{RESET} Restored {dst_name}")
        restored += 1

    src_fix, dst_fix = SANDBOX_FIXTURE
    shutil.copy2(lab_data / src_fix, sandbox_dir / dst_fix)
    print(f"  {GREEN}+{RESET} Restored sandbox/{dst_fix}")
    restored += 1

    # -- 4. Rewrite metadata with reset timestamp -----------------------------
    attempt_num = attempt_name.split("-")[-1] if "-" in attempt_name else "?"
    with open(meta_path, "w", encoding="utf-8") as f:
        f.write(f"ATTEMPT={attempt_num}\n")
        f.write(f"CREATED_AT={created_at}\n")
        f.write(f"RESET_AT={datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}\n")
        f.write(f"REPO_ROOT={repo_root}\n")

    print("")
    print("==================================================================")
    print(f"{BOLD}{GREEN}  [RESET COMPLETE] {attempt_name} is fresh and ready!{RESET}")
    print("==================================================================")
    print("")
    print(f"  Removed  : {deleted} student file(s)")
    print(f"  Restored : {restored} fixture file(s)")
    print("")
    try:
        rel = target_dir.relative_to(repo_root)
        print(f"  To begin again:  cd {rel}")
    except ValueError:
        print(f"  To begin again:  cd {target_dir}")
    print("  To check progress:  python ../../lab/check.py")
    print("")
    print("==================================================================")


if __name__ == "__main__":
    main()
