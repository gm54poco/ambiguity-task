from psychopy import visual, event, core
import random

import urn_params as params


# -----------------------------------------------------------------------------
# Tutorial layout
# -----------------------------------------------------------------------------

CONTINUE_TEXT_POS = (0, -0.38)
CONTINUE_TEXT_HEIGHT = 0.028


# -----------------------------------------------------------------------------
# Tutorial settings
# -----------------------------------------------------------------------------

TUTORIAL_FIXED_AMOUNT = 1.00
TUTORIAL_CORRECT_GUESS_AMOUNT = 0.10

# Example k used for the known-k tutorial.
TUTORIAL_KNOWN_K = 2

TUTORIAL_BALL_RADIUS = 0.045


# Positions used only on the interactive "explore the urns" screen.
TUTORIAL_URN_POSITIONS = {
    "fixed": (-0.42, 0.05),
    "known_k": (0.0, 0.05),
    "unknown_k": (0.42, 0.05),
}

TUTORIAL_URN_SIZE = (0.25, 0.25)

TUTORIAL_CLICK_WIDTH = 0.30
TUTORIAL_CLICK_HEIGHT = 0.34

TUTORIAL_BOTTOM_Y = -0.40


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
    color=None,
    align_text="center",
):
    """Create a standard text stimulus."""

    return visual.TextStim(
        win=win,
        text=text,
        pos=pos,
        color=(
            params.TEXT_COLOR
            if color is None
            else color
        ),
        height=height,
        wrapWidth=wrap_width,
        bold=bold,
        alignText=align_text,
        font="Arial",
    )


def draw_continue_text(
    win,
    text="Press SPACE to continue.",
    bold=False,
):
    """Draw the standard continue instruction."""

    stim = draw_text(
        win=win,
        text=text,
        pos=CONTINUE_TEXT_POS,
        height=CONTINUE_TEXT_HEIGHT,
        wrap_width=1.20,
        bold=bold,
    )

    stim.draw()


def quit_experiment(win):
    """Close the PsychoPy window and quit."""

    win.close()
    core.quit()


def wait_for_space_or_escape(win):
    """Wait for SPACE to continue or ESCAPE to quit."""

    keys = event.waitKeys(
        keyList=[
            "space",
            "escape",
        ]
    )

    if "escape" in keys:
        quit_experiment(win)


def get_urn_image_path(
    urn_name,
    state,
):
    """Return the image path for one pretty urn."""

    if state not in {
        "closed",
        "opened",
    }:
        raise ValueError(
            "state must be 'closed' or 'opened'"
        )

    return str(
        params.PRETTY_URNS_DIR
        / f"{urn_name}_{state}.png"
    )


def draw_urn(
    win,
    urn_name,
    pos,
    label="",
    state="closed",
    size=None,
):
    """Draw one pretty urn and optionally its label."""

    if size is None:
        size = params.URN_IMAGE_SIZE

    urn = visual.ImageStim(
        win=win,
        image=get_urn_image_path(
            urn_name,
            state,
        ),
        pos=pos,
        size=size,
    )

    urn.draw()

    if label:

        label_stim = draw_text(
            win=win,
            text=label,
            pos=(
                pos[0],
                pos[1]
                + size[1] / 2
                + 0.055,
            ),
            height=0.032,
            bold=True,
        )

        label_stim.draw()

    return urn


def draw_ball(
    win,
    color,
    pos,
    radius=None,
):
    """Draw one blue or magenta ball."""

    if radius is None:
        radius = TUTORIAL_BALL_RADIUS

    ball = visual.Circle(
        win=win,
        radius=radius,
        pos=pos,
        fillColor=color,
        lineColor="black",
        lineWidth=1.5,
    )

    ball.draw()


def draw_ball_row(
    win,
    colors,
    y,
    start_x=None,
    spacing=0.095,
    radius=0.032,
):
    """
    Draw a centered row of colored balls.

    Returns the x positions of the balls so that other
    elements, such as arrows, can line up with them.
    """

    n = len(colors)

    if start_x is None:
        total_width = (
            (n - 1)
            * spacing
        )

        start_x = (
            -total_width / 2
        )

    x_positions = []

    for i, color in enumerate(colors):

        x = (
            start_x
            + i * spacing
        )

        draw_ball(
            win=win,
            color=color,
            pos=(x, y),
            radius=radius,
        )

        x_positions.append(x)

    return x_positions


# -----------------------------------------------------------------------------
# Introduction
# -----------------------------------------------------------------------------


def show_intro(win):
    """Explain the general task structure."""

    title = draw_text(
        win=win,
        text="How the task works",
        pos=(0, 0.34),
        height=0.055,
        bold=True,
    )

    body = draw_text(
        win=win,
        text=(
            "During the experiment, you will choose between different urns.\n\n"

            "Some urns give you a fixed amount of money.\n\n"

            "Other urns give you the chance to earn more money by "
            "predicting whether the next ball will be BLUE or MAGENTA.\n\n"

            "You will now be able to explore the different types of urn."
        ),
        pos=(0, 0.03),
        height=0.035,
        wrap_width=1.25,
    )

    title.draw()
    body.draw()

    draw_continue_text(
        win
    )

    win.flip()

    wait_for_space_or_escape(win)


# -----------------------------------------------------------------------------
# Interactive urn overview
# -----------------------------------------------------------------------------


