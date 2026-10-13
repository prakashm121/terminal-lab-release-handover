# Reviewer Notes: TA + Tech Lab 2

**Author:** Prakash Jayavant Mandi
**Scenario:** CloudRetail incident handover. A canary release broke checkout, and the learner finds the failing service, the ticket owners and the config change, then completes a handover report.
**Learner time:** 60 to 90 minutes
**Repository:** https://github.com/prakashm121/terminal-lab-release-handover
**Codespace:** https://codespaces.new/prakashm121/terminal-lab-release-handover?quickstart=1

## Contents of the repository

| Item | Path |
|---|---|
| Student lab book (9 pages, PDF) | `book/lab-book.pdf` |
| Editable book source | `book/lab-book.md` |
| Start a fresh attempt (never overwrites an older one) | `lab/start.py` |
| Read-only checker | `lab/check.py` |
| Reference solution | `lab/solution/solve.py` |
| Codespace environment | `.devcontainer/devcontainer.json`, `.devcontainer/Dockerfile` |
| Setup and launch instructions | `README.md` |

`start.py` and `check.py` are the scripts used in the README and the video.

## 1. Tool-to-experiment mapping

The experiments follow the order of the video and the book. Each result is used again later.

| # | Tool | What the learner does in the story | Flags and keys taught | Result it produces |
|---|---|---|---|---|
| 1 | `less` | Search the build log for the fatal error of the current release | `Space`, `b`, `g`, `G`, `/FATAL`, `n`, `N`, `q` | The failing service: `checkout-service` |
| 2 | `cut` | Pull the checkout tickets and read the assignee field | `-d "\|"` (quoted), `-f 1,4`, `-f 4` | `checkout_tickets.txt` (7 rows) |
| 3 | `sort` | Order the tickets by severity; trigger the `>` trap in a sandbox | text vs numeric order, `-n`, `-r`, `-t`, `-k 3,3n`, `>` to a different file | `sorted_tickets.txt` |
| 4 | `uniq` | Count tickets per assignee; compare two pipeline orders | adjacent duplicates, `-c`, `sort \| uniq -c` | `owners_summary.txt` |
| 5 | `diff` | Compare the working config with the broken one | identical files, `-u`, `-`, `+`, input order, saving the output | `config.diff` |
| 6 | `nano` | Create a new file, repair the config, finish the report | `Ctrl+O`, `Enter`, `Ctrl+X`, `Ctrl+W` | `failing_service.txt`, `config-fixed.env`, `handover.md` |
| 7 | `history` | Bring back and edit commands typed earlier in the lab | `history 10`, `history \| grep -F`, `Ctrl+R` (repeat), `Right Arrow`, `Ctrl+G` | Reused and edited commands |

## 2. Answer key

`python3 lab/solution/solve.py <attempt-folder>` produces the file results. The interactive steps (`less`, `nano`, `history`) cannot be scripted, so the script writes their results directly.

Commands run from inside `lab-work/attempt-N/`.

### Experiment 1: less
```bash
wc -l build.log
grep -c FATAL build.log
less build.log
```
Inside `less`: `Space` and `b` move by screen, `G` and `g` jump to the end and start, `/FATAL` then `n` and `N` move between matches, `q` quits. The log has more than one FATAL line, so the learner reads the surrounding lines to choose the one that belongs to the current release. Answer: `checkout-service`.

### Experiment 2: cut
```bash
head -n 3 tickets.txt
cut -d "|" -f 1,4 tickets.txt
grep -F "|checkout-service|" tickets.txt > checkout_tickets.txt
cut -d "|" -f 4 checkout_tickets.txt
```
Fields: `ID|service|severity|assignee|status|title`. An unquoted `cut -d | -f 1` does not work: Bash treats the `|` as a pipe and splits the command in two. `checkout_tickets.txt` has 7 rows:

