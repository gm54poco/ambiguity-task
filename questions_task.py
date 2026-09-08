from psychopy import visual, event, core

import questions_params as qparams


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


def ask_key_question(
    win,
    question_text,
    valid_keys,
    question_pos=None,
    question_height=None,
    question_wrap_width=None,
):
    """Ask a keyboard-response question."""

    event.clearEvents()

    question = draw_text(
        win=win,
        text=question_text,
        pos=(
            question_pos
            or qparams.QUESTION_POS
        ),
        height=(
            question_height
            or qparams.QUESTION_HEIGHT
        ),
        wrap_width=(
            question_wrap_width
            or qparams.QUESTION_WRAP_WIDTH
        ),
        bold=True,
    )

    question.draw()

    win.flip()

    keys = event.waitKeys(
        keyList=(
            valid_keys
            + ["escape"]
        )
    )

    if "escape" in keys:

        quit_experiment(
            win
        )

    return keys[0]


# -----------------------------------------------------------------------------
# Likert questions
# -----------------------------------------------------------------------------


def ask_likert_question(
    win,
    question_text,
    labels,
):
    """Ask a five-point Likert question using keys 1-5."""

    event.clearEvents()

    while True:

        question = draw_text(
            win=win,
            text=question_text,
            pos=qparams.QUESTION_POS,
            height=qparams.QUESTION_HEIGHT,
            wrap_width=qparams.QUESTION_WRAP_WIDTH,
            bold=True,
        )

        question.draw()

        for i, value in enumerate(
            qparams.LIKERT_VALUES
        ):

            x_pos = (
                qparams.LIKERT_X_POSITIONS[i]
            )

            circle = visual.Circle(
                win=win,
                radius=qparams.LIKERT_RADIUS,
                pos=(
                    x_pos,
                    qparams.LIKERT_Y,
                ),
                fillColor=None,
                lineColor="black",
                lineWidth=2,
            )

            number = visual.TextStim(
                win=win,
                text=str(value),
                pos=(
                    x_pos,
                    qparams.LIKERT_Y,
                ),
                color="black",
                height=0.035,
                bold=True,
                font="Arial",
            )

            label = visual.TextStim(
                win=win,
                text=labels[i],
                pos=(
                    x_pos,
                    qparams.LABEL_Y,
                ),
                color="black",
                height=qparams.LABEL_HEIGHT,
                wrapWidth=qparams.LABEL_WRAP_WIDTH,
                alignText="center",
                font="Arial",
            )

            circle.draw()
            number.draw()
            label.draw()

        bottom = draw_text(
            win=win,
            text="Press a number from 1 to 5.",
            pos=qparams.BOTTOM_TEXT_POS,
            height=qparams.BOTTOM_TEXT_HEIGHT,
        )

        bottom.draw()

        win.flip()

        keys = event.getKeys(
            keyList=(
                qparams.LIKERT_KEYS
                + ["escape"]
            )
        )

        if "escape" in keys:

            quit_experiment(
                win
            )

        for key in qparams.LIKERT_KEYS:

            if key in keys:

                return int(key)


# -----------------------------------------------------------------------------
# Cycle reconstruction display
# -----------------------------------------------------------------------------


def draw_cycle_response(
    win,
    responses,
):
    """
    Draw the participant's current reconstructed sequence.

    Blue responses appear as blue balls.
    Magenta responses appear as magenta balls.
    """

    if not responses:

        placeholder = draw_text(
            win=win,
            text="Your sequence will appear here",
            pos=(
                0,
                qparams.CYCLE_BALL_Y,
            ),
            height=0.027,
            wrap_width=1.0,
        )

        placeholder.draw()

        return

    n_balls = len(
        responses
    )

    total_width = (
        (n_balls - 1)
        * qparams.CYCLE_BALL_SPACING
    )

    start_x = (
        -total_width / 2
    )

    for i, color in enumerate(
        responses
    ):

        x_pos = (
            start_x
            + i
            * qparams.CYCLE_BALL_SPACING
        )

        ball = visual.Circle(
            win=win,
            radius=qparams.CYCLE_BALL_RADIUS,
            pos=(
                x_pos,
                qparams.CYCLE_BALL_Y,
            ),
            fillColor=color,
            lineColor="black",
            lineWidth=2,
        )

        ball.draw()


# -----------------------------------------------------------------------------
# Cycle reconstruction question
# -----------------------------------------------------------------------------


