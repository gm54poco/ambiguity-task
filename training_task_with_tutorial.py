"""Guided practice for the urn prediction experiment.

Place this file next to urn_task.py, urn_params.py and the existing assets folder.
It is designed for the optimized urn_task.py version (October 2026).

Run on its own:
    python training_task.py

Or integrate before the real experiment:
    import training_task
    training_task.run_training()

A separate interactive guessing tutorial precedes four ordinary practice rounds.
Practice does not call the staircase, run post-round questions, or award real
points. It temporarily adapts the reward header and surprise-ball count;
original parameters are restored after practice, including on errors.
"""

import random
from contextlib import contextmanager

from psychopy import core, event, visual

import urn_params as params
import urn_task as task
import math


# Total number of practice rounds (urn choices). Change this as needed.
# Round 1 is always known-k; round 2 is always unknown-k.
# Later rounds are assigned known/unknown at random.
ROUND_N = 4

PRACTICE_TRIALS = 10
PRACTICE_FLIPS = 1  # 1/10 = 10% for a 10-trial practice block
PRACTICE_MAX_REWARD = PRACTICE_TRIALS * params.REWARD_PER_CORRECT_GUESS
PRACTICE_DETERMINISTIC_VALUES = [15, 24]

# Separate interactive tutorial before the four ordinary practice rounds.
TUTORIAL_K = 2
TUTORIAL_CYCLE = ("blue", "magenta")
TUTORIAL_PATTERN_EXPLANATION_AFTER = 6
TUTORIAL_SURPRISE_TRIAL = 7  # the predicted BLUE becomes MAGENTA
MAGICIAN_IMAGE_PATH = params.BASE_DIR / "assets" / "magician.png"
TUTORIAL_STEP_COUNT = 10
TUTORIAL_ANIMATION_FRAMES = 12
TARGET_IMAGE_PATH = params.BASE_DIR / "assets" / "target.png"

# Reuse PsychoPy stimuli instead of rebuilding text for every animation frame.
_TEXT_CACHE = {}
_IMAGE_CACHE = {}

URN_LID_IMAGE = params.BASE_DIR / "assets" / "pretty_urns" / "urn_lid.png"

TUTORIAL_ANIMATION_FRAMES = 10      # balls going into urn
TUTORIAL_LID_FRAMES = 8             # lid closing animation

# Adjust this so the bottom of the OPEN urn matches the closed urn
OPEN_URN_Y_OFFSET = -0.03

# Starting point of the lid (higher = starts further above)
LID_START_Y_OFFSET = 0.18



def _text(win, message, y, height=0.034, color="#172b49", bold=False,
          wrap_width=1.18, x=0):
    key = (id(win), str(message), x, y, height, color, bold, wrap_width)
    stim = _TEXT_CACHE.get(key)
    if stim is None:
        stim = task.draw_text(
            win, message, (x, y), height=height,
            wrap_width=wrap_width, color=color, bold=bold,
        )
        _TEXT_CACHE[key] = stim
    return stim


def _wait_space(win):
    event.clearEvents()
    keys = event.waitKeys(keyList=["space", "return", "num_enter", "escape"])
    if "escape" in keys:
        task.quit_experiment(win)


def _wait_tutorial_nav(win):
    """SPACE/ENTER advances; BACKSPACE goes to the previous tutorial stage."""
    event.clearEvents()
    keys = event.waitKeys(
        keyList=["space", "return", "num_enter", "backspace", "escape"]
    )
    if "escape" in keys:
        task.quit_experiment(win)
    return -1 if "backspace" in keys else 1


def _opening_screen(win, heading, subtitle=None, footer="Press SPACE to continue"):
    """Minimal full-screen opening; nothing else appears until SPACE."""
    _text(win, heading, 0.2, height=params.TITLE_HEIGHT, bold=True).draw()
    if subtitle:
        _text(win, subtitle, -0.025, height=params.BODY_HEIGHT,
              color="#334155", wrap_width=1.05).draw()
    _text(win, footer, -0.29, height=0.025,
          color="#576a82").draw()
    win.flip()
    _wait_space(win)

# Two-step instruction layout
INSTRUCTION_STEP_Y = 0.415
INSTRUCTION_TITLE_Y = 0.295
INSTRUCTION_TEXT_TOP_Y = 0.155
INSTRUCTION_TEXT_HEIGHT = 0.026
INSTRUCTION_FOOTER_Y = -0.425

INSTRUCTION_NAVY = "#172b49"
INSTRUCTION_BODY = "#334155"
INSTRUCTION_MUTED = "#576a82"

def _instruction_paragraph(win, lines, x, top_y,
                           width=0.61, spacing=0.115):
    for index, line in enumerate(lines):
        visual.TextStim(
            win=win,
            text=line,
            pos=(x, top_y - index * spacing),
            height=INSTRUCTION_TEXT_HEIGHT,
            wrapWidth=width,
            color=INSTRUCTION_BODY,
            alignText="left",
            anchorHoriz="left",
            anchorVert="top",
        ).draw()



def _instruction_urn_image(win, urn_name, opened, pos, size):
    """Reuse the same urn image during tutorial pages and animation frames."""
    path = params.PRETTY_URNS_DIR / (
        f"{urn_name}_{'opened' if opened else 'closed'}.png"
    )
    key = (id(win), "tutorial_urn", str(path), tuple(size))
    stim = _IMAGE_CACHE.get(key)
    if stim is None:
        stim = visual.ImageStim(
            win=win, image=str(path), size=size, interpolate=True,
        )
        _IMAGE_CACHE[key] = stim
    stim.pos = pos
    stim.draw()


def _practice_step_screen(win, step):
    title = (
        "Choosing an urn"
        if step == 1
        else "Guessing the next ball"
    )

    _text(win, f"STEP {step} OF 2", INSTRUCTION_STEP_Y,
          height=0.020, color=INSTRUCTION_MUTED,
          bold=True).draw()

    _text(win, title, INSTRUCTION_TITLE_Y,
          height=0.048, color=INSTRUCTION_NAVY,
          bold=True).draw()

    visual.Line(
        win, start=(-0.72, 0.235), end=(0.72, 0.235),
        lineColor="#cbd0d5", lineWidth=1.0
    ).draw()

    visual.Line(
        win, start=(-0.72, -0.375), end=(0.72, -0.375),
        lineColor="#cbd0d5", lineWidth=1.0
    ).draw()

    _text(win, "Press SPACE to continue",
          INSTRUCTION_FOOTER_Y, height=0.022,
          color=INSTRUCTION_MUTED).draw()

    urn_names = list(params.PRETTY_URN_NAMES)

    if step == 1:
        _instruction_paragraph(
            win,
            [
                "You will choose between two urns.",
                "One allows you to earn a fixed number of points.",
                "The other allows you to earn points based on the number of correct guesses.",
                "Both urns contain the same type of game."
            ],
            x=-0.70,
            top_y=INSTRUCTION_TEXT_TOP_Y
        )

        for x, name, label in (
            (0.29, urn_names[0], "Fixed reward"),
            (0.58, urn_names[1], "Points per correct guess"),
        ):
            _instruction_urn_image(
                win, name, opened=False,
                pos=(x, 0.035),
                size=(0.24, 0.26)
            )

            _text(win, label, -0.175,
                  height=0.020,
                  color=INSTRUCTION_BODY,
                  x=x, wrap_width=0.29).draw()

    else:
        _instruction_paragraph(
            win,
            [
                "You will draw colored balls from the chosen urn.",
                "You will guess the color of the next ball.",
                "After each guess, the actual color will be revealed."
            ],
            x=0.10,
            top_y=INSTRUCTION_TEXT_TOP_Y,
            width=0.59
        )

        _text(
            win, "Previous draws (example)",
            0.12, height=0.020,
            color=INSTRUCTION_MUTED,
            x=-0.37
        ).draw()

        for i, color in enumerate(
            ("blue", "magenta", "magenta", "blue", "magenta")
        ):
            visual.Circle(
                win,
                pos=(-0.55 + i * 0.09, 0.025),
                radius=0.026,
                fillColor=params.ball_display_color(color),
                lineColor=None,
                edges=40
            ).draw()

        _text(
            win, "B = blue       M = magenta",
            -0.10, height=0.019,
            color=INSTRUCTION_BODY,
            x=-0.37
        ).draw()

    win.flip()
    _wait_space(win)


def _fixation(win, duration=0.50):
    """Brief neutral fixation immediately before each urn-choice screen."""
    _text(win, "+", 0, height=0.070, bold=True).draw()
    win.flip()
    core.wait(duration)



@contextmanager
def _practice_header_values():
    """Change only what the inherited header displays; always restore."""
    old_max = params.MAX_AMBIGUOUS_REWARD
    old_flips = params.N_RANDOM_DRAWS
    try:
        params.MAX_AMBIGUOUS_REWARD = PRACTICE_MAX_REWARD
        params.N_RANDOM_DRAWS = PRACTICE_FLIPS
        yield
    finally:
        params.MAX_AMBIGUOUS_REWARD = old_max
        params.N_RANDOM_DRAWS = old_flips


