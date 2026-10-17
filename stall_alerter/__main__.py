import argparse
import sys
from collections import Counter
from dataclasses import replace
from datetime import date, datetime

from .core import ConfigError, find_stalled, load_board, load_config, problem_type, summarise

DEFAULT_TOP = 20


def iso_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a valid date; use YYYY-MM-DD, e.g. 2026-10-14")


def non_negative_int(value):
    try:
        n = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{value}' is not a whole number")
    if n < 0:
        raise argparse.ArgumentTypeError(f"'{value}' must be 0 or more")
    return n


def main(argv=None):
    parser = argparse.ArgumentParser(prog="stall_alerter", description="List stalled candidates to follow up first.")
    parser.add_argument("csv_path", help="Path to the hiring-board CSV")
    parser.add_argument("--today", type=iso_date, help="Treat this date (YYYY-MM-DD) as today. Defaults to the real date.")
    parser.add_argument("--config", default="config.json", help="Path to the thresholds config (default: config.json)")
    parser.add_argument("--threshold", type=non_negative_int, help="Override the default threshold for stages not set in the config")
    parser.add_argument("--top", type=non_negative_int, default=DEFAULT_TOP, help=f"Print only the N most urgent candidates (default {DEFAULT_TOP}; 0 = all)")
    parser.add_argument("--show-problems", action="store_true", help="List every skipped or suspicious row instead of counts")
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
    problems = problems + [
        (c.line_no, f"future date: {c.candidate_id} ({c.name}) stage date {c.entered_stage_on} is in the future")
        for c in candidates
        if c.entered_stage_on > today
    ]
    problems.sort()

    print(f"Stalled candidates as of {today}: {len(stalled)}")
    if stalled:
        per_stage, per_owner = summarise(stalled)
        print("  By stage: " + ", ".join(f"{k} {v}" for k, v in per_stage.items()))
        print("  By owner: " + ", ".join(f"{k} {v}" for k, v in per_owner.items()))

        shown = stalled if args.top == 0 else stalled[: args.top]
        label = "all" if len(shown) == len(stalled) else f"top {len(shown)} of {len(stalled)}"
        print(f"\nMost urgent ({label}):")
        print(f"{'#':>3}  {'Name':<22} {'Stage':<20} {'Days':>4} {'Limit':>5}  Next action")
        print("-" * 120)
        for i, s in enumerate(shown, 1):
            c = s.candidate
            print(f"{i:>3}  {c.name:<22} {c.stage:<20} {s.days_in_stage:>4} {s.threshold:>5}  {s.action}")

    if problems:
        print(f"\nSkipped or suspicious rows: {len(problems)}")
        if args.show_problems:
            for line_no, reason in problems:
                print(f"  line {line_no}: {reason}")
        else:
            for label, n in Counter(problem_type(r) for _, r in problems).most_common():
                print(f"  {n} {label}")
            print("  (use --show-problems to list them all)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
