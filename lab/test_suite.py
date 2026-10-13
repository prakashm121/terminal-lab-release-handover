#!/usr/bin/env python3
"""
lab/test_suite.py
Automated end-to-end regression test suite.
Runs all verification checks locally in one command.
Strictly ASCII-compatible across Windows, Linux, and macOS.
"""

import sys
import shutil
import subprocess
from pathlib import Path

def run_step(desc, cmd):
    print(f"--> [TEST] {desc}...")
    res = subprocess.run(cmd, shell=True)
    if res.returncode != 0:
        print(f"  [FAIL]: {desc} (Exit code: {res.returncode})", file=sys.stderr)
        sys.exit(res.returncode)
    print(f"  [PASS]: {desc}\n")

def main():
    repo_root = Path(__file__).resolve().parent.parent
    work_dir = repo_root / "lab-work"

    print("==================================================================")
    print("  Tech Lab 2: Automated End-to-End Regression Test Suite")
    print("==================================================================")
    print(f"Repository Root: {repo_root}\n")

    # Step 1: Pre-flight tool verification
    run_step("1. Environment Pre-Flight Verification", f'"{sys.executable}" "{repo_root}/scripts/verify_environment.py"')

    # Step 2: Booklet compilation and page count check
    run_step("2. Student Booklet PDF Generation", f'"{sys.executable}" "{repo_root}/book/build_booklet.py"')

    # Clean any leftover lab-work
    if work_dir.exists():
        shutil.rmtree(work_dir)

    # Step 3: Fresh attempt initialization
    run_step("3. Fresh Workspace Initialization (start.py)", f'"{sys.executable}" "{repo_root}/lab/start.py"')

    # Step 4: Execute reference solution
    run_step("4. Reference Solution Execution (solve.py)", f'"{sys.executable}" "{repo_root}/lab/solution/solve.py" "{work_dir}/attempt-1"')

    # Step 5: Verify 100% passing check
    run_step("5. Automated Verification Pass (check.py)", f'"{sys.executable}" "{repo_root}/lab/check.py" "{work_dir}/attempt-1"')

    # Step 6: Verify shell wrapper
    run_step("6. Shell Wrapper Compatibility (check.sh)", "bash lab/check.sh lab-work/attempt-1")

    # Step 7: Verify failure detection in demo-broken
    print("--> [TEST] 7. Detecting Intentional Error in demo-broken...")
    res = subprocess.run(f'"{sys.executable}" "{repo_root}/lab/check.py" "{repo_root}/lab/demo-broken"', shell=True, capture_output=True, text=True)
    if res.returncode == 1 and "Unsorted duplicate detected" in res.stdout:
        print("  [PASS]: demo-broken failed with expected Task 4 hint.\n")
    else:
        print("  [FAIL]: check.py did not properly flag demo-broken!", file=sys.stderr)
        sys.exit(1)

    # Clean up test attempts
    if work_dir.exists():
        shutil.rmtree(work_dir)

    print("==================================================================")
    print("  ALL REGRESSION TESTS PASSED (7/7 STEPS SUCCESSFUL)!")
    print("  The repository is 100% technically correct and submission-ready.")
    print("==================================================================")

if __name__ == "__main__":
    main()
