# Day 2

## Goal for today

Improve the first working version by fixing the most important weaknesses found during Day 1 testing and making the stall rules configurable.

## What I prompted

### Prompt 1

Day 2 — I want to improve the Stall Alerter based on testing the first version.

I independently tested the CLI with:

python -m stall_alerter data/board.csv --today 15-10-2026

I found that an incorrectly formatted --today value causes an unhandled ValueError and Python traceback. This is inconsistent with the CSV validation, where a bad date is reported as a suspicious row and processing continues.

Fix this so an invalid --today value produces a clear user-facing error instead of a Python traceback. Add a test for this behavior.

I also want to fix the following Day 1 weaknesses:

1. Duplicate candidate IDs:
If multiple rows have the same candidate_id, do not silently treat them as separate candidates. Report the duplicate as a data-quality problem and exclude those duplicate records from the normal stalled-candidate results.

2. Per-stage thresholds:
Create a config.json file that allows different stall thresholds for different stages.

Use a default threshold of 5 days for any stage that is not explicitly configured.

If config.json is missing, the program should still work using the default 5-day threshold.

3. Better follow-up actions:
The suggested action should include the candidate's owner and the number of days they have been in the current stage.

For example:
"Owner john: chase interviewer for technical feedback; candidate has been waiting 19 days."

Keep the action appropriate to the candidate's stage.

4. Tests:
Add pytest tests covering:
- duplicate candidate IDs
- per-stage thresholds
- default threshold
- missing config.json
- improved follow-up actions
- invalid --today input
- the existing core behavior

Keep the existing command working:

python -m stall_alerter data/board.csv --today 2026-10-14

Keep the project small and focused. Do not add an LLM or business-day calculations yet.

Before changing the code, briefly explain your implementation approach. Then make the changes and run the tests.

### Prompt 2

I want to use Offer = 3, Onsite Interview = 5, Technical Interview = 7, Phone Interview = 5, Screening = 5, Applied = 5, with a default of 5. Update the config and any affected tests. Do not change the implementation logic.

## What the AI got wrong / what I changed

The AI initially chose the per-stage threshold values itself instead of asking me to choose them. I reviewed the values and decided to use:

- Offer: 3 days
- Onsite Interview: 5 days
- Technical Interview: 7 days
- Phone Interview: 5 days
- Screening: 5 days
- Applied: 5 days
- Default: 5 days

I then gave the AI a second prompt telling it to update the configuration and affected tests without changing the implementation logic.

The AI also decided that duplicate IDs should cause all copies to be excluded from the normal results. I accepted that behavior for now because the tool cannot reliably determine which duplicate record is correct.

## What broke

During testing, I found that:

- An invalid `--today` value such as `15-10-2026` originally caused a Python `ValueError` traceback instead of a clear user-facing error.
- Duplicate candidate ID `C-1003` appeared twice in the sample data.
- The original implementation used one global threshold, which was too blunt for different recruitment stages.
- The original follow-up actions did not identify the owner or how long the candidate had been waiting.

The invalid `--today` behavior was the problem I found through testing. The AI had suggested a list of edge-case experiments, and I ran them before writing the Day 2 prompt.

## Habit I caught myself in

I caught myself wanting to call every unexpected behavior a bug. Testing `--threshold 0` showed that the program was actually behaving correctly: it flagged every eligible candidate with more than zero days in their stage.

That helped me distinguish between a genuine bug and behavior that I simply did not like. The global threshold being too blunt supported the per-stage threshold feature that was already planned.

## Tomorrow

Raise the load by testing the Stall Alerter with a much larger and messier dataset, then record what actually breaks or becomes impractical before deciding what to fix.