def _draw_hint_background(win, selected_urn, sequence, trial_results):
    """Draw the usual trial screen, then dim it behind a centred card."""
    # Match the actual minimalist practice prediction screen under the modal.
    _practice_draw_prediction(win, selected_urn, sequence, trial_results)
    # Dim the background without fully hiding the trial context.
    visual.Rect(
        win, pos=(0, 0), width=2.2, height=2.2,
        fillColor="#101827", lineColor=None, opacity=0.83
    ).draw()


def _draw_hint_card(win, heading, footer):
    visual.Rect(
        win, pos=(0, 0.005), width=0.90, height=0.54,
        fillColor="#303c50", lineColor="#61738b", lineWidth=1.6,
    ).draw()

    _text(win, footer, -0.225, height=0.025,
          color="#bfd0e8", bold=True).draw()


def _context_hint(win, selected_urn, sequence, trial_results,
                  title, explanation, pattern_length=None):
    """Show a clean centred card explaining the pattern concept."""
    _draw_hint_background(win, selected_urn, sequence, trial_results)
    _draw_hint_card(win, "Pattern", "Press SPACE to begin")

    if pattern_length is not None:
        _text(win, f"Pattern length: {pattern_length}", 0.155,
            height=0.042, bold=True,
            color="#f1f5f9").draw()

        radius = 0.026 if pattern_length >= 3 else 0.029
        spacing = 0.065
        group_width = (pattern_length - 1) * spacing

        # Exactly k circles, not two copies separated by an arrow.
        for idx in range(pattern_length):
            px = -group_width / 2 + idx * spacing
            visual.Circle(
                win=win,
                pos=(px, 0.045),
                radius=radius,
                fillColor="#253f62",
                lineColor="#bdc8d7",
                lineWidth=1.6,
            ).draw()

        _text(
            win,
            f"The pattern has {pattern_length} position(s) and repeats.\n\n"
            "(This explanation won't appear in the real task.)",
            -0.055,
            height=0.026,
            wrap_width=0.70,
            color="#f1f5f9"
        ).draw()
    else:
    # Heading
        _text(
            win, "Pattern length (<4)",
            0.155, height=0.042,
            bold=True, color="#f1f5f9"
        ).draw()

        # Unknown pattern illustration
        radius = 0.026
        positions = [-0.15, -0.085, -0.02]

        for px in positions:
            visual.Circle(
                win=win,
                pos=(px, 0.045),
                radius=radius,
                fillColor=params.BACKGROUND_COLOR,
                lineColor="#bdc8d7",
                lineWidth=1.6,
            ).draw()

        # Question mark
        _text(
            win, "?", 0.045,
            height=0.050, x=0.12,
            bold=True, color="#f1f5f9"
        ).draw()

        # First explanation
        _text(
            win,
            "The pattern has fewer than 4 positions.",
            -0.055,
            height=0.026,
            wrap_width=0.70,
            color="#f1f5f9"
        ).draw()

        # Second explanation
        _text(
            win,
            "The exact length is not provided.\n\n"
            "(This explanation won't appear in the real task.)",
            -0.13, #antes .11
            height=0.024,
            wrap_width=0.70,
            color="#cbd5e1"
        ).draw()
    win.flip()
    _wait_space(win)


def _hint_for_trial(selected_urn, condition, trial_number):
    """Only one introductory pattern-length hint; no B/M or bar reminders."""
    if trial_number != 1:
        return None
    if condition == "known":
        return (
            "Pattern length",
            "",
            selected_urn["ambiguous_k"],
        )
    return (
        "Pattern length",
        "The repeating pattern has fewer than 4 positions. "
        "Its exact length is unknown.",
        None,
    )


def _draw_magician(win, pos=(0.47, -0.19), size=(0.30, 0.30)):
    """Display the user's transparent assets/magician.png on a tutorial screen."""
    key = (id(win), str(MAGICIAN_IMAGE_PATH), tuple(size))
    stim = _IMAGE_CACHE.get(key)
    if stim is None:
        stim = visual.ImageStim(
            win=win, image=str(MAGICIAN_IMAGE_PATH), size=size,
            interpolate=True,
        )
        _IMAGE_CACHE[key] = stim
    stim.pos = pos
    stim.draw()


def _draw_surprise_hat(win, pos, radius, tag="reveal"):
    """A small top hat above an actual surprise ball (also in draw history)."""
    x, y = pos
    r = radius
    navy, pink = "#172b49", "#e7428b"
    # Reuse the three simple shapes throughout each animation / history redraw.
    parts = (
        ("crown", (x, y + 1.42*r), (1.28*r, 0.90*r), navy),
        ("band", (x, y + 1.20*r), (1.30*r, 0.19*r), pink),
        ("brim", (x, y + 0.98*r), (1.96*r, 0.28*r), navy),
    )
    for name, center, size, color in parts:
        stim = task._cached(
            win, ("surprise_hat", tag, name),
            lambda: visual.Rect(win=win, pos=center,
                                width=size[0], height=size[1],
                                fillColor=color, lineColor=color),
        )
        stim.pos = center
        stim.width, stim.height = size
        stim.draw()


def _practice_draw_history(win, sequence, surprise_indices=()):
    """Keep the existing history, adding a little hat above surprise balls."""
    task.draw_sequence_feedback(win, sequence)
    for index in surprise_indices:
        if index < len(sequence):
            _draw_surprise_hat(win, task.get_feedback_ball_position(index),
                               params.FEEDBACK_BALL_RADIUS, tag=("history", index))


def _tutorial_intro(win, urn, sequence, results):
    """Show the normal guessing urn with only the pattern and color instructions."""
    _practice_draw_prediction(win, urn, sequence, results,
                              tutorial_intro=True,
                              tutorial_prompt="Guess BLUE first: press B")
    _text(win, "Press SPACE to begin", -0.145,
          height=0.022, color="#576a82").draw()
    win.flip()
    _wait_space(win)


def _draw_pattern_pair_boxes(win, pair_starts):
    """Highlight consecutive two-ball groups in the existing draw history."""
    for index in pair_starts:
        x1, y = task.get_feedback_ball_position(index)
        x2, _ = task.get_feedback_ball_position(index + 1)
        visual.Rect(
            win=win, pos=((x1+x2)/2, y),
            width=(x2-x1) + 2*params.FEEDBACK_BALL_RADIUS + 0.012,
            height=2*params.FEEDBACK_BALL_RADIUS + 0.024,
            fillColor=None, lineColor="#80579c", lineWidth=2.5,
        ).draw()


def _tutorial_repeating_pattern(win, urn, sequence, results):
    """Pause after six normal outcomes and identify each repeated pair."""
    _practice_draw_prediction(win, urn, sequence, results,
                              tutorial_intro=True,
                              tutorial_heading="Notice: the pattern of 2 repeats")
    _draw_pattern_pair_boxes(win, (0, 2, 4))
    _text(win, "BLUE - MAGENTA    BLUE - MAGENTA    BLUE - MAGENTA",
          0.087, height=0.023, wrap_width=1.12).draw()
    _text(win, "Press SPACE to guess again", -0.135,
          height=0.023, color="#576a82").draw()
    win.flip()
    _wait_space(win)


def _tutorial_surprise(win, urn, sequence, results, pattern_color, outcome):
    """Explain the precise opposite-color outcome before the ball is revealed."""
    _practice_draw_prediction(win, urn, sequence, results,
                              hide_urn_type=True)
    _text(win, "Sometimes a SURPRISE BALL appears", 0.440,
          height=0.030, bold=True).draw()
    _text(win, f"Pattern predicts: {pattern_color.upper()}", 0.107,
          height=0.025, x=-0.33).draw()
    _text(win, f"Surprise ball: {outcome.upper()}", 0.065,
          height=0.025, x=-0.33).draw()
    _text(win, "The surprise changes the ball to the opposite color.",
          -0.085, height=0.022, wrap_width=0.83, x=-0.25).draw()
    _text(win, "Press SPACE to reveal", -0.155,
          height=0.021, color="#576a82", x=-0.25,
          wrap_width=0.68).draw()
    win.flip()
    _wait_space(win)


def _tutorial_continue(win, urn, sequence, results, surprise_indices):
    """Prompt a new guess after the magician has changed one ball."""
    _practice_draw_prediction(win, urn, sequence, results,
                              surprise_indices=surprise_indices,
                              tutorial_prompt="Guess again! The pattern continues.")
    _text(win, "Press SPACE to continue", -0.165,
          height=0.022, color="#576a82").draw()
    win.flip()
    _wait_space(win)