def ask_cycle_reconstruction(
    win,
    selected_urn,
):
    """
    Ask the participant to reconstruct the underlying sequence.

    Controls:

        B
            Add a blue ball.

        M
            Add a magenta ball.

        BACKSPACE
            Remove the most recently entered ball.

        SPACE
            Submit the answer.

        ESCAPE
            Quit the experiment.

    Known-k condition:
        exactly k balls must be entered.

    Unknown-k condition:
        participant chooses the sequence length.
    """

    responses = []

    participant_knows_k = (
        selected_urn[
            "participant_knows_k"
        ]
    )

    true_k = (
        selected_urn[
            "ambiguous_k"
        ]
    )

    error_message = ""

    event.clearEvents()

    while True:

        # -----------------------------------------------------------------
        # Question
        # -----------------------------------------------------------------

        question = draw_text(
            win=win,
            text=qparams.CYCLE_QUESTION,
            pos=qparams.CYCLE_QUESTION_POS,
            height=qparams.CYCLE_QUESTION_HEIGHT,
            wrap_width=qparams.CYCLE_QUESTION_WRAP_WIDTH,
            bold=True,
        )

        question.draw()

        # -----------------------------------------------------------------
        # Current sequence
        # -----------------------------------------------------------------

        draw_cycle_response(
            win=win,
            responses=responses,
        )

# -----------------------------------------------------------------
# Compact controls
# -----------------------------------------------------------------

        instruction = draw_text(
            win=win,
            text=qparams.CYCLE_INSTRUCTION_KNOWN,
            pos=qparams.CYCLE_INSTRUCTION_POS,
            height=qparams.CYCLE_INSTRUCTION_HEIGHT,
            wrap_width=1.20,
        )

        instruction.draw()

        # -----------------------------------------------------------------
        # Error message
        # -----------------------------------------------------------------

        if error_message:

            error = draw_text(
                win=win,
                text=error_message,
                pos=qparams.CYCLE_ERROR_POS,
                height=qparams.CYCLE_ERROR_HEIGHT,
                wrap_width=1.15,
                bold=True,
                color="darkred",
            )

            error.draw()

        win.flip()

        # -----------------------------------------------------------------
        # Keyboard response
        # -----------------------------------------------------------------

        keys = event.waitKeys(
            keyList=[
                "b",
                "m",
                "backspace",
                "space",
                "escape",
            ]
        )

        key = keys[0]

        # -----------------------------------------------------------------
        # Escape
        # -----------------------------------------------------------------

        if key == "escape":

            quit_experiment(
                win
            )

        # -----------------------------------------------------------------
        # Delete
        # -----------------------------------------------------------------

        if key == "backspace":

            if responses:

                responses.pop()

            error_message = ""

            continue

        # -----------------------------------------------------------------
        # Add Blue
        # -----------------------------------------------------------------

        if key == "b":

            if participant_knows_k:

                if len(responses) < true_k:

                    responses.append(
                        "blue"
                    )

                else:

                    error_message = (
                        f"This rule contains {true_k} balls. "
                        "Press BACKSPACE if you want to change one."
                    )

            else:

                if (
                    len(responses)
                    < qparams.MAX_CYCLE_RESPONSE_LENGTH
                ):

                    responses.append(
                        "blue"
                    )

                    error_message = ""

                else:

                    error_message = (
                        "You have reached the maximum sequence length. "
                        "Press BACKSPACE if you want to change it."
                    )

            continue

        # -----------------------------------------------------------------
        # Add Magenta
        # -----------------------------------------------------------------

        if key == "m":

            if participant_knows_k:

                if len(responses) < true_k:

                    responses.append(
                        "magenta"
                    )

                    error_message = ""

                else:

                    error_message = (
                        f"This rule contains {true_k} balls. "
                        "Press BACKSPACE if you want to change one."
                    )

            else:

                if (
                    len(responses)
                    < qparams.MAX_CYCLE_RESPONSE_LENGTH
                ):

                    responses.append(
                        "magenta"
                    )

                    error_message = ""

                else:

                    error_message = (
                        "You have reached the maximum sequence length. "
                        "Press BACKSPACE if you want to change it."
                    )

            continue

        # -----------------------------------------------------------------
        # SPACE = submit
        # -----------------------------------------------------------------

        if key == "space":

            # Known-k condition
            if participant_knows_k:

                if len(responses) != true_k:

                    error_message = (
                        f"Please enter exactly {true_k} balls "
                        "before pressing SPACE."
                    )

                    continue

            # Unknown-k condition
            else:

                if len(responses) == 0:

                    error_message = (
                        "Please enter at least one ball "
                        "before pressing SPACE."
                    )

                    continue

            return list(
                responses
            )


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
                "4",
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


if __name__ == "__main__":

    win = visual.Window(
        size=[1200, 800],
        fullscr=False,
        color="lightgrey",
        units="height",
    )

    dummy_urn = {
        "ambiguous_k": 3,
        "participant_knows_k": False,
        "label": "Urn A",
    }

    results = run_post_block_questions(
        win=win,
        selected_urn=dummy_urn,
    )

    print(
        results
    )

    win.close()

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
                "4",
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