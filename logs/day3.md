# Day 3 Log

## What I prompted

Day 3: raise the load.

Generate a large test board at `data/big_board.csv` with 10,000 rows.

Include realistic messy data such as:

- mixed date formats
- blank lines
- extra spaces in headers and/or values
- duplicate candidate IDs
- unknown stages

Run the existing Stall Alerter against the 10,000-row board and measure how long it takes.

Before fixing anything, report honestly:

1. What breaks or produces errors.
2. What is slow or inefficient.
3. Any other important behavior you observe at this scale.

Then fix only issues that actually break or materially prevent the tool from handling the larger dataset correctly. Do not proactively redesign working parts.

Add pytest tests for every fix you make.

Do not add an LLM, business-day calculations, or unrelated features yet.

Before changing code, briefly explain your implementation approach. Keep the project small and focused.

I deliberately asked the AI to report problems before fixing them, and to fix only real breaks. On Days 1 and 2 it reported and fixed in one go, so I couldn't see the "before" state.

## What came back

The AI wrote `scripts/make_big_board.py`, a reproducible generator using a fixed random seed. It produced a 10,000-row board with spaced headers, mixed date formats, blank lines, empty rows, duplicate IDs and unknown stages.

## What broke

1. **Headers with spaces stopped the whole run.** A header like ` stage ` gave `Error: CSV is missing required columns`, and not a single row was processed.

2. **Line numbers were wrong after blank lines.** A duplicate was reported as being "on line 149" when it was actually on line 151. Nothing crashed, but the tool gave an incorrect location for the problem.

The AI found the second bug by checking a reported line number against the actual file.

## What was slow

Nothing significant. A 10,000-row run took about 0.2 seconds. Most of the time was spent parsing dates, so performance was not a problem at this scale.

## What was fixed

- Header names are now trimmed and lowercased before the required-column check.
- Line numbers now come from the CSV reader's real line counter, so they match the actual file.
- Tests were added for spaced or capitalised headers, line numbers after blank lines, duplicate line numbers, and loading a 10,000-row board.

The test suite increased to 24 tests, and all 24 passed.

## What I checked

I regenerated the board on my machine with the script, ran:

`python -m pytest`

and confirmed that all 24 tests passed.

I also ran:

`python -m stall_alerter data/big_board.csv --today 2026-10-14`

The run completed successfully and reported the problem rows at the end, including examples such as `unknown stage 'On hold'` and bad dates such as `Sep 15 2026`.

The small board still gave the same result as Day 2: 24 stalled candidates and 6 problem rows.

## What's still wrong (not fixed today, on purpose)

- **The output is too long to use.** The 10,000-row board produced 6,132 stalled candidates and 729 problem rows, resulting in roughly 6,900 lines of output. This is too much for a recruiter or manager to practically read.

- **About 5% of dates are rejected.** 467 dates were rejected, including formats such as `14/10/2026` and `Oct 14 2026`. Rejecting ambiguous formats such as `03/10/2026` is deliberate because the program cannot safely know whether the date means March 10 or October 3.

- **The duplicate rule hides 92 real candidates at scale.** Because the Day 2 rule excludes all copies of a duplicated candidate ID, the effect is much larger on a 10,000-row dataset than it was on the original 51-row dataset.

- **Fully blank lines are skipped without a specific blank-line report.** Rows containing empty values are instead reported as missing fields such as `missing candidate_id`.

- **The generated data affects the results.** The AI generated dates spread across 45 days, which partly explains why 61% of candidates were classified as stalled. Therefore, the 61% figure reflects the test data as well as the behavior of the tool.

- **The AI-generated CSV did not copy successfully to my machine.** The 650 KB file timed out during the copy, so I regenerated it locally using the provided generator script.

## Decisions I made

- I decided that the most important issue to take into Day 4 is the excessive output length. At 10,000 rows, thousands of lines are not practical to review, so Day 4 will focus on making the output usable at scale.

- I will add a `--top N` option so the tool can show only the most urgent candidates, while still providing a summary of the full results.

- I will add a summary showing the total number of stalled candidates and counts by stage and owner.

- I will leave the date-format behavior unchanged for now. Automatically guessing ambiguous formats such as `03/10/2026` could introduce incorrect dates, so rejecting them is safer.

- I will leave the duplicate behavior unchanged for now. Although excluding all duplicate copies hides some genuine candidates, changing that rule requires deciding how the program should determine which record is correct. I will not redesign it without a clear rule.

- I will not change the generated test-data distribution simply to make the stalled percentage look more realistic. The purpose of the load test is to expose how the tool behaves under a large dataset.

## Habit I caught myself in

I caught myself wanting to just fix everything I noticed instead of deciding which problems actually mattered. The load test showed several imperfections, but I learned to separate a real break from a behavior I simply dislike and keep the scope focused.

## Tomorrow

Make the output usable at scale by adding a top-N option, a useful summary, and a more manageable way of displaying problem rows.