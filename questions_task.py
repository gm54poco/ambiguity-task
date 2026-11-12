from psychopy import visual, event, core

import questions_params as qparams
import urn_params as params

# Set True to run this questionnaire on its own with a dummy urn.
# When called by urn_task.py, real urn details are always used.
TEST_MODE = True
TEST_K = 3
TEST_PARTICIPANT_KNOWS_K = False


# -----------------------------------------------------------------------------
# General helpers
# -----------------------------------------------------------------------------


def draw_text(
    win,
    text,
    pos,
    height=0.05,
    wrap_width=1.4,
    bold=False,
    color="black",
):
    """Create a standard text stimulus."""

    return visual.TextStim(
        win=win,
        text=text,
        pos=pos,
        color=color,
        height=height,
        wrapWidth=wrap_width,
        bold=bold,
        font="Arial",
        alignText="center",
    )


def quit_experiment(win):
    """Close the PsychoPy window and stop the experiment."""

    win.close()
    core.quit()


# -----------------------------------------------------------------------------
# General keyboard question
# -----------------------------------------------------------------------------


def _number_keys(values):
    return [str(v) for v in values] + [f"num_{v}" for v in values]


def _get_number(key):
    return int(key.replace("num_", ""))


def ask_key_question(
    win, question_text, valid_keys,
    question_pos=None, question_height=None, question_wrap_width=None,
):
    """Show selectable number options; SPACE confirms the highlighted value."""
    values = sorted({_get_number(k) for k in valid_keys
                     if k.isdigit() or k.startswith("num_")})
    if not values:
        raise ValueError("ask_key_question requires numerical valid_keys")

    question = draw_text(
        win, question_text,
        question_pos if question_pos is not None else qparams.QUESTION_POS,
        height=question_height if question_height is not None else qparams.QUESTION_HEIGHT,
        wrap_width=question_wrap_width if question_wrap_width is not None else qparams.QUESTION_WRAP_WIDTH,
        bold=True,
    )
    option_y = -0.08
    spacing = 0.20
    start_x = -spacing * (len(values) - 1) / 2
    options = []
    for index, value in enumerate(values):
        x = start_x + index * spacing
        circle = visual.Circle(win, radius=0.040, pos=(x, option_y),
                               fillColor="white", lineColor="black", lineWidth=2)
        number = draw_text(win, str(value), (x, option_y), height=0.032, bold=True)
        options.append((value, circle, number))
    prompt = draw_text(win, "Press 1–4 to select an answer.",
                       (0, -0.30), height=0.027)
    selected = None

    def render():
        question.draw()
        for value, circle, number in options:
            circle.fillColor = "darkgrey" if selected == value else "white"
            circle.draw()
            number.draw()
        prompt.text = ("Press SPACE to continue." if selected is not None
                       else "Press a number to select an answer.")
        prompt.draw()
        win.flip()

    event.clearEvents()
    render()
    while True:
        key = event.waitKeys(keyList=_number_keys(values) + ["space", "escape"])[0]
        if key == "escape":
            quit_experiment(win)
        if key == "space":
            if selected is not None:
                return str(selected)
        else:
            selected = _get_number(key)
            render()



def ask_likert_question(win, question_text, labels):
    """Five-point scale with ticks and rectangular selection marker."""

    question = draw_text(
        win, question_text, (0, 0.22),
        height=qparams.QUESTION_HEIGHT,
        wrap_width=qparams.QUESTION_WRAP_WIDTH,
        bold=True
    )

    values = list(qparams.LIKERT_VALUES)
    positions = list(qparams.LIKERT_X_POSITIONS)

    # Adjustable layout
    scale_y = -0.06
    label_y = -0.17
    number_y = scale_y + 0.085
    tick_height = 0.055
    marker_width = 0.025
    marker_height = 0.075

    scale_line = visual.Line(
        win,
        start=(positions[0], scale_y),
        end=(positions[-1], scale_y),
        lineColor="black",
        lineWidth=2
    )

    items = []

    for value, x, label in zip(values, positions, labels):
        tick = visual.Line(
            win,
            start=(x, scale_y - tick_height / 2),
            end=(x, scale_y + tick_height / 2),
            lineColor="black",
            lineWidth=2
        )

        number = draw_text(
            win, str(value), (x, number_y),
            height=0.032, bold=True
        )

        description = draw_text(
            win, label, (x, label_y),
            height=qparams.LABEL_HEIGHT,
            wrap_width=qparams.LABEL_WRAP_WIDTH
        )

        items.append((value, tick, number, description))

    marker = visual.Rect(
        win,
        width=marker_width,
        height=marker_height,
        pos=(0, scale_y),
        fillColor="white",
        lineColor="black",
        lineWidth=2
    )

    footer = draw_text(
        win, "Press a number from 1 to 5.",
        (0, -0.38), height=0.027
    )

    selected = None

    def render():
        question.draw()
        scale_line.draw()

        for value, tick, number, description in items:
            tick.draw()
            number.draw()
            description.draw()

        if selected is not None:
            marker.pos = (positions[values.index(selected)], scale_y)
            marker.draw()

        footer.text = (
            "Press SPACE to continue."
            if selected is not None
            else "Press a number from 1 to 5."
        )
        footer.draw()
        win.flip()

    event.clearEvents()
    render()

    while True:
        key = event.waitKeys(
            keyList=_number_keys(values) + ["space", "escape"]
        )[0]

        if key == "escape":
            quit_experiment(win)

        if key == "space" and selected is not None:
            return selected

        if key != "space":
            selected = _get_number(key)
            render()



