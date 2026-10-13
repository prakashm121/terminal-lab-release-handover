# Reviewer Notes & Instructor Guide

**Assignment:** TA + Tech Lab 2: Core Unix Terminal Tooling  
**Author / Candidate:** Candidate Submission  
**Scenario:** CloudRetail SRE Incident Handover (Triaging Canary Outage INC-94821)  
**Deliverables Directory:**
- Student Booklet PDF: `book/lab-book.pdf` (9 pages, strictly adheres to 5–10 page requirement)
- Fresh-Attempt Script: `lab/start.py` & `lab/start.sh` (creates `lab-work/attempt-N`, non-destructive)
- Automated Checker: `lab/check.py` & `lab/check.sh` (read-only, styled hint blocks, visual score card)
- Reset Script: `lab/reset.py` (wipes & re-scaffolds an attempt; confirmation-gated, non-destructive to fixtures)
- Reference Solution: `lab/solution/solve.py` & `lab/solution/solve.sh`
- Deliberate Validation Failure: `lab/demo-broken/` (for video walkthrough)
- Devcontainer Environment: `.devcontainer/devcontainer.json` & `.devcontainer/Dockerfile`

---

## 1. Tool-to-Experiment Mapping

Every tool is taught through a single, continuous Software Engineering incident narrative. Each output directly feeds the next step and culminates in the final handover deliverable.

| Step | Tool | Hands-On Role in Incident Story | Key Flags & Concepts Taught | Artifact Produced |
| :---: | :---: | :--- | :--- | :--- |
| **1** | `history` | Recall earlier failed curl probes and grep queries without retyping. | `history 10`, `history \| grep`, `!N`, `Ctrl+R` (reverse search, cycle older matches, Right Arrow to edit in place, `Ctrl+G` to cancel). | `investigation.log` |
| **2** | `less` | Deep search through 180+ line CI/CD build and deploy log to find crashing container. | `Space`, `b`, `g`, `G`, `/pattern`, `n`, `N`, `q`. Why `cat` fails on production logs. | `failing_service.txt` (`checkout-service`) |
| **3** | `cut` | Isolate fields from Jira incident database (`tickets.txt`). | Quoted delimiter `-d "|"`, `-f 1,4`, field ranges. Why unquoted `|` errors in bash. | `checkout_tickets.txt` (7 records) |
| **4** | `sort` | Order tickets by numerical severity and demonstrate shell truncation trap. | `-n` (numeric vs text ASCII sort: why `100` sorts before `2` in ASCII), `-r`, `-t "|"`, `-k 3,3n`, `-o` safe output. | `sorted_tickets.txt` & sandbox trap demo |
| **5** | `uniq` | Aggregate ticket load per engineer and prove pipeline order sensitivity. | `-c` (occurrence count), adjacent-only restriction, non-commutative Unix pipelines (`sort \| uniq` vs `uniq \| sort`). | `owners_summary.txt` (`3 alice`, `3 bob`, `1 charlie`) |
| **6** | `diff` | Compare stable v2.4.0 vs broken v2.4.1 config, isolate 50ms timeout bug. | Standard diff symbols (`<`, `>`, `c`, `a`, `d`) vs unified diff (`diff -u`, `---`, `+++`, `-`, `+`, `@@`). | `config.diff` |
| **7** | `nano` | In-terminal editing to repair configuration and assemble final incident report. | `Ctrl+O` WriteOut, `Enter`, `Ctrl+X` Exit, `Ctrl+W` Where Is / search, `Ctrl+K` cut, `Ctrl+U` paste/uncut. | `config-fixed.env` & `handover.md` |

---

## 2. Complete Answer Key & Reference Solution

The full end-to-end solution can be executed automatically via `python3 lab/solution/solve.py <directory>` or manually as follows:

### Task 1: `history`
```bash
# Investigative commands run in terminal:
curl -s http://localhost:8080/healthz
grep -i "timeout" build.log
tail -n 15 build.log

# Reverse search via Ctrl+R -> 'timeout' -> Right Arrow -> add -n -> Enter
# Record to audit log:
echo "grep -E '(FATAL|ERROR|CRITICAL)' build.log" >> investigation.log
```

### Task 2: `less`
```bash
less build.log
# Inside less: /FATAL -> Enter -> n -> inspect stack trace -> q
echo "checkout-service" > failing_service.txt
```

### Task 3: `cut`
```bash
grep "checkout-service" tickets.txt > checkout_tickets.txt
```
*Extracted Records:*
```text
CR-102|checkout-service|1|alice|OPEN|Checkout gateway connection timeout in canary
CR-18|checkout-service|2|bob|OPEN|Database pool max connections sizing review
CR-9|checkout-service|1|alice|OPEN|Canary pods entering CrashLoopBackOff state
CR-22|checkout-service|3|charlie|OPEN|Update Prometheus metrics exporter to v1.4
CR-105|checkout-service|2|bob|OPEN|Payment gateway retry attempts dropped to zero
CR-7|checkout-service|1|alice|OPEN|Investigate DB_TIMEOUT_MS env var regression
CR-402|checkout-service|4|bob|OPEN|Add structured JSON logging to checkout handlers
```

### Task 4: `sort` & Redirection Trap
```bash
# Safe sorting by severity field (column 3, numeric):
sort -t "|" -k 3,3n checkout_tickets.txt > sorted_tickets.txt

# Sandbox demonstration of truncation trap:
sort sandbox/tickets_copy.txt > sandbox/tickets_copy.txt
# Result: sandbox/tickets_copy.txt is truncated to 0 bytes by shell O_TRUNC before sort reads!
```