def _tutorial_pattern_returns(win, urn, sequence, results, surprise_indices):
    """Emphasize that later draws follow the original repeating pattern."""
    _practice_draw_prediction(win, urn, sequence, results,
                              surprise_indices=surprise_indices,
                              hide_urn_type=True)
    _draw_pattern_pair_boxes(win, (8,))
    _text(win, "The original pattern continues", 0.440,
          height=0.031, bold=True).draw()
    _text(win, "The magician changed only one ball, not the pattern.",
          0.085, height=0.024).draw()
    _text(win, "Press SPACE to finish this round", -0.135,
          height=0.022, color="#576a82").draw()
    win.flip()
    _wait_space(win)



# =============================================================================
# INTERACTIVE, REVERSIBLE TUTORIAL (BEFORE THE FOUR PRACTICE ROUNDS)
# =============================================================================
# Stage 0 is deliberately title-only. Stages 2, 4 and 6 collect actual B/M
# guesses. Backspace revisits previous explanations without erasing guesses.


def _draw_tutorial_progress(win, stage, total=TUTORIAL_STEP_COUNT):
    """Small segmented progress indicator on every tutorial screen."""
    total_width = 0.94
    gap = 0.010
    width = (total_width - gap * (total - 1)) / total
    left = -total_width / 2 + width / 2
    y = 0.477
    for i in range(total):
        fill = "#5379B8" if i <= stage else "#d4dce6"
        visual.Rect(
            win, pos=(left + i * (width + gap), y),
            width=width, height=0.008,
            fillColor=fill, lineColor=None,
        ).draw()
    _text(win, f"{stage + 1} / {total}", 0.477,
          height=0.015, color="#728198", x=-0.595).draw()


def _tutorial_footer(win, previous=True, message="SPACE: next"):
    hint = message
    if previous:
        hint += "       BACKSPACE: previous explanation"
    _text(win, hint, -0.435, height=0.018, color="#576a82").draw()


def _tutorial_title(win, title, stage, subtitle=None):
    _draw_tutorial_progress(win, stage)
    _text(win, title, 0.340, height=0.043, bold=True,
          color=INSTRUCTION_NAVY, wrap_width=1.40).draw()
    if subtitle:
        _text(win, subtitle, 0.268, height=0.024,
              color=INSTRUCTION_BODY, wrap_width=1.35).draw()


def _tutorial_ball(win, color, x, y, radius=0.029):
    visual.Circle(
        win, pos=(x, y), radius=radius,
        fillColor=params.ball_display_color(color),
        lineColor="#172b49", lineWidth=1.0, edges=40,
    ).draw()


def _tutorial_draw_reward_comparison(win, stage, assignment):
    """Show the actual main-task urn cards and highlight one description at a time."""
    headings = {
        6: "Compare how you get points",
        7: "Here you can get points for each ball you guess correctly",
        8: "Here you get the written amount of points, guaranteed.\n Correct guesses do not change the amount.",
    }
    _draw_tutorial_progress(win, stage)
    _text(win, headings[stage], 0.405,
          height=0.047 if stage == 6 else 0.034,
          color=INSTRUCTION_NAVY, bold=True, wrap_width=1.46).draw()
    _text(win, "Press SPACE learn about the urns |  BACKSPACE to see the previous explanation", 0.325,
          height=0.023, color=INSTRUCTION_MUTED,wrap_width=1.45,).draw()

    for side in ("left", "right"):
        urn = assignment[side]
        x = params.URN_LEFT_POS[0] if side == "left" else params.URN_RIGHT_POS[0]
        _draw_reward_urn(win, urn, x, REWARD_CHOICE_URN_SCALE)
        # The same function and coordinates used in urn_task.py's real choice.
        task.draw_selection_condition_text(win, urn, x)
        selected = ((stage == 7 and urn["urn_type"] == "ambiguous") or
                    (stage == 8 and urn["urn_type"] == "deterministic"))
        
        if selected:
            # Highlight the entire card without covering its text.
            visual.Rect(
                win,
                pos=(x, -0.280),
                width=0.53,
                height=0.190,
                fillColor=None,
                lineColor="#80579c",
                lineWidth=3,
            ).draw()

def _tutorial_draw_scene(win, stage, urn, sequence, trials,
                         pending=None, assignment=None):
    """Draw an explanatory moment without replacing the guessing-game layout."""
    results = [entry["correct"] for entry in trials]
    six_seq = sequence[:TUTORIAL_PATTERN_EXPLANATION_AFTER]
    six_results = results[:TUTORIAL_PATTERN_EXPLANATION_AFTER]
    surprises = (TUTORIAL_SURPRISE_TRIAL - 1,) if len(sequence) >= TUTORIAL_SURPRISE_TRIAL else ()

    if stage == 0:
        _draw_tutorial_progress(win, stage)
        _text(win, "You will play a guessing game.", 0.100,
              height=params.TITLE_HEIGHT, bold=True).draw()
        _text(win, "Here is how the game works:", -0.025,
              height=params.BODY_HEIGHT, color=INSTRUCTION_BODY).draw()
        _text(win, "Press SPACE to start", -0.258,
              height=0.036, bold=True, color=INSTRUCTION_NAVY).draw()

    elif stage == 1:
        urn["_tutorial_step"] = stage
        _practice_draw_prediction(
            win, urn, six_seq, six_results, tutorial_intro=True,
            tutorial_prompt="Make your guess" if not trials else "Keep guessing",
            tutorial_first_guess=not bool(trials),
        )

    elif stage == 2:
        urn["_tutorial_step"] = stage

        _practice_draw_prediction(
            win,
            urn,
            six_seq,
            six_results,
            tutorial_intro=True,
            tutorial_prompt="Guess the next ball",
            reminder=True,
        )

        if pending is not None:
            _text(
                win,
                "Press SPACE to continue",
                -0.195,
                height=0.023,
                color=INSTRUCTION_MUTED,
            ).draw()

    
    elif stage == 3:
        # Clean surprise-ball explanation screen.
        # No score bar, pattern information, or progress indicator.

        # Title
        _text(
            win,
            "Surprise ball!",
            0.405,
            height=0.055,
            bold=True,
            color=INSTRUCTION_NAVY,
        ).draw()

        # Explanation
        _text(
            win,
            "Sometimes a ball that has the opposite color\n"
            "from the pattern will appear.",
            0.300,
            height=0.028,
            color=INSTRUCTION_MUTED,
            wrap_width=1.40,
        ).draw()

        # Keep the original draw history
        _practice_draw_history(win, six_seq)

        # Labels above the demonstration
        _text(
            win,
            "The pattern predicts",
            0.055,
            x=-0.25,
            height=0.025,
            color=INSTRUCTION_BODY,
        ).draw()

        _text(
            win,
            "Surprise ball",
            0.055,
            x=0.24,
            height=0.025,
            color=INSTRUCTION_BODY,
        ).draw()

        # Blue ball -> magenta surprise ball
        ball_y = -0.065

        _tutorial_ball(
            win, "blue", -0.25, ball_y, radius=0.043
        )

        _text(
            win, "→", ball_y,
            x=0.0, height=0.045,
            color=INSTRUCTION_NAVY,
        ).draw()

        _tutorial_ball(
            win, "magenta", 0.24, ball_y, radius=0.043
        )

        # Keep the surprise hat
        _draw_surprise_hat(
            win,
            (0.24, ball_y),
            0.043,
            tag="tutorial_surprise",
        )

        # Optional: show only the upper part of the urn
        visual.ImageStim(
            win=win,
            image=str(urn["opened_image"]),
            pos=(0, -0.68),
            size=params.SELECTED_URN_SIZE,
            interpolate=True,
        ).draw()

        # Continue instruction
        _text(
            win,
            "Press SPACE to continue",
            -0.27,
            height=0.024,
            color=INSTRUCTION_MUTED,
        ).draw()


    elif stage == 4:
        urn["_tutorial_step"] = stage
        _practice_draw_prediction(
            win, urn, sequence[:PRACTICE_TRIALS], results[:PRACTICE_TRIALS],
            tutorial_intro=True, surprise_indices=surprises,
            tutorial_prompt="Keep guessing!",
        )

    elif stage == 5:
        urn["_tutorial_step"] = stage
        _practice_draw_prediction(
            win, urn, sequence[:PRACTICE_TRIALS], results[:PRACTICE_TRIALS],
            tutorial_intro=True, surprise_indices=surprises,
            tutorial_prompt="The original pattern continues",
        )

        _text(
            win,
            "Press SPACE to continue",
            -0.185,  # Position underneath the main prompt
            height=0.023,
            color="#66758b",
        ).draw()

    elif stage in (6, 7, 8):
        if assignment is None:
            raise ValueError("Tutorial comparison requires the practice urn assignment")
        _tutorial_draw_reward_comparison(win, stage, assignment)

    elif stage == 9:
        _draw_tutorial_progress(win, stage)

        # Title
        _text(win, "Your goal!", 0.37, height=0.054, bold=True, color=INSTRUCTION_NAVY, ).draw()

        # Target image
        visual.ImageStim(win=win, image=str(TARGET_IMAGE_PATH), pos=(0, 0.085), size=(0.4, 0.4), interpolate=True, ).draw()

        # Goal explanation
        _text(win, "Your goal is to get as many points as possible in all rounds.", -0.17, height=0.042, color=INSTRUCTION_BODY, wrap_width=1.20, ).draw()

        # Continue instruction
        _text(win, "Press SPACE to continue", -0.32, height=0.024, color=INSTRUCTION_MUTED,).draw()
    else:
        raise ValueError(f"Unsupported tutorial stage: {stage}")



