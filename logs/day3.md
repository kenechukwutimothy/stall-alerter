# Day 3 Log

## What I prompted

```
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
```

I deliberately asked the AI to report problems before fixing them, and to fix only real breaks. On Days 1 and 2 it reported and fixed in one go, so I couldn't see the "before" state.

## What came back

The AI wrote `scripts/make_big_board.py`, a reproducible generator (fixed random seed). It produced a 10,000-row board with spaced headers, mixed date formats, blank lines, empty rows, duplicate IDs and unknown stages.

## What broke

1. **Headers with spaces stopped the whole run.** A header like ` stage ` gave `Error: CSV is missing required columns`, and not a single row was processed.
2. **Line numbers were wrong after blank lines.** A duplicate was reported "on line 149" when it was really on line 151. Nothing crashed, it just gave a wrong answer without any warning.

The AI found the second bug only because it checked a reported line number against the real file. Tests and output alone would not have shown it.

## What was slow

Nothing. 10,000 rows run in about 0.2 seconds. Most of the time is spent parsing dates. Speed is not a problem at this size.

## What was fixed

- Header names are now trimmed and lowercased before the required-column check.
- Line numbers now come from the CSV reader's real line counter, so they match the file.
- New tests: spaced or capitalised headers, line numbers after blank lines, duplicate line numbers, and loading a 10,000-row board. 24 tests pass.

## What I checked

I regenerated the board on my machine with the script, ran `python -m pytest` (24 passed), and ran:

```
python -m stall_alerter data/big_board.csv --today 2026-10-14
```

The run completed and listed the problem rows at the end, for example `line 10038: unknown stage 'On hold'` and `line 10117: bad date 'Sep 15 2026'`.

The small board still gives the same result as on Day 2: 24 stalled candidates and 6 problem rows.

## What's still wrong (not fixed today, on purpose)

- **The output is too long to use.** 6,132 stalled candidates plus 729 problem rows comes to about 6,900 lines. No recruiter will read that.
- **About 5% of dates are rejected** (`14/10/2026`, `Oct 14 2026`). That's 467 candidates missing from the results. Rejecting `03/10` is deliberate because it's ambiguous, but `Oct 14 2026` isn't ambiguous and is still rejected.
- **The duplicate rule hides 92 real candidates at scale.** The Day 2 trade-off is much bigger than it looked on 51 rows.
- **Fully blank lines are skipped without a report.** Rows of empty commas are reported as "missing candidate_id".
- **The AI generated the data with dates spread over 45 days.** That partly explains why 61% of candidates show as stalled, so the number reflects the test data as much as the tool.
- The CSV file (650 KB) timed out when the AI copied it to my machine, so I regenerated it locally with the script.

## Decisions I made

[YOUR WORDS: which of the issues above you're taking into Day 4 and why. For example: "The output length is the most important. I'll add a --top N option and a summary per owner on Day 4. I'm leaving date formats as they are because guessing dd/mm vs mm/dd is riskier than rejecting."]

## Habit I caught myself in

[YOUR WORDS: one honest line. For example: wanting to just say "fix everything" instead of choosing; assuming 10,000 rows would be slow; feeling the urge to skip the log because I was tired.]