# -----------------------------------------------------------------------------
# Cycle reconstruction (same color options as the urn prediction task)
# -----------------------------------------------------------------------------


def draw_cycle_response(win, responses, total_slots):
    """
    Draw empty outlined balls that fill as the participant
    enters blue or magenta responses.
    """

    spacing = qparams.CYCLE_BALL_SPACING
    radius = qparams.CYCLE_BALL_RADIUS
    y = qparams.CYCLE_BALL_Y

    start_x = -spacing * (total_slots - 1) / 2
    SOFT_COLORS = {
    "blue": params.BALL_BLUE,
    "magenta": params.BALL_MAGENTA,}
    for i in range(total_slots):
        x = start_x + i * spacing

        if i < len(responses):
            fill_color = SOFT_COLORS[responses[i]]
            line_color = SOFT_COLORS[responses[i]]
        else:
            fill_color = None
            line_color = "#536e8c"

        visual.Circle(
            win=win,
            radius=radius,
            pos=(x, y),
            fillColor=fill_color,
            lineColor=line_color,
            lineWidth=2
        ).draw()



def ask_cycle_reconstruction(win, selected_urn, estimated_k=None):
    """
    Reconstruct a sequence using B and M.

    Known k:
        Number of slots equals the true k.

    Unknown k:
        Number of slots equals the participant's estimated k.

    Not sure:
        Show up to 4 slots and allow a variable-length response.
    """

    knows_k = selected_urn["participant_knows_k"]
    true_k = selected_urn["ambiguous_k"]

    if knows_k:
        total_slots = true_k
        require_exact_length = True

    elif estimated_k in (1, 2, 3):
        total_slots = estimated_k
        require_exact_length = True

    else:
        total_slots = qparams.MAX_CYCLE_RESPONSE_LENGTH
        require_exact_length = False

    responses = []
    error_message = ""

    # --------------------------------------------------
    # Question
    # --------------------------------------------------

    question = draw_text(
        win,
        "What was the sequence?",
        qparams.CYCLE_QUESTION_POS,
        height=qparams.CYCLE_QUESTION_HEIGHT,
        wrap_width=qparams.CYCLE_QUESTION_WRAP_WIDTH,
        bold=True
    )

    # --------------------------------------------------
    # Minimalist color legend
    # --------------------------------------------------

    legend_y = -0.22
    legend_ball_radius = 0.012
    legend_text_height = 0.026

    blue_ball = visual.Circle(
        win=win,
        radius=legend_ball_radius,
        pos=(-0.12, legend_y),
        fillColor="#5379B8",
        lineColor=None
    )

    blue_label = draw_text(
        win,
        "B",
        (-0.08, legend_y),
        height=legend_text_height,
        color="#536e8c"
    )

    magenta_ball = visual.Circle(
        win=win,
        radius=legend_ball_radius,
        pos=(0.08, legend_y),
        fillColor="#B966A8",
        lineColor=None
    )

    magenta_label = draw_text(
        win,
        "M",
        (0.12, legend_y),
        height=legend_text_height,
        color="#536e8c"
    )

    # --------------------------------------------------
    # Action instructions
    # --------------------------------------------------

    action_instruction = draw_text(
        win,
        "Backspace to undo  ·  Space to confirm",
        (0, -0.30),
        height=0.025,
        color="#536e8c"
    )

    # --------------------------------------------------
    # Error message
    # --------------------------------------------------

    error = draw_text(
        win,
        "",
        qparams.CYCLE_ERROR_POS,
        height=qparams.CYCLE_ERROR_HEIGHT,
        wrap_width=1.15,
        bold=True,
        color="darkred"
    )

    # --------------------------------------------------
    # Draw screen
    # --------------------------------------------------

    def render():
        question.draw()

        draw_cycle_response(
            win,
            responses,
            total_slots
        )

        # Color legend
        blue_ball.draw()
        blue_label.draw()

        magenta_ball.draw()
        magenta_label.draw()

        # Keyboard instructions
        action_instruction.draw()

        # Error feedback
        error.text = error_message

        if error_message:
            error.draw()

        win.flip()

    event.clearEvents()
    render()

    # --------------------------------------------------
    # Participant responses
    # --------------------------------------------------

    while True:

        key = event.waitKeys(
            keyList=[
                "b",
                "m",
                "backspace",
                "space",
                "escape"
            ]
        )[0]

        if key == "escape":
            quit_experiment(win)

        elif key == "backspace":

            if responses:
                responses.pop()

            error_message = ""

        elif key in ("b", "m"):

            if len(responses) < total_slots:

                responses.append(
                    "blue" if key == "b" else "magenta"
                )

                error_message = ""

            else:
                error_message = (
                    "Sequence is full. "
                    "Press BACKSPACE to change your answer."
                )

        elif key == "space":

            if not responses:
                error_message = "Please enter at least one ball."

            elif require_exact_length and len(responses) != total_slots:
                error_message = (
                    f"Please enter exactly {total_slots} balls."
                )

            else:
                return list(responses)

        render()

