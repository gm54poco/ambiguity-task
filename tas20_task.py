from psychopy import visual, event, core
import csv
import os
from datetime import datetime

import questionnaire_params as params
import participant_info

# Set to True when testing: no participant GUI or demographics entry.
TEST_MODE = True
TEST_PARTICIPANT_ID = "TEST_101"



def reverse_score(response):
    return 6 - response


def classify_tas20(total_score):
    if total_score <= params.TAS20_CUTOFFS["non_alexithymic_max"]:
        return "non-alexithymic"
    elif params.TAS20_CUTOFFS["borderline_min"] <= total_score <= params.TAS20_CUTOFFS["borderline_max"]:
        return "borderline"
    elif total_score >= params.TAS20_CUTOFFS["alexithymic_min"]:
        return "alexithymic"
    else:
        return "unclassified"


def calculate_subscale_scores(responses):
    subscale_scores = {}

    for subscale_name, item_ids in params.TAS20_SUBSCALES.items():
        subscale_scores[subscale_name] = sum(responses[item_id] for item_id in item_ids)

    return subscale_scores


def draw_text(win, text, pos, height=0.05, wrap_width=1.4, bold=False):
    return visual.TextStim(
        win=win,
        text=text,
        pos=pos,
        color=params.TEXT_COLOR,
        height=height,
        wrapWidth=wrap_width,
        bold=bold,
        font="Arial"
    )


def create_likert_scale(win):
    """Match the post-block questionnaire: ticks and a rectangular marker."""
    x_positions = [-0.40, -0.20, 0.0, 0.20, 0.40]
    scale_y = -0.06
    label_y = -0.17
    number_y = scale_y + 0.085
    tick_height = 0.055
    marker_width = 0.025
    marker_height = 0.075

    scale_line = visual.Line(
        win=win,
        start=(x_positions[0], scale_y),
        end=(x_positions[-1], scale_y),
        lineColor="black",
        lineWidth=2,
    )

    labels = [
        "Strongly\ndisagree",
        "Disagree",
        "Neither agree\nnor disagree",
        "Agree",
        "Strongly\nagree",
    ]

    scale_items = []
    for value, x_pos, label_text in zip(range(1, 6), x_positions, labels):
        tick = visual.Line(
            win=win,
            start=(x_pos, scale_y - tick_height / 2),
            end=(x_pos, scale_y + tick_height / 2),
            lineColor="black",
            lineWidth=2,
        )
        number = visual.TextStim(
            win=win, text=str(value), pos=(x_pos, number_y),
            color="black", height=0.032, bold=True, font="Arial",
        )
        label = visual.TextStim(
            win=win, text=label_text, pos=(x_pos, label_y),
            color="black", height=0.026, wrapWidth=0.16, font="Arial",
        )
        scale_items.append({"value": value, "tick": tick,
                            "number": number, "label": label})

    selection_marker = visual.Rect(
        win=win, width=marker_width, height=marker_height,
        pos=(0, scale_y), fillColor="white", lineColor="black", lineWidth=2,
    )
    return scale_line, scale_items, selection_marker, x_positions, scale_y