```text
CR-102|checkout-service|1|alice|OPEN|Checkout gateway connection timeout in canary
CR-18|checkout-service|2|bob|OPEN|Database pool max connections sizing review
CR-9|checkout-service|1|alice|OPEN|Canary pods entering CrashLoopBackOff state
CR-22|checkout-service|3|charlie|OPEN|Update Prometheus metrics exporter to v1.4
CR-105|checkout-service|2|bob|OPEN|Payment gateway retry attempts dropped to zero
CR-7|checkout-service|1|alice|OPEN|Investigate DB_TIMEOUT_MS env var regression
CR-402|checkout-service|4|bob|OPEN|Add structured JSON logging to checkout handlers
```

### Experiment 3: sort
```bash
printf '2\n9\n18\n102\n' | sort        # 102 18 2 9 (text order)
printf '2\n9\n18\n102\n' | sort -n     # 2 9 18 102
printf '2\n9\n18\n102\n' | sort -nr    # 102 18 9 2
sort -t "|" -k 3,3n checkout_tickets.txt > sorted_tickets.txt
```
`-t "|"` sets the field separator, `-k 3,3` sorts on field 3 only, and `n` compares it as a number. Rows with the same severity are ordered by whole-line comparison, so their order can differ between locales. Compare the severity order, not the tie order.

**Trap (in the sandbox copy only):**
```bash
wc -l sandbox/tickets_copy.txt
sort sandbox/tickets_copy.txt > sandbox/tickets_copy.txt
wc -l sandbox/tickets_copy.txt         # 0
```
Bash applies `>` first and empties the destination, so `sort` reads an empty file. The input file and the destination of `>` must be different files. A safe version is `sort file > file.tmp && mv file.tmp file`.

### Experiment 4: uniq
```bash
printf 'alice\nalice\nbob\n' | uniq                                      # adjacent duplicates merge
cut -d "|" -f 4 checkout_tickets.txt | uniq -c                           # every count is 1
cut -d "|" -f 4 checkout_tickets.txt | sort | uniq -c                    # 3 alice, 3 bob, 1 charlie
cut -d "|" -f 4 checkout_tickets.txt | uniq -c | sort -nr                # wrong: hides the busiest owner
cut -d "|" -f 4 checkout_tickets.txt | sort | uniq -c | sort -nr         # right
cut -d "|" -f 4 checkout_tickets.txt | sort | uniq -c | sed 's/^[ \t]*//' > owners_summary.txt
```
`owners_summary.txt` contains `3 alice`, `3 bob` and `1 charlie`. The `sed` step only removes the padding that `uniq -c` adds.

### Experiment 5: diff
```bash
diff config-v1.env config-v1.env           # no output: identical
diff -u config-v1.env config-v2.env        # shows the changes
diff -u config-v1.env config-v2.env > config.diff
```
The first file is the old working config and the second is the broken one. A line starting with `-` is only in the first file, and a line starting with `+` is only in the second. Two settings changed:

| Setting | `config-v1.env` | `config-v2.env` |
|---|---|---|
| `DB_TIMEOUT_MS` | 5000 | 50 |
| `PAYMENT_RETRY_ATTEMPTS` | 3 | 0 |

### Experiment 6: nano
1. `nano failing_service.txt`: type `checkout-service`, `Ctrl+O`, `Enter`, `Ctrl+X`. Check with `cat`, then reopen it.
2. `nano config-fixed.env`: set `DB_TIMEOUT_MS=5000` and `PAYMENT_RETRY_ATTEMPTS=3`. Save with `Ctrl+O`, `Enter`, exit with `Ctrl+X`.
3. `diff -u config-v1.env config-fixed.env` prints nothing.
4. `nano handover.md`: replace every placeholder using the earlier results (failing service, fatal log lines, `sorted_tickets.txt`, `owners_summary.txt`, the config change). `grep -F "[" handover.md` finds no placeholder left.

