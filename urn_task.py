from psychopy import visual, event, core
import random

import urn_params as params
from questions_task import run_post_block_questions


# -----------------------------------------------------------------------------
# General drawing helpers
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


def get_urn_image_path(
    urn_name,
    state,
):
    """Return the path to a pretty-urn image."""

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


def create_image_urn(
    win,
    pos,
    label_text,
    image_path,
    size=None,
    show_label=True,
    bottom_text=None,
):
    """Create an urn image, with an optional label above and text below."""

    urn_size = (
        params.URN_IMAGE_SIZE
        if size is None
        else size
    )

    urn_image = visual.ImageStim(
        win=win,
        image=image_path,
        pos=pos,
        size=urn_size,
    )

    parts = [urn_image]

    if show_label:
        label_y_offset = urn_size[1] / 2 + 0.07

        label = visual.TextStim(
            win=win,
            text=label_text,
            pos=(
                pos[0],
                pos[1] + label_y_offset,
            ),
            color=params.TEXT_COLOR,
            height=params.LABEL_HEIGHT,
            bold=True,
            font="Arial",
        )

        parts.append(label)

    if bottom_text is not None:
        bottom_y_offset = urn_size[1] / 2 + 0.06

        response = visual.TextStim(
            win=win,
            text=bottom_text,
            pos=(
                pos[0],
                pos[1] - bottom_y_offset,
            ),
            color=params.TEXT_COLOR,
            height=0.028,
            bold=True,
            font="Arial",
        )

        parts.append(response)

    return parts


def draw_all(parts):
    """Draw all stimuli in a list."""

    for part in parts:

        part.draw()


def quit_experiment(win):
    """Close the window and terminate the experiment."""

    win.close()

    core.quit()


# -----------------------------------------------------------------------------
# k-cycle generation
# -----------------------------------------------------------------------------


def has_smaller_period(sequence):
    """
    Return True if the sequence is actually generated
    by a shorter repeating period.
    """

    n = len(
        sequence
    )

    for period in range(
        1,
        n,
    ):

        if n % period != 0:

            continue

        matches = True

        for i in range(n):

            if (
                sequence[i]
                != sequence[
                    i % period
                ]
            ):

                matches = False

                break

        if matches:

            return True

    return False


def generate_k_cycle(k):
    """Generate a genuine cycle of length k."""

    while True:

        cycle = [
            random.choice(
                params.BALL_COLORS
            )
            for _ in range(k)
        ]

        if not has_smaller_period(
            cycle
        ):

            return cycle


def serialise_cycle(cycle):
    """Convert a cycle to a readable string."""

    return "-".join(
        cycle
    )


def cycles_match(
    true_cycle,
    response_cycle,
):
    """
    Check whether two cycles are equivalent up to rotation.

    Example:

        B B M
        B M B
        M B B

    all represent the same repeating 3-cycle.
    """

    if len(true_cycle) != len(
        response_cycle
    ):

        return False

    doubled = (
        true_cycle
        + true_cycle
    )

    k = len(
        true_cycle
    )

    for start in range(k):

        rotation = (
            doubled[
                start:
                start + k
            ]
        )

        if rotation == response_cycle:

            return True

    return False


def generate_latent_sequence(
    cycle,
    n_draws,
):
    """
    Generate a specified number of clean observations
    from the latent cycle.

    Example:

        cycle = [blue, blue, magenta]
        n_draws = 7

    gives:

        blue
        blue
        magenta
        blue
        blue
        magenta
        blue
    """

    k = len(
        cycle
    )

    return [
        cycle[i % k]
        for i in range(
            n_draws
        )
    ]


# -----------------------------------------------------------------------------
# Urn conditions
# -----------------------------------------------------------------------------



# -----------------------------------------------------------------------------
# Urn conditions
# -----------------------------------------------------------------------------


def create_ambiguous_urn(
    urn_name,
    label,
    ambiguous_condition,
):
    """
    Create one ambiguous urn.

    ambiguous_condition must be:
        "known"
        or
        "unknown"
    """

    k = random.choice(
        params.AMBIGUOUS_K_OPTIONS
    )

    cycle = generate_k_cycle(
        k
    )

    if ambiguous_condition == "known":

        return {
            "urn_type": "ambiguous",
            "urn_name": urn_name,
            "label": label,

            "closed_image": get_urn_image_path(
                urn_name,
                "closed",
            ),

            "opened_image": get_urn_image_path(
                urn_name,
                "opened",
            ),

            "condition": (
                params.CONDITION_KNOWN_X_UNKNOWN_F
            ),

            "condition_description": (
                params.KNOWN_X_DESCRIPTION
            ),

            "participant_knows_k": True,

            "ambiguous_k": k,
            "cycle": cycle,

            # Money depends on performance
            "payoff_type": "performance",
            "value": None,
        }

    elif ambiguous_condition == "unknown":

        return {
            "urn_type": "ambiguous",
            "urn_name": urn_name,
            "label": label,

            "closed_image": get_urn_image_path(
                urn_name,
                "closed",
            ),

            "opened_image": get_urn_image_path(
                urn_name,
                "opened",
            ),

            "condition": (
                params.CONDITION_UNKNOWN_X_UNKNOWN_F
            ),

            "condition_description": (
                params.UNKNOWN_X_DESCRIPTION
            ),

            "participant_knows_k": False,

            "ambiguous_k": k,
            "cycle": cycle,

            "payoff_type": "performance",
            "value": None,
        }

    raise ValueError(
        "ambiguous_condition must be 'known' or 'unknown'"
    )