def show_urn_overview(
    win,
    urn_names,
):
    """
    Show all three urn types.

    Participants can explore them in any order.

    Once BOTH prediction urns have been explored,
    the noise explanation is shown automatically once.
    """

    mouse = event.Mouse(
        win=win
    )

    mouse.clickReset()
    event.clearEvents()

    visited = {
        "fixed": False,
        "known_k": False,
        "unknown_k": False,
    }

    noise_explained = False

    click_areas = {}

    for (
        urn_type,
        pos,
    ) in TUTORIAL_URN_POSITIONS.items():

        click_areas[
            urn_type
        ] = visual.Rect(
            win=win,
            width=TUTORIAL_CLICK_WIDTH,
            height=TUTORIAL_CLICK_HEIGHT,
            pos=pos,
            fillColor=None,
            lineColor=None,
        )

    while True:

        # -------------------------------------------------------------
        # Automatically explain noise once both prediction urns
        # have been explored.
        # -------------------------------------------------------------

        if (
            visited["known_k"]
            and visited["unknown_k"]
            and not noise_explained
        ):

            show_noise_explanation(
                win
            )

            noise_explained = True

            mouse.clickReset()
            event.clearEvents()

        # -------------------------------------------------------------
        # Main overview
        # -------------------------------------------------------------

        title = draw_text(
            win=win,
            text="Explore the urns",
            pos=(0, 0.41),
            height=0.048,
            bold=True,
        )

        instruction = draw_text(
            win=win,
            text=(
                "Click each urn to learn what happens if you choose it."
            ),
            pos=(0, 0.33),
            height=0.030,
        )

        title.draw()
        instruction.draw()

        # -------------------------------------------------------------
        # Fixed-value urn
        # -------------------------------------------------------------

        draw_urn(
            win=win,
            urn_name=urn_names[
                "fixed"
            ],
            pos=TUTORIAL_URN_POSITIONS[
                "fixed"
            ],
            label="Urn A",
            size=TUTORIAL_URN_SIZE,
        )

        # -------------------------------------------------------------
        # Known-k prediction urn
        # -------------------------------------------------------------

        draw_urn(
            win=win,
            urn_name=urn_names[
                "known_k"
            ],
            pos=TUTORIAL_URN_POSITIONS[
                "known_k"
            ],
            label="Urn B",
            size=TUTORIAL_URN_SIZE,
        )

        # -------------------------------------------------------------
        # Unknown-k prediction urn
        # -------------------------------------------------------------

        draw_urn(
            win=win,
            urn_name=urn_names[
                "unknown_k"
            ],
            pos=TUTORIAL_URN_POSITIONS[
                "unknown_k"
            ],
            label="Urn C",
            size=TUTORIAL_URN_SIZE,
        )

        # -------------------------------------------------------------
        # Short descriptions
        # -------------------------------------------------------------

        fixed_text = draw_text(
            win=win,
            text="Fixed amount",
            pos=(-0.42, -0.18),
            height=0.027,
            bold=visited["fixed"],
        )

        known_text = draw_text(
            win=win,
            text="Prediction task\n (k known)",
            pos=(0.0, -0.18),
            height=0.027,
            bold=visited["known_k"],
        )

        unknown_text = draw_text(
            win=win,
            text="Prediction task\n (k unknown)",
            pos=(0.42, -0.18),
            height=0.027,
            bold=visited["unknown_k"],
        )

        fixed_text.draw()
        known_text.draw()
        unknown_text.draw()

        # -------------------------------------------------------------
        # Bottom instruction
        # -------------------------------------------------------------

        if all(
            visited.values()
        ):

            draw_continue_text(
                win,
                text="Press SPACE to continue.",
            )

        else:

            bottom = draw_text(
                win=win,
                text=(
                    "Click each urn before continuing."
                ),
                pos=(
                    0,
                    TUTORIAL_BOTTOM_Y,
                ),
                height=0.029,
            )

            bottom.draw()

        win.flip()

        # -------------------------------------------------------------
        # Keyboard
        # -------------------------------------------------------------

        keys = event.getKeys(
            keyList=[
                "space",
                "escape",
            ]
        )

        if "escape" in keys:
            quit_experiment(win)

        if (
            "space" in keys
            and all(
                visited.values()
            )
        ):
            return

        # -------------------------------------------------------------
        # Mouse selection
        # -------------------------------------------------------------

        if mouse.isPressedIn(
            click_areas[
                "fixed"
            ]
        ):

            mouse.clickReset()

            visited[
                "fixed"
            ] = True

            show_fixed_urn_demo(
                win=win,
                urn_name=urn_names[
                    "fixed"
                ],
            )

            event.clearEvents()

            continue

        if mouse.isPressedIn(
            click_areas[
                "known_k"
            ]
        ):

            mouse.clickReset()

            visited[
                "known_k"
            ] = True

            show_known_k_demo(
                win=win,
                urn_name=urn_names[
                    "known_k"
                ],
            )

            event.clearEvents()

            continue

        if mouse.isPressedIn(
            click_areas[
                "unknown_k"
            ]
        ):

            mouse.clickReset()

            visited[
                "unknown_k"
            ] = True

            show_unknown_k_demo(
                win=win,
                urn_name=urn_names[
                    "unknown_k"
                ],
            )

            event.clearEvents()

            continue


