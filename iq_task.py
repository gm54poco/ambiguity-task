"""Short matrix-reasoning task for PsychoPy.

Put this file in your Experiment folder, alongside assets/.
Required images: assets/IQ_test/stimuli/Pract1.png, Pract1_sol.png,
Pract2.png, Pract2_sol.png, and the twelve numbered question PNGs.

Participants select with NUMPAD 1-8 (Num Lock on) or number-row 1-8,
then press SPACE to confirm. A translucent brown rectangle marks their selection.
ESC quits, preserving completed responses. No answers are revealed in real trials.
"""
from __future__ import annotations

import csv
import re
from datetime import datetime
from pathlib import Path
import urn_params as params

from psychopy import core, event, gui, visual

ROOT = Path(__file__).resolve().parent
STIMULI_DIR = ROOT / "assets" / "IQ_test" / "stimuli"
OUTPUT_DIR = ROOT / "data" / "IQ_test"
QUESTION_NUMBERS = [1, 4, 8, 11, 15, 18, 21, 23, 25, 30, 31, 35]
PRACTICE_IDS = [1, 2]
FULLSCREEN = True     # Set False when testing on your computer.
WINDOW_SIZE = (1280, 800)
BACKGROUND = "#f5f5f2"
TEXT_COLOR = "#23312b"
GREEN = "#168c55"
SELECTION_BROWN = "#a77a4f"
SELECTION_BORDER = "#86562e"

# ================================================================
# VISUAL SETTINGS — adjust PRACTICE and MAIN independently.
# PsychoPy uses "height" units: screen height = 1.0.
# IMAGE_SCALE multiplies the automatically fitted image size.
# IMAGE_POS moves the image (x, y); positive y means upwards.
# All box coordinates below are fractions of the displayed image:
# x = 0 is its LEFT edge, x = 1 is its RIGHT edge;
# y = 0 is its TOP edge,  y = 1 is its BOTTOM edge.
# Numbers 1-4 use the first row; numbers 5-8 the second row.
# Box width/height are fractions of the IMAGE width/height.
# BOX_OFFSET shifts every box in SCREEN height units (x, y).
# ================================================================
PRACTICE_VISUAL = {
    "IMAGE_SCALE": 0.85,
    "IMAGE_POS": (0.0, -0.015),
    "OPTION_CENTERS_X": [0.204, 0.395, 0.585, 0.77],
    "OPTION_CENTERS_Y": [0.700, 0.906],
    "OPTION_BOX_W": 0.171,
    "OPTION_BOX_H": 0.164,
    "BOX_OFFSET": (0.015, 0.0),
}

MAIN_VISUAL = {
    "IMAGE_SCALE": 1.52,
    "IMAGE_POS": (0.0, -0.15),
    # Horizontal positions (columns 1–4)
    "OPTION_CENTERS_X": [0.204, 0.395, 0.585, 0.77],
    # Vertical positions (top row, bottom row)
    "OPTION_CENTERS_Y": [0.544, 0.665],
    # Brown selection box dimensions
    "OPTION_BOX_W": 0.171,
    "OPTION_BOX_H": 0.082,
    # Fine adjustments
    "BOX_OFFSET": (0.03, 0.0),
}

# Leave blank unless you have an authorized, verified scoring key.
# Example: ANSWER_KEY = {1: 3, 4: 2, ...}
# Answer key: item number -> correct alternative
ANSWER_KEY = {
    1: 5,
    4: 4,
    8: 1,
    11: 5,
    15: 2,
    18: 7,
    21: 8,
    23: 6,
    25: 7,
    30: 5,
    31: 4,
    35: 3,
}


def find_question_image(number):
    """Support e.g. 1.png, Q1.png, Question1.png, Item1.png, APM1.png."""
    candidates = [
        f"{number}.png", f"Q{number}.png", f"q{number}.png",
        f"Question{number}.png", f"question{number}.png",
        f"Item{number}.png", f"item{number}.png",
        f"APM{number}.png", f"RAPM{number}.png",
    ]
    for name in candidates:
        candidate = STIMULI_DIR / name
        if candidate.is_file():
            return candidate
    # Also accepts simple variants such as 'Question_01.png'.
    for candidate in STIMULI_DIR.glob("*.png"):
        stem = candidate.stem.lower()
        if "sol" in stem or "pract" in stem:
            continue
        found = re.search(r"(\d+)$", stem)
        if found and int(found.group(1)) == number:
            return candidate
    return None


def file_check():
    required = [STIMULI_DIR / f"Pract{k}{suffix}.png"
                for k in PRACTICE_IDS for suffix in ("", "_sol")]
    missing = [str(p) for p in required if not p.is_file()]
    question_paths = {}
    for q in QUESTION_NUMBERS:
        path = find_question_image(q)
        if path is None:
            missing.append(f"Question {q} (e.g. {q}.png)")
        else:
            question_paths[q] = path
    if missing:
        raise FileNotFoundError(
            "Some IQ task images are missing from:\n" + str(STIMULI_DIR)
            + "\n\nMissing:\n" + "\n".join(missing)
        )
    return question_paths