def create_deterministic_urn(
    urn_name,
    label,
    value,
):
    """
    Create the sure-value urn.

    The participant can still play prediction trials,
    but its monetary payoff is fixed and does not
    increase as a result of correct predictions.
    """

    # Give it a sequence so that it remains playable.
    #
    # You can change this later if the deterministic
    # urn should use a different sequence-generating rule.
    k = random.choice(
        params.AMBIGUOUS_K_OPTIONS
    )

    cycle = generate_k_cycle(
        k
    )

    return {
        "urn_type": "deterministic",
        "urn_name": urn_name,
        "label": label,

        "closed_image": get_urn_image_path(
            urn_name,
            "closed",
        ),

        "opened_image": get_urn_image_path(
            urn_name,
            "opened",
        ),

        "condition": "deterministic",

        "condition_description": (
            f"Fixed value: €{value:.2f}"
        ),

        # These allow the existing prediction-game
        # functions to work without crashing.
        "participant_knows_k": True,
        "ambiguous_k": k,
        "cycle": cycle,

        # Important distinction
        "payoff_type": "fixed",
        "value": value,
    }


def assign_urns_to_sides(
    deterministic_value,
    ambiguous_condition,
):
    """Pair one deterministic and one ambiguous urn."""

    urn_names = random.sample(
        params.PRETTY_URN_NAMES,
        2,
    )

    deterministic_side = random.choice(
        ["left", "right"]
    )

    ambiguous_side = (
        "right"
        if deterministic_side == "left"
        else "left"
    )

    side_labels = {
        "left": params.LEFT_URN_LABEL,
        "right": params.RIGHT_URN_LABEL,
    }

    side_names = {
        "left": urn_names[0],
        "right": urn_names[1],
    }

    assignment = {}

    assignment[deterministic_side] = (
        create_deterministic_urn(
            urn_name=side_names[
                deterministic_side
            ],
            label=side_labels[
                deterministic_side
            ],
            value=deterministic_value,
        )
    )

    assignment[ambiguous_side] = (
        create_ambiguous_urn(
            urn_name=side_names[
                ambiguous_side
            ],
            label=side_labels[
                ambiguous_side
            ],
            ambiguous_condition=ambiguous_condition,
        )
    )

    return assignment

# -----------------------------------------------------------------------------
# Selection screen
# -----------------------------------------------------------------------------


def draw_selection_condition_text(
    win,
    urn,
    x_pos,
):
    """Draw condition/value information below an urn."""

    if urn["urn_type"] == "deterministic":

        condition_text = (
            f"Fixed value: €{urn['value']:.2f}\n\n"
            "Number of correct answers do not change this amount."
        )

    else:

        if urn["participant_knows_k"]:
            info_text = (
                urn["condition_description"].format(
                    k=urn["ambiguous_k"]
                )
            )
        else:
            info_text = urn["condition_description"]

        condition_text = (
            f"{info_text}\n\n"
            f"Earn €{params.REWARD_PER_CORRECT_GUESS:.2f} "
            "for each correct answer.\n"
            f"Maximum: €{params.MAX_AMBIGUOUS_REWARD:.2f}"
        )

    text_stim = draw_text(
        win=win,
        text=condition_text,
        pos=(
            x_pos,
            params.CONDITION_TEXT_Y,
        ),
        height=params.CONDITION_TEXT_HEIGHT,
        wrap_width=params.CONDITION_TEXT_WRAP_WIDTH,
    )

    text_stim.draw()