# -----------------------------------------------------------------------------
# Fixed-value urn
# -----------------------------------------------------------------------------


def show_fixed_urn_demo(
    win,
    urn_name,
):
    """Explain the fixed-value urn."""

    title = draw_text(
        win=win,
        text="Urn A: Fixed amount",
        pos=(0, 0.39),
        height=0.048,
        bold=True,
    )

    explanation = draw_text(
        win=win,
        text=(
            "If you choose this urn, you receive the displayed amount.\n\n"

            "You do not play the urn or make any predictions.\n"
            "You simply receive the money."
        ),
        pos=(0, 0.22),
        height=0.034,
        wrap_width=1.15,
    )

    title.draw()
    explanation.draw()

    draw_urn(
        win=win,
        urn_name=urn_name,
        pos=(0, -0.02),
        state="opened",
        size=(0.34, 0.34),
    )

    money = draw_text(
        win=win,
        text=(
            f"You receive "
            f"€{TUTORIAL_FIXED_AMOUNT:.2f}"
        ),
        pos=(0, -0.27),
        height=0.045,
        bold=True,
    )

    money.draw()

    draw_continue_text(
        win,
        text="Press SPACE to return to the urns.",
    )

    win.flip()

    wait_for_space_or_escape(win)


# -----------------------------------------------------------------------------
# Real-task-style prediction display helpers
# -----------------------------------------------------------------------------


def make_tutorial_urn(
    urn_name,
):
    """Create the minimal urn dictionary needed for practice."""

    return {
        "urn_name": urn_name,

        "opened_image": (
            get_urn_image_path(
                urn_name,
                "opened",
            )
        ),
    }


def draw_tutorial_open_urn(
    win,
    tutorial_urn,
):
    """Draw the opened urn like the real experiment."""

    urn = visual.ImageStim(
        win=win,
        image=tutorial_urn[
            "opened_image"
        ],
        pos=params.SELECTED_URN_POS,
        size=params.SELECTED_URN_SIZE,
    )

    urn.draw()


def draw_tutorial_dividers(
    win,
):
    """Draw the same divider lines as the real experiment."""

    top_line = visual.Line(
        win=win,
        start=(
            -params.DIVIDER_WIDTH / 2,
            params.TOP_DIVIDER_Y,
        ),
        end=(
            params.DIVIDER_WIDTH / 2,
            params.TOP_DIVIDER_Y,
        ),
        lineColor=params.DIVIDER_LINE_COLOR,
        lineWidth=params.DIVIDER_LINE_WIDTH,
    )

    bottom_line = visual.Line(
        win=win,
        start=(
            -params.DIVIDER_WIDTH / 2,
            params.BOTTOM_DIVIDER_Y,
        ),
        end=(
            params.DIVIDER_WIDTH / 2,
            params.BOTTOM_DIVIDER_Y,
        ),
        lineColor=params.DIVIDER_LINE_COLOR,
        lineWidth=params.DIVIDER_LINE_WIDTH,
    )

    top_line.draw()
    bottom_line.draw()


def draw_tutorial_sequence_feedback(
    win,
    sequence,
):
    """Draw the sequence in the same way as the real experiment."""

    title = draw_text(
        win=win,
        text=params.SEQUENCE_TITLE,
        pos=params.SEQUENCE_TITLE_POS,
        height=params.SEQUENCE_TITLE_HEIGHT,
        wrap_width=0.30,
        bold=True,
        align_text="left",
    )

    title.draw()

    for i, color in enumerate(
        sequence
    ):

        row = (
            i
            // params.FEEDBACK_BALLS_PER_ROW
        )

        column = (
            i
            % params.FEEDBACK_BALLS_PER_ROW
        )

        x_pos = (
            params.FEEDBACK_START_X
            + column
            * params.FEEDBACK_SPACING_X
        )

        y_pos = (
            params.FEEDBACK_START_Y
            - row
            * params.FEEDBACK_SPACING_Y
        )

        ball = visual.Circle(
            win=win,
            radius=params.FEEDBACK_BALL_RADIUS,
            pos=(
                x_pos,
                y_pos,
            ),
            fillColor=color,
            lineColor="black",
            lineWidth=1.5,
        )

        ball.draw()


# -----------------------------------------------------------------------------
# Known-k explanation
# -----------------------------------------------------------------------------


