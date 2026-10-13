#!/usr/bin/env python3
"""
Tech Lab 2: Automated Verification Script (check.py)

GUARANTEES:
1. Strictly READ-ONLY: Never alters, modifies, or writes to any student file.
2. Can be run from within an attempt directory or from the repository root.
3. Provides clean, human-readable PASS/FAIL diagnostics with action hints.
"""

import os
import sys
import re
from pathlib import Path

# ANSI Color Codes
USE_COLOR = sys.stdout.isatty() or os.name != 'nt' or os.environ.get('TERM')

GREEN  = "\033[0;32m"  if USE_COLOR else ""
RED    = "\033[0;31m"  if USE_COLOR else ""
YELLOW = "\033[1;33m"  if USE_COLOR else ""
BLUE   = "\033[0;34m"  if USE_COLOR else ""
CYAN   = "\033[0;36m"  if USE_COLOR else ""
BOLD   = "\033[1m"     if USE_COLOR else ""
DIM    = "\033[2m"     if USE_COLOR else ""
RESET  = "\033[0m"     if USE_COLOR else ""

# UTF-8 symbol support (falls back to ASCII on Windows cp1252 terminals)
_enc = getattr(sys.stdout, "encoding", "ascii") or "ascii"
USE_UTF8 = _enc.lower().replace("-", "") in ("utf8", "utf16", "utf32")

HRULE    = "\u2500" if USE_UTF8 else "-"   # ─  horizontal rule
ARROW    = "\u279c" if USE_UTF8 else "->"  # ➜  hint arrow
BLK_FULL = "\u2588" if USE_UTF8 else "#"   # █  filled bar block
BLK_EMPT = "\u2591" if USE_UTF8 else "."   # ░  empty bar block
ICO_PASS = "\u2714" if USE_UTF8 else "+"   # ✔  tick
ICO_FAIL = "\u2718" if USE_UTF8 else "x"   # ✘  cross
ICO_STAR = "\u2726" if USE_UTF8 else "*"   # ✦  star (all-pass)
ICO_HALF = "\u25d0" if USE_UTF8 else "~"   # ◐  half-circle (almost)

def resolve_target_dir() -> Path:
    if len(sys.argv) > 1:
        return Path(sys.argv[1]).resolve()
    
    current = Path(".").resolve()
    if (current / ".attempt_meta").exists() or (current / "handover.md").exists():
        return current
    
    # Try finding the latest attempt under lab-work/
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    work_dir = repo_root / "lab-work"
    
    if work_dir.is_dir():
        attempts = sorted([d for d in work_dir.iterdir() if d.is_dir() and d.name.startswith("attempt-")])
        if attempts:
            return attempts[-1].resolve()
            
    print(f"{RED}[ERROR]{RESET} Cannot locate an attempt directory to verify.")
    print("Please cd into your attempt folder (e.g., 'cd lab-work/attempt-1') and run:")
    print("  python3 ../../lab/check.py")
    sys.exit(1)


def _wrap(text: str, width: int = 58) -> list[str]:
    """Simple word-wrap that respects the given column width."""
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        if current and len(current) + 1 + len(word) > width:
            lines.append(current)
            current = word
        else:
            current = (current + " " + word).strip()
    if current:
        lines.append(current)
    return lines or [""]


