#!/usr/bin/env python3
"""
Helper script to fix the deliberate error in the validation demo.
"""
import os
import sys
from pathlib import Path
from collections import Counter

def main():
    script_dir = Path(__file__).resolve().parent
    tickets_file = script_dir / "checkout_tickets.txt"
    owners_file = script_dir / "owners_summary.txt"

    print("Applying fix: Sorting assignees before aggregating...")
    lines = tickets_file.read_text(encoding="utf-8").splitlines()
    assignees = [line.split("|")[3] for line in lines if len(line.split("|")) > 3]
    counts = Counter(sorted(assignees))
    owners_lines = [f"{count} {owner}" for owner, count in sorted(counts.items())]
    owners_file.write_text("\n".join(owners_lines) + "\n", encoding="utf-8")

    print("Fix applied! Now re-running checker:")
    check_py = script_dir.parent / "check.py"
    os.system(f'python3 "{check_py}" "{script_dir}"')

if __name__ == "__main__":
    main()