def show_known_k_explanation(
    win,
):
    """
    Explain what it means when the previous k draws are relevant.

    Example uses k=2 without explicitly revealing the repeating cycle.
    """

    # -----------------------------------------------------------------
    # Screen 1
    # -----------------------------------------------------------------

    title = draw_text(
        win=win,
        text=(
            "What does 'the previous 2 draws are relevant' mean?"
        ),
        pos=(0, 0.38),
        height=0.043,
        bold=True,
    )

    explanation = draw_text(
        win=win,
        text=(
            "It means that the TWO most recent draws together "
            "contain information about what comes next.\n\n"

            "For example, imagine the previous two draws are:"
        ),
        pos=(0, 0.21),
        height=0.032,
        wrap_width=1.15,
    )

    title.draw()
    explanation.draw()

    draw_ball(
        win=win,
        color="blue",
        pos=(-0.12, 0.04),
        radius=0.040,
    )

    draw_ball(
        win=win,
        color="magenta",
        pos=(0.02, 0.04),
        radius=0.040,
    )

    arrow = draw_text(
        win=win,
        text="→   ?",
        pos=(0.20, 0.04),
        height=0.050,
        bold=True,
    )

    arrow.draw()

    sequence_label = draw_text(
        win=win,
        text="BLUE followed by MAGENTA",
        pos=(-0.05, -0.07),
        height=0.027,
        bold=True,
    )

    sequence_label.draw()

    explanation_2 = draw_text(
        win=win,
        text=(
            "These two draws together are relevant for predicting "
            "the next outcome.\n\n"

            "You are told HOW MANY previous draws are relevant, "
            "but you are not told the exact rule that connects them "
            "to the next ball."
        ),
        pos=(0, -0.20),
        height=0.030,
        wrap_width=1.18,
    )

    explanation_2.draw()

    draw_continue_text(
        win,
        text="Press SPACE to continue.",
    )

    win.flip()

    wait_for_space_or_escape(win)

    # -----------------------------------------------------------------
    # Screen 2
    # -----------------------------------------------------------------

    title = draw_text(
        win=win,
        text="Your task is to learn the relationship",
        pos=(0, 0.36),
        height=0.046,
        bold=True,
    )

    body = draw_text(
        win=win,
        text=(
            "You will see a sequence of outcomes and make a prediction "
            "on every trial.\n\n"

            "If 2 previous draws are relevant, look at how sequences "
            "of TWO balls relate to what tends to appear next.\n\n"

            "For example:\n"
        ),
        pos=(0, 0.17),
        height=0.032,
        wrap_width=1.18,
    )

    title.draw()
    body.draw()

    draw_ball(
        win=win,
        color="blue",
        pos=(-0.13, -0.04),
        radius=0.038,
    )

    draw_ball(
        win=win,
        color="magenta",
        pos=(-0.01, -0.04),
        radius=0.038,
    )

    arrow = draw_text(
        win=win,
        text="→",
        pos=(0.10, -0.04),
        height=0.045,
        bold=True,
    )

    question_mark = draw_text(
        win=win,
        text="?",
        pos=(0.22, -0.04),
        height=0.050,
        bold=True,
    )

    arrow.draw()
    question_mark.draw()

    body_2 = draw_text(
        win=win,
        text=(
            "Watch the outcomes and use them to learn what tends "
            "to come next.\n\n"

            "You will not be shown the answer to the rule directly."
        ),
        pos=(0, -0.22),
        height=0.030,
        wrap_width=1.15,
    )

    body_2.draw()

    draw_continue_text(
        win,
        text="Press SPACE to try some predictions.",
    )

    win.flip()

    wait_for_space_or_escape(win)


# -----------------------------------------------------------------------------
# Unknown-k explanation
# -----------------------------------------------------------------------------


def show_unknown_k_explanation(
    win,
):
    """
    Explain the condition where the number of relevant
    previous draws is unknown.
    """

    title = draw_text(
        win=win,
        text="Less information about the rule",
        pos=(0, 0.38),
        height=0.048,
        bold=True,
    )

    explanation = draw_text(
        win=win,
        text=(
            "For this type of prediction urn, previous draws still "
            "contain information about what comes next.\n\n"

            "However, you are NOT told how many previous draws "
            "are relevant.\n\n"

            "You therefore need to work out both:\n\n"

            "• how many previous draws are relevant\n\n"

            "• what relationship they have with the next outcome"
        ),
        pos=(0, 0.04),
        height=0.032,
        wrap_width=1.20,
    )

    explanation_2 = draw_text(
        win=win,
        text=(
            "Use the sequence you observe and your prediction feedback "
            "to make the best predictions you can."
        ),
        pos=(0, -0.27),
        height=0.030,
        wrap_width=1.15,
    )

    title.draw()
    explanation.draw()
    explanation_2.draw()

    draw_continue_text(
        win,
        text="Press SPACE to try some predictions.",
    )

    win.flip()

    wait_for_space_or_escape(win)


# -----------------------------------------------------------------------------
# Explicit noise explanation
# -----------------------------------------------------------------------------