# -----------------------------------------------------------------------------
# Main post-block question sequence
# -----------------------------------------------------------------------------


def run_post_block_questions(
    win,
    selected_urn,
):
    """Run the complete post-block questionnaire."""

    results = {}

    # -----------------------------------------------------------------
    # Estimate k only when it was unknown
    # -----------------------------------------------------------------

    if not selected_urn[
        "participant_knows_k"
    ]:

        key = ask_key_question(
            win=win,
            question_text=qparams.K_QUESTION,
            valid_keys=[
                "1",
                "2",
                "3",
                "num_1",
                "num_2",
                "num_3",
            ],
            question_pos=qparams.K_QUESTION_POS,
            question_height=qparams.K_QUESTION_HEIGHT,
            question_wrap_width=qparams.K_QUESTION_WRAP_WIDTH,
        )

        results["estimated_k"] = (
            qparams.K_RESPONSE_KEYS[
                key
            ]
        )

    else:

        # Participant was already told k.
        results["estimated_k"] = (
            selected_urn[
                "ambiguous_k"
            ]
        )

    # -----------------------------------------------------------------
    # Reconstruct inferred underlying sequence
    # -----------------------------------------------------------------

    results["estimated_cycle"] = (
        ask_cycle_reconstruction(
            win=win,
            selected_urn=selected_urn,
            estimated_k=results["estimated_k"],
        )
    )

    # -----------------------------------------------------------------
    # Confidence
    # -----------------------------------------------------------------

    results["confidence"] = (
        ask_likert_question(
            win=win,
            question_text=qparams.CONFIDENCE_QUESTION,
            labels=qparams.CONFIDENCE_LABELS,
        )
    )

    # -----------------------------------------------------------------
    # Liking
    # -----------------------------------------------------------------

    results["liking"] = (
        ask_likert_question(
            win=win,
            question_text=qparams.LIKING_QUESTION,
            labels=qparams.LIKING_LABELS,
        )
    )

    # -----------------------------------------------------------------
    # Difficulty
    # -----------------------------------------------------------------

    results["difficulty"] = (
        ask_likert_question(
            win=win,
            question_text=qparams.DIFFICULTY_QUESTION,
            labels=qparams.DIFFICULTY_LABELS,
        )
    )

    # -----------------------------------------------------------------
    # Mental effort
    # -----------------------------------------------------------------

    results["mental_effort"] = (
        ask_likert_question(
            win=win,
            question_text=qparams.EFFORT_QUESTION,
            labels=qparams.EFFORT_LABELS,
        )
    )

    return results


# -----------------------------------------------------------------------------
# Standalone test
# -----------------------------------------------------------------------------


######### FOR THE TRAINING PART ONLY

def run_training_questions(
    win,
    selected_urn,
):
    """
    Ask only the inference questions needed for training.

    Always ask for the inferred sequence.

    Ask how many previous draws were relevant only when
    k was unknown to the participant.
    """

    results = {}

    # -----------------------------------------------------------------
    # Estimate k only when it was unknown
    # -----------------------------------------------------------------

    if not selected_urn[
        "participant_knows_k"
    ]:

        key = ask_key_question(
            win=win,
            question_text=qparams.K_QUESTION,
            valid_keys=[
                "1",
                "2",
                "3",
                "num_1",
                "num_2",
                "num_3",
            ],
            question_pos=qparams.K_QUESTION_POS,
            question_height=qparams.K_QUESTION_HEIGHT,
            question_wrap_width=qparams.K_QUESTION_WRAP_WIDTH,
        )

        results[
            "estimated_k"
        ] = qparams.K_RESPONSE_KEYS[
            key
        ]

    else:

        # Participant was already told k.
        results[
            "estimated_k"
        ] = selected_urn[
            "ambiguous_k"
        ]

    # -----------------------------------------------------------------
    # Reconstruct inferred sequence
    # -----------------------------------------------------------------

    results[
        "estimated_cycle"
    ] = ask_cycle_reconstruction(
        win=win,
        selected_urn=selected_urn,
    )

    return results

if __name__ == "__main__":
    if not TEST_MODE:
        raise RuntimeError("Set TEST_MODE = True to run questions_task.py standalone. "
                           "For real sessions, run it through urn_task.py.")
    win = visual.Window(size=[1200, 800], fullscr=False,
                        color="lightgrey", units="height")
    dummy_urn = {
        "ambiguous_k": TEST_K,
        "participant_knows_k": TEST_PARTICIPANT_KNOWS_K,
        "label": "Test Urn",
    }
    try:
        print(run_post_block_questions(win=win, selected_urn=dummy_urn))
    finally:
        win.close()


