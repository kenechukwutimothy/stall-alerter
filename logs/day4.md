# Day 4

## Goal for today

Make the output usable at scale.

## What I prompted

Day 4: make the output usable at scale.
Add --top N (default 20) so only the N most urgent candidates are printed.
Before the list, print a short summary: total stalled, count per stage, and count per owner.
Collapse the problem rows into counts by type (e.g. “467 bad dates”), with --show-problems to list them all.
Validate --threshold so negative numbers give a clear error.
Update the README, including the config example with my thresholds. Add tests for each change. Explain your approach first.

## What came back

The AI added:
- `--top N`, defaulting to 20.
- A summary showing total stalled candidates, counts by stage, and counts by owner.
- Problem counts grouped by type.
- `--show-problems` to display individual problem rows.
- Validation preventing negative `--threshold` and `--top` values.
- README updates and tests.

The 10,000-row output went from about 6,900 lines to 34.

## What the AI got wrong / what I changed

Two tests failed on the AI's first run. One was a line-counting mistake. The other was an existing Day 2 test that expected the old full problem-row output. I checked that this was caused by the intentional Day 4 output change and updated the test to use `--show-problems`.

## What broke

- The top 20 candidates are all Offer candidates because later stages are ranked first.
- Candidates with the same number of stalled days follow file order because there is no secondary tie-breaker.
- At 10,000 rows, 6,132 candidates were stalled and 729 rows were suspicious/problematic.

## Decisions I made

- I kept the stage-first ranking because it follows the original requirement.
- I kept file order for ties for now because a secondary ranking was not required.
- I accepted the updated problem-output test because the Day 4 requirement intentionally changed how problems are displayed.

## Habit I caught myself in

I caught myself wanting to change behavior simply because the large dataset exposed an output pattern I did not like. I separated "this is surprising" from "this is actually a bug" and kept the behavior that still matched the stated requirement.

## Tomorrow

Review the project and prepare the final unlearning notes / remaining improvements.