def show_noise_explanation(
    win,
):
    """
    Explain occasional noisy draws.

    Uses a clean k=2 example:
        underlying pattern: B M B M B M
        observed outcomes: B M B B B M

    The fourth observation is noisy:
        expected M, observed B.

    The latent rule itself continues normally afterward.
    """

    # -----------------------------------------------------------------
    # Screen 1: general explanation
    # -----------------------------------------------------------------

    title = draw_text(
        win=win,
        text="Occasionally, an outcome may differ from the rule",
        pos=(0, 0.38),
        height=0.044,
        bold=True,
    )

    explanation = draw_text(
        win=win,
        text=(
            "The prediction urns usually follow their underlying rule.\n\n"

            "However, occasionally one draw may differ from what "
            "the underlying rule would predict.\n\n"

            "We will call this a noisy draw.\n\n"

            "A noisy draw does NOT change the underlying rule. "
            "Afterward, the rule continues as before."
        ),
        pos=(0, 0.05),
        height=0.032,
        wrap_width=1.20,
    )

    title.draw()
    explanation.draw()

    draw_continue_text(
        win,
        text="Press SPACE to see an example.",
    )

    win.flip()

    wait_for_space_or_escape(win)

    # -----------------------------------------------------------------
    # Screen 2: visual example
    # -----------------------------------------------------------------

    title = draw_text(
        win=win,
        text="Example of a noisy draw",
        pos=(0, 0.41),
        height=0.047,
        bold=True,
    )

    intro = draw_text(
        win=win,
        text=(
            "Imagine that the underlying rule would produce "
            "the following pattern:"
        ),
        pos=(0, 0.31),
        height=0.030,
        wrap_width=1.15,
    )

    title.draw()
    intro.draw()

    # -------------------------------------------------------------
    # Latent pattern row
    # -------------------------------------------------------------

    pattern_label = draw_text(
        win=win,
        text="Underlying pattern:",
        pos=(-0.43, 0.17),
        height=0.029,
        bold=True,
        align_text="left",
    )

    pattern_label.draw()

    pattern = [
        "blue",
        "magenta",
        "blue",
        "magenta",
        "blue",
        "magenta",
    ]

    pattern_x = draw_ball_row(
        win=win,
        colors=pattern,
        y=0.17,
        start_x=-0.22,
        spacing=0.095,
        radius=0.031,
    )

    # -------------------------------------------------------------
    # Observed outcomes row
    # -------------------------------------------------------------

    observed_label = draw_text(
        win=win,
        text="Observed outcomes:",
        pos=(-0.43, -0.02),
        height=0.029,
        bold=True,
        align_text="left",
    )

    observed_label.draw()

    observed = [
        "blue",
        "magenta",
        "blue",
        "blue",       # Noise: expected magenta
        "blue",
        "magenta",
    ]

    observed_x = draw_ball_row(
        win=win,
        colors=observed,
        y=-0.02,
        start_x=-0.22,
        spacing=0.095,
        radius=0.031,
    )

    # -------------------------------------------------------------
    # Arrow to noise trial
    # -------------------------------------------------------------

    noisy_index = 3

    arrow = draw_text(
        win=win,
        text="↑",
        pos=(
            observed_x[
                noisy_index
            ],
            -0.105,
        ),
        height=0.050,
        bold=True,
        color="darkred",
    )

    noise_label = draw_text(
        win=win,
        text="noisy draw",
        pos=(
            observed_x[
                noisy_index
            ],
            -0.165,
        ),
        height=0.025,
        bold=True,
        color="darkred",
    )

    arrow.draw()
    noise_label.draw()

    explanation = draw_text(
        win=win,
        text=(
            "At the marked draw, the underlying pattern predicts MAGENTA, "
            "but the observed outcome is BLUE.\n\n"

            "Notice that the underlying pattern itself does not change. "
            "The following outcomes continue according to the same rule."
        ),
        pos=(0, -0.285),
        height=0.028,
        wrap_width=1.18,
    )

    explanation.draw()

    draw_continue_text(
        win,
        text="Press SPACE to continue.",
    )

    win.flip()

    wait_for_space_or_escape(win)


# -----------------------------------------------------------------------------
# Prediction practice
# -----------------------------------------------------------------------------


def collect_demo_prediction(
    win,
    tutorial_urn,
    sequence,
    instruction_text,
    trial_number,
    total_trials,
):
    """Collect one B/M practice prediction."""

    event.clearEvents()

    while True:

        instruction = draw_text(
            win=win,
            text=instruction_text,
            pos=params.TRIAL_INSTRUCTION_POS,
            height=params.TRIAL_INSTRUCTION_HEIGHT,
            wrap_width=params.TRIAL_INSTRUCTION_WRAP_WIDTH,
        )

        prompt = draw_text(
            win=win,
            text=params.GUESS_PROMPT,
            pos=params.GUESS_PROMPT_POS,
            height=params.GUESS_PROMPT_HEIGHT,
            bold=True,
        )

        counter = draw_text(
            win=win,
            text=(
                f"Practice {trial_number} / {total_trials}"
            ),
            pos=params.TRIAL_COUNTER_POS,
            height=params.TRIAL_COUNTER_HEIGHT,
            bold=True,
        )

        instruction.draw()

        draw_tutorial_dividers(
            win
        )

        draw_tutorial_sequence_feedback(
            win=win,
            sequence=sequence,
        )

        prompt.draw()
        counter.draw()

        draw_tutorial_open_urn(
            win=win,
            tutorial_urn=tutorial_urn,
        )

        win.flip()

        keys = event.getKeys(
            keyList=[
                "b",
                "m",
                "escape",
            ]
        )

        if "escape" in keys:
            quit_experiment(win)

        if "b" in keys:
            return "blue"

        if "m" in keys:
            return "magenta"