### Experiment 7: history
```bash
history 10
history | grep -F "build.log"
```
`Ctrl+R`, type `build.log`, press `Ctrl+R` again to reach `grep -c FATAL build.log`, press `Right Arrow`, change `FATAL` to `ERROR`, check the line, then `Enter`. Then `Ctrl+R`, type `tickets`, and press `Ctrl+G`: nothing runs and the prompt is restored. The learner can also recall the earlier `diff -u` command, delete its `> config.diff` ending, and change `config-v2.env` to `config-fixed.env` to verify the repair.

## 3. Validation

Run from inside an attempt folder:

```bash
python3 ../../lab/check.py
```

The checker only reads files and never changes them. It runs 7 checks, one per task. A failing check prints a hint under it.

**Demonstration of a wrong result (also in the video):**
1. With a correct attempt, run `cut -d "|" -f 4 checkout_tickets.txt | uniq -c > owners_summary.txt`. This forgets `sort`.
2. Run the checker. The uniq check fails with a hint to sort before `uniq -c`. The other six checks still pass. The wording of the hint is whatever `check.py` prints.
3. Fix it with `cut -d "|" -f 4 checkout_tickets.txt | sort | uniq -c | sed 's/^[ \t]*//' > owners_summary.txt`.
4. Run the checker again. All 7 checks pass.

**Expected `diff` output.** In experiment 5, `diff` prints differences on purpose. That is the normal result of comparing two different files, not an error. Only an empty result from a comparison with the correct version means the repair is complete.

**What the checker cannot show.** It checks saved files. It cannot prove that the learner used `history`, `nano` or `less`. A reviewer should ask the learner to find and edit an earlier command, save a change in `nano`, and search in `less`.

## 4. Three improvements over the reference lab

| # | Improvement | In the reference lab | In this lab |
|---|---|---|---|
| 1 | One connected scenario | Practice uses separate datasets (names, scores, timetables). Only the last challenge combines skills. | Each result feeds the next: the log gives the service, the service selects the tickets, the tickets give the owners, the config diff gives the cause, and all of it goes into `handover.md`. |
| 2 | Both traps are run by the learner | The `>` rule is stated in a note and a hint but never demonstrated. `uniq` is shown before and after `sort`, but only the sorted order is counted. | The learner empties a sandbox file with `sort file > file`, and compares `uniq -c \| sort -nr` with `sort \| uniq -c \| sort -nr` on the same data. |
| 3 | Hints in the checker, and a shown failure | The checker prints `PASS` or `CHECK` for each file with no explanation. | Each failing check prints a hint. The video shows a deliberately wrong result being caught, fixed and passing. |

The lab book is 9 pages. The reference booklet is 13 pages.

## 5. Time

**Expected learner time:** 60 to 90 minutes, for learners who know the Lab 1 commands.

**Actual time spent by the author:** about 17 hours.

| Work | Hours |
|---|---|
| Pedagogy and incident design | 1.5 |
| Data and core scripts (`start.py`, `check.py`) | 3.0 |
| Lab book writing and PDF layout | 4.0 |
| Codespace setup and fresh-Codespace testing | 2.0 |
| Validation demo, README and these notes | 1.5 |
| Walkthrough script and rehearsal | 1.5 |
| Loom recording, editing and timestamps | 2.5 |
| Final checks and submission email | 1.0 |

## 6. Assumptions and limits

- Learners know `cd`, `pwd`, `ls`, `cat` and basic `grep` from Lab 1.
- The lab runs in the Codespace defined in `.devcontainer/`. It has not been tested on other systems.
- Every attempt uses the same dataset, so the expected results are the same for all learners. The checker is readable and can be edited by a learner, so a pass is feedback and not proof of authorship.
- Blockers: none.

## 7. AI use

I used Claude to plan the lab, to help draft the starter scripts and data files, to help draft the walkthrough script, and to review these notes.

I ran every experiment by hand in a Codespace while recording the walkthrough. [Add anything else you rewrote or tested yourself, or delete this line.]
