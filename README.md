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
- `--threshold N` – days in a stage before it counts as stalled (default 5)

Example:

```
python -m stall_alerter data/board.csv --today 2026-10-14
```

## Test

```
python -m pytest
```
