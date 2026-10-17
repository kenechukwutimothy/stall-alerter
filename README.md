# Stall Alerter

Reads a hiring-board CSV and lists stalled candidates to follow up first.

## Install

Requires Python 3.10+.

```
pip install pytest
```

## Run

```
python -m stall_alerter data/board.csv
```

Options:

- `--today YYYY-MM-DD` – treat this date as today (useful because the sample data is dated around 14 Oct 2026)
- `--config PATH` – thresholds file (default `config.json`)
- `--threshold N` – override the default threshold for stages not listed in the config (must be 0 or more)
- `--top N` – print only the N most urgent candidates (default 20; `0` prints all)
- `--show-problems` – list every skipped or suspicious row instead of a count per type

Example:

```
python -m stall_alerter data/board.csv --today 2026-10-14
```

## Output

1. A summary: total stalled, then counts per stage and per owner (always over all stalled candidates, not just the ones printed).
2. The most urgent candidates (top 20 by default), later stages first, then longest wait.
3. A count of skipped or suspicious rows by type.

## Configuration

`config.json` sets how many days each stage may take before a candidate counts as stalled:

```json
{
  "default_threshold": 5,
  "stage_thresholds": {
    "Applied": 5,
    "Screening": 5,
    "Phone Interview": 5,
    "Technical Interview": 7,
    "Onsite Interview": 5,
    "Offer": 3
  }
}
```

- Stages not listed use `default_threshold`.
- If `config.json` is missing, every stage uses 5 days.
- If it is not valid JSON, the tool stops with an error rather than guessing.

## Data problems

Rows with missing fields, bad dates, unknown stages or future dates are skipped. By default the output shows a count per problem type; add `--show-problems` to list each row with its line number.
If two or more rows share a `candidate_id`, all of them are excluded and reported, because the tool cannot tell which one is correct.

## Load testing

`data/big_board.csv` is a 10,000-row messy board for load testing. Regenerate it with:

```
python scripts/make_big_board.py 10000 data/big_board.csv
```

## Test

```
python -m pytest
```