def collect_urn_choice(
    win,
    urn_assignment,
):
    """Select left or right urn using the arrow keys."""

    event.clearEvents()

    while True:

        title = draw_text(
            win=win,
            text=params.SELECT_INSTRUCTIONS,
            pos=(
                0,
                0.40,
            ),
            height=0.047,
            bold=True,
        )

        choice_instruction = draw_text(
            win=win,
            text="Press LEFT for Urn A or RIGHT for Urn B.",
            pos=(
                0,
                0.31,
            ),
            height=0.028,
            bold=False,
        )

        left_display = create_image_urn(
            win=win,
            pos=params.URN_LEFT_POS,
            label_text=urn_assignment["left"]["label"],
            image_path=urn_assignment["left"]["closed_image"],
            bottom_text=None,
        )

        right_display = create_image_urn(
            win=win,
            pos=params.URN_RIGHT_POS,
            label_text=urn_assignment["right"]["label"],
            image_path=urn_assignment["right"]["closed_image"],
            bottom_text=None,
        )

        bottom_text = draw_text(
            win=win,
            text=params.SELECTION_BOTTOM_TEXT,
            pos=(
                0,
                -0.45,
            ),
            height=0.024,
        )

        title.draw()
        choice_instruction.draw()

        draw_all(left_display)
        draw_all(right_display)

        draw_selection_condition_text(
            win=win,
            urn=urn_assignment["left"],
            x_pos=params.URN_LEFT_POS[0],
        )

        draw_selection_condition_text(
            win=win,
            urn=urn_assignment["right"],
            x_pos=params.URN_RIGHT_POS[0],
        )

        bottom_text.draw()

        win.flip()

        keys = event.waitKeys(
            keyList=[
                "left",
                "right",
                "escape",
            ]
        )

        if "escape" in keys:
            quit_experiment(win)

        if "left" in keys:
            return "left"

        if "right" in keys:
            return "right"


# -----------------------------------------------------------------------------
# Noise schedule
# -----------------------------------------------------------------------------


def create_noise_schedule(
    n_trials,
    pattern_probability,
):
    """
    Create an exact randomly shuffled noise schedule.

    With 20 trials and p=.80 this gives:
        16 rule-consistent trials
        4 noise trials
    """

    n_pattern = round(
        n_trials
        * pattern_probability
    )

    n_noise = (
        n_trials
        - n_pattern
    )

    schedule = (
        [False] * n_pattern
        + [True] * n_noise
    )

    random.shuffle(
        schedule
    )

    return schedule


# -----------------------------------------------------------------------------
# Latent sequence
# -----------------------------------------------------------------------------


def get_pattern_prediction(
    cycle,
    prediction_index,
):
    """
    Return the expected outcome from the fixed latent cycle.
    """

    k = len(
        cycle
    )

    cycle_position = (
        prediction_index
        % k
    )

    return cycle[
        cycle_position
    ]


def opposite_color(color):
    """Return the opposite ball color."""

    if color == "blue":

        return "magenta"

    if color == "magenta":

        return "blue"

    raise ValueError(
        f"Unknown color: {color}"
    )


def generate_next_outcome(
    selected_urn,
    prediction_index,
    is_noise_trial,
):
    """
    Generate one observed outcome.

    Rule trial:
        display the latent-cycle outcome.

    Noise trial:
        display the opposite color.

    Noise does not change later positions in the latent cycle.
    """

    cycle = (
        selected_urn[
            "cycle"
        ]
    )

    pattern_prediction = (
        get_pattern_prediction(
            cycle=cycle,
            prediction_index=prediction_index,
        )
    )

    if is_noise_trial:

        outcome = opposite_color(
            pattern_prediction
        )

    else:

        outcome = (
            pattern_prediction
        )

    return (
        outcome,
        pattern_prediction,
    )


# -----------------------------------------------------------------------------
# Trial display
# -----------------------------------------------------------------------------


def draw_trial_dividers(win):
    """Draw horizontal divider lines."""

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


def draw_sequence_feedback(
    win,
    sequence,
):
    """Draw the observed ball history."""

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


def get_trial_instruction(
    selected_urn,
):
    """Return the correct condition-specific instruction."""

    if selected_urn[
        "urn_type"
    ] == "deterministic":

        return (
            "Do you think the next ball will be "
            "BLUE or MAGENTA?\n"
            "Your performance does not change your "
            "fixed reward.\n"
            "(B = Blue, M = Magenta)"
        )

    if selected_urn[
        "participant_knows_k"
    ]:

        return (
            params.KNOWN_X_TRIAL_INSTRUCTION.format(
                k=selected_urn[
                    "ambiguous_k"
                ]
            )
        )

    return (
        params.UNKNOWN_X_TRIAL_INSTRUCTION
    )


def draw_selected_open_urn(
    win,
    selected_urn,
):
    """Draw the selected urn during prediction trials."""

    urn_display = create_image_urn(
        win=win,
        pos=params.SELECTED_URN_POS,
        label_text=selected_urn[
            "label"
        ],
        image_path=selected_urn[
            "opened_image"
        ],
        size=params.SELECTED_URN_SIZE,
        show_label=False,
    )

    draw_all(
        urn_display
    )


