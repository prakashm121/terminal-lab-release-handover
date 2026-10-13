#!/usr/bin/env python3
"""
Tech Lab 2: Reference Solution Script (solve.py)
Generates the complete passing solution for automated testing and verification.
"""

import os
import sys
import re
from pathlib import Path
from collections import Counter
import difflib

def main():
    target_dir = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
    target_dir.mkdir(parents=True, exist_ok=True)
    print(f"Solving incident handover in: {target_dir}")

    # Task 1: Record investigative command & identify failing service
    inv_log = target_dir / "investigation.log"
    with open(inv_log, "a", encoding="utf-8") as f:
        f.write("grep -E '(FATAL|ERROR|CRITICAL)' build.log\n")

    failing_svc = target_dir / "failing_service.txt"
    failing_svc.write_text("checkout-service\n", encoding="utf-8")

    # Task 2: Extract checkout-service tickets
    tickets_src = target_dir / "tickets.txt"
    if not tickets_src.exists():
        tickets_src = target_dir.parent.parent / "lab" / "data" / "tickets.txt"

    tickets_lines = tickets_src.read_text(encoding="utf-8").splitlines()
    checkout_tickets = [line for line in tickets_lines if "checkout-service" in line]

    (target_dir / "checkout_tickets.txt").write_text("\n".join(checkout_tickets) + "\n", encoding="utf-8")

    # Task 3: Sort tickets by severity (Column 3, numeric)
    def get_severity(line):
        parts = line.split("|")
        return int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 99

    sorted_tickets = sorted(checkout_tickets, key=get_severity)
    (target_dir / "sorted_tickets.txt").write_text("\n".join(sorted_tickets) + "\n", encoding="utf-8")

    # Task 4: Deduplicate and count assignees (sort | uniq -c)
    assignees = [line.split("|")[3] for line in checkout_tickets if len(line.split("|")) > 3]
    counts = Counter(sorted(assignees))
    owners_lines = [f"{count} {owner}" for owner, count in sorted(counts.items())]
    (target_dir / "owners_summary.txt").write_text("\n".join(owners_lines) + "\n", encoding="utf-8")

    # Task 5: Generate diff
    c1 = target_dir / "config-v1.env"
    c2 = target_dir / "config-v2.env"
    if not c1.exists():
        c1 = target_dir.parent.parent / "lab" / "data" / "config-v1.env"
    if not c2.exists():
        c2 = target_dir.parent.parent / "lab" / "data" / "config-v2.env"

    c1_lines = c1.read_text(encoding="utf-8").splitlines(keepends=True)
    c2_lines = c2.read_text(encoding="utf-8").splitlines(keepends=True)
    diff = list(difflib.unified_diff(c1_lines, c2_lines, fromfile="config-v1.env", tofile="config-v2.env"))
    (target_dir / "config.diff").write_text("".join(diff), encoding="utf-8")

    # Task 6: Repair working configuration
    c2_content = c2.read_text(encoding="utf-8")
    repaired = c2_content.replace("DB_TIMEOUT_MS=50\n", "DB_TIMEOUT_MS=5000\n")
    repaired = repaired.replace("PAYMENT_RETRY_ATTEMPTS=0\n", "PAYMENT_RETRY_ATTEMPTS=3\n")
    (target_dir / "config-fixed.env").write_text(repaired, encoding="utf-8")

    # Task 7: Populate handover.md
    handover_template = target_dir / "handover.md"
    handover_content = f"""# Incident Handover Report: Canary Release v2.4.1

## 1. Incident Overview
- **Incident ID:** INC-94821
- **Severity:** P1 (Critical Outage)
- **Investigator / On-Call Engineer:** SRE Lead Engineer
- **Failing Microservice:** checkout-service
- **Deployment Status:** Canary Halted / Rolled Back

## 2. Root Cause Analysis
- **Observed Symptoms:** Pods entered CrashLoopBackOff after failing healthcheck probe (`/healthz` returned 503).
- **Log Error Excerpt:**
  ```text
  [2026-10-12 03:41:06] [checkout-service] [ERROR] Connection handshake exceeded configured timeout threshold (50ms)
  [2026-10-12 03:41:08] [checkout-service] [FATAL] Database connection pool failed to initialize. Expected timeout >= 5000ms. Configured value is 50ms.
  [2026-10-12 03:41:10] [checkout-service] [FATAL] Process exiting with status code 1
  ```
- **Configuration Root Cause:**
  - Parameter: `DB_TIMEOUT_MS`
  - Bad Value (v2.4.1): `50`
  - Expected Stable Value (v2.4.0): `5000`

## 3. Triage & Ticket Allocation
Below are the open tickets for the failing service, prioritized by Severity (1=Critical to 4=Low):
```text
{chr(10).join(sorted_tickets)}
```

## 4. Engineer Workload Summary
Active ticket count per owner for the affected service (generated via `sort | uniq -c`):
```text
{chr(10).join(owners_lines)}
```

## 5. Remediation & Verification
- **Configuration Diff Saved:** `config.diff`
- **Working Config Corrected:** `config-fixed.env` (restored DB_TIMEOUT_MS to 5000 and PAYMENT_RETRY_ATTEMPTS to 3)
- **Next Actions:** Re-trigger canary deploy pipeline for `checkout-service` once morning shift signs off.
"""
    handover_template.write_text(handover_content, encoding="utf-8")
    print("Solution generated successfully.")

if __name__ == "__main__":
    main()
