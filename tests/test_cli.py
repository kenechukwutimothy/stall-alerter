import pytest

from stall_alerter.__main__ import main


def test_invalid_today_gives_clear_error_not_traceback(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["data/board.csv", "--today", "15-10-2026"])
    assert exc.value.code == 2
    err = capsys.readouterr().err
    assert "'15-10-2026' is not a valid date" in err
    assert "Traceback" not in err


def test_existing_command_still_works(capsys):
    assert main(["data/board.csv", "--today", "2026-10-14"]) == 0
    out = capsys.readouterr().out
    assert "Stalled candidates as of 2026-10-14" in out
    assert "duplicate candidate_id C-1003" in out


def test_runs_without_config_file(tmp_path, capsys):
    assert main(["data/board.csv", "--today", "2026-10-14", "--config", str(tmp_path / "missing.json")]) == 0


def test_missing_csv_is_reported(capsys):
    assert main(["data/nothing.csv"]) == 1
    assert "Error:" in capsys.readouterr().err
