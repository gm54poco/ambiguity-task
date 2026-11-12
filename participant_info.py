"""Collect and save participant demographics before the urn experiment."""

import csv
from pathlib import Path
from psychopy import gui, core

DATA_DIR = Path(__file__).resolve().parent / "data"
PARTICIPANTS_FILE = DATA_DIR / "participants.csv"


def collect_participant_info():
    """Display a PsychoPy form and return participant information."""
    dialog = gui.Dlg(title="Participant Information")
    dialog.addText("Please enter your participant information.")
    dialog.addField("Participant ID:", "")
    dialog.addField("Age:", "")
    dialog.addField("Field of study:", "")
    dialog.addField("Test run (print only, save no files):", False)
    responses = dialog.show()

    if not dialog.OK:
        core.quit()

    if isinstance(responses, dict):
        values = list(responses.values())
    else:
        values = list(responses)

    participant_id, age_text, field_of_study = (
        str(x).strip() for x in values[:3]
    )
    raw_test_value = values[3]
    test_run = (raw_test_value if isinstance(raw_test_value, bool)
                else str(raw_test_value).strip().lower() in {"true", "yes", "1", "on"})
    if not participant_id.isdigit():
        raise ValueError("Participant ID must be a number.")
    if not age_text.isdigit() or not (1 <= int(age_text) <= 120):
        raise ValueError("Age must be a whole number between 1 and 120.")
    if not field_of_study:
        raise ValueError("Field of study cannot be empty.")

    return {
        "participant_id": participant_id,
        "age": int(age_text),
        "field_of_study": field_of_study,
        "test_run": test_run,
    }


def save_participant_info(info):
    """Append participant information without overwriting previous records."""
    if info.get("test_run", False):
        print("TEST MODE: participant information not saved:", info)
        return
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if PARTICIPANTS_FILE.exists():
        with PARTICIPANTS_FILE.open("r", newline="", encoding="utf-8") as file:
            if any(row["participant_id"] == info["participant_id"]
                   for row in csv.DictReader(file)):
                raise ValueError(f"Participant ID {info['participant_id']} already exists.")

    is_new = not PARTICIPANTS_FILE.exists() or PARTICIPANTS_FILE.stat().st_size == 0
    with PARTICIPANTS_FILE.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["participant_id", "age", "field_of_study"])
        if is_new:
            writer.writeheader()
        writer.writerow({key: info[key] for key in
                         ("participant_id", "age", "field_of_study")})


if __name__ == "__main__":
    participant = collect_participant_info()
    save_participant_info(participant)
    print(participant)