def _animate_tutorial_balls_into_urn(win, sequence, assignment):
    """Balls enter open urns, lids descend, then closed urns appear."""

    colors = list(sequence[:PRACTICE_TRIALS])

    # Animation settings
    n = max(1, TUTORIAL_ANIMATION_FRAMES)
    lid_frames = 8

    # Adjust these values to align the lid with your urn image.
    lid_final_offset = 0.17
    lid_start_offset = 0.18

    def draw_background():
        _draw_tutorial_progress(win, 6)

        _text(
            win,
            "Compare how you can get points",
            0.340,
            height=0.043,
            bold=True
        ).draw()

        _text(
            win,
            "Blue and magenta balls are hidden inside the urns",
            0.252,
            height=0.023,
            color=INSTRUCTION_BODY
        ).draw()

    # --------------------------------------------------
    # PART 1: Balls move into the OPEN urns
    # --------------------------------------------------

    for frame in range(n + 1):

        t = frame / n
        eased = t * t * (3.0 - 2.0 * t)

        draw_background()

        # Draw the opened urns
        for side in ("left", "right"):

            urn = assignment[side]

            urn_x = (
                params.URN_LEFT_POS[0]
                if side == "left"
                else params.URN_RIGHT_POS[0]
            )

            _draw_reward_urn(
                win,
                urn,
                urn_x,
                REWARD_CHOICE_URN_SCALE,
                y_offset=OPEN_URN_Y_OFFSET,
                opened=True
            )

        # Move a copy of the sequence into each urn
        for side in ("left", "right"):

            target_x = (
                params.URN_LEFT_POS[0]
                if side == "left"
                else params.URN_RIGHT_POS[0]
            )

            for i, color in enumerate(colors):

                start_x = -0.38 + i * 0.085
                start_y = 0.155

                dest_x = target_x + ((i % 3) - 1) * 0.016

                # Match the height where the lid will eventually stop
                lid_final_y = (
                    params.URN_LEFT_POS[1]
                    + OPEN_URN_Y_OFFSET
                    + lid_final_offset
                )

                # Balls move toward the urn's opening
                dest_y = lid_final_y - 0.02

                # Balls rise first, then travel toward the urn.
                rise_height = 0.12
                rise_fraction = 0.35

                if eased < rise_fraction:
                    # Phase A: Rise vertically
                    p = eased / rise_fraction
                    x = start_x
                    y = start_y + rise_height * p

                else:
                    # Phase B: Move toward and into the urn
                    p = (eased - rise_fraction) / (1.0 - rise_fraction)
                    p = p * p * (3.0 - 2.0 * p)

                    x = start_x + (dest_x - start_x) * p
                    y = start_y + rise_height + (
                        dest_y - (start_y + rise_height)
                    ) * p

                # Balls disappear once inside the urn
                if eased < 0.94:

                    _tutorial_ball(
                        win,
                        color,
                        x,
                        y,
                        radius=0.020 * (1.0 - 0.65 * eased)
                    )

        win.flip()
        core.wait(0.005)

    # --------------------------------------------------
    # PART 2: Lids descend onto the OPEN urns
    # --------------------------------------------------

    for frame in range(lid_frames + 1):

        t = frame / lid_frames
        eased = t * t * (3.0 - 2.0 * t)

        draw_background()

        for side in ("left", "right"):

            urn = assignment[side]

            urn_x = (
                params.URN_LEFT_POS[0]
                if side == "left"
                else params.URN_RIGHT_POS[0]
            )

            # Open urn stays in exactly the same position
            _draw_reward_urn(
                win,
                urn,
                urn_x,
                REWARD_CHOICE_URN_SCALE,
                y_offset=OPEN_URN_Y_OFFSET,
                opened=True
            )

            # Calculate the final lid position
            lid_final_y = (
                params.URN_LEFT_POS[1]
                + OPEN_URN_Y_OFFSET
                + lid_final_offset
            )

            # Start lid above the urn
            lid_start_y = lid_final_y + lid_start_offset

            # Move lid downward
            lid_y = (
                lid_start_y
                + (lid_final_y - lid_start_y) * eased
            )

            _draw_urn_lid(
                win,
                urn_x,
                lid_y,
                scale=1.0
            )

        win.flip()
        core.wait(0.005)

    # --------------------------------------------------
    # PART 3: Replace with the fully CLOSED urn images
    # --------------------------------------------------

    draw_background()

    for side in ("left", "right"):

        urn = assignment[side]

        urn_x = (
            params.URN_LEFT_POS[0]
            if side == "left"
            else params.URN_RIGHT_POS[0]
        )

        # Exactly the same position and size as the real choice
        _draw_reward_urn(
            win,
            urn,
            urn_x,
            REWARD_CHOICE_URN_SCALE,
            y_offset=0,
            opened=False
        )

    win.flip()
    core.wait(0.08)



def _tutorial_record_guess(win, urn, sequence, trials,
                           surprise_indices, trial_number, guess, rt):
    """Use the existing prediction/outcome animation; never award real points."""
    is_surprise = trial_number == TUTORIAL_SURPRISE_TRIAL
    pattern_idx = params.N_INITIAL_DRAWS + trial_number - 1
    color, expected = task.generate_next_outcome(
        selected_urn=urn,
        prediction_index=pattern_idx,
        is_noise_trial=is_surprise,
    )
    if is_surprise:
        assert expected == "blue" and color == "magenta"
    sequence.append(color)
    trials.append({
        "trial_number": trial_number,
        "guess": guess,
        "outcome": color,
        "correct": guess == color,
        "response_time": rt,
        "is_noise_trial": is_surprise,
        "pattern_prediction": expected,
        "prediction_index": pattern_idx,
    })
    if is_surprise:
        surprise_indices.append(trial_number - 1)
    _practice_show_outcome(
        win, urn, sequence, [entry["correct"] for entry in trials],
        guess, color, guess == color,
        final_trial=False, trial_number=trial_number,
        is_surprise=is_surprise,
        surprise_indices=surprise_indices,
        tutorial_intro=True,
    )


def _tutorial_collect_draws(win, urn, sequence, trials,
                            surprise_indices, final_trial, stage,
                            auto_advance=False):
    """Play the next draws; never repeat recorded answers when revisiting."""
    urn["_tutorial_step"] = stage
    
    already_completed = len(trials) >= final_trial
    pattern_pause_completed = False

    while len(trials) < final_trial:

        # Explain the repeating pattern after four balls.
        if (
            stage == 1
            and len(trials) == 4
            and not pattern_pause_completed
        ):
            urn["_tutorial_step"] = 2

            _practice_draw_prediction(
                win,
                urn,
                sequence,
                [entry["correct"] for entry in trials],
                tutorial_intro=True,
                tutorial_prompt="Notice how the pattern of 2 repeats",
            )

            _text(
                win,
                "Press SPACE to continue",
                -0.185,
                height=0.023,
                color=INSTRUCTION_MUTED,
            ).draw()

            win.flip()

            if _wait_tutorial_nav(win) == -1:
                return -1

            pattern_pause_completed = True
            urn["_tutorial_step"] = stage

        next_trial = len(trials) + 1

        if next_trial == TUTORIAL_SURPRISE_TRIAL:
            raise RuntimeError("Surprise draw 7 is handled after the explanation")
        if next_trial == 1:
            prompt = "Make your guess"
        elif stage == 4 and next_trial == TUTORIAL_SURPRISE_TRIAL + 1:
            prompt = "The original pattern continues"
        else:
            prompt = "Keep guessing"
        guess, rt = _practice_collect_prediction(
            win, urn, sequence, [entry["correct"] for entry in trials],
            tutorial_intro=True, tutorial_prompt=prompt,
            tutorial_first_guess=(next_trial == 1),
            surprise_indices=surprise_indices, allow_back=True,
        )
        if guess is None:
            return -1
        _tutorial_record_guess(win, urn, sequence, trials, surprise_indices,
                               next_trial, guess, rt)
    # Arriving at the sixth or tenth draw automatically changes the caption
    # on the same screen, not to a new explanatory page.
    if auto_advance and not already_completed:
        return 1
    _tutorial_draw_scene(win, stage, urn, sequence, trials)
    win.flip()
    return _wait_tutorial_nav(win)