def collect_prediction(
    win,
    selected_urn,
    sequence,
    trial_number,
    total_trials=None,
):
    """Collect one B/M prediction and reaction time."""
    if total_trials is None:
        total_trials = params.N_TRIALS_PER_BLOCK
    event.clearEvents()

    response_clock = (
        core.Clock()
    )

    while True:

        instruction = draw_text(
            win=win,
            text=get_trial_instruction(
                selected_urn
            ),
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
                f"{trial_number} / "
                f"{total_trials}"
            ),
            pos=params.TRIAL_COUNTER_POS,
            height=params.TRIAL_COUNTER_HEIGHT,
            bold=True,
        )

        instruction.draw()

        draw_trial_dividers(
            win
        )

        draw_sequence_feedback(
            win=win,
            sequence=sequence,
        )

        prompt.draw()

        draw_selected_open_urn(
            win=win,
            selected_urn=selected_urn,
        )

        counter.draw()

        win.flip()

        keys = event.getKeys(
            keyList=(
                list(
                    params.GUESS_KEYS.keys()
                )
                + ["escape"]
            ),
            timeStamped=response_clock,
        )

        if keys:

            key, response_time = (
                keys[0]
            )

            if key == "escape":

                quit_experiment(
                    win
                )

            return (
                params.GUESS_KEYS[
                    key
                ],
                response_time,
            )


def show_trial_outcome(
    win,
    selected_urn,
    sequence,
    trial_number,
    guess,
    outcome,
    total_trials=None,
    wait_for_continue=False,
):
    """Show the actual outcome and correctness feedback."""

    if total_trials is None:
        total_trials = params.N_TRIALS_PER_BLOCK

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
        text=get_trial_instruction(
            selected_urn
        ),
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
            f"{trial_number} / "
            f"{total_trials}"
        ),
        pos=params.TRIAL_COUNTER_POS,
        height=params.TRIAL_COUNTER_HEIGHT,
        bold=True,
    )

    # -------------------------------------------------------------
    # Draw normal trial screen
    # -------------------------------------------------------------

    instruction.draw()

    draw_trial_dividers(
        win
    )

    draw_sequence_feedback(
        win=win,
        sequence=sequence,
    )

    result.draw()
    outcome_ball.draw()

    draw_selected_open_urn(
        win=win,
        selected_urn=selected_urn,
    )

    counter.draw()

    # -------------------------------------------------------------
    # On the final trial, add the SPACE prompt
    # -------------------------------------------------------------

    if wait_for_continue:

        continue_text = draw_text(
            win=win,
            text=params.SELECTED_URN_CONTINUE_TEXT,
            pos=(0, -0.20),
            height=0.034,
            wrap_width=1.10,
        )

        continue_text.draw()

    # Show everything
    win.flip()

    # -------------------------------------------------------------
    # Waiting behaviour
    # -------------------------------------------------------------

    if wait_for_continue:

        # Clear any old key presses before waiting
        event.clearEvents()

        keys = event.waitKeys(
            keyList=[
                "space",
                "escape",
            ]
        )

        if "escape" in keys:
            quit_experiment(
                win
            )

    else:

        # Normal trials only stay visible briefly
        core.wait(
            params.REVEAL_DURATION
        )

        event.clearEvents()

        core.wait(
            params.INTER_TRIAL_INTERVAL
        )


# -----------------------------------------------------------------------------
# Prediction block
# -----------------------------------------------------------------------------


