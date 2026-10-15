import argparse
import sys
from dataclasses import replace
from datetime import date, datetime

from .core import ConfigError, find_stalled, load_board, load_config


def iso_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid date; use YYYY-MM-DD, e.g. 2026-10-14")


def main(argv=None):
    parser = argparse.ArgumentParser(prog="stall_alerter", description="List stalled candidates to follow up first.")
    parser.add_argument("csv_path", help="Path to the hiring-board CSV")
    parser.add_argument("--today", type=iso_date, help="Treat this date (YYYY-MM-DD) as today. Defaults to the real date.")
    parser.add_argument("--config", default="config.json", help="Path to the thresholds config (default: config.json)")
    parser.add_argument("--threshold", type=int, help="Override the default threshold for stages not set in the config")
    args = parser.parse_args(argv)

    today = args.today or date.today()

    try:
        config, warnings = load_config(args.config)
        if args.threshold is not None:
            config = replace(config, default_threshold=args.threshold)
        candidates, problems = load_board(args.csv_path)
    except (OSError, ValueError, ConfigError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    for w in warnings:
        print(f"Warning: {w}", file=sys.stderr)

    stalled = find_stalled(candidates, today, config)

    print(f"Stalled candidates as of {today}: {len(stalled)}\n")
    if stalled:
        print(f"{'#':>3}  {'Name':<22} {'Stage':<20} {'Days':>4} {'Limit':>5}  Next action")
        print("-" * 120)
        for i, s in enumerate(stalled, 1):
            c = s.candidate
            print(f"{i:>3}  {c.name:<22} {c.stage:<20} {s.days_in_stage:>4} {s.threshold:>5}  {s.action}")

    future = [c for c in candidates if c.entered_stage_on > today]
    if problems or future:
        print(f"\nSkipped or suspicious rows: {len(problems) + len(future)}")
        for line_no, reason in problems:
            print(f"  line {line_no}: {reason}")
        for c in future:
            print(f"  line {c.line_no}: {c.candidate_id} ({c.name}) stage date {c.entered_stage_on} is in the future")
    return 0


if __name__ == "__main__":
    sys.exit(main())