def show_demo_feedback(
    win,
    tutorial_urn,
    sequence,
    instruction_text,
    trial_number,
    total_trials,
    guess,
    outcome,
):
    """Show practice feedback using the real-task layout."""

    correct = (
        guess == outcome
    )

    result_text = (
        "Correct"
        if correct
        else "Incorrect"
    )

    result_color = (
        params.CORRECT_TEXT_COLOR
        if correct
        else params.INCORRECT_TEXT_COLOR
    )

    instruction = draw_text(
        win=win,
        text=instruction_text,
        pos=params.TRIAL_INSTRUCTION_POS,
        height=params.TRIAL_INSTRUCTION_HEIGHT,
        wrap_width=params.TRIAL_INSTRUCTION_WRAP_WIDTH,
    )

    result = draw_text(
        win=win,
        text=result_text,
        pos=params.RESULT_TEXT_POS,
        height=params.RESULT_TEXT_HEIGHT,
        bold=True,
        color=result_color,
    )

    outcome_ball = visual.Circle(
        win=win,
        radius=params.OUTCOME_BALL_RADIUS,
        pos=params.OUTCOME_BALL_POS,
        fillColor=outcome,
        lineColor="black",
        lineWidth=2,
    )

    counter = draw_text(
        win=win,
        text=(
            f"Practice {trial_number} / {total_trials}"
        ),
        pos=params.TRIAL_COUNTER_POS,
        height=params.TRIAL_COUNTER_HEIGHT,
        bold=True,
    )

    instruction.draw()

    draw_tutorial_dividers(
        win
    )

    draw_tutorial_sequence_feedback(
        win=win,
        sequence=sequence,
    )

    result.draw()
    outcome_ball.draw()
    counter.draw()

    draw_tutorial_open_urn(
        win=win,
        tutorial_urn=tutorial_urn,
    )

    win.flip()

    core.wait(
        params.REVEAL_DURATION
    )

    event.clearEvents()

    core.wait(
        params.INTER_TRIAL_INTERVAL
    )


# -----------------------------------------------------------------------------
# Known-k prediction practice
# -----------------------------------------------------------------------------


def run_known_k_prediction_demo(
    win,
    urn_name,
):
    """
    Run a short known-k practice task.

    The participant is told that the previous 2 draws
    are relevant together.

    As in the actual experiment, 4 initial draws are shown.
    """

    tutorial_urn = make_tutorial_urn(
        urn_name
    )

    # k = 2 latent example:
    #
    # B M B M | B M B M B M
    #
    # Always show 4 initial draws, matching the real experiment.
    sequence = [
        "blue",
        "magenta",
        "blue",
        "magenta",
    ]

    instruction_text = (
        "The next ball depends on the previous 2 draws.\n"
        "The exact rule is unknown.\n"
        "(B = Blue, M = Magenta)"
    )

    demo_outcomes = [
        "blue",
        "magenta",
        "blue",
        "magenta",
        "blue",
        "magenta",
    ]

    score = 0

    total_trials = len(
        demo_outcomes
    )

    for (
        trial_number,
        outcome,
    ) in enumerate(
        demo_outcomes,
        start=1,
    ):

        guess = collect_demo_prediction(
            win=win,
            tutorial_urn=tutorial_urn,
            sequence=sequence,
            instruction_text=instruction_text,
            trial_number=trial_number,
            total_trials=total_trials,
        )

        if guess == outcome:
            score += 1

        sequence.append(
            outcome
        )

        show_demo_feedback(
            win=win,
            tutorial_urn=tutorial_urn,
            sequence=sequence,
            instruction_text=instruction_text,
            trial_number=trial_number,
            total_trials=total_trials,
            guess=guess,
            outcome=outcome,
        )

    return score


# -----------------------------------------------------------------------------
# Unknown-k prediction practice
# -----------------------------------------------------------------------------


def run_unknown_k_prediction_demo(
    win,
    urn_name,
):
    """
    Run a short unknown-k practice task.

    The participant knows that previous draws matter,
    but not how many.

    Again, 4 initial draws are shown so the number of initial
    observations does not reveal k.
    """

    tutorial_urn = make_tutorial_urn(
        urn_name
    )

    # Latent k = 3 example:
    #
    # B B M B | B M B B M B ...
    #
    # Four initial draws are shown just as in the actual task.
    sequence = [
        "blue",
        "blue",
        "magenta",
        "blue",
    ]

    instruction_text = (
        "The next ball depends on previous draws.\n"
        "You are not told how many previous draws are relevant.\n"
        "The exact rule is unknown.\n"
        "(B = Blue, M = Magenta)"
    )

    # Continue the underlying B-B-M cycle from position 4.
    demo_outcomes = [
        "blue",
        "magenta",
        "blue",
        "blue",
        "magenta",
        "blue",
    ]

    score = 0

    total_trials = len(
        demo_outcomes
    )

    for (
        trial_number,
        outcome,
    ) in enumerate(
        demo_outcomes,
        start=1,
    ):

        guess = collect_demo_prediction(
            win=win,
            tutorial_urn=tutorial_urn,
            sequence=sequence,
            instruction_text=instruction_text,
            trial_number=trial_number,
            total_trials=total_trials,
        )

        if guess == outcome:
            score += 1

        sequence.append(
            outcome
        )

        show_demo_feedback(
            win=win,
            tutorial_urn=tutorial_urn,
            sequence=sequence,
            instruction_text=instruction_text,
            trial_number=trial_number,
            total_trials=total_trials,
            guess=guess,
            outcome=outcome,
        )

    return score


# -----------------------------------------------------------------------------
# Known-k prediction urn
# -----------------------------------------------------------------------------