def make_text(win, message, y=0.0, height=0.031, width=1.35, color=TEXT_COLOR):
    return visual.TextStim(
        win, text=message, pos=(0, y), height=height,
        color=color, wrapWidth=width, alignText="center", units="height"
    )


def quit_if_esc(keys):
    if "escape" in keys:
        raise KeyboardInterrupt


def image_stim(win, path, visual_settings):
    # PsychoPy's ImageStim can load transparent PNGs; fill behind with off-white.
    img = visual.ImageStim(win, image=str(path), units="height", interpolate=True)
    # In 'height' units: screen height=1; x span=screen aspect ratio.
    natural_width, natural_height = img._origSize
    scale = min(0.95 / natural_height,
                (win.size[0] / win.size[1] * 0.94) / natural_width)
    scale *= visual_settings["IMAGE_SCALE"]
    img.size = (natural_width * scale, natural_height * scale)
    img.pos = visual_settings["IMAGE_POS"]
    return img


def screen(win, heading, message, footer="Press SPACE to continue"):
    event.clearEvents(eventType="keyboard")
    while True:
        make_text(win, heading, y=0.24 if heading == "Find the missing piece" else 0.18, height=params.TITLE_HEIGHT, color=GREEN).draw()
        make_text(win, message, y=0.015, height=params.BODY_HEIGHT, width=1.36).draw()
        make_text(win, footer, y=-0.30, height=0.026).draw()
        win.flip()
        keys = event.getKeys()
        quit_if_esc(keys)
        if "space" in keys:
            return
        core.wait(0.01)


def parse_choice(key):
    """Different PsychoPy backends use different numeric keypad names."""
    if key in list("12345678"):
        return int(key)
    key = key.lower()
    m = re.fullmatch(r"(?:num_|num|numpad|kp_|kp)([1-8])", key)
    return int(m.group(1)) if m else None


def selected_option_box(win, img, answer, visual_settings):
    """Highlight a numbered option on the composite question image."""
    column = (answer - 1) % 4
    row = (answer - 1) // 4
    x = (img.pos[0]
         + (visual_settings["OPTION_CENTERS_X"][column] - 0.5) * img.size[0]
         + visual_settings["BOX_OFFSET"][0])
    y = (img.pos[1]
         + (0.5 - visual_settings["OPTION_CENTERS_Y"][row]) * img.size[1]
         + visual_settings["BOX_OFFSET"][1])
    return visual.Rect(
        win, units="height", pos=(x, y),
        size=(visual_settings["OPTION_BOX_W"] * img.size[0],
              visual_settings["OPTION_BOX_H"] * img.size[1]),
        fillColor=SELECTION_BROWN, lineColor=SELECTION_BORDER,
        opacity=0.30, lineWidth=4,
    )


def ask_matrix(win, image_path, heading, practice=False):
    """Select 1-8; show highlight; SPACE confirms; return selection + confirm RT."""
    visual_settings = PRACTICE_VISUAL if practice else MAIN_VISUAL
    img = image_stim(win, image_path, visual_settings)
    selected = None
    selection_rt = None
    event.clearEvents(eventType="keyboard")
    clock = core.Clock()
    first_frame = True

    while True:
        make_text(win, heading, y=0.463, height=0.032, color=GREEN).draw()
        img.draw()
        if selected is not None:
            selected_option_box(win, img, selected, visual_settings).draw()
            footer = "Press SPACE to confirm · Press another number to change"
        else:
            footer = "Press 1–8 to select an answer."
        make_text(win, footer, y=-0.463, height=0.023).draw()
        if first_frame:
            win.callOnFlip(clock.reset)
            first_frame = False
        win.flip()

        for key, response_time in event.getKeys(timeStamped=clock):
            if key == "escape":
                raise KeyboardInterrupt
            answer = parse_choice(key)
            if answer is not None:
                selected = answer
                selection_rt = response_time
            elif key == "space" and selected is not None:
                return selected, round(selection_rt, 4), round(response_time, 4)
        core.wait(0.005)


def show_solution(win, solution_path, answer, practice_number):
    img = image_stim(win, solution_path, PRACTICE_VISUAL)
    event.clearEvents(eventType="keyboard")
    while True:
        make_text(win, f"Practice {practice_number}: solution", y=0.463,
                  height=0.032, color=GREEN).draw()
        img.draw()
        make_text(win, f"Your answer: {answer}    |    Correct option is highlighted in green.",
                  y=-0.427, height=0.023).draw()
        make_text(win, "Press SPACE to continue", y=-0.472, height=0.023).draw()
        win.flip()
        keys = event.getKeys()
        quit_if_esc(keys)
        if "space" in keys:
            return
        core.wait(0.01)


# Fields are stable across practice and the twelve scored questions.
IQ_CSV_FIELDS = [
    "participant_id", "started", "phase", "trial", "item",
    "response", "reaction_time_s", "confirmation_time_s", "correct"
]