def main():
    target_dir = resolve_target_dir()

    print("==================================================================")
    print(f"{BOLD}{CYAN}  CloudRetail SRE Incident Handover - Verification Check{RESET}")
    print("==================================================================")
    print(f"Verifying workspace: {BLUE}{target_dir}{RESET}")
    print("")

    total_checks = 7
    passed_checks = 0
    failed_checks = 0
    # Stores (status, label) tuples for the final score card
    results: list[tuple[bool, str]] = []

    def pass_check(task_name: str):
        nonlocal passed_checks
        print(f"  [{GREEN}PASS{RESET}] {task_name}")
        passed_checks += 1
        results.append((True, task_name))

    def fail_check(task_name: str, hint: str):
        nonlocal failed_checks
        print(f"  [{RED}FAIL{RESET}] {task_name}")
        # Hint block — indented and styled for readability
        print(f"  {DIM}{HRULE * 62}{RESET}")
        hint_lines = _wrap(hint, width=58)
        for i, line in enumerate(hint_lines):
            prefix = f"  {YELLOW}{ARROW}{RESET} " if i == 0 else "      "
            print(f"{prefix}{line}")
        print(f"  {DIM}{HRULE * 62}{RESET}")
        failed_checks += 1
        results.append((False, task_name))

    # --------------------------------------------------------------------------
    failing_svc_file = target_dir / "failing_service.txt"
    handover_file = target_dir / "handover.md"

    svc_identified = False
    if failing_svc_file.is_file():
        content = failing_svc_file.read_text(encoding="utf-8", errors="ignore").lower()
        if "checkout-service" in content:
            svc_identified = True
            pass_check("Task 1 (less): Failing service correctly identified as 'checkout-service'")
    
    if not svc_identified:
        if handover_file.is_file():
            content = handover_file.read_text(encoding="utf-8", errors="ignore")
            if re.search(r"Failing Microservice:.*checkout-service", content, re.IGNORECASE):
                svc_identified = True
                pass_check("Task 1 (less): Failing service identified as 'checkout-service' in handover.md")

    if not svc_identified:
        fail_check(
            "Task 1 (less): Failing service not identified",
            "Inspect build.log using 'less build.log', search for '/FATAL' or '/CRITICAL', and write the service name into failing_service.txt (or fill Section 1 of handover.md)."
        )

    # --------------------------------------------------------------------------
    # Check 2: Tool [cut/grep] - Extracted Tickets for Failing Service
    # --------------------------------------------------------------------------
    tickets_file = target_dir / "checkout_tickets.txt"
    if tickets_file.is_file() and tickets_file.stat().st_size > 0:
        lines = tickets_file.read_text(encoding="utf-8", errors="ignore").splitlines()
        checkout_count = sum(1 for line in lines if "checkout-service" in line)
        other_count = sum(1 for line in lines if any(svc in line for svc in ["auth-service", "inventory-api", "frontend-web"]))
        
        if checkout_count >= 5 and other_count == 0:
            pass_check(f"Task 2 (cut/grep): Isolated tickets for checkout-service ({checkout_count} records)")
        elif other_count > 0:
            fail_check(
                "Task 2 (cut/grep): checkout_tickets.txt contains unrelated services",
                "Filter only 'checkout-service' records before extracting fields."
            )
        else:
            fail_check(
                "Task 2 (cut/grep): Incomplete checkout_tickets.txt",
                "Ensure all 7 checkout-service tickets from tickets.txt are extracted."
            )
    else:
        fail_check(
            "Task 2 (cut/grep): Missing checkout_tickets.txt",
            "Extract checkout-service tickets into checkout_tickets.txt using grep and cut."
        )

    # --------------------------------------------------------------------------
    # Check 3: Tool [sort] - Priority Ordering by Severity
    # --------------------------------------------------------------------------
    sorted_file = target_dir / "sorted_tickets.txt"
    if sorted_file.is_file() and sorted_file.stat().st_size > 0:
        lines = sorted_file.read_text(encoding="utf-8", errors="ignore").splitlines()
        sev1_idx = next((i for i, line in enumerate(lines) if "|1|" in line), None)
        sev4_idx = next((i for i, line in enumerate(lines) if "|4|" in line), None)

        if sev1_idx is not None and sev4_idx is not None and sev1_idx < sev4_idx:
            pass_check("Task 3 (sort): Tickets sorted by Severity in priority order")
        else:
            fail_check(
                "Task 3 (sort): sorted_tickets.txt is not sorted by numerical severity",
                "Use 'sort -t \"|\" -k 3,3n' to sort by severity field numerically."
            )
    else:
        fail_check(
            "Task 3 (sort): Missing sorted_tickets.txt",
            "Sort your extracted checkout tickets by severity into sorted_tickets.txt."
        )

    # --------------------------------------------------------------------------
    # Check 4: Tool [uniq] - Owner Workload Distribution & Aggregation Trap
    # --------------------------------------------------------------------------
    owners_file = target_dir / "owners_summary.txt"
    if owners_file.is_file() and owners_file.stat().st_size > 0:
        owners_content = owners_file.read_text(encoding="utf-8", errors="ignore")
        alice_occurrences = len(re.findall(r"\balice\b", owners_content, re.IGNORECASE))
        bob_occurrences = len(re.findall(r"\bbob\b", owners_content, re.IGNORECASE))

        if alice_occurrences == 1 and bob_occurrences == 1:
            has_counts = len(re.findall(r"\d+\s+(alice|bob)", owners_content, re.IGNORECASE))
            if has_counts >= 2:
                pass_check("Task 4 (uniq): Owner summary properly sorted and aggregated with counts")
            else:
                fail_check(
                    "Task 4 (uniq): Missing occurrence counts in owners_summary.txt",
                    "Use 'uniq -c' after sorting assignees to count tickets per engineer."
                )
        elif alice_occurrences > 1:
            fail_check(
                "Task 4 (uniq): Unsorted duplicate detected in owners_summary.txt!",
                "The 'uniq' command only merges ADJACENT duplicate lines. You MUST pipe to 'sort' BEFORE 'uniq -c'."
            )
        else:
            fail_check(
                "Task 4 (uniq): Missing expected engineers in owners_summary.txt",
                "Ensure owners_summary.txt includes ticket counts for alice, bob, and charlie."
            )
    else:
        fail_check(
            "Task 4 (uniq): Missing owners_summary.txt",
            "Extract assignees, sort them, and count with 'uniq -c' into owners_summary.txt."
        )

    # --------------------------------------------------------------------------
    # Check 5: Tool [diff] - Saved Configuration Differences
    # --------------------------------------------------------------------------
    diff_file = target_dir / "config.diff"
    if diff_file.is_file() and diff_file.stat().st_size > 0:
        diff_content = diff_file.read_text(encoding="utf-8", errors="ignore")
        if "DB_TIMEOUT_MS" in diff_content:
            pass_check("Task 5 (diff): config.diff captures configuration drift (DB_TIMEOUT_MS)")
        else:
            fail_check(
                "Task 5 (diff): config.diff does not contain DB_TIMEOUT_MS changes",
                "Generate diff between config-v1.env and config-v2.env: 'diff -u config-v1.env config-v2.env > config.diff'"
            )
    else:
        fail_check(
            "Task 5 (diff): Missing or empty config.diff",
            "Save diff of config-v1.env and config-v2.env into config.diff."
        )

    # --------------------------------------------------------------------------
    # Check 6: Tool [nano/edit] - Repaired Configuration File
    # --------------------------------------------------------------------------
    repaired_file = target_dir / "config-fixed.env"
    if repaired_file.is_file():
        repaired_content = repaired_file.read_text(encoding="utf-8", errors="ignore")
        timeout_match = re.search(r"^DB_TIMEOUT_MS\s*=\s*(\d+)", repaired_content, re.MULTILINE)
        retry_match = re.search(r"^PAYMENT_RETRY_ATTEMPTS\s*=\s*(\d+)", repaired_content, re.MULTILINE)

        timeout_val = timeout_match.group(1) if timeout_match else None
        retry_val = retry_match.group(1) if retry_match else None

        if timeout_val == "5000" and retry_val == "3":
            pass_check("Task 6 (nano): config-fixed.env restored with correct DB_TIMEOUT_MS=5000 and PAYMENT_RETRY_ATTEMPTS=3")
        elif timeout_val == "50":
            fail_check(
                "Task 6 (nano): config-fixed.env still has broken DB_TIMEOUT_MS=50",
                "Edit config-fixed.env with nano and restore DB_TIMEOUT_MS=5000."
            )
        else:
            fail_check(
                "Task 6 (nano): Incomplete fixes in config-fixed.env",
                "Ensure DB_TIMEOUT_MS is 5000 and PAYMENT_RETRY_ATTEMPTS is 3."
            )
    else:
        fail_check(
            "Task 6 (nano): Missing config-fixed.env",
            "Copy config-v2.env to config-fixed.env and repair the broken values."
        )

    # --------------------------------------------------------------------------
    # Check 7: Synthesis - Completed Handover Report (handover.md)
    # --------------------------------------------------------------------------
    if handover_file.is_file():
        handover_content = handover_file.read_text(encoding="utf-8", errors="ignore")
        placeholders_left = len(re.findall(r"(\[YOUR NAME HERE\]|\[REPLACE WITH|\[PASTE|\[FILL IN\])", handover_content))

        if placeholders_left == 0:
            if "checkout-service" in handover_content.lower() and "5000" in handover_content:
                pass_check("Task 7 (handover.md): Report fully populated and placeholders removed")
            else:
                fail_check(
                    "Task 7 (handover.md): Report is missing key incident details",
                    "Verify that handover.md includes checkout-service, log excerpts, and config values."
                )
        else:
            fail_check(
                f"Task 7 (handover.md): {placeholders_left} template placeholder(s) remaining",
                "Open handover.md with 'nano handover.md' and replace all remaining brackets [ ... ]."
            )
    else:
        fail_check(
            "Task 7 (handover.md): Missing handover.md",
            "Ensure handover.md is present in your attempt directory."
        )

    # --------------------------------------------------------------------------
    # Final Score Card
    # --------------------------------------------------------------------------
    _print_score_card(results, passed_checks, total_checks)
    sys.exit(0 if passed_checks == total_checks else 1)


