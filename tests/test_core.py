import json
from datetime import date

import pytest

from stall_alerter.core import (
    Candidate,
    Config,
    ConfigError,
    find_stalled,
    load_board,
    load_config,
    parse_row,
    remove_duplicates,
    suggest_action,
)

TODAY = date(2026, 10, 14)


def cand(stage, entered, name="X", cid="C-1", owner="john", line_no=2):
    return Candidate(cid, name, "Engineer", stage, entered, owner, line_no)


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


# --- duplicates ---

def test_duplicate_ids_are_excluded_and_reported():
    cands = [
        cand("Offer", date(2026, 10, 1), "first", cid="C-7", line_no=3),
        cand("Screening", date(2026, 10, 1), "unique", cid="C-8", line_no=4),
        cand("Applied", date(2026, 9, 1), "second", cid="C-7", line_no=9),
    ]
    unique, problems = remove_duplicates(cands)
    assert [c.name for c in unique] == ["unique"]
    assert len(problems) == 1
    assert "C-7" in problems[0][1] and "3, 9" in problems[0][1]


def test_sample_board_reports_the_duplicate():
    candidates, problems = load_board("data/board.csv")
    assert "C-1003" not in {c.candidate_id for c in candidates}
    assert any("duplicate candidate_id C-1003" in reason for _, reason in problems)


# --- thresholds and config ---

def test_per_stage_threshold_applies():
    config = Config(default_threshold=5, stage_thresholds={"Offer": 2})
    three_days = date(2026, 10, 11)
    result = find_stalled([cand("Offer", three_days), cand("Screening", three_days)], TODAY, config)
    assert [s.candidate.stage for s in result] == ["Offer"]
    assert result[0].threshold == 2


def test_unconfigured_stage_uses_default():
    config = Config(default_threshold=5, stage_thresholds={"Offer": 2})
    assert config.threshold_for("Screening") == 5


def test_missing_config_file_uses_defaults(tmp_path):
    config, warnings = load_config(tmp_path / "nope.json")
    assert config.default_threshold == 5
    assert config.stage_thresholds == {}
    assert warnings == []


def test_config_file_is_read(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"default_threshold": 6, "stage_thresholds": {"offer": 1}}))
    config, _ = load_config(path)
    assert config.default_threshold == 6
    assert config.threshold_for("Offer") == 1


def test_unknown_stage_in_config_is_warned(tmp_path):
    path = tmp_path / "config.json"
    path.write_text(json.dumps({"stage_thresholds": {"Final Round": 3}}))
    config, warnings = load_config(path)
    assert config.stage_thresholds == {}
    assert "Final Round" in warnings[0]


def test_broken_config_raises_clear_error(tmp_path):
    path = tmp_path / "config.json"
    path.write_text("{not json")
    with pytest.raises(ConfigError, match="not valid JSON"):
        load_config(path)


# --- actions ---

def test_action_includes_owner_and_days():
    c = cand("Technical Interview", date(2026, 9, 25), owner="john")
    assert suggest_action(c, 19) == (
        "Owner john: chase interviewer for technical feedback; candidate has been waiting 19 days."
    )


def test_action_matches_stage():
    result = find_stalled([cand("Offer", date(2026, 10, 1), owner="amaka")], TODAY)
    assert result[0].action.startswith("Owner amaka: call the candidate")
    assert "13 days" in result[0].action
