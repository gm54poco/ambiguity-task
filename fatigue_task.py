"""Five-point fatigue question administered before practice and after the main task.

Uses the same Likert-scale interface and confirm-with-SPACE interaction as
questions_task.ask_likert_question. Responses are saved independently so the
pre-task answer is retained even if the experiment is interrupted later.
"""

import json
from datetime import datetime, timezone

import urn_params as params
from questions_task import ask_likert_question

FATIGUE_QUESTION = "How tired do you feel right now?"
FATIGUE_LABELS = [
    "Not at all\ntired",
    "Slightly\ntired",
    "Moderately\ntired",
    "Very\ntired",
    "Extremely\ntired",
]


def ask_fatigue(win):
    """Return a confirmed integer 1–5; uses the existing Likert design."""
    return int(ask_likert_question(win, FATIGUE_QUESTION, FATIGUE_LABELS))


def save_fatigue_response(participant_id, stage, response, test_mode=False):
    """Store one of two fatigue ratings in data/<id>/fatigue.json.

    stage must be 'before_practice' or 'after_main'. A second write to the same
    stage is rejected to prevent accidental overwrites.
    """
    if stage not in ("before_practice", "after_main"):
        raise ValueError(f"Unknown fatigue stage: {stage}")
    if type(response) is not int or response not in range(1, 6):
        raise ValueError("Fatigue response must be an integer from 1 to 5")

    participant_id = str(participant_id)
    entry = {
        "response": response,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    if test_mode:
        print(f"TEST MODE — fatigue {stage} (not saved):", json.dumps(entry))
        return None

    folder = params.BASE_DIR / params.DATA_FOLDER / participant_id
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "fatigue.json"

    if path.exists():
        with path.open("r", encoding="utf-8") as handle:
            record = json.load(handle)
        if str(record.get("participant_id")) != participant_id:
            raise ValueError("Fatigue file has a different participant ID")
    else:
        if stage != "before_practice":
            raise ValueError("Cannot save post-task fatigue without pre-task record")
        record = {
            "participant_id": participant_id,
            "question": FATIGUE_QUESTION,
            "scale": {"min": 1, "max": 5, "labels": FATIGUE_LABELS},
            "before_practice": None,
            "after_main": None,
        }

    if record.get(stage) is not None:
        raise FileExistsError(f"Fatigue response for {stage} already exists")

    record[stage] = entry
    # Write and replace to avoid partial JSON if saving is interrupted.
    temp_path = path.with_suffix(".json.tmp")
    with temp_path.open("w", encoding="utf-8") as handle:
        json.dump(record, handle, ensure_ascii=False, indent=2)
    temp_path.replace(path)
    return path
