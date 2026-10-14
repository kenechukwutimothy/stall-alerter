# Day 1 Log

## What I prompted

```
Build a small Python command-line tool called Stall Alerter.

The tool should be run with:

python -m stall_alerter data/board.csv

It should read a CSV containing these columns:
candidate_id, name, role, stage, entered_stage_on, owner

A candidate should be considered stalled when they have been in their current stage for more than 5 days. Candidates whose stage is Hired, Rejected, or Withdrawn should be ignored.

The stalled candidates should be sorted by later hiring stages first, and then by the number of days they have been stalled, with the candidates stalled for the longest appearing first.

For each stalled candidate, print their name, current stage, number of days stalled, and one suggested next action.

Create a sample data/board.csv with about 50 rows, including a few deliberately messy records so that we can test how the tool handles imperfect data.

Also create a few basic pytest tests covering the core functionality.

Keep the scope small and focused. This is a working slice, not the final design.
```

## What came back

The AI produced a first working version of the Stall Alerter as a Python command-line tool. It reads the hiring-board CSV, identifies candidates who have been in their current stage for more than five days, sorts the results by stage and duration, and provides a suggested next action.

It also added a `--today` option so the sample data gives the same result whatever day it is run, and a `--threshold` option.

The sample board contains 51 rows. The tool identified 26 stalled candidates and reported 5 skipped or suspicious rows.

## What I checked

I created a virtual environment, installed pytest, and ran the test suite.

Result: 7 tests passed.

I also ran the command-line tool against the sample board using:

```
python -m stall_alerter data/board.csv --today 2026-10-14
```

The output showed 26 stalled candidates and 5 suspicious rows.

I confirmed that the suspicious rows included:
- missing entered_stage_on
- an ambiguous date format
- an unknown stage
- a missing candidate name
- a future stage date

I also checked that Mary Okoro, whose row had extra spaces and a lowercase stage name, was cleaned up and included correctly.

## What the AI got wrong

The AI listed these limitations itself when it handed over the code. I checked each one against the code and the output.

- **Duplicate candidate IDs are not detected.** I confirmed this in my own run: Joy Nwosu appears at #26 with ID C-1003, which another candidate also uses, and nothing flagged it.
- **"Days stalled" shows total days in the stage, not days beyond the five-day threshold.** My prompt was ambiguous here. I decided that total days in stage is more useful because it shows the actual length of inactivity, so I am keeping it.
- **The suggested action is fixed per stage.** It does not take the candidate's owner or the length of the wait into account.
- **Stage names are hard-coded.** A board that uses different stage names would have its records rejected as unknown stages.
- **Dates must be YYYY-MM-DD.** Other formats such as 03/10/2026 are rejected rather than interpreted.

## Habit I caught myself in

Before running the tests, I assumed I needed to install Django. That was habit from my usual projects. This tool only needs the Python standard library plus pytest.

## What I learned

The first implementation showed me that a working program can still have important limitations. Passing tests does not necessarily mean the tool is robust against messy real-world data.

I also learned that I need to be more explicit about ambiguous requirements when prompting AI. In particular, "days stalled" could mean total days in the stage or days beyond the five-day threshold.

I should not rely only on the AI's own list of what is wrong. Next time I want to find at least one problem myself before reading its summary.

## Next step

Improve the handling of the most important weaknesses while keeping the scope of the tool small. My priorities are duplicate detection and per-stage thresholds in a config file.
