import argparse
import sys
from datetime import date, datetime

from .core import STALL_THRESHOLD_DAYS, find_stalled, load_board


def main(argv=None):
    parser = argparse.ArgumentParser(prog="stall_alerter", description="List stalled candidates to follow up first.")
    parser.add_argument("csv_path", help="Path to the hiring-board CSV")
    parser.add_argument("--today", help="Treat this date (YYYY-MM-DD) as today. Defaults to the real date.")
    parser.add_argument("--threshold", type=int, default=STALL_THRESHOLD_DAYS, help="Days in a stage before it counts as stalled")
    args = parser.parse_args(argv)

    today = datetime.strptime(args.today, "%Y-%m-%d").date() if args.today else date.today()

    try:
        candidates, problems = load_board(args.csv_path)
    except (OSError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    stalled = find_stalled(candidates, today, args.threshold)

    print(f"Stalled candidates as of {today} (more than {args.threshold} days in stage): {len(stalled)}\n")
    if stalled:
        print(f"{'#':>3}  {'Name':<22} {'Stage':<20} {'Days':>4}  Next action")
        print("-" * 100)
        for i, s in enumerate(stalled, 1):
            c = s.candidate
            print(f"{i:>3}  {c.name:<22} {c.stage:<20} {s.days_in_stage:>4}  {s.action}")

    future = [c for c in candidates if c.entered_stage_on > today]
    if problems or future:
        print(f"\nSkipped or suspicious rows: {len(problems) + len(future)}")
        for line_no, reason in problems:
            print(f"  line {line_no}: {reason}")
        for c in future:
            print(f"  {c.candidate_id} ({c.name}): stage date {c.entered_stage_on} is in the future")
    return 0


if __name__ == "__main__":
    sys.exit(main())
