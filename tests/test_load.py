from stall_alerter.core import load_board

HEADER = "candidate_id,name,role,stage,entered_stage_on,owner\n"


def write(tmp_path, text):
    path = tmp_path / "board.csv"
    path.write_text(text, encoding="utf-8")
    return path


def test_headers_with_spaces_and_capitals_are_accepted(tmp_path):
    path = write(tmp_path, " Candidate_ID,name , role,STAGE ,entered_stage_on, owner \nC-1,Ada,Eng,Offer,2026-10-01,john\n")
    candidates, problems = load_board(path)
    assert [c.candidate_id for c in candidates] == ["C-1"]
    assert problems == []


def test_line_numbers_stay_correct_after_blank_lines(tmp_path):
    text = HEADER + "C-1,Ada,Eng,Offer,2026-10-01,john\n\n\nC-2,Bola,Eng,Offer,01/10/2026,john\n"
    _, problems = load_board(write(tmp_path, text))
    assert problems == [(5, "bad date '01/10/2026' (expected YYYY-MM-DD)")]


def test_duplicate_line_numbers_are_real_file_lines(tmp_path):
    text = HEADER + "C-1,Ada,Eng,Offer,2026-10-01,john\n\nC-1,Bola,Eng,Offer,2026-10-02,john\n"
    _, problems = load_board(write(tmp_path, text))
    assert "lines 2, 4" in problems[0][1]


def test_big_board_loads(tmp_path):
    import subprocess, sys
    out = tmp_path / "big.csv"
    subprocess.run([sys.executable, "scripts/make_big_board.py", "10000", str(out)], check=True, capture_output=True)
    candidates, problems = load_board(out)
    assert len(candidates) > 8000
    assert problems