### Task 5: `uniq` & Pipeline Order Demonstration
```bash
# The bug when omitting sort (Experiment A):
cut -d "|" -f 4 checkout_tickets.txt | uniq -c
# Output: 1 alice, 1 bob, 1 alice, 1 charlie, 1 bob, 1 alice, 1 bob (unmerged!)

# The correct order (Experiment B):
cut -d "|" -f 4 checkout_tickets.txt | sort | uniq -c | sed 's/^[ \t]*//' > owners_summary.txt
# Output:
# 3 alice
# 3 bob
# 1 charlie
```

### Task 6: `diff`
```bash
diff -u config-v1.env config-v2.env > config.diff
```
*Identified Root Cause:*
`DB_TIMEOUT_MS=50` (regressed from stable `5000ms`, causing instant TCP handshake timeouts).

### Task 7: `nano` & Synthesis
- Edit `config-fixed.env` using `nano`:
  - Set `DB_TIMEOUT_MS=5000`
  - Set `PAYMENT_RETRY_ATTEMPTS=3`
- Edit `handover.md` using `nano`:
  - Fill all metadata, paste log snippet, tickets table, owner summary, and config diff verification.

---

## 3. Three Concrete Improvements Over the Reference Lab

| # | Improvement | Weakness in Reference Lab | How Our Lab Solves It |
| :-: | :--- | :--- | :--- |
| **1** | **Strict, High-Signal Page Count (9 Pages vs 13 Pages)** | The reference booklet was 13 pages (violating the 5–10 page constraint) with excessive filler text, pilot disclaimers, and unnecessary padding. | Our booklet is exactly 9 pages. Every section is dense with high-value technical context, visual tables, clear flags, and explicit step-by-step instructions. |
| **2** | **Explicit Experimental Traps (Same-File Truncation & Sort-Before-Uniq Order)** | The reference lab omitted the same-file `>` truncation trap entirely, and only mentioned "order matters" as a passive quiz question with no hands-on proof. | We built two dedicated experiments: (1) A safe sandbox test demonstrating why shell `O_TRUNC` destroys files in `sort file > file`, and (2) A side-by-side comparison showing why `cut \| uniq -c` fails on non-adjacent lines while `cut \| sort \| uniq -c` succeeds. |
| **3** | **Integrated SRE Narrative, Read-Only Checker with Auto-Hints & Visual Score Card** | The reference lab used disparate, unconnected toy datasets and a Python checker that leaked solution strings with a plain PASS/FAIL line. | We contextualized the entire lab into a single SRE deployment incident (INC-94821). Our `check.py` is strictly read-only, prints a **styled word-wrapped hint block** (with `➜` arrow) under every failing check, and displays a **visual block-character progress bar** plus a **per-check score card** at the end (`Score: 6/7  ████████░░░░  85%`). |
| **4** | **`lab/reset.py` — Confirmation-Gated Attempt Reset** | The reference lab had no reset path. Students who made a mistake had to manually find and delete their output files, or start a new attempt with a higher number. | `python3 lab/reset.py` shows a full manifest of files that will be deleted, requires the student to type `yes` to proceed, then wipes all 7 student-generated output files and the `sandbox/` directory before restoring all fixtures. Attempt number and creation timestamp are preserved in `.attempt_meta`. |

---

## 4. Expected Learner Completion Time & Actual Time Spent

- **Expected Learner Completion Time:** 90–120 Minutes
  - Tailored for students who completed Lab 1 (basic navigation and simple file inspection).
  - Scaffolded progression: high guidance in early experiments (`history`, `less`), tapering off towards the independent synthesis task (`nano` handover).
- **Actual Time Spent by Author:** ~7 Hours total
  - *Pedagogy & Incident Design:* 1.5 Hours
  - *Data Engineering & Core Tooling (`start.py`, `check.py`):* 2.0 Hours
  - *Student Lab Book Authoring & PDF Layout Optimization:* 2.5 Hours
  - *Automated CI & Codespace Pre-Flight Testing:* 1.0 Hour

---

## 5. Blockers or Assumptions

- **Assumptions on Learner Prerequisite Knowledge:**
  - Assumes students already understand Lab 1 fundamentals: `cd`, `pwd`, `ls`, `cat`, and basic `grep`.
  - Assumes students have access to a standard Unix terminal environment (Bash) or GitHub Codespaces.
- **Platform Compatibility Assumptions:**
  - Standardized on POSIX-compliant utilities (`coreutils`, `diffutils`, `less`, `nano`) and Python 3.8+.
  - Fully compatible with Ubuntu 22.04 LTS devcontainers, GitHub Codespaces, and local Linux/WSL environments.
- **Blockers Encountered & Resolved:**
  - *Cross-Platform Windows Redirection:* The same-file truncation trap (`sort file > file`) behaves differently across shells; solved by isolating it into a safe `sandbox/` folder with explicit explanation of shell `O_TRUNC` evaluation order.
  - *Booklet Length Restriction:* The initial reference lab was 13 pages (violating the 5–10 page constraint); resolved by eliminating pilot filler text and condensing into a high-density, professional 9-page guide.

---

## 6. AI Usage Disclosure

- **What AI was used for:**
  - Assisted in brainstorming the CloudRetail SRE failed-deploy incident scenario.
  - Scaffolding realistic multi-stage log lines for `build.log` and tabular Jira records for `tickets.txt`.
- **What was manually designed, checked, and verified by Author:**
  - All educational sequencing, experiment goals, and flag explanations.
  - All test scripts (`start.py`, `check.py`, `solve.py`, `verify_environment.py`, CI workflow).
  - Both experimental traps (same-file `>` truncation mechanics and pipeline order sensitivity in `sort | uniq`).
  - Tested 100% end-to-end in a clean container environment to ensure zero broken paths or unhandled edge cases.