def _run_practice_tutorial(win):
    """Teach the rules, compare payoffs, then pass the SAME urns to practice."""
    name = params.PRETTY_URN_NAMES[0]
    urn = task.create_ambiguous_urn(
        name, "Example urn", "known", TUTORIAL_K,
        cycle=list(TUTORIAL_CYCLE),
    )
    sequence = list(task.generate_latent_sequence(
        list(TUTORIAL_CYCLE), params.N_INITIAL_DRAWS,
    ))
    # Prepare the first real practice choice now, to preserve the urns shown
    # in the comparison when the "Choose an urn" prompt appears.
    first_assignment = task.assign_urns_to_sides(
        deterministic_value=random.choice(PRACTICE_DETERMINISTIC_VALUES),
        ambiguous_condition="known", k=TUTORIAL_K,
    )
    trials, surprises = [], []
    pending_seventh = None
    transition_seen = False
    stage = 0
    while stage < TUTORIAL_STEP_COUNT:
        urn["_tutorial_step"] = stage
        if stage == 1:
            move = _tutorial_collect_draws(
                win, urn, sequence, trials, surprises, 6, stage,
                auto_advance=True,
            )
        elif stage == 2 and pending_seventh is None:
            # Immediately after the repeating-pattern explanation, B/M is the
            # response for ball 7. The pair boxes remain on the prediction view.
            guess, rt = _practice_collect_prediction(
                win, urn, sequence, [entry["correct"] for entry in trials],
                tutorial_intro=True,
                tutorial_prompt="Notice how the pattern of 2 repeats",
                allow_back=True,
            )
            if guess is None:
                move = -1
            else:
                pending_seventh = (guess, rt)
                move = 1
        elif stage == 4:
            move = _tutorial_collect_draws(
                win, urn, sequence, trials, surprises,
                PRACTICE_TRIALS, stage, auto_advance=True,
            )
        else:
            if stage == 6 and not transition_seen:
                _animate_tutorial_balls_into_urn(win, sequence, first_assignment)
                transition_seen = True
            _tutorial_draw_scene(
                win, stage, urn, sequence, trials,
                pending=pending_seventh, assignment=first_assignment,
            )
            win.flip()
            move = _wait_tutorial_nav(win)
            if stage == 0 and move == 1:
                _text(
                    win,
                    "You will guess the color of the balls inside an urn\n by pressing B for blue or M for magenta.",
                    0.05,
                    height=0.040,
                    bold=True,
                    color=INSTRUCTION_NAVY,
                ).draw()

                    # Keyboard instructions (softer color)
                _text(
                    win,
                    "At any time, press BACKSPACE to see the previous explanation.\n\n\n"
                    "Press SPACE to continue.",
                    -0.10,
                    height=params.BODY_HEIGHT,
                    bold=False,
                    color=INSTRUCTION_MUTED,
                ).draw()

                win.flip()
                move = _wait_tutorial_nav(win)

        # Reveal the changed-color ball only after the participant has seen
        # the magician's explanation, while retaining the same urn screen.
        if stage == 3 and move == 1 and len(trials) == 6:
            if pending_seventh is None:
                raise RuntimeError("The seventh guess was not collected")
            guess, rt = pending_seventh
            _tutorial_record_guess(
                win, urn, sequence, trials, surprises,
                TUTORIAL_SURPRISE_TRIAL, guess, rt,
            )
        if move == 1:
            stage += 1
        else:
            stage = max(0, stage - 1)

    return {
        "trial_data": trials,
        "full_sequence": list(sequence),
        "surprise_trial": TUTORIAL_SURPRISE_TRIAL,
        "k": TUTORIAL_K,
        "cycle": list(TUTORIAL_CYCLE),
        "first_practice_assignment": first_assignment,
    }


REWARD_CHOICE_URN_SCALE = 1.3


def _draw_small_indicator_row(win, label, filled, x, y,
                              total=3,
                              text_color="#334155",
                              active_color="#334155",
                              empty_color="#b8c4d2",
                              radius=0.008,
                              spacing=0.026):
    """Draw a label with 3 small indicator balls, like in the task UI."""
    _text(
        win, label, y, 0.020,
        color=text_color, x=x - 0.075, wrap_width=0.18
    ).draw()

    start_x = x + 0.015
    for i in range(total):
        active = i < filled
        visual.Circle(
            win,
            pos=(start_x + i * spacing, y),
            radius=radius,
            fillColor=active_color if active else None,
            lineColor=active_color if active else empty_color,
            lineWidth=1.2,
            edges=48,
        ).draw()

def _reward_title(win, choosing=False):
    heading = "Choose an urn" if choosing else "Compare the rewards"

    _text(win, heading, 0.405, 0.047, bold=True).draw()

    instruction = (
        "Press ← or → to choose"
        if choosing
        else "Press SPACE to continue"
    )

    _text(
        win, instruction, 0.325, 0.026,
        color="#576a82"
    ).draw()



def _draw_reward_urn(win, urn, x, scale=1.0, y_offset=0, opened=False):
    """Draw an open or closed urn."""
    if scale <= 0.001:
        return

    image = str(
        urn["opened_image"] if opened else urn["closed_image"]
    )

    width, height = params.URN_IMAGE_SIZE

    visual.ImageStim(
        win=win,
        image=image,
        pos=(x, params.URN_LEFT_POS[1] + y_offset),
        size=(width * scale, height * scale),
        interpolate=True,
    ).draw()

def _draw_urn_lid(win, x, y, scale=1.0):
    visual.ImageStim(
        win=win,
        image=str(URN_LID_IMAGE),
        pos=(x, y),
        size=(0.37 * scale, 0.17 * scale),   # tweak if needed
        interpolate=True,
    ).draw()


def _render_reward_stage(win, assignment, choosing=True):
    """Draw both urns once, without obsolete tutorial animations."""
    _reward_title(win, choosing=True)
    for side in ("left", "right"):
        urn = assignment[side]
        x = params.URN_LEFT_POS[0] if side == "left" else params.URN_RIGHT_POS[0]
        _draw_reward_urn(win, urn, x, REWARD_CHOICE_URN_SCALE)
        task.draw_selection_condition_text(win, urn, x)
    win.flip()


def _standard_urn_selection(win, assignment):
    """Use the same final choice layout without repeating the tutorial."""

    _render_reward_stage(win, assignment, choosing=True)

    event.clearEvents()

    while True:
        keys = event.waitKeys(keyList=["left", "right", "escape"])

        if "escape" in keys:
            task.quit_experiment(win)

        if "left" in keys:
            return "left"

        if "right" in keys:
            return "right"


def _round_summary(win, block_number, points, correct_count):
    """Practice-round timeline with a compact reward/accuracy card."""
    accuracy = 100 * correct_count / PRACTICE_TRIALS
    EXPECTED_ACCURACY= 0.8
    EXPECTED_COLOR = "#BF6B32"  # BurntOrange
    # ---------------------------------------------------------
    # Minimal practice progress indicator
    # ---------------------------------------------------------

    # Small heading
    _text(
        win,
        f"PRACTICE · ROUND {block_number} OF {ROUND_N}",
        0.33,
        height=0.022,
        color="#64748b",
        bold=True,
    ).draw()

    # Four horizontal progress bars
    bar_width = 0.085
    bar_height = 0.01
    bar_gap = 0.014
    bar_y = 0.275

    total_width = ROUND_N * bar_width + (ROUND_N - 1) * bar_gap
    start_x = -total_width / 2 + bar_width / 2

    for i in range(ROUND_N):
        x = start_x + i * (bar_width + bar_gap)

        completed = i < block_number

        color = "#2e7bd4" if completed else "#aab8ca"

        visual.Rect(
            win,
            pos=(x, bar_y),
            width=bar_width,
            height=bar_height,
            fillColor=color,
            lineColor=color,
        ).draw()

    
    # ---------------------------------------------------------
    # Circular accuracy indicator + points
    # ---------------------------------------------------------
    circle_x = -0.17
    circle_y = -0.015
    ring_radius = 0.103
    ring_width = 11

    # Full grey background ring
    visual.Circle(
        win,
        pos=(circle_x, circle_y),
        radius=ring_radius,
        fillColor=None,
        lineColor="#aab8ca",
        lineWidth=ring_width,
        edges=180,
    ).draw()

    # Blue accuracy arc, starting at the top, clockwise
    # Smooth blue accuracy arc
    fraction = max(0.0, min(1.0, accuracy / 100))

    if fraction > 0:
        n_points = max(30, int(360 * fraction))

        angles = [
            math.pi / 2 - 2 * math.pi * fraction * i / n_points
            for i in range(n_points + 1)
        ]

        vertices = [
            (
                circle_x + ring_radius * math.cos(angle),
                circle_y + ring_radius * math.sin(angle),
            )
            for angle in angles
        ]

        visual.ShapeStim(
            win,
            vertices=vertices,
            closeShape=False,
            fillColor=None,
            lineColor="#2e7bd4",
            lineWidth=ring_width,
            interpolate=True,
        ).draw()

        # ---------------------------------------------------------
    # Expected accuracy marker on the circular ring
    # ---------------------------------------------------------

    expected_angle = (
        math.pi / 2 - 2 * math.pi * EXPECTED_ACCURACY
    )

    # Line starts slightly inside and ends slightly
    # outside the circular accuracy ring.
    inner_radius = ring_radius - 0.018
    outer_radius = ring_radius + 0.018

    start_x = circle_x + inner_radius * math.cos(expected_angle)
    start_y = circle_y + inner_radius * math.sin(expected_angle)

    end_x = circle_x + outer_radius * math.cos(expected_angle)
    end_y = circle_y + outer_radius * math.sin(expected_angle)

    visual.Line(
        win,
        start=(start_x, start_y),
        end=(end_x, end_y),
        lineColor=EXPECTED_COLOR,
        lineWidth=4.5,
    ).draw()

    # Accuracy inside the ring
    _text(
        win, f"{accuracy:.0f}%",
        circle_y + 0.012,
        height=0.048,
        bold=True,
        x=circle_x,
    ).draw()

    _text(
        win, "correct",
        circle_y - 0.038,
        height=0.022,
        color="#64748b",
        x=circle_x,
    ).draw()
    _text(
        win,
        f"Average: {EXPECTED_ACCURACY:.0%}",
        circle_y - ring_radius - 0.065,
        height=0.020,
        color=EXPECTED_COLOR,
        x=circle_x,
    ).draw()

    # Subtle vertical separator
    visual.Line(
        win,
        start=(0.015, -0.145),
        end=(0.015, 0.05),
        lineColor="#b7c2d0",
        lineWidth=1.5,
    ).draw()

    # Points on the right
    _text(
        win, f"{points:g} points",
        0.032,
        height=0.052,
        bold=True,
        x=0.205,
    ).draw()

    _text(
        win, "earned this round",
        -0.025,
        height=0.023,
        color="#64748b",
        x=0.205,
    ).draw()

    _text(win, "Practice points do not count toward your final score.",
          -0.303, height=0.020, color="#576a82").draw()
    _text(win, "Press SPACE to continue", -0.366,
          height=0.022, color="#576a82").draw()
    win.flip()
    _wait_space(win)


