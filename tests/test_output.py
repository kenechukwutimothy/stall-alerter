from datetime import date

import pytest

from stall_alerter.__main__ import main
from stall_alerter.core import Candidate, Stalled, problem_type, summarise

ARGS = ["data/board.csv", "--today", "2026-10-14"]


def run(capsys, *extra):
    assert main(ARGS + list(extra)) == 0
    return capsys.readouterr().out


def table_rows(out):
    return [l for l in out.splitlines() if l[:3].strip().isdigit() and "Owner " in l]


def test_top_limits_printed_rows(capsys):
    out = run(capsys, "--top", "5")
    assert len(table_rows(out)) == 5
    assert "top 5 of 24" in out


def test_default_top_is_20(capsys):
    assert len(table_rows(run(capsys))) == 20


def test_top_zero_shows_all(capsys):
    out = run(capsys, "--top", "0")
    assert len(table_rows(out)) == 24
    assert "Most urgent (all)" in out


def test_top_keeps_most_urgent_first(capsys):
    top1 = table_rows(run(capsys, "--top", "1"))[0]
    everyone = table_rows(run(capsys, "--top", "0"))[0]
    assert top1 == everyone


def test_summary_counts_cover_all_stalled_not_just_top(capsys):
    out = run(capsys, "--top", "1")
    by_stage = next(l for l in out.splitlines() if "By stage:" in l)
    total = sum(int(part.rsplit(" ", 1)[1]) for part in by_stage.split(": ", 1)[1].split(", "))
    assert total == 24


def test_summarise_orders_stages_and_owners():
    c = lambda stage, owner: Stalled(Candidate("C", "N", "R", stage, date(2026, 1, 1), owner), 9, 5, "")
    per_stage, per_owner = summarise([c("Screening", "amy"), c("Offer", "bob"), c("Offer", "amy")])
    assert list(per_stage.items()) == [("Offer", 2), ("Screening", 1)]
    assert list(per_owner.items()) == [("amy", 2), ("bob", 1)]


def test_problems_are_collapsed_into_counts(capsys):
    out = run(capsys)
    assert "1 duplicate IDs" in out
    assert "1 bad dates" in out
    assert "1 future dates" in out
    assert "line 47:" not in out
    assert "--show-problems" in out


def test_show_problems_lists_every_row(capsys):
    out = run(capsys, "--show-problems")
    assert "line 47: bad date '03/10/2026'" in out
    assert "line 51: future date" in out


@pytest.mark.parametrize("reason,label", [
    ("bad date 'x'", "bad dates"),
    ("unknown stage 'x'", "unknown stages"),
    ("missing name", "missing fields"),
    ("duplicate candidate_id C-1 on lines 2, 3; all copies excluded", "duplicate IDs"),
    ("something new", "other"),
])
def test_problem_type(reason, label):
    assert problem_type(reason) == label


@pytest.mark.parametrize("flag", ["--threshold", "--top"])
def test_negative_numbers_give_clear_error(flag, capsys):
    with pytest.raises(SystemExit) as exc:
        main(ARGS + [flag, "-3"])
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "'-3' must be 0 or more" in err
    assert "Traceback" not in err