def run_trials(
    win,
    selected_urn,
    n_trials=None,
):
    """
    Run one complete prediction block.

    Every participant sees the same number of initial draws,
    regardless of k.

    The latent cycle continues from those initial draws rather
    than restarting when prediction trial 1 begins.

    After the final prediction, the participant can inspect the
    complete ball history and must press SPACE to continue.
    """

    if n_trials is None:
        n_trials = params.N_TRIALS_PER_BLOCK

    k = selected_urn[
        "ambiguous_k"
    ]

    cycle = selected_urn[
        "cycle"
    ]

    # -----------------------------------------------------------------
    # Initial observations
    # -----------------------------------------------------------------

    seed_sequence = (
        generate_latent_sequence(
            cycle=cycle,
            n_draws=params.N_INITIAL_DRAWS,
        )
    )

    sequence = list(
        seed_sequence
    )

    # -----------------------------------------------------------------
    # Noise schedule
    # -----------------------------------------------------------------

    noise_schedule = (
        create_noise_schedule(
            n_trials,
            params.PATTERN_PROBABILITY,
        )
    )

    trial_data = []

    # -----------------------------------------------------------------
    # Trials
    # -----------------------------------------------------------------

    for (
        trial_number,
        is_noise_trial,
    ) in enumerate(
        noise_schedule,
        start=1,
    ):

        history_before_draw = list(
            sequence
        )

        guess, response_time = (
            collect_prediction(
                win=win,
                selected_urn=selected_urn,
                sequence=sequence,
                trial_number=trial_number,
                total_trials=n_trials,
            )
        )

        # Absolute position in the latent sequence.
        #
        # Example:
        #
        # If 4 initial balls were already displayed, prediction
        # trial 1 corresponds to latent position 4.
        prediction_index = (
            params.N_INITIAL_DRAWS
            + trial_number
            - 1
        )

        (
            outcome,
            pattern_prediction,
        ) = generate_next_outcome(
            selected_urn=selected_urn,
            prediction_index=prediction_index,
            is_noise_trial=is_noise_trial,
        )

        sequence.append(
            outcome
        )

        correct = (
            guess == outcome
        )

        outcome_matches_pattern = (
            outcome
            == pattern_prediction
        )

        cycle_position = (
            prediction_index
            % k
        )

        trial_data.append(
            {
                "trial_number": trial_number,

                "guess": guess,
                "outcome": outcome,
                "correct": correct,
                "response_time": response_time,

                "k": k,

                "prediction_index": (
                    prediction_index
                ),

                "cycle_position": (
                    cycle_position
                ),

                "is_noise_trial": (
                    is_noise_trial
                ),

                "pattern_prediction": (
                    pattern_prediction
                ),

                "outcome_matches_pattern": (
                    outcome_matches_pattern
                ),

                "history_before_draw": (
                    history_before_draw
                ),

                "payoff_type": (
                    selected_urn[
                        "payoff_type"
                    ]
                ),

                "prediction_affects_earnings": (
                    selected_urn[
                        "payoff_type"
                    ]
                    == "performance"
                ),
            }
        )

        # -------------------------------------------------------------
        # Show outcome
        #
        # On the final trial, keep the full history on screen and
        # wait for the participant to press SPACE.
        # -------------------------------------------------------------

        wait_for_continue = (
            trial_number
            == n_trials
        )

        show_trial_outcome(
            win=win,
            selected_urn=selected_urn,
            sequence=sequence,
            trial_number=trial_number,
            guess=guess,
            outcome=outcome,
            total_trials=n_trials,
            wait_for_continue=wait_for_continue,
        )

    # -----------------------------------------------------------------
    # Summary
    # -----------------------------------------------------------------

    number_correct = sum(
        row["correct"]
        for row in trial_data
    )

    accuracy = (
        number_correct
        / len(trial_data)
    )

    # -----------------------------------------------------------------
    # Block earnings
    # -----------------------------------------------------------------

    if selected_urn[
        "urn_type"
    ] == "ambiguous":

        block_earnings = (
            number_correct
            * params.REWARD_PER_CORRECT_GUESS
        )

    else:

        block_earnings = (
            selected_urn[
                "value"
            ]
        )

    # -----------------------------------------------------------------
    # Print rule information for debugging/piloting
    # -----------------------------------------------------------------

    print(
        "\n"
        + "=" * 70
    )

    print(
        "BLOCK RULE INFORMATION"
    )

    print(
        "=" * 70
    )

    print(
        f"k = {k}"
    )

    print(
        "Underlying cycle:",
        serialise_cycle(
            cycle
        ),
    )

    print(
        "Initial draws:",
        seed_sequence,
    )

    print(
        "Noise trials:",
        [
            i + 1
            for i, is_noise
            in enumerate(
                noise_schedule
            )
            if is_noise
        ],
    )

    print(
        "Latent pattern predictions:",
        [
            row[
                "pattern_prediction"
            ]
            for row
            in trial_data
        ],
    )

    print(
        "Actual observed outcomes:",
        [
            row[
                "outcome"
            ]
            for row
            in trial_data
        ],
    )

    print(
        "Full observed sequence:",
        sequence,
    )

    print(
        "=" * 70
        + "\n"
    )

    return {
        "seed_sequence": (
            seed_sequence
        ),

        "full_sequence": (
            sequence
        ),

        "trial_data": (
            trial_data
        ),

        "number_correct": (
            number_correct
        ),

        "accuracy": (
            accuracy
        ),

        "number_noise_trials": sum(
            row[
                "is_noise_trial"
            ]
            for row
            in trial_data
        ),

        "number_pattern_trials": sum(
            not row[
                "is_noise_trial"
            ]
            for row
            in trial_data
        ),

        "number_pattern_consistent": sum(
            row[
                "outcome_matches_pattern"
            ]
            for row
            in trial_data
        ),

        "block_earnings": (
            block_earnings
        ),

        "reward_per_correct_guess": (
            params.REWARD_PER_CORRECT_GUESS
        ),
    }

# -----------------------------------------------------------------------------
# Ambiguous-condition schedule
# -----------------------------------------------------------------------------


def create_ambiguous_condition_schedule(
    total_blocks,
):
    """
    Create a balanced schedule of ambiguous conditions.

    Example with 20 blocks:
        10 known
        10 unknown

    The order is randomized.
    """

    n_known = (
        total_blocks // 2
    )

    n_unknown = (
        total_blocks
        - n_known
    )

    schedule = (
        ["known"] * n_known
        + ["unknown"] * n_unknown
    )

    random.shuffle(
        schedule
    )

    return schedule