# -----------------------------------------------------------------------------
# Minimal practice prediction display (does not modify the real task).
# -----------------------------------------------------------------------------
# Minimal top-left labels + circles (PsychoPy height units).
# Adjust these values to move or resize the interface.
PRACTICE_INFO_LABEL_X = -0.66
PRACTICE_INFO_BALL_START_X = -0.35
PRACTICE_INFO_ROW_Y = (0.374, 0.326)
PRACTICE_URN_TYPE_Y = 0.422
PRACTICE_INFO_TEXT_HEIGHT = 0.019
PRACTICE_INFO_BALL_RADIUS = 0.007
PRACTICE_INFO_BALL_SPACING = 0.023
PRACTICE_INFO_COLOR = "#253f62"
PRACTICE_INFO_EMPTY_COLOR = "#536e8c"

# Simple score text and a thin line, as in the second mockup.
PRACTICE_BAR_Y = 0.26
PRACTICE_SCORE_LEFT_X = -0.62
PRACTICE_SCORE_RIGHT_X = 0.58
PRACTICE_REMINDER_AFTER = 3.0
PRACTICE_GUESS_Y = -0.040
# Short, optional feedback animations: preserve the urn -> history movement.
PRACTICE_FEEDBACK_SECONDS = 0.14


def _practice_draw_prediction(win, selected_urn, sequence, trial_results,
                              guess_color=None, reminder=False,
                              points_override=None, tutorial_intro=False,
                              tutorial_prompt=None, surprise_indices=(),
                              tutorial_heading=None, hide_urn_type=False,
                              tutorial_first_guess=False):
    """Practice prediction UI, also used for in-place tutorial explanations."""
    known = bool(selected_urn["participant_knows_k"])
    visible_length = int(selected_urn["ambiguous_k"]) if known else 0
    reward_type = (
        "Guaranteed points" if selected_urn["urn_type"] == "deterministic"
        else "Points per correct guess"
    )

    if tutorial_intro:
        _draw_tutorial_progress(win, selected_urn.get("_tutorial_step", 1))
        _text(win, tutorial_heading or "Guess the next ball", 0.430,
              height=0.043, bold=True).draw()
    elif not hide_urn_type:
        visual.TextStim(
            win, text="Urn type",
            pos=(PRACTICE_INFO_LABEL_X, PRACTICE_URN_TYPE_Y),
            height=0.019, color=PRACTICE_INFO_COLOR,
            alignText="left", anchorHoriz="left",
        ).draw()
        visual.TextStim(
            win, text=reward_type,
            pos=(PRACTICE_INFO_BALL_START_X-0.01, PRACTICE_URN_TYPE_Y),
            height=0.019, bold=True, color=PRACTICE_INFO_COLOR,
            alignText="left", anchorHoriz="left",
        ).draw()

    pattern_label = (
        f"Pattern length ({visible_length})" if known else "Pattern length (<4)"
    )
    # The tutorial now explicitly shows the ONE surprise ball, rather than
    # the old "possible colors" instruction. No points/accuracy is displayed.
    info_rows = [
        (pattern_label, visible_length),
        (f"Surprise balls ({PRACTICE_FLIPS})", PRACTICE_FLIPS),
    ]
    for row_index, (label, filled) in enumerate(info_rows):
        y = PRACTICE_INFO_ROW_Y[row_index]
        task.draw_text(
            win, label, (PRACTICE_INFO_LABEL_X, y),
            height=PRACTICE_INFO_TEXT_HEIGHT,
            color=PRACTICE_INFO_COLOR, align_text="left",
        ).draw()
        # Known k: draw exactly k filled circles (no unused outlines).
        # Unknown k: retain three hollow circles to represent an undisclosed length.
        total_balls = (visible_length if known else 3) if row_index == 0 else PRACTICE_FLIPS
        for index in range(total_balls):
            x = PRACTICE_INFO_BALL_START_X + index * PRACTICE_INFO_BALL_SPACING
            circle = task._cached(
                win, ("practice_info_circle", row_index, index, x, y,
                      PRACTICE_INFO_BALL_RADIUS),
                lambda x=x, y=y: visual.Circle(
                    win, pos=(x, y), radius=PRACTICE_INFO_BALL_RADIUS,
                    lineWidth=1.3, edges=32,
                ),
            )
            active = index < filled
            circle.fillColor = PRACTICE_INFO_COLOR if active else None
            circle.lineColor = (PRACTICE_INFO_COLOR if active
                                else PRACTICE_INFO_EMPTY_COLOR)
            circle.draw()

        if (row_index == 0 and known and tutorial_intro
                and selected_urn.get("_tutorial_step") == 2 and len(sequence) == 4):
            # Mirror the pair boxes around the six observed balls.
            outline_width = ((visible_length - 1) * PRACTICE_INFO_BALL_SPACING
                             + 2 * PRACTICE_INFO_BALL_RADIUS + 0.019)
            visual.Rect(
                win=win,
                pos=(PRACTICE_INFO_BALL_START_X
                     + (visible_length - 1) * PRACTICE_INFO_BALL_SPACING / 2, y),
                width=outline_width, height=0.034,
                fillColor=None, lineColor="#80579c", lineWidth=2.0,
            ).draw()

    correct = sum(bool(v) for v in trial_results)
    bar_left = PRACTICE_SCORE_LEFT_X
    bar_right = PRACTICE_SCORE_RIGHT_X - 0.13
    bar_width = bar_right - bar_left
    bar_y = PRACTICE_BAR_Y
    bar_height = 0.035
    task._draw_pill(win, bar_left, bar_right, bar_y, bar_height,
                    "#d6dce5", "practice_track")

    # Same scoring basis as the main task: the bar fills for correct guesses,
    # not merely for the number of balls already drawn.
    fraction = min(1.0, correct / PRACTICE_TRIALS)

    fill_width = bar_width * fraction
    if fill_width >= bar_height:
        task._draw_pill(win, bar_left, bar_left + fill_width, bar_y,
                        bar_height, "#789bc0", "practice_fill")

    fixed = selected_urn["urn_type"] == "deterministic"
    completed = len(trial_results)
    accuracy = 100 * correct / completed if completed else 0
    # The tutorial illustrates possible points; they are not paid or recorded
    # as the participant's actual practice reward.
    points = (correct * params.REWARD_PER_CORRECT_GUESS if tutorial_intro else
              selected_urn["value"] if fixed else
              correct * params.REWARD_PER_CORRECT_GUESS)
    if points_override is not None:
        points = points_override
    task.draw_text(
        win, f"{points:g} pts", (bar_left + 0.018, bar_y),
        height=0.021, bold=True,
        color="#ffffff" if fill_width >= 0.10 else PRACTICE_INFO_COLOR,
        align_text="left",
    ).draw()
    task.draw_text(
        win, f"{accuracy:.0f}% correct", (PRACTICE_SCORE_RIGHT_X, bar_y),
        height=0.020, color=PRACTICE_INFO_COLOR, align_text="right",
    ).draw()

    _practice_draw_history(win, sequence, surprise_indices=surprise_indices)
    if tutorial_intro and selected_urn.get("_tutorial_step") == 2 and len(sequence) == 4:
        _draw_pattern_pair_boxes(win, (0, 2))
    task.draw_selected_open_urn(win, selected_urn)

    if tutorial_prompt:
        # Same caption position for the pattern, magician and continuation.
        size = (0.027 if len(tutorial_prompt) > 52 else
                0.039 if tutorial_first_guess else
                0.032 if tutorial_intro else 0.024)
        _text(win, tutorial_prompt, -0.115,
              height=size,
              bold=True, color=INSTRUCTION_NAVY,
              wrap_width=1.40).draw()
    if tutorial_intro:
        if (selected_urn.get("_tutorial_step") == 2 and tutorial_prompt != "Notice how the pattern of 2 repeats"):
            _text(win, "Press B for blue or M for magenta", -0.202,
                  height=0.023, color="#66758b").draw()

    if guess_color is not None:
        guess_ball = task._cached(
            win, ("practice_guess_ball", PRACTICE_GUESS_Y),
            lambda: visual.Circle(
                win, pos=(0, PRACTICE_GUESS_Y), radius=0.048,
                lineWidth=1.6, edges=32,
            ),
        )
        guess_ball.fillColor = params.ball_display_color(guess_color)
        guess_ball.lineColor = params.ball_display_color(guess_color)
        guess_ball.draw()

    if (reminder or tutorial_first_guess) and (not tutorial_intro or selected_urn.get("_tutorial_step") != 2):
        # Show key guidance immediately on the first tutorial guess;
        # otherwise keep the usual delayed reminder.
        _text(win, "Press B for blue or M for magenta", -0.202,
              0.023, color="#66758b").draw()