def show_known_k_demo(
    win,
    urn_name,
):
    """Explain and demonstrate the known-k prediction urn."""

    title = draw_text(
        win=win,
        text="Urn B: Prediction task",
        pos=(0, 0.38),
        height=0.050,
        bold=True,
    )

    explanation = draw_text(
        win=win,
        text=(
            "If you choose this urn, you play a prediction task.\n\n"

            "You predict whether the next ball will be BLUE or MAGENTA.\n\n"

            "The more correct predictions you make, the more money "
            "you can earn.\n\n"

            "This means that you have the chance to earn more money "
            "than with the fixed-value urn.\n\n"

            "For this type of urn, you are told HOW MANY previous draws "
            "are relevant for predicting the next ball.\n\n"

            "You are not told the exact rule."
        ),
        pos=(0, 0.02),
        height=0.031,
        wrap_width=1.20,
    )

    title.draw()
    explanation.draw()

    draw_continue_text(
        win,
        text="Press SPACE to learn more.",
    )

    win.flip()

    wait_for_space_or_escape(win)

    show_known_k_explanation(
        win
    )

    score = run_known_k_prediction_demo(
        win=win,
        urn_name=urn_name,
    )

    show_demo_complete(
        win=win,
        score=score,
        total_trials=6,
    )


# -----------------------------------------------------------------------------
# Unknown-k prediction urn
# -----------------------------------------------------------------------------


def show_unknown_k_demo(
    win,
    urn_name,
):
    """Explain and demonstrate the unknown-k prediction urn."""

    title = draw_text(
        win=win,
        text="Urn C: Prediction task",
        pos=(0, 0.38),
        height=0.050,
        bold=True,
    )

    explanation = draw_text(
        win=win,
        text=(
            "If you choose this urn, you also play a prediction task.\n\n"

            "You predict whether the next ball will be BLUE or MAGENTA.\n\n"

            "The more correct predictions you make, the more money "
            "you can earn.\n\n"

            "This means that you have the chance to earn more money "
            "than with the fixed-value urn.\n\n"

            "For this type of urn, previous draws are relevant, "
            "but you are NOT told HOW MANY previous draws are relevant.\n\n"

            "You are also not told the exact rule."
        ),
        pos=(0, 0.01),
        height=0.031,
        wrap_width=1.20,
    )

    title.draw()
    explanation.draw()

    draw_continue_text(
        win,
        text="Press SPACE to learn more.",
    )

    win.flip()

    wait_for_space_or_escape(win)

    show_unknown_k_explanation(
        win
    )

    score = run_unknown_k_prediction_demo(
        win=win,
        urn_name=urn_name,
    )

    show_demo_complete(
        win=win,
        score=score,
        total_trials=6,
    )


# -----------------------------------------------------------------------------
# Practice completion
# -----------------------------------------------------------------------------


def show_demo_complete(
    win,
    score,
    total_trials,
):
    """Show results from one prediction practice."""

    title = draw_text(
        win=win,
        text="Practice complete",
        pos=(0, 0.30),
        height=0.050,
        bold=True,
    )

    results = draw_text(
        win=win,
        text=(
            f"You made {score} correct predictions "
            f"out of {total_trials}.\n\n"

            f"In this example, that would earn you "
            f"€{score * TUTORIAL_CORRECT_GUESS_AMOUNT:.2f}.\n\n"

            "The more correct predictions you make, "
            "the more money you can earn."
        ),
        pos=(0, 0.01),
        height=0.035,
        wrap_width=1.15,
    )

    title.draw()
    results.draw()

    draw_continue_text(
        win,
        text="Press SPACE to return to the urns.",
    )

    win.flip()

    wait_for_space_or_escape(win)


# -----------------------------------------------------------------------------
# Explain actual LEFT / RIGHT choice
# -----------------------------------------------------------------------------


def show_choice_explanation(
    win,
    left_urn_name,
    right_urn_name,
):
    """
    Let the participant practice selecting an urn
    using the LEFT and RIGHT arrow keys.
    """

    event.clearEvents()

    selected_side = None

    while True:

        # -------------------------------------------------------------
        # Main instruction
        # -------------------------------------------------------------

        if selected_side is None:

            instruction_text = (
                "Two urns will be shown side by side.\n"
                "Press the LEFT or RIGHT arrow key to select the urn you prefer."
            )

        elif selected_side == "left":

            instruction_text = (
                "You selected Urn A."
            )

        else:

            instruction_text = (
                "You selected Urn B."
            )

        instruction = draw_text(
            win=win,
            text=instruction_text,
            pos=(0, 0.37),
            height=0.035,
            wrap_width=1.20,
            bold=(
                selected_side is not None
            ),
        )

        instruction.draw()

        # -------------------------------------------------------------
        # Left urn
        # -------------------------------------------------------------

        draw_urn(
            win=win,
            urn_name=left_urn_name,
            pos=params.URN_LEFT_POS,
            label="Urn A",
            state="closed",
        )

        # -------------------------------------------------------------
        # Right urn
        # -------------------------------------------------------------

        draw_urn(
            win=win,
            urn_name=right_urn_name,
            pos=params.URN_RIGHT_POS,
            label="Urn B",
            state="closed",
        )

        # -------------------------------------------------------------
        # Instructions directly underneath each urn
        # -------------------------------------------------------------

        left_instruction_y = (
            params.URN_LEFT_POS[1]
            - params.URN_IMAGE_SIZE[1] / 2
            - 0.06
        )

        right_instruction_y = (
            params.URN_RIGHT_POS[1]
            - params.URN_IMAGE_SIZE[1] / 2
            - 0.06
        )

        left_text = draw_text(
            win=win,
            text="Press LEFT",
            pos=(
                params.URN_LEFT_POS[0],
                left_instruction_y,
            ),
            height=0.030,
            bold=True,
        )

        right_text = draw_text(
            win=win,
            text="Press RIGHT",
            pos=(
                params.URN_RIGHT_POS[0],
                right_instruction_y,
            ),
            height=0.030,
            bold=True,
        )

        left_text.draw()
        right_text.draw()

        # -------------------------------------------------------------
        # After a choice has been made, show continuation instruction
        # -------------------------------------------------------------

        if selected_side is not None:

            draw_continue_text(
                win,
                text="Press SPACE to continue.",
            )

        win.flip()

        # -------------------------------------------------------------
        # Keyboard
        # -------------------------------------------------------------

        if selected_side is None:

            keys = event.waitKeys(
                keyList=[
                    "left",
                    "right",
                    "escape",
                ]
            )

        else:

            keys = event.waitKeys(
                keyList=[
                    "left",
                    "right",
                    "space",
                    "escape",
                ]
            )

        # -------------------------------------------------------------
        # Escape
        # -------------------------------------------------------------

        if "escape" in keys:

            quit_experiment(
                win
            )

        # -------------------------------------------------------------
        # LEFT
        # -------------------------------------------------------------

        if "left" in keys:

            selected_side = "left"

            continue

        # -------------------------------------------------------------
        # RIGHT
        # -------------------------------------------------------------

        if "right" in keys:

            selected_side = "right"

            continue

        # -------------------------------------------------------------
        # SPACE
        # -------------------------------------------------------------

        if (
            "space" in keys
            and selected_side is not None
        ):

            return