def _print_score_card(
    results: list[tuple[bool, str]],
    passed: int,
    total: int,
) -> None:
    """Render a rich score card with a progress bar and per-check breakdown."""
    USE_COLOR = GREEN != ""  # noqa: F841 — re-read module-level
    failed = total - passed
    pct = int((passed / total) * 100)

    # ── Progress bar ──────────────────────────────────────────────────────────
    bar_width = 40
    filled     = round(bar_width * passed / total)
    empty      = bar_width - filled
    bar_filled = f"{GREEN}{BLK_FULL * filled}{RESET}"
    bar_empty  = f"{DIM}{BLK_EMPT * empty}{RESET}"
    bar        = f"[{bar_filled}{bar_empty}]"

    # ── Color the score based on result ───────────────────────────────────────
    if passed == total:
        score_color = GREEN
    elif passed >= total - 2:
        score_color = YELLOW
    else:
        score_color = RED

    print("")
    print("==================================================================")
    print(f"{BOLD}  SCORE CARD — INC-94821 Handover Verification{RESET}")
    print("==================================================================")
    print("")
    print(f"  Progress  {bar}  {score_color}{BOLD}{pct}%{RESET}")
    print(f"  Score     {score_color}{BOLD}{passed}/{total}{RESET} checks passed"
          + (f"  ({failed} remaining)" if failed else ""))
    print("")
    print(f"  {DIM}{HRULE * 62}{RESET}")
    print(f"  {BOLD}Check Breakdown:{RESET}")
    print(f"  {DIM}{HRULE * 62}{RESET}")

    # Per-check breakdown row
    for ok, label in results:
        icon   = f"{GREEN}{ICO_PASS}{RESET}" if ok else f"{RED}{ICO_FAIL}{RESET}"
        status = f"{GREEN}PASS{RESET}" if ok else f"{RED}FAIL{RESET}"
        # Trim label to a short task identifier for the table
        short  = label.split(":")[0].strip()   # e.g. "Task 3 (sort)"
        print(f"  {icon} {status}  {short}")

    print(f"  {DIM}{HRULE * 62}{RESET}")
    print("")

    if passed == total:
        print(f"{BOLD}{GREEN}  {ICO_STAR} ALL CHECKS PASSED — Outstanding work!{RESET}")
        print("    Your incident handover report is complete and verified.")
        print("    The morning shift is in good hands. Great job!")
    elif passed >= total - 2:
        print(f"{BOLD}{YELLOW}  {ICO_HALF} ALMOST THERE — {failed} check(s) remaining.{RESET}")
        print("    Re-read the hints above, fix the flagged files, and")
        print("    re-run:  python3 ../../lab/check.py")
    else:
        print(f"{BOLD}{RED}  {ICO_FAIL} {failed} check(s) failed.{RESET}")
        print("    Work through the hints above from top to bottom.")
        print("    Re-run:  python3 ../../lab/check.py   after each fix.")

    print("")
    print("==================================================================")


if __name__ == "__main__":
    main()