def _practice_collect_prediction(win, selected_urn, sequence, trial_results,
                                 tutorial_intro=False, tutorial_prompt=None,
                                 surprise_indices=(), allow_back=False,
                                 tutorial_first_guess=False):
    """Record reaction time from initial display; show hint only after 3 s."""
    event.clearEvents()
    clock = core.Clock()
    reminder_shown = False
    win.callOnFlip(clock.reset)
    # Time responses from when the prediction screen appears.
    _practice_draw_prediction(win, selected_urn, sequence, trial_results,
                              tutorial_intro=tutorial_intro,
                              tutorial_prompt=tutorial_prompt,
                              surprise_indices=surprise_indices,
                              tutorial_first_guess=tutorial_first_guess)
    win.flip()
    while True:
        allowed_keys = list(params.GUESS_KEYS.keys()) + ["escape"]
        if allow_back:
            allowed_keys.append("backspace")
        keys = event.getKeys(keyList=allowed_keys, timeStamped=clock)
        if keys:
            key, rt = keys[0]
            if key == "escape":
                task.quit_experiment(win)
            if key == "backspace":
                return None, None
            return params.GUESS_KEYS[key], float(rt)
        if not reminder_shown and clock.getTime() >= PRACTICE_REMINDER_AFTER:
            reminder_shown = True
            _practice_draw_prediction(win, selected_urn, sequence,
                                      trial_results, reminder=True,
                                      tutorial_intro=tutorial_intro,
                                      tutorial_prompt=tutorial_prompt,
                                      surprise_indices=surprise_indices,
                                      tutorial_first_guess=tutorial_first_guess)
            win.flip()
        core.wait(0.005)


# Animation settings (PsychoPy height units). Change these values to tune it.
PRACTICE_REVEAL_BALL_RADIUS = 0.12  # Larger than draw-history balls.
PRACTICE_START_HEIGHT_FRACTION = 0.35  # Higher value = starts higher in urn.
PRACTICE_RISE_FRAMES = 1
PRACTICE_FLIP_HALF_FRAMES = 1  # Always completes both halves of the flip.
PRACTICE_HISTORY_FRAMES = 1


def _practice_animate_ball_reveal(win, selected_urn, sequence,
                                  previous_results, guess, outcome,
                                  is_surprise=False, surprise_indices=(),
                                  tutorial_intro=False):
    """Rise as grey ball, visibly flip every time, shrink into history."""
    previous_sequence = sequence[:-1]
    history_pos = task.get_feedback_ball_position(len(sequence) - 1)
    start_pos = (
        params.SELECTED_URN_POS[0],
        params.SELECTED_URN_POS[1]
        + params.SELECTED_URN_SIZE[1] * PRACTICE_START_HEIGHT_FRACTION,
    )
    reveal_pos = params.OUTCOME_BALL_POS
    reveal_radius = PRACTICE_REVEAL_BALL_RADIUS
    history_radius = params.FEEDBACK_BALL_RADIUS
    hidden_grey = "#94a3b8"

    # Create only one stimulus per prediction rather than one per frame.
    moving_ball = visual.Circle(
        win=win, pos=start_pos, radius=reveal_radius,
        fillColor=hidden_grey, lineColor="black", lineWidth=2,
        edges=48,
    )

    def frame(pos, color, radius, width_scale=1.0, show_hat=False):
        # Previous observations stay visible until the new ball reaches history.
        _practice_draw_prediction(
            win, selected_urn, previous_sequence, previous_results,
            surprise_indices=surprise_indices, tutorial_intro=tutorial_intro,
        )
        moving_ball.pos = pos
        moving_ball.fillColor = params.ball_display_color(color)
        moving_ball.size = (
            2 * radius * max(0.01, width_scale),
            2 * radius,
        )
        moving_ball.draw()
        if is_surprise and show_hat:
            _draw_surprise_hat(win, pos, radius, tag="moving")
        win.flip()

    def ease(t):
        return t * t * (3 - 2 * t)

    def interpolate(a, b, fraction):
        return (a[0] + (b[0] - a[0]) * fraction,
                a[1] + (b[1] - a[1]) * fraction)

    # Rise: a short fixed frame sequence avoids inconsistent durations.
    for i in range(PRACTICE_RISE_FRAMES + 1):
        t = ease(i / PRACTICE_RISE_FRAMES)
        frame(interpolate(start_pos, reveal_pos, t), hidden_grey,
              reveal_radius)

    # Flip first half: grey ball narrows. Second half: colored ball expands.
    # Frame counts guarantee the change is always visible despite slow redraws.
    for i in range(PRACTICE_FLIP_HALF_FRAMES + 1):
        width = 1.0 - i / PRACTICE_FLIP_HALF_FRAMES
        frame(reveal_pos, hidden_grey, reveal_radius, width)
    for i in range(PRACTICE_FLIP_HALF_FRAMES + 1):
        width = i / PRACTICE_FLIP_HALF_FRAMES
        frame(reveal_pos, outcome, reveal_radius, width, show_hat=True)

    # Move to history while reducing the radius to the precise history radius.
    for i in range(PRACTICE_HISTORY_FRAMES + 1):
        t = ease(i / PRACTICE_HISTORY_FRAMES)
        radius = reveal_radius + (history_radius - reveal_radius) * t
        frame(interpolate(reveal_pos, history_pos, t), outcome, radius,
              show_hat=True)


def _practice_show_outcome(win, selected_urn, sequence, trial_results,
                           guess, outcome, correct, final_trial, trial_number,
                           is_surprise=False, surprise_indices=(),
                           tutorial_intro=False):
    """Brief guessed-color preview, then original urn-to-history animation."""
    previous = trial_results[:-1]

    # Hidden ball rises, flips to the actual outcome, then enters history.
    _practice_animate_ball_reveal(
        win, selected_urn, sequence, previous, guess, outcome,
        is_surprise=is_surprise, surprise_indices=surprise_indices,
        tutorial_intro=tutorial_intro,
    )

    _practice_draw_prediction(
        win, selected_urn, sequence, trial_results,
        surprise_indices=surprise_indices, tutorial_intro=tutorial_intro,
    )
    if final_trial:
        _text(win, "Press SPACE to continue", -0.18, 0.024,
              color="#000000").draw()
    win.flip()
    if final_trial:
        _wait_space(win)
    else:
        core.wait(PRACTICE_FEEDBACK_SECONDS)


