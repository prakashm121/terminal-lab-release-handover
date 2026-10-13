# Validation Demo: Catching and Fixing an Error

This directory contains a pre-built attempt for your **Loom recording validation demonstration**.

## Why this exists:
The grading rubric requires showing:
> "An incorrect result is shown being caught and then fixed."

In this directory, all tasks are completed correctly **except Task 4**, where `sort` was omitted before `uniq -c`. As a result, `owners_summary.txt` contains unaggregated duplicate lines (`1 alice`, `1 bob`, `1 alice`, etc.).

## How to present this on your Loom recording:

1. In your terminal, navigate to this directory:
   ```bash
   cd lab/demo-broken
   ```

2. Run the checker to show it catching the bug:
   ```bash
   bash ../check.sh .
   ```
   **Point out to the viewer:**
   Notice that Task 4 fails with:
   `[FAIL] Task 4 (uniq): Unsorted duplicate detected in owners_summary.txt!`
   `       Hint: The 'uniq' command only merges ADJACENT duplicate lines. You MUST pipe to 'sort' BEFORE 'uniq -c'.`

3. Explain the Unix concept:
   Explain to the viewer that `uniq` operates line-by-line on adjacent items only. Because the tickets list was unsorted, multiple occurrences of Alice and Bob were not adjacent, so `uniq` could not aggregate them.

4. Apply the fix:
   Either run the command manually:
   ```bash
   cut -d "|" -f 4 checkout_tickets.txt | sort | uniq -c | sed 's/^[ \t]*//' > owners_summary.txt
   ```
   Or execute the fix script:
   ```bash
   bash fix-demo.sh
   ```

5. Re-run the checker to demonstrate that all 7 checks now PASS:
   ```bash
   bash ../check.sh .
   ```
   **Point out to the viewer:**
   `RESULT: ALL CHECKS PASSED (7/7)`!