def show_block_earnings(
    win,
    selected_urn,
    block_results,
    training=False,
):
    """Show how much money was earned in the completed block."""

    block_earnings = (
        block_results[
            "block_earnings"
        ]
    )

    number_correct = (
        block_results[
            "number_correct"
        ]
    )

    if training:

        if selected_urn["urn_type"] == "ambiguous":

            message = (
                f"Score: {number_correct}/{params.N_TRIALS_PER_BLOCK}.\n\n"

                f"In the real task, this performance would correspond to "
                f"€{block_earnings:.2f}.\n\n"

                "This was a TRAINING block, so this amount does not "
                "count toward your final earnings.\n\n"

                "Press SPACE to continue."
            )

        else:

            message = (
                "You selected the fixed-value urn.\n\n"

                f"In the real task, this urn would give you "
                f"€{block_earnings:.2f}.\n\n"

                "This was a TRAINING block, so this amount does not "
                "count toward your final earnings.\n\n"

                "Press SPACE to continue."
            )

    else:

        if selected_urn["urn_type"] == "ambiguous":

            message = (
                f"Score: {number_correct}/{params.N_TRIALS_PER_BLOCK}\n\n"

                f"You earned €{block_earnings:.2f} \n\n"


                "Press SPACE to continue."
            )

        else:

            message = (
                "You selected the fixed-value urn.\n\n"

                f"You earned: "
                f"€{block_earnings:.2f}\n\n"

                "Your performance did not change "
                "this amount.\n\n"

                "Press SPACE to continue."
            )

    earnings_text = draw_text(
        win=win,
        text=message,
        pos=(
            0,
            0,
        ),
        height=0.043,
        wrap_width=1.15,
        bold=False,
    )

    earnings_text.draw()

    win.flip()

    keys = event.waitKeys(
        keyList=[
            "space",
            "escape",
        ]
    )

    if "escape" in keys:

        quit_experiment(
            win
        )
# -----------------------------------------------------------------------------
# Main task
# -----------------------------------------------------------------------------