def save_results(participant_id, responses_raw, responses_scored, reaction_times,
                 subscale_scores, total_score, classification):

    # Organize the output by participant: data/<participant_id>/TAS20_...csv
    participant_folder = participant_info.DATA_DIR / str(participant_id)
    participant_folder.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    filename = f"TAS20_{participant_id}_{timestamp}.csv"
    filepath = participant_folder / filename

    with open(filepath, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        writer.writerow([
            "participant_id",
            "item_id",
            "item_text",
            "reverse_scored",
            "raw_response",
            "scored_response",
            "reaction_time_seconds"
        ])

        for item in params.TAS20_ITEMS:
            item_id = item["id"]
            writer.writerow([
                participant_id,
                item_id,
                item["text"],
                item["reverse"],
                responses_raw[item_id],
                responses_scored[item_id],
                reaction_times[item_id]
            ])

        writer.writerow([])
        writer.writerow(["SUMMARY"])
        writer.writerow(["tas20_total_score", total_score])
        writer.writerow(["tas20_classification", classification])

        for subscale_name, score in subscale_scores.items():
            writer.writerow([subscale_name, score])

    return filepath


def run_tas20(participant=None, win=None, test_mode=None):
    """Run TAS-20 with an existing participant, or collect information once.

    When TEST_MODE=True, skip the GUI and use TEST_PARTICIPANT_ID.
    When participant is supplied by main.py, reuse that participant ID.
    Otherwise, collect and save demographics using participant_info.py.
    """
    if test_mode is None:
        test_mode = bool(participant.get("test_run", False)) if participant is not None else TEST_MODE
    if participant is not None:
        participant_id = str(participant["participant_id"])
    elif test_mode:
        participant_id = TEST_PARTICIPANT_ID
    else:
        participant = participant_info.collect_participant_info()
        participant_info.save_participant_info(participant)
        participant_id = participant["participant_id"]

    owns_window = win is None
    if owns_window:
        win = visual.Window(
            size=params.WINDOW_SIZE,
            fullscr=params.FULLSCREEN,
            color=params.BACKGROUND_COLOR,
            units="height",
            gammaErrorPolicy="warn",
        )
    title = draw_text(
        win,
        text="TAS20 Questionnaire",
        pos=(0, 0.24),
        height=0.048,
        wrap_width=1.36
    )
    instructions = draw_text(
        win,
        text=(
            "You will now answer a short questionnaire.\n\n"
            "For each statement, choose how much you agree or disagree.\n\n"
            "Use the number row or numpad (1-5) to answer.\nPress SPACE to continue after selecting an answer.\n\n"
            "Press SPACE to begin."
        ),
        pos=(0, 0.015),
        height=0.034,
        wrap_width=1.36
    )

    title.draw()
    instructions.draw()
    win.flip()

    keys = event.waitKeys(keyList=["space", "escape"])
    if "escape" in keys:
        raise KeyboardInterrupt("TAS-20 interrupted")

    responses_raw = {}
    responses_scored = {}
    reaction_times = {}

    for item_index, item in enumerate(params.TAS20_ITEMS):
        item_id = item["id"]
        selected_response = None

        # Create visual objects only once for each question.
        progress_text = draw_text(
            win, f"Question {item_index + 1} of {len(params.TAS20_ITEMS)}",
            (0, 0.42), height=0.035, bold=True
        )
        question_text = draw_text(
            win, item["text"], (0, 0.20), height=0.05, wrap_width=1.4
        )
        scale_line, scale_items, selection_marker, x_positions, scale_y = create_likert_scale(win)
        warning_text = draw_text(
            win, "", (0, -0.34), height=0.03
        )

        def draw_question():
            progress_text.draw()
            question_text.draw()
            scale_line.draw()
            for scale_item in scale_items:
                scale_item["tick"].draw()
                scale_item["number"].draw()
                scale_item["label"].draw()
            if selected_response is not None:
                selection_marker.pos = (x_positions[selected_response - 1], scale_y)
                selection_marker.draw()
            warning_text.draw()
            win.flip()

        event.clearEvents()
        response_clock = core.Clock()
        # Time the response from when the question first appears.
        win.callOnFlip(response_clock.reset)
        draw_question()

        while True:
            changed = False
            advance = False
            keys = event.getKeys(keyList=[
                "1", "2", "3", "4", "5", "space", "escape",
                "num_1", "num_2", "num_3", "num_4", "num_5"
            ])
            if "escape" in keys:
                raise KeyboardInterrupt("TAS-20 interrupted")

            for key in keys:
                if key in ("1", "2", "3", "4", "5") or key in (
                    "num_1", "num_2", "num_3", "num_4", "num_5"
                ):
                    value = int(key.replace("num_", ""))
                    if selected_response is None:
                        reaction_times[item_id] = response_clock.getTime()
                    if selected_response != value:
                        selected_response = value
                        changed = True
                elif key == "space" and selected_response is not None:
                    advance = True

            if advance:
                break

            if changed:
                warning_text.text = "Press SPACE to continue."
                draw_question()
            else:
                # Avoid a busy loop while waiting for an answer.
                core.wait(0.01)

        responses_raw[item_id] = selected_response
        responses_scored[item_id] = (
            reverse_score(selected_response) if item["reverse"]
            else selected_response
        )
        if item_id not in reaction_times:
            reaction_times[item_id] = response_clock.getTime()

    total_score = sum(responses_scored.values())
    subscale_scores = calculate_subscale_scores(responses_scored)
    classification = classify_tas20(total_score)

    if test_mode:
        filepath = None
        print("TEST MODE — TAS-20 responses not saved:")
        print({"participant_id": participant_id,
               "responses_raw": responses_raw,
               "reaction_times": reaction_times,
               "total_score": total_score,
               "subscale_scores": subscale_scores,
               "classification": classification})
    else:
        filepath = save_results(
            participant_id=participant_id,
            responses_raw=responses_raw,
            responses_scored=responses_scored,
            reaction_times=reaction_times,
            subscale_scores=subscale_scores,
            total_score=total_score,
            classification=classification,
        )
        print(f"TAS-20 results saved to: {filepath}")

    # When run by main.py, hand the existing window back for its final screen.
    if owns_window:
        win.close()

    return {
        "participant_id": participant_id,
        "total_score": total_score,
        "subscale_scores": subscale_scores,
        "classification": classification,
        "output_file": str(filepath) if filepath is not None else None,
    }


if __name__ == "__main__":
    try:
        run_tas20()
    except KeyboardInterrupt:
        print("TAS-20 interrupted.")