# -----------------------------------------------------------------------------
# Final summary
# -----------------------------------------------------------------------------


def show_final_instructions(
    win,
):
    """Summarize the task before the experiment starts."""

    title = draw_text(
        win=win,
        text="Summary",
        pos=(0, 0.39),
        height=0.052,
        bold=True,
    )

    body = draw_text(
        win=win,
        text=(
            "FIXED-VALUE URN\n"
            "You do not play the urn.\n"
            "You simply receive the displayed amount of money.\n\n"

            "PREDICTION URN\n"
            "You predict whether the next ball will be BLUE or MAGENTA.\n"
            "The more correct predictions you make, the more money you earn.\n"
            "You therefore have the chance to earn more money.\n\n"

            "Previous draws contain information about what comes next.\n"
            "Sometimes you will be told how many previous draws are relevant, "
            "and sometimes you will need to work this out yourself.\n\n"

            "Most outcomes follow the underlying rule, but occasionally "
            "an outcome may differ from what the rule predicts.\n\n"
        ),
        pos=(0, 0.01),
        height=0.028,
        wrap_width=1.25,
    )

    title.draw()
    body.draw()

    draw_continue_text(
        win,
        text="Press SPACE to begin the experiment.",
        bold=True,
    )

    win.flip()

    wait_for_space_or_escape(win)


# -----------------------------------------------------------------------------
# Main tutorial
# -----------------------------------------------------------------------------


def run_instructions(
    win,
):
    """
    Run the full interactive tutorial.

    Flow:

        1. General introduction.
        2. Show three urns together.
        3. Participant clicks each urn in any order.
        4. Fixed urn explains guaranteed payment.
        5. Known-k prediction urn explains:
              - k previous draws matter together
              - k itself is disclosed.
        6. Unknown-k prediction urn explains:
              - previous draws matter
              - number of relevant draws is not disclosed.
        7. As soon as BOTH prediction urns have been explored,
           explicitly explain noisy draws with a visual example.
        8. Explain LEFT/RIGHT preference response.
        9. Final summary.
    """

    tutorial_urns = random.sample(
        params.PRETTY_URN_NAMES,
        5,
    )

    urn_names = {
        "fixed": tutorial_urns[0],
        "known_k": tutorial_urns[1],
        "unknown_k": tutorial_urns[2],
    }

    choice_left_urn = (
        tutorial_urns[3]
    )

    choice_right_urn = (
        tutorial_urns[4]
    )

    # -----------------------------------------------------------------
    # Introduction
    # -----------------------------------------------------------------

    show_intro(
        win
    )

    # -----------------------------------------------------------------
    # Interactive exploration
    #
    # Noise explanation is triggered automatically inside this
    # function once both prediction urns have been explored.
    # -----------------------------------------------------------------

    show_urn_overview(
        win=win,
        urn_names=urn_names,
    )

    # -----------------------------------------------------------------
    # Explain actual left/right choice response
    # -----------------------------------------------------------------

    show_choice_explanation(
        win=win,
        left_urn_name=choice_left_urn,
        right_urn_name=choice_right_urn,
    )

    # -----------------------------------------------------------------
    # Final summary
    # -----------------------------------------------------------------

    show_final_instructions(
        win
    )


# -----------------------------------------------------------------------------
# Standalone test
# -----------------------------------------------------------------------------


if __name__ == "__main__":

    win = visual.Window(
        size=params.WINDOW_SIZE,
        fullscr=params.FULLSCREEN,
        color=params.BACKGROUND_COLOR,
        units="height",
    )

    run_instructions(
        win
    )

    win.close()