def run_urn_visual_test(
    block_number=1,
    total_blocks=1,
    deterministic_value=2.00,
    ambiguous_condition="known",
    training=False,
):
    """Run one complete urn block."""

    win = visual.Window(
        size=params.WINDOW_SIZE,
        fullscr=params.FULLSCREEN,
        color=params.BACKGROUND_COLOR,
        units="height",
    )

    # -----------------------------------------------------------------
    # Block start
    # -----------------------------------------------------------------

    if training and block_number == 1:

        block_message = params.TRAINING_INSTRUCTIONS

    elif training:

        block_message = (
            f"Training Block {block_number} "
            f"of {total_blocks}\n\n"
            "Press SPACE to begin."
        )

    else:

        block_message = (
            f"Block {block_number} "
            f"of {total_blocks}\n\n"
            "Press SPACE to begin."
        )


    block_text = draw_text(
        win=win,
        text=block_message,
        pos=(0, 0),
        height=0.045,
        wrap_width=1.2,
        bold=True,
    )

    block_text.draw()

    win.flip()

    keys = event.waitKeys(
        keyList=[
            "space",
            "escape",
        ]
    )

    if "escape" in keys:

        quit_experiment(
            win
        )

    # -----------------------------------------------------------------
    # Assign urns
    # -----------------------------------------------------------------

    urn_assignment = (
        assign_urns_to_sides(
            deterministic_value=(
                deterministic_value
            ),
            ambiguous_condition=(
                ambiguous_condition
            ),
        )
    )

    # -----------------------------------------------------------------
    # General prediction instructions
    # -----------------------------------------------------------------
    if block_number == 1:
        title = draw_text(
        win=win,
        text="General Instructions",
        pos=(0, 0.36),
        height=0.05,
        wrap_width=1.2,
        bold=True
    )
        instructions = draw_text(
            win=win,
            text=params.URN_INSTRUCTIONS,
            pos=(
                0,
                0,
            ),
            height=0.040,
            wrap_width=1.30,
        )
        title.draw()
        instructions.draw()

        win.flip()

        keys = event.waitKeys(
            keyList=[
                "space",
                "escape",
            ]
        )

        if "escape" in keys:

            quit_experiment(
                win
            )
    # -----------------------------------------------------------------
    # Urn preference
    # -----------------------------------------------------------------

    selected_side = (
        collect_urn_choice(
            win=win,
            urn_assignment=urn_assignment,
        )
    )

    selected_urn = (
        urn_assignment[
            selected_side
        ]
    )

    # -----------------------------------------------------------------
    # Selection confirmation
    # -----------------------------------------------------------------

    selected_text = draw_text(
        win=win,
        text=(
            params.SELECTED_URN_TEXT.format(
                urn_label=selected_urn[
                    "label"
                ]
            )
        ),
        pos=(
            0,
            0.36,
        ),
        height=0.050,
        bold=True,
    )

    condition_text = draw_text(
        win=win,
        text=get_trial_instruction(
            selected_urn
        ),
        pos=(
            0,
            0.22,
        ),
        height=0.034,
        wrap_width=1.10,
    )

    continue_text = draw_text(
        win=win,
        text=params.SELECTED_URN_CONTINUE_TEXT,
        pos=(0, -0.20),
        height=0.034,
        wrap_width=1.10,
    )

    selected_text.draw()
    condition_text.draw()
    continue_text.draw()

    draw_selected_open_urn(
        win=win,
        selected_urn=selected_urn,
    )

    win.flip()

    keys = event.waitKeys(
        keyList=[
            "space",
            "escape",
        ]
    )

    if "escape" in keys:

        quit_experiment(
            win
        )

    # -----------------------------------------------------------------
    # Prediction trials
    # -----------------------------------------------------------------

    block_results = (
        run_trials(
            win=win,
            selected_urn=selected_urn,
        )
    )
    # -----------------------------------------------------------------
    # Show money earned
    # -----------------------------------------------------------------

    show_block_earnings(
        win=win,
        selected_urn=selected_urn,
        block_results=block_results,
        training=training
    )

    # -----------------------------------------------------------------
    # Post-block questionnaire
    # -----------------------------------------------------------------

    question_results = (
        run_post_block_questions(
            win=win,
            selected_urn=selected_urn,
        )
    )

    # -----------------------------------------------------------------
    # Score inferred cycle
    # -----------------------------------------------------------------

    estimated_cycle = (
        question_results.get(
            "estimated_cycle"
        )
    )

    if (
        selected_urn.get(
            "cycle"
        )
        is not None
        and estimated_cycle is not None
    ):

        estimated_cycle_correct = (
            cycles_match(
                true_cycle=selected_urn[
                    "cycle"
                ],
                response_cycle=estimated_cycle,
            )
        )

    else:

        estimated_cycle_correct = None

    # -----------------------------------------------------------------
    # Useful debug output
    # -----------------------------------------------------------------

    print(
        "\n"
        + "=" * 70
    )

    print(
        f"BLOCK {block_number}"
    )

    print(
        "=" * 70
    )

    print(
        "Ambiguous condition:",
        ambiguous_condition,
    )

    print(
        "Deterministic value:",
        deterministic_value,
    )

    print(
        "Selected side:",
        selected_side,
    )

    print(
        "Selected urn type:",
        selected_urn[
            "urn_type"
        ],
    )

    if (
        selected_urn.get(
            "cycle"
        )
        is not None
    ):

        print(
            "TRUE CYCLE:",
            serialise_cycle(
                selected_urn[
                    "cycle"
                ]
            ),
        )

    if estimated_cycle is not None:

        print(
            "PARTICIPANT ESTIMATED CYCLE:",
            serialise_cycle(
                estimated_cycle
            ),
        )

    print(
        "ESTIMATED CYCLE CORRECT:",
        estimated_cycle_correct,
    )

    print(
        "=" * 70
        + "\n"
    )

    win.close()

    # -----------------------------------------------------------------
    # Results
    # -----------------------------------------------------------------

    return {
        # -------------------------------------------------------------
        # Block condition
        # -------------------------------------------------------------

        "ambiguous_condition": (
            ambiguous_condition
        ),

        "deterministic_value": (
            deterministic_value
        ),

        # -------------------------------------------------------------
        # Selected urn
        # -------------------------------------------------------------

        "selected_side": (
            selected_side
        ),

        "selected_urn_type": (
            selected_urn[
                "urn_type"
            ]
        ),

        "selected_urn_name": (
            selected_urn[
                "urn_name"
            ]
        ),

        "selected_condition": (
            selected_urn.get(
                "condition"
            )
        ),

        "selected_ambiguous_k": (
            selected_urn.get(
                "ambiguous_k"
            )
        ),

        "selected_cycle": (
            serialise_cycle(
                selected_urn[
                    "cycle"
                ]
            )
            if selected_urn.get(
                "cycle"
            )
            is not None
            else None
        ),

        "selected_participant_knows_k": (
            selected_urn.get(
                "participant_knows_k"
            )
        ),

        "selected_value": (
            selected_urn.get(
                "value"
            )
        ),

        "selected_payoff_type": (
            selected_urn.get(
                "payoff_type"
            )
        ),

        # -------------------------------------------------------------
        # Sequence data
        # -------------------------------------------------------------

        "draw_sequence": (
            block_results[
                "full_sequence"
            ]
        ),

        "seed_sequence": (
            block_results[
                "seed_sequence"
            ]
        ),

        "trial_data": (
            block_results[
                "trial_data"
            ]
        ),

        "number_correct": (
            block_results[
                "number_correct"
            ]
        ),

        "accuracy": (
            block_results[
                "accuracy"
            ]
        ),
        "block_earnings": (
            block_results[
                "block_earnings"
            ]
        ),

        "reward_per_correct_guess": (
            block_results[
                "reward_per_correct_guess"
            ]
        ),

        "number_pattern_trials": (
            block_results[
                "number_pattern_trials"
            ]
        ),

        "number_noise_trials": (
            block_results[
                "number_noise_trials"
            ]
        ),

        "number_pattern_consistent": (
            block_results[
                "number_pattern_consistent"
            ]
        ),

        # -------------------------------------------------------------
        # Left urn
        # -------------------------------------------------------------

        "left_urn_type": (
            urn_assignment[
                "left"
            ][
                "urn_type"
            ]
        ),

        "left_urn_name": (
            urn_assignment[
                "left"
            ][
                "urn_name"
            ]
        ),

        "left_condition": (
            urn_assignment[
                "left"
            ].get(
                "condition"
            )
        ),

        "left_ambiguous_k": (
            urn_assignment[
                "left"
            ].get(
                "ambiguous_k"
            )
        ),

        "left_cycle": (
            serialise_cycle(
                urn_assignment[
                    "left"
                ][
                    "cycle"
                ]
            )
            if urn_assignment[
                "left"
            ].get(
                "cycle"
            )
            is not None
            else None
        ),

        "left_participant_knows_k": (
            urn_assignment[
                "left"
            ].get(
                "participant_knows_k"
            )
        ),

        "left_value": (
            urn_assignment[
                "left"
            ].get(
                "value"
            )
        ),

        "left_payoff_type": (
            urn_assignment[
                "left"
            ].get(
                "payoff_type"
            )
        ),

        # -------------------------------------------------------------
        # Right urn
        # -------------------------------------------------------------

        "right_urn_type": (
            urn_assignment[
                "right"
            ][
                "urn_type"
            ]
        ),

        "right_urn_name": (
            urn_assignment[
                "right"
            ][
                "urn_name"
            ]
        ),

        "right_condition": (
            urn_assignment[
                "right"
            ].get(
                "condition"
            )
        ),

        "right_ambiguous_k": (
            urn_assignment[
                "right"
            ].get(
                "ambiguous_k"
            )
        ),

        "right_cycle": (
            serialise_cycle(
                urn_assignment[
                    "right"
                ][
                    "cycle"
                ]
            )
            if urn_assignment[
                "right"
            ].get(
                "cycle"
            )
            is not None
            else None
        ),

        "right_participant_knows_k": (
            urn_assignment[
                "right"
            ].get(
                "participant_knows_k"
            )
        ),

        "right_value": (
            urn_assignment[
                "right"
            ].get(
                "value"
            )
        ),

        "right_payoff_type": (
            urn_assignment[
                "right"
            ].get(
                "payoff_type"
            )
        ),

        # -------------------------------------------------------------
        # Post-block questions
        # -------------------------------------------------------------

        "estimated_k": (
            question_results.get(
                "estimated_k"
            )
        ),

        "estimated_cycle": (
            estimated_cycle
        ),

        "estimated_cycle_serialised": (
            serialise_cycle(
                estimated_cycle
            )
            if estimated_cycle is not None
            else None
        ),

        "estimated_cycle_correct": (
            estimated_cycle_correct
        ),

        "post_block_confidence": (
            question_results.get(
                "confidence"
            )
        ),

        "post_block_liking": (
            question_results.get(
                "liking"
            )
        ),

        "post_block_difficulty": (
            question_results.get(
                "difficulty"
            )
        ),

        "post_block_mental_effort": (
            question_results.get(
                "mental_effort"
            )
        ),
    }

