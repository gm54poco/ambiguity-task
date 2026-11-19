"""Standalone post-urn question about predicting surprise balls.

Place next to main.py and urn_params.py. The original fatigue_task.py
remains separate. Uses the existing PsychoPy window and saves one JSON record.
"""

import json
from datetime import datetime, timezone

from psychopy import core, event, visual

import urn_params as params

SURPRISE_QUESTION = (
    "During the urn task, how often did you try to predict "
    "when a surprise ball would appear?"
)
FREQUENCY_LABELS = ("Never", "Rarely", "Sometimes", "Often", "Always")

# PsychoPy 'height' units: change these values to fine-tune the layout.
SCALE_X = (-0.40, -0.20, 0.00, 0.20, 0.40)
SCALE_Y = -0.06
NAVY = "#172b49"
BODY = "#334155"
MUTED = "#576a82"


def ask_surprise_frequency(win):
    """Return a confirmed 1-5 answer; SPACE is ignored until a number is chosen."""
    selected = None

    title_stim = visual.TextStim(
        win, text="About the urn task", pos=(0, 0.36),
        height=0.048, color=NAVY, bold=True,
    )
    question_stim = visual.TextStim(
        win, text=SURPRISE_QUESTION, pos=(0, 0.19),
        height=0.032, wrapWidth=1.25, color=BODY,
    )
    footer_stim = visual.TextStim(
        win, text="Press 1-5 to choose. Press SPACE to confirm.",
        pos=(0, -0.34), height=0.025, color=MUTED,
    )

    # Match the TAS-20/fatigue-style Likert scale: horizontal line, five
    # short ticks, and a narrow rectangular selection marker (no circles).
    line = visual.Line(
        win, start=(SCALE_X[0], SCALE_Y), end=(SCALE_X[-1], SCALE_Y),
        lineColor="black", lineWidth=2,
    )
    ticks = [
        visual.Line(
            win,
            start=(x, SCALE_Y - 0.055 / 2),
            end=(x, SCALE_Y + 0.055 / 2),
            lineColor="black", lineWidth=2,
        )
        for x in SCALE_X
    ]
    numbers = [
        visual.TextStim(
            win, text=str(index), pos=(x, SCALE_Y + 0.085),
            height=0.032, bold=True, color="black", font="Arial",
        )
        for index, x in enumerate(SCALE_X, start=1)
    ]
    labels = [
        visual.TextStim(
            win, text=label, pos=(x, -0.17),
            height=0.026, color="black", wrapWidth=0.16, font="Arial",
        )
        for x, label in zip(SCALE_X, FREQUENCY_LABELS)
    ]
    selection_marker = visual.Rect(
        win, width=0.025, height=0.075,
        pos=(0, SCALE_Y),
        fillColor="white", lineColor="black", lineWidth=2,
    )

    def draw():
        title_stim.draw()
        question_stim.draw()
        line.draw()
        for tick, number, label in zip(ticks, numbers, labels):
            tick.draw()
            number.draw()
            label.draw()
        if selected is not None:
            selection_marker.pos = (SCALE_X[selected - 1], SCALE_Y)
            selection_marker.draw()
        footer_stim.draw()
        win.flip()

    event.clearEvents()
    draw()

    allowed_keys = ["1", "2", "3", "4", "5", "num_1", "num_2",
                    "num_3", "num_4", "num_5", "space", "escape"]
    while True:
        key = event.waitKeys(keyList=allowed_keys)[0]
        if key == "escape":
            win.close()
            core.quit()
        if key in ("1", "2", "3", "4", "5", "num_1", "num_2",
                   "num_3", "num_4", "num_5"):
            selected = int(key.replace("num_", ""))
            draw()
        elif key == "space" and selected is not None:
            return selected


def save_surprise_frequency(participant_id, response, test_mode=False):
    """Write one answer to its own JSON file, or print it during a test run."""
    if response not in range(1, 6):
        raise ValueError("Surprise-frequency response must be 1 through 5")

    record = {
        "participant_id": str(participant_id),
        "question": SURPRISE_QUESTION,
        "response": response,
        "response_label": FREQUENCY_LABELS[response - 1],
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    if test_mode:
        print("TEST MODE - surprise-ball frequency:", json.dumps(record))
        return None

    directory = params.BASE_DIR / params.DATA_FOLDER / str(participant_id)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "surprise_prediction.json"
    with path.open("x", encoding="utf-8") as output:
        json.dump(record, output, indent=2, ensure_ascii=False)
    return path


def run_surprise_question(win, participant_id, test_mode=False):
    """Show the surprise question and save its answer; leave fatigue to main.py."""
    response = ask_surprise_frequency(win)
    save_surprise_frequency(participant_id, response, test_mode=test_mode)
    return response