def _practice_block(win, block_number, condition, k, guided=False,
                    prepared_assignment=None, skip_fixation=False):
    """Ten prediction trials with the existing task visuals and RTs."""
    assignment = prepared_assignment
    if assignment is None:
        assignment = task.assign_urns_to_sides(
            deterministic_value=random.choice(PRACTICE_DETERMINISTIC_VALUES),
            ambiguous_condition=condition,
            k=k,
        )
    # Both urns have the same prediction-task parameters.
    ambiguous_urn = next(
        urn for urn in assignment.values()
        if urn["urn_type"] == "ambiguous"
    )

    deterministic_urn = next(
        urn for urn in assignment.values()
        if urn["urn_type"] == "deterministic"
    )

    # The first example demonstrates a real 2-ball repeat with a visible change.
    # Both urns keep identical underlying rules, regardless of which is chosen.
    if guided:
        ambiguous_urn["cycle"] = list(TUTORIAL_CYCLE)

    # Copy the task parameters, but preserve reward type and value.
    deterministic_urn["ambiguous_k"] = ambiguous_urn["ambiguous_k"]
    deterministic_urn["participant_knows_k"] = ambiguous_urn["participant_knows_k"]
    deterministic_urn["cycle"] = list(ambiguous_urn["cycle"])
    # Fixation before EVERY urn choice, including the second practice round.
    if not skip_fixation:
        _fixation(win)
    selected_side = _standard_urn_selection(win, assignment)
    selected_urn = assignment[selected_side]
    task.animate_selected_urn_transition(
        win, selected_urn, selected_side, assignment,
    )
    sequence = task.generate_latent_sequence(
        selected_urn["cycle"], params.N_INITIAL_DRAWS,
    )
    
    # Start with all trials following the underlying pattern.
    outcomes = [False] * PRACTICE_TRIALS

    # Randomly place the flipped ball(s) only in the last N trials.
    if guided:
        flip_positions = [TUTORIAL_SURPRISE_TRIAL - 1]
    else:
        flip_positions = random.sample(
            range(PRACTICE_TRIALS-1),
            PRACTICE_FLIPS,
        )

    for position in flip_positions:
        outcomes[position] = True

    trials = []
    surprise_indices = []

    for trial_number, is_flipped in enumerate(outcomes, start=1):
        previous_results = [entry["correct"] for entry in trials]
        introductory_stage = guided and trial_number <= TUTORIAL_PATTERN_EXPLANATION_AFTER

        if trial_number == 1:
            if guided:
                _tutorial_intro(win, selected_urn, sequence, previous_results)
            else:
                hint = _hint_for_trial(selected_urn, condition, trial_number)
                if hint:
                    _context_hint(win, selected_urn, sequence,
                                  previous_results, *hint)

        prompt = None
        if guided:
            if trial_number == 1:
                prompt = "Guess BLUE first (B)"
            elif trial_number <= 6:
                prompt = "Keep guessing: B for blue, M for magenta"
            elif trial_number == 7:
                prompt = "Guess the next ball: B or M"
            else:
                prompt = "Guess again: B or M"

        guess, reaction_time = _practice_collect_prediction(
            win, selected_urn, sequence, previous_results,
            tutorial_intro=introductory_stage,
            tutorial_prompt=prompt,
            surprise_indices=surprise_indices,
        )
        prediction_index = params.N_INITIAL_DRAWS + trial_number - 1
        outcome, pattern_prediction = task.generate_next_outcome(
            selected_urn=selected_urn,
            prediction_index=prediction_index,
            is_noise_trial=is_flipped,
        )
        # A surprise always has the opposite color from the underlying rule.
        if is_flipped:
            assert outcome == task.opposite_color(pattern_prediction)
            if guided:
                _tutorial_surprise(
                    win, selected_urn, sequence, previous_results,
                    pattern_prediction, outcome,
                )
            surprise_indices.append(trial_number - 1)

        sequence.append(outcome)
        correct = (guess == outcome)
        trials.append({
            "trial_number": trial_number,
            "guess": guess,
            "outcome": outcome,
            "correct": correct,
            "response_time": reaction_time,
            "is_noise_trial": is_flipped,
            "pattern_prediction": pattern_prediction,
            "prediction_index": prediction_index,
        })
        _practice_show_outcome(
            win, selected_urn, sequence,
            [entry["correct"] for entry in trials],
            guess, outcome, correct,
            final_trial=(trial_number == PRACTICE_TRIALS and not guided),
            trial_number=trial_number,
            is_surprise=is_flipped,
            surprise_indices=surprise_indices,
            tutorial_intro=introductory_stage,
        )

        if guided and trial_number == TUTORIAL_PATTERN_EXPLANATION_AFTER:
            _tutorial_repeating_pattern(
                win, selected_urn, sequence,
                [entry["correct"] for entry in trials],
            )
        elif guided and trial_number == TUTORIAL_SURPRISE_TRIAL:
            _tutorial_continue(
                win, selected_urn, sequence,
                [entry["correct"] for entry in trials], surprise_indices,
            )
        elif guided and trial_number == PRACTICE_TRIALS:
            _tutorial_pattern_returns(
                win, selected_urn, sequence,
                [entry["correct"] for entry in trials], surprise_indices,
            )

    correct_count = sum(entry["correct"] for entry in trials)
    points = (correct_count * params.REWARD_PER_CORRECT_GUESS
              if selected_urn["urn_type"] == "ambiguous"
              else selected_urn["value"])
    _round_summary(win, block_number, points, correct_count)

    return {
        "practice_block": block_number,
        "guided": guided,
        "surprise_trial_numbers": [i + 1 for i in surprise_indices],
        "condition": condition,
        "k": k,  # never shown when the condition is unknown
        "selected_side": selected_side,
        "selected_urn_type": selected_urn["urn_type"],
        "trial_data": trials,
        "number_correct": correct_count,
        "accuracy": correct_count / PRACTICE_TRIALS,
        "hypothetical_points": points,
        "full_sequence": list(sequence),
    }



def run_training(win=None, conditions=None):
    """Run ROUND_N ten-guess practice rounds.

    Args:
        win: Optional existing PsychoPy window with units='height'. If absent,
             a window is created and closed by this function.
        conditions: Optional explicit sequence of ROUND_N conditions. The first
                    two must be known, unknown. Remaining entries may vary.

    Returns:
        A dictionary of PRACTICE-ONLY results. No experimental data or
        staircase state is changed.
    """
    if not isinstance(ROUND_N, int) or isinstance(ROUND_N, bool) or ROUND_N < 2:
        raise ValueError("ROUND_N must be an integer of at least 2")
    if conditions is None:
        remaining_n = ROUND_N - 2

        # Split remaining rounds equally between known and unknown
        n_known = remaining_n // 2
        n_unknown = remaining_n - n_known

        remaining_conditions = (
            ["known"] * n_known
            + ["unknown"] * n_unknown
        )

        # Randomize their order
        random.shuffle(remaining_conditions)

        # First two rounds are fixed
        conditions = ["known", "unknown"] + remaining_conditions
    else:
        conditions = list(conditions)
        if (len(conditions) != ROUND_N
                or conditions[:2] != ["known", "unknown"]
                or any(c not in ("known", "unknown") for c in conditions)):
            raise ValueError(
                "conditions must contain ROUND_N entries, beginning "
                "with 'known', 'unknown'"
            )

    owns_window = win is None
    if owns_window:
        win = visual.Window(
            size=params.WINDOW_SIZE,
            fullscr=params.FULLSCREEN,
            color=params.BACKGROUND_COLOR,
            units="height",
            monitor=params.MONITOR_NAME,
            gammaErrorPolicy="warn",
        )

    try:
        
        # First teach the rule, the surprise, and the two reward systems.
        # The tutorial is independent from the four scored-as-practice rounds.
        with _practice_header_values():
            tutorial_result = _run_practice_tutorial(win)
            results = []
            for block_number, condition in enumerate(conditions, start=1):
                # Actual practice starts only after the full explanation.
                k = (TUTORIAL_K if block_number == 1 else
                     random.choice(params.AMBIGUOUS_K_OPTIONS))
                results.append(_practice_block(
                    win, block_number, condition, k, guided=False,
                    prepared_assignment=(tutorial_result["first_practice_assignment"]
                                         if block_number == 1 else None),
                    skip_fixation=(block_number == 1),
                ))

        _opening_screen(
            win,
            "Practice completed",
            (
                "The main task will now begin.\n\n"
                "From this point onward, all points you earn "
                "will count toward your final score.\n\n"
                "In the main task, surprise balls will not wear hats."
            ),
            footer="Press SPACE to continue",
        )

        # ------------------------------------------
        # Goal reminder before the main experiment
        # ------------------------------------------

        # Title
        _text(
            win,
            "Reminder!",
            0.37,
            height=0.054,
            bold=True,
            color=INSTRUCTION_NAVY,
        ).draw()

        # Target image
        visual.ImageStim(
            win=win,
            image=str(TARGET_IMAGE_PATH),
            pos=(0, 0.085),
            size=(0.40, 0.40),
            interpolate=True,
        ).draw()

        # Goal explanation
        _text(
            win,
            "Your goal is to get as many points as possible in all rounds.",
            -0.17,
            height=0.042,
            color=INSTRUCTION_BODY,
            wrap_width=1.20,
        ).draw()

        # Continue instruction
        _text(
            win,
            "Press SPACE to begin the main task",
            -0.32,
            height=0.024,
            color=INSTRUCTION_MUTED,
        ).draw()

        win.flip()
        _wait_space(win)

        return {"tutorial": tutorial_result,
                "practice_blocks": results,
                "condition_order": list(conditions)}
    finally:
        _TEXT_CACHE.clear()
        _IMAGE_CACHE.clear()
        if owns_window:
            task._clear_visual_cache(win)
            win.close()


if __name__ == "__main__":
    run_training()