def run_iq_task(win=None, participant=None, test_mode=False):
    """Run IQ task inside main.py, or stand-alone with its own PsychoPy window.

    Reuses the existing window when provided; never closes an external window.
    Writes completed responses after every question in non-test mode.
    Returns a summary dict. Escape raises KeyboardInterrupt to the caller.
    """
    questions = file_check()
    if participant is None:
        dialog = gui.Dlg(title="Matrix reasoning task")
        dialog.addField("Participant ID:", "TEST")
        dialog.addField("Test mode (do not save CSV):", bool(test_mode))
        inputs = dialog.show()
        if not dialog.OK:
            return None
        participant_id = str(inputs[0]).strip()
        test_mode = bool(inputs[1])
    else:
        participant_id = str(participant["participant_id"])
        # Respect the experiment's test mode, regardless of the IQ default.
        test_mode = bool(test_mode or participant.get("test_run", False))

    if not participant_id or not re.fullmatch(r"[A-Za-z0-9_-]+", participant_id):
        raise ValueError("Participant ID must use letters, digits, hyphens or underscores only.")

    started = datetime.now().isoformat(timespec="seconds")
    rows = []
    owns_window = win is None
    if owns_window:
        win = visual.Window(
            size=WINDOW_SIZE, fullscr=FULLSCREEN, color=BACKGROUND,
            colorSpace="hex", units="height", allowGUI=False,
            gammaErrorPolicy="warn",
        )

    # In integrated mode: data/<participant_id>/IQ_....csv
    # The filename includes a timestamp and must not overwrite earlier sessions.
    output_file = None
    if not test_mode:
        output_dir = ROOT / "data" / participant_id
        output_dir.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        output_file = output_dir / f"IQ_{participant_id}_{stamp}.csv"
        with output_file.open("x", newline="", encoding="utf-8-sig") as file:
            csv.DictWriter(file, fieldnames=IQ_CSV_FIELDS).writeheader()

    def record(row):
        rows.append(row)
        if test_mode:
            print("TEST MODE — IQ response:", row)
        else:
            with output_file.open("a", newline="", encoding="utf-8-sig") as file:
                csv.DictWriter(file, fieldnames=IQ_CSV_FIELDS).writerow(row)

    previous_mouse_visible = win.mouseVisible
    try:
        win.mouseVisible = False
        screen(
            win,
            "Find the missing piece",
            "\n\nYou will see pictures with a missing piece.\n\n"
            "For each picture, choose the piece that fits best "
            "in the empty space.\n\n"
            "Press a number (1-8) to choose your answer.\n"
            "Press SPACE to confirm your choice and move to the next question.\n\n"
            "You will start with 2 practice questions."
        )

        for practice_number in PRACTICE_IDS:
            answer, rt, confirm_rt = ask_matrix(
                win, STIMULI_DIR / f"Pract{practice_number}.png",
                f"Practice {practice_number} of {len(PRACTICE_IDS)}", practice=True
            )
            record(dict(participant_id=participant_id, started=started,
                        phase="practice", trial=practice_number,
                        item=f"Pract{practice_number}", response=answer,
                        reaction_time_s=rt, confirmation_time_s=confirm_rt, correct=""))
            show_solution(win, STIMULI_DIR / f"Pract{practice_number}_sol.png",
                          answer, practice_number)

        screen(
            win,
            "Practice complete",
            f"You will now answer {len(QUESTION_NUMBERS)} more questions.\n\n"
            "Press 1–8 to select an answer.\n"
            "Press SPACE to confirm and continue.\n\n"
            "No feedback will be shown during this task."
        )

        for trial, item_no in enumerate(QUESTION_NUMBERS, start=1):
            response, rt, confirm_rt = ask_matrix(
                win, questions[item_no], f"Question {trial} of {len(QUESTION_NUMBERS)}"
            )
            correct_answer = ANSWER_KEY.get(item_no)
            correctness = (int(response == correct_answer)
                           if correct_answer is not None else "")
            record(dict(participant_id=participant_id, started=started,
                        phase="main", trial=trial, item=item_no,
                        response=response, reaction_time_s=rt,
                        confirmation_time_s=confirm_rt, correct=correctness))

        total_correct = sum(row["correct"] == 1 for row in rows if row["phase"] == "main")
        n_main = sum(row["phase"] == "main" for row in rows)
        print(f"IQ test score: {total_correct}/{n_main}")
        if owns_window:
            screen(win, "Task completed",
                   "You have completed the pattern reasoning questions.\nThank you.",
                   footer="Press SPACE to finish")
        return {
            "participant_id": participant_id,
            "score": total_correct,
            "total_questions": n_main,
            "responses": rows,
            "output_file": str(output_file) if output_file is not None else None,
        }
    finally:
        win.mouseVisible = previous_mouse_visible
        if owns_window:
            win.close()


def main():
    try:
        return run_iq_task()
    except KeyboardInterrupt:
        print("IQ task interrupted. Completed responses are retained if saving is enabled.")
        return None


if __name__ == "__main__":
    main()
