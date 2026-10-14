# Intent: Stall Alerter

## What I'm building
A command-line tool that reads a CSV export of a hiring board. It finds candidates who have sat in one stage longer than a set number of days, and prints a ranked list: who to follow up with first, and what to do for each.

## Who it's for
A recruiter or hiring manager who has 50 to 5,000 candidates on a board and no time to scan every row. They should be able to run one command each morning and get a short, ordered to-do list.

## Input
A CSV with at least these columns:

| column | example |
|---|---|
| candidate_id | C-1042 |
| name | Ada Okafor |
| role | Backend Engineer |
| stage | Technical Interview |
| entered_stage_on | 2026-10-01 |
| owner | john |

Optional columns used if present: `last_contact_on`, `priority`, `source`.

## Output
A ranked table (and an optional CSV or JSON file) with:
- candidate, role, stage, owner
- days stalled
- a priority score
- one recommended next action, written in plain English (e.g. "Chase interviewer for feedback; candidate has waited 9 days after technical interview").

## Rules (first version)
- A candidate is "stalled" when days in their current stage exceed that stage's threshold. The default is 5 days, and each stage can override it in a config file.
- Ranking puts later stages first (an offer stalled for 6 days matters more than a screening stalled for 6 days), then more days over threshold.
- Closed stages (Hired, Rejected, Withdrawn) are ignored.

## Definition of done
- `python -m stall_alerter board.csv` prints a ranked list.
- Thresholds are configurable without code changes.
- Bad rows (missing dates, unknown stages) are reported, not silently dropped, and don't crash the run.
- Tests cover the stall rule, the ranking, and messy input.
- The README explains how to install, run and test it.

## How I intend to work (AI-first)
- I describe the behaviour and let the AI write the first draft of code and tests. I don't start from a blank file.
- I check every AI output by running it and reading the tests, and I record in the log what was wrong and how I re-prompted.
- I let the AI generate sample data, including deliberately messy rows.

## Habits I'm trying to drop
_Replace these with your own honest ones before submitting._
- Writing everything by hand before asking the AI.
- Building the "perfect" structure on day 1 instead of a working slice.
- Testing by eyeballing output instead of writing tests.
- Hiding what went wrong.

## How I'll raise the load
After a working first version, I'll make it harder in steps and log what breaks:
1. Per-stage thresholds and business days (skip weekends and holidays).
2. Messy real-world data: mixed date formats, blank cells, duplicate candidates, unknown stages.
3. Scale: 10,000+ rows, and timing it.
4. Smarter actions: generate the next-action text with an LLM, with a rule-based fallback when the API fails.

## Out of scope
- No web UI, no sending emails or messages, no live integration with an ATS.
