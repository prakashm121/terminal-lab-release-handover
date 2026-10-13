#!/usr/bin/env python3
"""
scripts/verify_environment.py
Pre-flight verification script for Tech Lab 2 Codespace and local environments.
Verifies that all 7 required Unix tools and dependencies are installed and accessible.
"""

import sys
import shutil
import subprocess

GREEN = "\033[0;32m"
RED = "\033[0;31m"
BOLD = "\033[1m"
RESET = "\033[0m"

REQUIRED_TOOLS = [
    ("bash", "Shell environment"),
    ("nano", "Interactive editor"),
    ("less", "Log file pager"),
    ("sort", "Text and numerical sorter"),
    ("uniq", "Duplicate line filter"),
    ("cut", "Field extraction utility"),
    ("diff", "File comparison utility"),
]

def check_python():
    v = sys.version_info
    if v.major >= 3 and v.minor >= 8:
        print(f"  [{GREEN}OK{RESET}] python3 ({v.major}.{v.minor}.{v.micro})")
        return True
    print(f"  [{RED}FAIL{RESET}] python3: Version {v.major}.{v.minor} is below required 3.8+")
    return False

def check_tool(cmd, desc):
    path = shutil.which(cmd)
    if path:
        print(f"  [{GREEN}OK{RESET}] {cmd:<8} - {desc} ({path})")
        return True
    else:
        print(f"  [{RED}FAIL{RESET}] {cmd:<8} - {desc} (NOT FOUND in PATH)")
        return False

def main():
    print("==================================================================")
    print(f"{BOLD}  Tech Lab 2: Environment Pre-Flight Verification{RESET}")
    print("==================================================================")
    print("Verifying required tools for the 7 terminal experiments:")
    print("")

    all_ok = True
    if not check_python():
        all_ok = False

    for cmd, desc in REQUIRED_TOOLS:
        if not check_tool(cmd, desc):
            all_ok = False

    print("")
    print("==================================================================")
    if all_ok:
        print(f"{BOLD}{GREEN}  ENVIRONMENT READY: All tools installed and verified!{RESET}")
        print("  To begin your lab attempt, run:")
        print("    python lab/start.py   (or: bash lab/start.sh)")
        print("==================================================================")
        sys.exit(0)
    else:
        print(f"{BOLD}{RED}  ENVIRONMENT INCOMPLETE: Missing required tools.{RESET}")
        print("  If running in Docker/Codespaces, rebuild your container.")
        print("==================================================================")
        sys.exit(1)

if __name__ == "__main__":
    main()
