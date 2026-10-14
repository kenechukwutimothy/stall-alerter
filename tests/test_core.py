from datetime import date

from stall_alerter.core import Candidate, find_stalled, load_board, parse_row

TODAY = date(2026, 10, 14)


def cand(stage, entered, name="X"):
    return Candidate("C-1", name, "Engineer", stage, entered, "john")


def test_more_than_five_days_is_stalled():
    result = find_stalled([cand("Screening", date(2026, 10, 8))], TODAY)
    assert len(result) == 1
    assert result[0].days_in_stage == 6


def test_exactly_five_days_is_not_stalled():
    assert find_stalled([cand("Screening", date(2026, 10, 9))], TODAY) == []


def test_closed_stages_are_ignored():
    old = date(2026, 9, 1)
    cands = [cand("Hired", old), cand("Rejected", old), cand("Withdrawn", old)]
    assert find_stalled(cands, TODAY) == []


def test_later_stage_ranks_first_then_longest_wait():
    cands = [
        cand("Screening", date(2026, 9, 1), "old screen"),
        cand("Offer", date(2026, 10, 7), "recent offer"),
        cand("Offer", date(2026, 10, 1), "older offer"),
    ]
    names = [s.candidate.name for s in find_stalled(cands, TODAY)]
    assert names == ["older offer", "recent offer", "old screen"]


def test_bad_rows_are_reported_not_crashing():
    row = {"candidate_id": "C-9", "name": "A", "role": "R", "stage": "Offer", "entered_stage_on": "03/10/2026", "owner": "j"}
    cand_, reason = parse_row(row)
    assert cand_ is None
    assert "bad date" in reason

    row["entered_stage_on"] = "2026-10-01"
    row["stage"] = "Phone Scren"
    cand_, reason = parse_row(row)
    assert cand_ is None
    assert "unknown stage" in reason


def test_stage_names_are_trimmed_and_case_insensitive():
    row = {"candidate_id": "C-9", "name": "A", "role": "R", "stage": "  onsite interview ", "entered_stage_on": "2026-10-01", "owner": "j"}
    cand_, _ = parse_row(row)
    assert cand_.stage == "Onsite Interview"


def test_sample_board_loads():
    candidates, problems = load_board("data/board.csv")
    assert len(candidates) > 40
    assert len(problems) >= 4
