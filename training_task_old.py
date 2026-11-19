"""Guided practice for the urn prediction experiment.

Place this file next to urn_task.py, urn_params.py and the existing assets folder.
It is designed for the optimized urn_task.py version (October 2026).

Run on its own:
    python training_task.py

Or integrate before the real experiment:
    import training_task
    training_task.run_training()

The practice does NOT call the staircase, does NOT run the post-block
questionnaire, and does NOT award real points. It temporarily adapts the
header's maximum reward and flipped-ball count for 10-trial practice blocks;
all original parameters are restored, including on error or early exit.
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
PRACTICE_FLIP_LAST_N = 4
PRACTICE_MAX_REWARD = PRACTICE_TRIALS * params.REWARD_PER_CORRECT_GUESS
PRACTICE_DETERMINISTIC_VALUES = [15, 24]
# Reuse PsychoPy stimuli instead of rebuilding text for every animation frame.
_TEXT_CACHE = {}
_IMAGE_CACHE = {}



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
    keys = event.waitKeys(keyList=["space", "escape"])
    if "escape" in keys:
        task.quit_experiment(win)


def _opening_screen(win, heading, subtitle=None, footer="Press SPACE to continue"):
    """Minimal full-screen opening; nothing else appears until SPACE."""
    _text(win, heading, 0.2, height=0.053, bold=True).draw()
    if subtitle:
        _text(win, subtitle, -0.025, height=0.029,
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
    path = params.PRETTY_URNS_DIR / (
        f"{urn_name}_{'opened' if opened else 'closed'}.png"
    )

    visual.ImageStim(
        win=win,
        image=str(path),
        pos=pos,
        size=size,
        interpolate=True
    ).draw()


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
        group_centers = (-0.17, 0.17)

        for group_cx in group_centers:
            for idx in range(pattern_length):
                px = group_cx - group_width / 2 + idx * spacing
                visual.Circle(
                    win=win,
                    pos=(px, 0.045),
                    radius=radius,
                    fillColor="#253f62",
                    lineColor="#bdc8d7",
                    lineWidth=1.6,
                ).draw()

        _text(win, "→", 0.045, height=0.046,
            x=0, color="#f1f5f9").draw()

        _text(
            win,
            f"The sequence follows a repeating pattern of {pattern_length}.\n\n"
            "(This explanation won't appear in the real task.)",
            -0.055,
            height=0.026,
            wrap_width=0.70,
            color="#f1f5f9"
        ).draw()
    else:
    # Heading
        _text(
            win, "Pattern length < 4",
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


def _flipped_outcome_hint(win, selected_urn, sequence, trial_results):
    """Explain a flipped outcome during guided practice."""

    _draw_hint_background(win, selected_urn, sequence, trial_results)
    _draw_hint_card(win, "Flipped ball", "Press SPACE to reveal")

    # Heading
    _text(
        win, f"Flipped balls: {PRACTICE_FLIPS}",
        0.155, height=0.042,
        bold=True, color="#f1f5f9"
    ).draw()

    # Blue ball
    visual.Circle(
        win=win, pos=(-0.11, 0.045), radius=0.032,
        fillColor=params.BALL_BLUE, lineColor=params.BALL_BLUE,
        lineWidth=1.5,
    ).draw()

    # Arrow
    _text(
        win, "→", 0.045, height=0.046,
        x=0, color="#f1f5f9"
    ).draw()

    # Magenta ball
    visual.Circle(
        win=win, pos=(0.11, 0.045), radius=0.032,
        fillColor=params.BALL_MAGENTA, lineColor=params.BALL_MAGENTA,
        lineWidth=1.5,
    ).draw()

    # Explanation
    _text(
        win,
        "This ball has the opposite color from the pattern.",
        -0.055, height=0.026,
        wrap_width=0.70,
        color="#f1f5f9"
    ).draw()

    _text(
        win,
        "\nIn the real task, you will not be told which balls are flipped.",
        -0.105, height=0.024,
        wrap_width=0.72,
        color="#cbd5e1"
    ).draw()

    win.flip()
    _wait_space(win)



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
def _reward_card(win, urn, x, y=-0.280, width=0.49):
    """Compact reward information card for an urn."""
    ambiguous = urn["urn_type"] == "ambiguous"

    # Same colors for both urns
    fill = "#EDF1F5"      # Light blue-gray background
    border = "#C4CDD8"    # Neutral border
    accent = "#172B49"    # Dark navy text

    visual.Rect(
        win,
        pos=(x, y),
        width=width,
        height=0.190,
        fillColor=fill,
        lineColor=border,
        lineWidth=1.2,
    ).draw()

    # ------------------------------
    # Heading
    # ------------------------------
    heading = "MAXIMUM REWARD" if ambiguous else "GUARANTEED REWARD"
    _text(
        win, heading, y + 0.067, 0.018,
        color="#475569", bold=True,
        x=x, wrap_width=width - 0.03
    ).draw()

    # ------------------------------
    # Main amount
    # ------------------------------
    if ambiguous:
        amount = f"+{params.REWARD_PER_CORRECT_GUESS:g} pts (max {PRACTICE_MAX_REWARD:g})"
        subtitle = "earn points per correct guess"

        _text(
            win, amount, y + 0.020, 0.042,
            color=accent, bold=True,
            x=x, wrap_width=width - 0.03
        ).draw()

        _text(
            win, subtitle, y - 0.02, 0.020,
            color=accent,
            x=x, wrap_width=width - 0.05
        ).draw()
    else:
        amount = f"{urn['value']:g} pts"

        _text(
            win, amount, y + 0.020, 0.042,
            color=accent, bold=True,
            x=x, wrap_width=width - 0.03
        ).draw()

        _text(
            win, "Fixed reward", y - 0.02, 0.020,
            color=accent,
            x=x, wrap_width=width - 0.05
        ).draw()

    # ------------------------------
    # Pattern length + flipped balls
    # ------------------------------
    if urn["participant_knows_k"]:
        visible_length = int(urn["ambiguous_k"])
    else:
        visible_length = 0   # unknown k -> all hollow

    _draw_small_indicator_row(
        win,
        "Pattern length",
        visible_length,
        x=x,
        y=y - 0.060,
        text_color="#334155",
        active_color="#334155",
        empty_color="#94a3b8",
    )



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


def _draw_reward_urn(win, urn, x, scale=1.0, y_offset=0):
    """Draw cached closed-urn textures (same display dimensions on both sides)."""
    if scale <= 0.001:
        return
    image = str(urn["closed_image"])
    width, height = params.URN_IMAGE_SIZE
    size = (width * scale, height * scale)
    key = (id(win), image, size)
    stim = _IMAGE_CACHE.get(key)
    if stim is None:
        stim = visual.ImageStim(win=win, image=image, size=size)
        _IMAGE_CACHE[key] = stim
    stim.pos = (x, params.URN_LEFT_POS[1] + y_offset)
    stim.draw()


def _render_reward_stage(win, assignment, choosing=True):
    """Draw both urns once, without obsolete tutorial animations."""
    _reward_title(win, choosing=True)
    for side in ("left", "right"):
        urn = assignment[side]
        x = params.URN_LEFT_POS[0] if side == "left" else params.URN_RIGHT_POS[0]
        _draw_reward_urn(win, urn, x, REWARD_CHOICE_URN_SCALE)
        _reward_card(win, urn, x, width=0.53)
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
PRACTICE_INFO_BALL_START_X = -0.46
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
                              points_override=None):
    """Practice prediction screen, using cached PsychoPy stimuli."""
    known = bool(selected_urn["participant_knows_k"])
    visible_length = int(selected_urn["ambiguous_k"]) if known else 0
    reward_type = (
        "Fixed reward"
        if selected_urn["urn_type"] == "deterministic"
        else "Performance-dependent reward"
    )

    visual.TextStim(
        win,
        text="Urn type",
        pos=(PRACTICE_INFO_LABEL_X, PRACTICE_URN_TYPE_Y),
        height=0.019,
        color=PRACTICE_INFO_COLOR,
        alignText="left",
        anchorHoriz="left",
    ).draw()

    visual.TextStim(
        win,
        text=reward_type,
        pos=(PRACTICE_INFO_BALL_START_X-0.01, PRACTICE_URN_TYPE_Y),
        height=0.019,
        bold=True,
        color=PRACTICE_INFO_COLOR,
        alignText="left",
        anchorHoriz="left",
    ).draw()
    # Reuse text and indicator circles on every animation frame.
        
    pattern_label = (
        f"Pattern length ({visible_length})"
        if known else "Pattern length (?)"
    )

    for row_index, (label, filled) in enumerate((
        (pattern_label, visible_length),
        (f"Flipped balls ({PRACTICE_FLIPS})", PRACTICE_FLIPS),
    )):

        y = PRACTICE_INFO_ROW_Y[row_index]
        task.draw_text(
            win, label, (PRACTICE_INFO_LABEL_X, y),
            height=PRACTICE_INFO_TEXT_HEIGHT,
            color=PRACTICE_INFO_COLOR, align_text="left",
        ).draw()
        total_balls = 3 if row_index == 0 else PRACTICE_FLIPS
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

    fixed = selected_urn["urn_type"] == "deterministic"
    correct = sum(bool(v) for v in trial_results)
    completed = len(trial_results)
    accuracy = 100 * correct / completed if completed else 0
    points = (selected_urn["value"] if fixed
              else correct * params.REWARD_PER_CORRECT_GUESS)
    if points_override is not None:
        points = points_override

    progress = min(1.0, correct / PRACTICE_TRIALS)
    bar_left = PRACTICE_SCORE_LEFT_X
    bar_right = PRACTICE_SCORE_RIGHT_X - 0.13
    bar_width = bar_right - bar_left
    bar_y = PRACTICE_BAR_Y
    bar_height = 0.035

    # Reuse the exact cached rounded-bar drawing function from urn_task.py.
    task._draw_pill(win, bar_left, bar_right, bar_y, bar_height,
                    "#d6dce5", "practice_track")
    fill_width = bar_width * progress
    if fill_width >= bar_height:
        task._draw_pill(win, bar_left, bar_left + fill_width, bar_y,
                        bar_height, "#789bc0", "practice_fill")

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

    task.draw_sequence_feedback(win, sequence)
    task.draw_selected_open_urn(win, selected_urn)

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

    if reminder:
        _text(win, "Press B for blue or M for magenta", -0.145,
              0.023, color="#66758b").draw()


def _practice_collect_prediction(win, selected_urn, sequence, trial_results):
    """Record reaction time from initial display; show hint only after 3 s."""
    event.clearEvents()
    clock = core.Clock()
    reminder_shown = False
    win.callOnFlip(clock.reset)
    # Time responses from when the prediction screen appears.
    _practice_draw_prediction(win, selected_urn, sequence, trial_results)
    win.flip()
    while True:
        keys = event.getKeys(keyList=list(params.GUESS_KEYS.keys()) + ["escape"],
                             timeStamped=clock)
        if keys:
            key, rt = keys[0]
            if key == "escape":
                task.quit_experiment(win)
            return params.GUESS_KEYS[key], float(rt)
        if not reminder_shown and clock.getTime() >= PRACTICE_REMINDER_AFTER:
            reminder_shown = True
            _practice_draw_prediction(win, selected_urn, sequence,
                                      trial_results, reminder=True)
            win.flip()
        core.wait(0.005)


# Animation settings (PsychoPy height units). Change these values to tune it.
PRACTICE_REVEAL_BALL_RADIUS = 0.12  # Larger than draw-history balls.
PRACTICE_START_HEIGHT_FRACTION = 0.35  # Higher value = starts higher in urn.
PRACTICE_RISE_FRAMES = 1
PRACTICE_FLIP_HALF_FRAMES = 1  # Always completes both halves of the flip.
PRACTICE_HISTORY_FRAMES = 1


def _practice_animate_ball_reveal(win, selected_urn, sequence,
                                  previous_results, guess, outcome):
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

    def frame(pos, color, radius, width_scale=1.0):
        # Previous observations stay visible until the new ball reaches history.
        _practice_draw_prediction(win, selected_urn,
                                  previous_sequence, previous_results)
        moving_ball.pos = pos
        moving_ball.fillColor = params.ball_display_color(color)
        moving_ball.size = (
            2 * radius * max(0.01, width_scale),
            2 * radius,
        )
        moving_ball.draw()
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
        frame(reveal_pos, outcome, reveal_radius, width)

    # Move to history while reducing the radius to the precise history radius.
    for i in range(PRACTICE_HISTORY_FRAMES + 1):
        t = ease(i / PRACTICE_HISTORY_FRAMES)
        radius = reveal_radius + (history_radius - reveal_radius) * t
        frame(interpolate(reveal_pos, history_pos, t), outcome, radius)


def _practice_show_outcome(win, selected_urn, sequence, trial_results,
                           guess, outcome, correct, final_trial, trial_number):
    """Brief guessed-color preview, then original urn-to-history animation."""
    previous = trial_results[:-1]

    # Hidden ball rises, flips to the actual outcome, then enters history.
    _practice_animate_ball_reveal(
        win, selected_urn, sequence, previous, guess, outcome
    )

    _practice_draw_prediction(win, selected_urn, sequence, trial_results)
    if final_trial:
        _text(win, "Press SPACE to continue", -0.18, 0.024,
              color="#000000").draw()
    win.flip()
    if final_trial:
        _wait_space(win)
    else:
        core.wait(PRACTICE_FEEDBACK_SECONDS)


def _practice_block(win, block_number, condition, k):
    """Ten prediction trials with the existing task visuals and RTs."""
    deterministic_reward = random.choice(PRACTICE_DETERMINISTIC_VALUES)

    assignment = task.assign_urns_to_sides(
        deterministic_value=deterministic_reward,
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

    # Copy the task parameters, but preserve reward type and value.
    deterministic_urn["ambiguous_k"] = ambiguous_urn["ambiguous_k"]
    deterministic_urn["participant_knows_k"] = ambiguous_urn["participant_knows_k"]
    deterministic_urn["cycle"] = list(ambiguous_urn["cycle"])
    # Fixation before EVERY urn choice, including the second practice round.
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
    flip_positions = random.sample(
        range(PRACTICE_TRIALS - PRACTICE_FLIP_LAST_N, PRACTICE_TRIALS),
        PRACTICE_FLIPS
    )

    for position in flip_positions:
        outcomes[position] = True

    trials = []

    
    for trial_number, is_flipped in enumerate(outcomes, start=1):
        previous_results = [entry["correct"] for entry in trials]

        # Show pattern-length information at the start of every practice round.
        if trial_number == 1:
            hint = _hint_for_trial(selected_urn, condition, trial_number)

            if hint:
                _context_hint(
                    win, selected_urn, sequence,
                    previous_results, *hint
                )


        guess, reaction_time = _practice_collect_prediction(
            win, selected_urn, sequence, previous_results,
        )
        prediction_index = params.N_INITIAL_DRAWS + trial_number - 1
        outcome, pattern_prediction = task.generate_next_outcome(
            selected_urn=selected_urn,
            prediction_index=prediction_index,
            is_noise_trial=is_flipped,
        )
        # The demonstration occurs after the response, immediately before
        # revealing the actual flipped outcome. Only the first round is guided.
        if is_flipped:
            _flipped_outcome_hint(
                win, selected_urn, sequence, previous_results,
            )
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
            final_trial=(trial_number == PRACTICE_TRIALS),
            trial_number=trial_number,
        )

    correct_count = sum(entry["correct"] for entry in trials)
    points = (correct_count * params.REWARD_PER_CORRECT_GUESS
              if selected_urn["urn_type"] == "ambiguous"
              else selected_urn["value"])
    _round_summary(win, block_number, points, correct_count)

    return {
        "practice_block": block_number,
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
        )

    try:
        
        _opening_screen(
            win,
            "Practice",
            (
                f"You will now complete {ROUND_N} practice rounds "
                "to become familiar with the task.\n\n"
                "Practice rounds do not count toward your final score."
            ),
        )

        _practice_step_screen(win, 1)

        _practice_step_screen(win, 2)

        with _practice_header_values():
            results = []
            for block_number, condition in enumerate(conditions, start=1):
                # Use plausible k values without revealing the unknown one.
                k =random.choice((2, 3))
                results.append(_practice_block(
                    win, block_number, condition, k
                ))

        _opening_screen(
            win,
            "Practice completed",
            (
                "The main task will now begin.\n\n"
                "From this point onward, all points you earn "
                "will count toward your final score.\n\n"
            ),
            footer="Press SPACE to continue",
        )
        return {"practice_blocks": results,
                "condition_order": list(conditions),}
    finally:
        _TEXT_CACHE.clear()
        _IMAGE_CACHE.clear()
        if owns_window:
            task._clear_visual_cache(win)
            win.close()


if __name__ == "__main__":
    run_training()
