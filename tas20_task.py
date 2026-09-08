from psychopy import visual, event, core, gui
import csv
import os
from datetime import datetime

import questionnaire_params as params


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


def create_button(win, text, pos, size=(0.28, 0.14), selected=False):
    fill_color = "lightgrey" if not selected else "darkgrey"

    rect = visual.Rect(
        win=win,
        width=size[0],
        height=size[1],
        pos=pos,
        fillColor=fill_color,
        lineColor="black",
        lineWidth=2
    )

    label = visual.TextStim(
        win=win,
        text=text,
        pos=pos,
        color="black",
        height=0.035,
        wrapWidth=size[0] * 0.9,
        font="Arial"
    )

    return rect, label


def create_likert_scale(win, selected_response=None):
    scale_items = []

    x_positions = [-0.50, -0.25, 0.0, 0.25, 0.50]
    y_circle = -0.15
    y_label = -0.25
    y_number = -0.08

    line = visual.Line(
        win=win,
        start=(x_positions[0], y_circle),
        end=(x_positions[-1], y_circle),
        lineColor="black",
        lineWidth=2
    )

    labels = [
        "Strongly\ndisagree",
        "Disagree",
        "Neither agree\nnor disagree",
        "Agree",
        "Strongly\nagree"
    ]

    for value, x_pos, label_text in zip([1, 2, 3, 4, 5], x_positions, labels):
        selected = selected_response == value

        circle = visual.Circle(
            win=win,
            radius=0.025,
            pos=(x_pos, y_circle),
            fillColor="darkgrey" if selected else "white",
            lineColor="black",
            lineWidth=2
        )

        number = visual.TextStim(
            win=win,
            text=str(value),
            pos=(x_pos, y_number),
            color="black",
            height=0.035,
            font="Arial"
        )

        label = visual.TextStim(
            win=win,
            text=label_text,
            pos=(x_pos, y_label),
            color="black",
            height=0.025,
            wrapWidth=0.20,
            font="Arial"
        )

        scale_items.append({
            "value": value,
            "circle": circle,
            "number": number,
            "label": label
        })

    return line, scale_items


def save_results(participant_id, responses_raw, responses_scored, reaction_times,
                 subscale_scores, total_score, classification):

    if not os.path.exists(params.DATA_FOLDER):
        os.makedirs(params.DATA_FOLDER)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"TAS20_{participant_id}_{timestamp}.csv"
    filepath = os.path.join(params.DATA_FOLDER, filename)

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


def run_tas20():
    info = {
        "participant_id": "",
        "age": "",
        "gender": ""
    }

    dialog = gui.DlgFromDict(
        dictionary=info,
        title="Participant Information"
    )

    if not dialog.OK:
        core.quit()

    participant_id = info["participant_id"].strip()

    if participant_id == "":
        participant_id = "anonymous"

    win = visual.Window(
        size=params.WINDOW_SIZE,
        fullscr=params.FULLSCREEN,
        color=params.BACKGROUND_COLOR,
        units="height"
    )

    mouse = event.Mouse(win=win)

    instructions = draw_text(
        win,
        text=(
            "You will now answer a short questionnaire.\n\n"
            "For each statement, choose how much you agree or disagree.\n\n"
            "You can respond by clicking one of the circles or by pressing keys 1-5.\n\n"
            "Press SPACE to begin."
        ),
        pos=(0, 0.1),
        height=0.045,
        wrap_width=1.3
    )

    instructions.draw()
    win.flip()

    keys = event.waitKeys(keyList=["space", "escape"])
    if "escape" in keys:
        win.close()
        core.quit()

    responses_raw = {}
    responses_scored = {}
    reaction_times = {}

    for item_index, item in enumerate(params.TAS20_ITEMS):

        item_id = item["id"]
        item_text = item["text"]

        selected_response = None
        rt_clock = core.Clock()
        rt_clock.reset()

        while True:
            progress_text = draw_text(
                win,
                text=f"Question {item_index + 1} of {len(params.TAS20_ITEMS)}",
                pos=(0, 0.42),
                height=0.035,
                bold=True
            )

            question_text = draw_text(
                win,
                text=item_text,
                pos=(0, 0.20),
                height=0.05,
                wrap_width=1.4
            )

            instruction_text = draw_text(
                win,
                text="Choose one option:",
                pos=(0, 0.02),
                height=0.035
            )

            scale_line, scale_items = create_likert_scale(
                win=win,
                selected_response=selected_response
            )

            next_rect, next_label = create_button(
                win=win,
                text="Next",
                pos=(0.48, -0.40),
                size=(0.22, 0.09),
                selected=False
            )

            if selected_response is None:
                warning_text = draw_text(
                    win,
                    text="",
                    pos=(0, -0.34),
                    height=0.03
                )
            else:
                warning_text = draw_text(
                    win,
                    text="Press ENTER or click Next to continue.",
                    pos=(0, -0.34),
                    height=0.03
                )

            progress_text.draw()
            question_text.draw()
            instruction_text.draw()

            scale_line.draw()

            for scale_item in scale_items:
                scale_item["circle"].draw()
                scale_item["number"].draw()
                scale_item["label"].draw()

            warning_text.draw()
            next_rect.draw()
            next_label.draw()

            win.flip()

            keys = event.getKeys(keyList=["1", "2", "3", "4", "5", "return", "escape"])

            if "escape" in keys:
                win.close()
                core.quit()

            for key in keys:
                if key in ["1", "2", "3", "4", "5"]:
                    if selected_response is None:
                        reaction_times[item_id] = rt_clock.getTime()

                    selected_response = int(key)

                elif key == "return":
                    if selected_response is not None:
                        break

            if selected_response is not None and "return" in keys:
                break

            if mouse.getPressed()[0]:
                for scale_item in scale_items:
                    if scale_item["circle"].contains(mouse):
                        if selected_response is None:
                            reaction_times[item_id] = rt_clock.getTime()

                        selected_response = scale_item["value"]
                        core.wait(0.1)

                if next_rect.contains(mouse) and selected_response is not None:
                    core.wait(0.1)
                    break

        responses_raw[item_id] = selected_response

        if item["reverse"]:
            responses_scored[item_id] = reverse_score(selected_response)
        else:
            responses_scored[item_id] = selected_response

        if item_id not in reaction_times:
            reaction_times[item_id] = rt_clock.getTime()

    total_score = sum(responses_scored.values())
    subscale_scores = calculate_subscale_scores(responses_scored)
    classification = classify_tas20(total_score)

    filepath = save_results(
        participant_id=participant_id,
        responses_raw=responses_raw,
        responses_scored=responses_scored,
        reaction_times=reaction_times,
        subscale_scores=subscale_scores,
        total_score=total_score,
        classification=classification
    )

    end_text = draw_text(
        win,
        text=(
            "Thank you.\n\n"
            "The questionnaire is complete.\n\n"
            "Press SPACE to finish."
        ),
        pos=(0, 0.1),
        height=0.05,
        wrap_width=1.2
    )

    end_text.draw()
    win.flip()

    keys = event.waitKeys(keyList=["space", "escape"])
    if "escape" in keys:
        win.close()
        core.quit()

    print(f"Data saved to: {filepath}")

    win.close()
    core.quit()


if __name__ == "__main__":
    run_tas20()