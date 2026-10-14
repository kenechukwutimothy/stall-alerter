import csv
from dataclasses import dataclass
from datetime import date, datetime

STALL_THRESHOLD_DAYS = 5

STAGE_ORDER = [
    "Applied",
    "Screening",
    "Phone Interview",
    "Technical Interview",
    "Onsite Interview",
    "Offer",
]

CLOSED_STAGES = {"Hired", "Rejected", "Withdrawn"}

ACTIONS = {
    "Applied": "Review the application and decide whether to screen.",
    "Screening": "Finish the screen and send the candidate a yes or no.",
    "Phone Interview": "Book the phone interview or collect the interviewer's notes.",
    "Technical Interview": "Chase the interviewer for technical feedback.",
    "Onsite Interview": "Hold the debrief and make a hire or no-hire decision.",
    "Offer": "Call the candidate today to close or revise the offer.",
}

REQUIRED_COLUMNS = ["candidate_id", "name", "role", "stage", "entered_stage_on", "owner"]

_STAGE_LOOKUP = {s.lower(): s for s in STAGE_ORDER + sorted(CLOSED_STAGES)}


@dataclass
class Candidate:
    candidate_id: str
    name: str
    role: str
    stage: str
    entered_stage_on: date
    owner: str


@dataclass
class Stalled:
    candidate: Candidate
    days_in_stage: int
    action: str


def normalise_stage(raw):
    return _STAGE_LOOKUP.get((raw or "").strip().lower())


def parse_row(row):
    """Return (Candidate, None) or (None, reason)."""
    for col in REQUIRED_COLUMNS:
        if not (row.get(col) or "").strip():
            return None, f"missing {col}"
    stage = normalise_stage(row["stage"])
    if stage is None:
        return None, f"unknown stage '{row['stage'].strip()}'"
    try:
        entered = datetime.strptime(row["entered_stage_on"].strip(), "%Y-%m-%d").date()
    except ValueError:
        return None, f"bad date '{row['entered_stage_on'].strip()}' (expected YYYY-MM-DD)"
    return Candidate(
        candidate_id=row["candidate_id"].strip(),
        name=row["name"].strip(),
        role=row["role"].strip(),
        stage=stage,
        entered_stage_on=entered,
        owner=row["owner"].strip(),
    ), None


def load_board(path):
    """Read the CSV. Return (candidates, problems) where problems is a list of (line_no, reason)."""
    candidates, problems = [], []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"CSV is missing required columns: {', '.join(missing)}")
        for line_no, row in enumerate(reader, start=2):
            cand, reason = parse_row(row)
            if cand:
                candidates.append(cand)
            else:
                problems.append((line_no, reason))
    return candidates, problems


def find_stalled(candidates, today, threshold=STALL_THRESHOLD_DAYS):
    stalled = []
    for c in candidates:
        if c.stage in CLOSED_STAGES:
            continue
        days = (today - c.entered_stage_on).days
        if days > threshold:
            stalled.append(Stalled(c, days, ACTIONS[c.stage]))
    stalled.sort(key=lambda s: (-STAGE_ORDER.index(s.candidate.stage), -s.days_in_stage))
    return stalled
