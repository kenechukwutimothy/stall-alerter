import csv
import json
import os
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, datetime

DEFAULT_THRESHOLD_DAYS = 5

STAGE_ORDER = [
    "Applied",
    "Screening",
    "Phone Interview",
    "Technical Interview",
    "Onsite Interview",
    "Offer",
]

CLOSED_STAGES = {"Hired", "Rejected", "Withdrawn"}

ACTION_TEMPLATES = {
    "Applied": "review the application and decide whether to screen",
    "Screening": "finish the screen and send the candidate a yes or no",
    "Phone Interview": "book the phone interview or collect the interviewer's notes",
    "Technical Interview": "chase interviewer for technical feedback",
    "Onsite Interview": "hold the debrief and make a hire or no-hire decision",
    "Offer": "call the candidate to close or revise the offer",
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
    line_no: int = 0


@dataclass
class Stalled:
    candidate: Candidate
    days_in_stage: int
    threshold: int
    action: str


@dataclass
class Config:
    default_threshold: int = DEFAULT_THRESHOLD_DAYS
    stage_thresholds: dict = field(default_factory=dict)

    def threshold_for(self, stage):
        return self.stage_thresholds.get(stage, self.default_threshold)


class ConfigError(Exception):
    pass


def normalise_stage(raw):
    return _STAGE_LOOKUP.get((raw or "").strip().lower())


def load_config(path):
    """Return (Config, warnings). A missing file gives the defaults; a broken file raises ConfigError."""
    if not os.path.exists(path):
        return Config(), []
    try:
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
    except json.JSONDecodeError as e:
        raise ConfigError(f"{path} is not valid JSON ({e.msg} at line {e.lineno})")

    warnings = []
    default = raw.get("default_threshold", DEFAULT_THRESHOLD_DAYS)
    if not isinstance(default, int) or default < 0:
        raise ConfigError(f"default_threshold in {path} must be a whole number of 0 or more")

    thresholds = {}
    for name, days in (raw.get("stage_thresholds") or {}).items():
        stage = normalise_stage(name)
        if stage is None or stage in CLOSED_STAGES:
            warnings.append(f"config: ignoring threshold for unknown or closed stage '{name}'")
            continue
        if not isinstance(days, int) or days < 0:
            raise ConfigError(f"threshold for '{name}' in {path} must be a whole number of 0 or more")
        thresholds[stage] = days
    return Config(default, thresholds), warnings


def parse_row(row, line_no=0):
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
        line_no=line_no,
    ), None


def remove_duplicates(candidates):
    """Drop every candidate whose ID appears more than once. Return (unique, problems)."""
    by_id = defaultdict(list)
    for c in candidates:
        by_id[c.candidate_id].append(c)
    unique, problems = [], []
    for c in candidates:
        group = by_id[c.candidate_id]
        if len(group) == 1:
            unique.append(c)
        elif c is group[0]:
            lines = ", ".join(str(g.line_no) for g in group)
            problems.append((group[0].line_no, f"duplicate candidate_id {c.candidate_id} on lines {lines}; all copies excluded"))
    return unique, problems


def load_board(path):
    """Read the CSV. Return (candidates, problems) where problems is a list of (line_no, reason)."""
    candidates, problems = [], []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or [])]
        if missing:
            raise ValueError(f"CSV is missing required columns: {', '.join(missing)}")
        for line_no, row in enumerate(reader, start=2):
            cand, reason = parse_row(row, line_no)
            if cand:
                candidates.append(cand)
            else:
                problems.append((line_no, reason))
    candidates, dup_problems = remove_duplicates(candidates)
    problems = sorted(problems + dup_problems)
    return candidates, problems


def suggest_action(candidate, days):
    return f"Owner {candidate.owner}: {ACTION_TEMPLATES[candidate.stage]}; candidate has been waiting {days} days."


def find_stalled(candidates, today, config=None):
    config = config or Config()
    stalled = []
    for c in candidates:
        if c.stage in CLOSED_STAGES:
            continue
        days = (today - c.entered_stage_on).days
        limit = config.threshold_for(c.stage)
        if days > limit:
            stalled.append(Stalled(c, days, limit, suggest_action(c, days)))
    stalled.sort(key=lambda s: (-STAGE_ORDER.index(s.candidate.stage), -s.days_in_stage))
    return stalled