########STAIRCASE 
def update_staircase(
    staircase,
    choice,
    min_value=0.00,
    max_value=5.00,
):
    """
    Update deterministic value based on choice.

    ambiguous choice:
        increase sure value

    deterministic choice:
        decrease sure value

    After a reversal, reduce step size.
    """

    step_sizes = [
        0.50,
        0.25,
        0.10,
    ]

    previous_choice = (
        staircase[
            "previous_choice"
        ]
    )

    # Detect reversal
    if (
        previous_choice is not None
        and choice != previous_choice
    ):

        staircase[
            "reversals"
        ].append(
            staircase[
                "value"
            ]
        )

        staircase[
            "step_index"
        ] = min(
            staircase[
                "step_index"
            ] + 1,
            len(step_sizes) - 1,
        )

    step = step_sizes[
        staircase[
            "step_index"
        ]
    ]

    if choice == "ambiguous":

        staircase[
            "value"
        ] += step

    elif choice == "deterministic":

        staircase[
            "value"
        ] -= step

    else:

        raise ValueError(
            "choice must be "
            "'ambiguous' or 'deterministic'"
        )

    staircase[
        "value"
    ] = max(
        min_value,
        min(
            max_value,
            staircase[
                "value"
            ],
        ),
    )

    staircase[
        "previous_choice"
    ] = choice

    return staircase

if __name__ == "__main__":

    results = run_urn_visual_test()

    print(
        results
    )