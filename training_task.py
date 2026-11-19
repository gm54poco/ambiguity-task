"""Practice tutorial and four urn-prediction practice rounds.

Install beside urn_task.py, urn_params.py, and the existing assets folder.
Keep the same PsychoPy units='height' window and the same urn/ball assets.

Use from the experiment:
    import training_task
    training_task.run_training(win=win)

Or preview independently:
    python training_task.py

This file does not alter urn_task.py, staircases, or the main experiment.
The example and four practice rounds award no real points.
"""

import math
import random
from contextlib import contextmanager
from psychopy import core, event, visual
import urn_params as params
import urn_task as task

# Main practice design (kept from the old training file).
ROUND_N = 4
PRACTICE_TRIALS = 10
PRACTICE_FLIPS = 1
PRACTICE_FLIP_LAST_N = 4
PRACTICE_MAX_REWARD = PRACTICE_TRIALS * params.REWARD_PER_CORRECT_GUESS
PRACTICE_DETERMINISTIC_VALUES = [15, 24]

# The interactive illustration is separate from the four practice rounds.
EXAMPLE_TRIALS = 10
EXAMPLE_K = 2
EXAMPLE_CYCLE = ("blue", "magenta")
EXAMPLE_SURPRISE_TRIAL = 7

# Always read explanation font sizes from urn_params.
TITLE_HEIGHT = params.TITLE_HEIGHT
BODY_HEIGHT = params.BODY_HEIGHT
NAV_HEIGHT = 0.021   # Navigation hints are UI, not explanations.

NAVY = "#172b49"
INSTRUCTION_NAVY = NAVY  # shared with the newer tutorial screen
BODY_COLOR = "#334155"
MUTED = "#576a82"
_TEXT_CACHE = {}
_IMAGE_CACHE = {}
_SHAPE_CACHE = {}
# Target illustration
TARGET_IMAGE_PATH = params.BASE_DIR / "assets" / "stars.png"

# Target illustration size and position
TARGET_SIZE = (0.5, 0.5) #before 0.5
TARGET_POS = (0, 0.2) #before 0.65


REWARD_CHOICE_URN_SCALE = 1.3
PRACTICE_INFO_LABEL_X = -0.66
PRACTICE_INFO_BALL_START_X = -0.35
PRACTICE_INFO_ROW_Y = (0.374, 0.326)
PRACTICE_URN_TYPE_Y = 0.422
PRACTICE_INFO_TEXT_HEIGHT = 0.019
PRACTICE_INFO_BALL_RADIUS = 0.007
PRACTICE_INFO_BALL_SPACING = 0.023
PRACTICE_INFO_COLOR = "#253f62"
PRACTICE_INFO_EMPTY_COLOR = "#536e8c"
PRACTICE_BAR_Y = 0.26
PRACTICE_SCORE_LEFT_X = -0.62
PRACTICE_SCORE_RIGHT_X = 0.58
PRACTICE_REMINDER_AFTER = 3.0
PRACTICE_GUESS_Y = -0.040
PRACTICE_FEEDBACK_SECONDS = 0.14
PRACTICE_REVEAL_BALL_RADIUS = 0.12
PRACTICE_START_HEIGHT_FRACTION = 0.35
PRACTICE_RISE_FRAMES = 1
PRACTICE_FLIP_HALF_FRAMES = 1
PRACTICE_HISTORY_FRAMES = 1


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


def _left_text(win, message, x, y, height=0.019, color=NAVY, bold=False):
    """Cache top-left task labels; crucial for fast redraw during ball animation."""
    key = (id(win), 'left', str(message), x, y, height, color, bold)
    stim = _TEXT_CACHE.get(key)
    if stim is None:
        stim = task.draw_text(win, message, (x, y), height=height,
                              color=color, bold=bold, align_text='left')
        _TEXT_CACHE[key] = stim
    return stim


def _right_text(win, message, x, y, height=0.020, color=NAVY, bold=False):
    """Cache right-aligned live accuracy readouts."""
    key = (id(win), 'right', str(message), x, y, height, color, bold)
    stim = _TEXT_CACHE.get(key)
    if stim is None:
        stim = task.draw_text(win, message, (x, y), height=height,
                              color=color, bold=bold, align_text='right')
        _TEXT_CACHE[key] = stim
    return stim


def _exp_title(win, message, y=0.34, x=0, wrap=1.50, height=TITLE_HEIGHT):
    return _text(win, message, y, height=height, color=NAVY,
                 bold=True, wrap_width=wrap, x=x)


def _exp_body(win, message, y, x=0, color=BODY_COLOR, wrap=1.50, bold=False):
    return _text(win, message, y, height=BODY_HEIGHT, color=color,
                 wrap_width=wrap, bold=bold, x=x)


def _footer(win, msg='Press SPACE to continue'):
    _text(win, msg, -0.424, height=NAV_HEIGHT, color=MUTED).draw()


def _navigation(win, can_back=False):
    """SPACE continues; BACKSPACE revisits earlier explanatory pages only."""
    event.clearEvents()
    keys = ['space', 'return', 'num_enter', 'escape']
    if can_back:
        keys.append('backspace')
    pressed = event.waitKeys(keyList=keys)
    if 'escape' in pressed:
        task.quit_experiment(win)
    return -1 if 'backspace' in pressed else 1


def _wait_space(win):
    _navigation(win, can_back=False)


def _ball(win, color, x, y, radius=0.033, tag=None):
    """Use the exact blue/magenta palette from urn_params."""
    key = (id(win), 'ball', tag or color, radius)
    stim = _SHAPE_CACHE.get(key)
    if stim is None:
        stim = visual.Circle(win, pos=(x, y), radius=radius, edges=48,
                             fillColor=params.ball_display_color(color),
                             lineColor=None, lineWidth=0)
        _SHAPE_CACHE[key] = stim
    stim.pos = (x, y)
    stim.fillColor = params.ball_display_color(color)
    stim.lineColor = None
    stim.lineWidth = 0
    stim.draw()


def _example_ball_row(win, colors, y, spacing=0.095, radius=0.033,
                      question=False, tag='row'):
    n = len(colors) + (1 if question else 0)
    start = -(n - 1) * spacing / 2
    for i, color in enumerate(colors):
        _ball(win, color, start + i * spacing, y, radius,
              tag=(tag, i))
    if question:
        x = start + len(colors) * spacing
        key = (id(win), 'question-circle', radius)
        stim = _SHAPE_CACHE.get(key)
        if stim is None:
            stim = visual.Circle(win, pos=(x, y), radius=radius, edges=48,
                                 fillColor=None, lineColor=NAVY, lineWidth=2)
            _SHAPE_CACHE[key] = stim
        stim.pos = (x, y)
        stim.draw()
        _text(win, '?', y, height=BODY_HEIGHT, bold=True, x=x).draw()


def _grouped_pattern_row(win, colors, pattern_length, y,
                         center_x=0.18, spacing=0.083,
                         radius=0.025):
    """Draw six balls with outlines marking each repeating unit."""

    n = len(colors)
    start_x = center_x - (n - 1) * spacing / 2

    # Draw an outline around each repeating group.
    for group_start in range(0, n, pattern_length):

        group_size = min(pattern_length, n - group_start)

        group_center_x = (
            start_x
            + (group_start + (group_size - 1) / 2) * spacing
        )

        box_width = (
            (group_size - 1) * spacing
            + 2 * radius
            + 0.018
        )

        visual.Rect(
            win=win,
            pos=(group_center_x, y),
            width=box_width,
            height=2 * radius + 0.035,
            fillColor=None,
            lineColor="#98A4B5",
            lineWidth=1.0
        ).draw()

    # Draw the six balls inside the outlined groups.
    for i, color in enumerate(colors):
        x = start_x + i * spacing

        _ball(
            win, color, x, y,
            radius=radius,
            tag=("grouped_pattern", pattern_length, i)
        )
def _intro_block_text(win, message, y, x=-0.60, wrap=1.20):
    stim = task.draw_text(
        win,
        message,
        (x, y),
        height=0.04,
        color=BODY_COLOR,
        wrap_width=wrap,
        align_text="left"
    )
    stim.anchorHoriz = "left"
    stim.anchorVert = "top"
    return stim
def _intro_page(win, page):
    """Four short, illustrated explanation screens in the requested order."""
    if page == 0:

        # =========================
        # Title
        # =========================
        _intro_block_text(
            win,
            "Your task in this game is to earn as many points as possible.",
            y=0.365,
            wrap=1.45
        ).draw()

        # =========================
        # Stars image
        # =========================
        target_key = (id(win), "target_image")
        target = _IMAGE_CACHE.get(target_key)

        if target is None:
            target = visual.ImageStim(
                win=win,
                image=str(TARGET_IMAGE_PATH),
                size=TARGET_SIZE,
                interpolate=True
            )
            _IMAGE_CACHE[target_key] = target

        target.pos = TARGET_POS
        target.draw()

        # =========================
        # Paragraphs
        # =========================
        _intro_block_text(
            win,
            "First, you will choose between two urns, each urn contains twenty colored balls.",
            y=0.07
        ).draw()

        _intro_block_text(
            win,
            "After choosing an urn, you will draw balls from it, guessing their color one at a time",
            y=-0.045
        ).draw()

        _intro_block_text(
            win,
            "Depending on the urn you choose you can earn different amount of money. "
            "Some urns guarantee a certain amount, while others depend on on how many colors you guess correctly.",
            y=-0.16
        ).draw()

        # =========================
        # Divider line
        # =========================
        visual.Line(
            win,
            start=(-0.62, -0.37),
            end=(0.62, -0.37),
            lineColor="#A8B3C2",
            lineWidth=1.3
        ).draw()

    elif page == 1:

        _exp_title(
            win,
            "The balls you pick follow a repeating sequence",
            y=0.365
        ).draw()

        _exp_body(
            win,
            "Here are some examples:",
            y=0.262
        ).draw()

        examples = (
            (1, ("blue",) * 6, 0.120),
            (2, ("blue", "magenta") * 3, -0.070),
            (3, ("blue", "magenta", "magenta") * 2, -0.260),
        )

        for length, sequence, y in examples:

            _exp_body(
                win,
                f"Pattern length = {length}",
                y=y - 0.045,
                x=-0.4,
                wrap=0.52
            ).draw()

            # Draw the balls ONLY ONCE, with grouped outlines
            _grouped_pattern_row(
                win,
                colors=sequence,
                pattern_length=length,
                y=y - 0.045,
                center_x=0.18,
                spacing=0.090,
                radius=0.025
            )

    #elif page == 2:
    #    _exp_title(win, 'Your task is to figure out the pattern', y=0.315).draw()
    #    _exp_body(win, 'For example, with a pattern length of 2:', 0.185).draw()
    #    _example_ball_row(win, ('blue', 'magenta', 'blue', 'magenta'),
    #                      -0.015, spacing=0.127, radius=0.047,
    #                      question=True, tag='pattern_question')
    #    _exp_body(win, 'Which color comes next?', -0.205).draw()
    

    elif page == 2:

        # -----------------------------------
        # Title
        # -----------------------------------
        _exp_title(
            win,
            "Surprise ball!",
            y=0.365
        ).draw()

        # -----------------------------------
        # Explanation
        # -----------------------------------
        _exp_body(
            win,
            "Sometimes, a “surprise ball” comes out with the opposite color to the one expected from the sequence."
            "\n\nThis does not change the sequence: the following balls continue in their usual order.",
            y=0.245
        ).draw()

        # -----------------------------------
        # Labels above the balls
        # -----------------------------------
        _exp_body(
            win,
            "Pattern",
            y=0.065,
            x=-0.25,
            wrap=0.40
        ).draw()

        _exp_body(
            win,
            "Surprise ball",
            y=0.065,
            x=0.25,
            wrap=0.40
        ).draw()

        # -----------------------------------
        # Pattern ball: BLUE
        # -----------------------------------
        ball_y = -0.085
        ball_radius = 0.047

        _ball(
            win,
            "blue",
            x=-0.25,
            y=ball_y,
            radius=ball_radius,
            tag="intro_pattern_ball"
        )

        # Arrow
        _text(
            win,
            "→",
            y=ball_y,
            x=0,
            height=BODY_HEIGHT,
            color=NAVY
        ).draw()

        # -----------------------------------
        # Surprise ball: MAGENTA
        # -----------------------------------
        _ball(
            win,
            "magenta",
            x=0.25,
            y=ball_y,
            radius=ball_radius,
            tag="intro_surprise_ball"
        )

        # Magician's hat
        _draw_surprise_hat(
            win,
            pos=(0.25, ball_y),
            radius=ball_radius,
            tag="intro_surprise_hat"
        )

    else:
        raise ValueError(f'Unknown introductory page: {page}')
    _footer(win, 'SPACE: next     BACKSPACE: previous' if page else 'Press SPACE to continue')
    win.flip()



def _run_intro_pages(win):
    page = 0
    while page < 3:
        _intro_page(win, page)
        page = max(0, page + _navigation(win, can_back=(page > 0)))


def _simple_page(
    win, title, body,
    footer='Press SPACE to continue',
    title_y=0.205,
    body_y=-0.015,
    wrap=1.28,
    title_wrap=1.50,
    title_height=TITLE_HEIGHT
):
    _exp_title(win, title, y=title_y, wrap=title_wrap, height=title_height).draw()
    _exp_body(win, body, y=body_y, wrap=wrap).draw()
    _footer(win, footer)
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


def _draw_hint_background(win, selected_urn, sequence, trial_results):
    _practice_draw_prediction(win, selected_urn, sequence, trial_results)
    visual.Rect(win, pos=(0, 0), width=2.2, height=2.2,
                fillColor='#101827', lineColor=None, opacity=0.83).draw()


def _draw_hint_card(win, footer='Press SPACE to begin'):
    visual.Rect(win, pos=(0, 0.005), width=0.99, height=0.60,
                fillColor='#303c50', lineColor='#61738b',
                lineWidth=1.6).draw()
    _text(win, footer, -0.244, height=NAV_HEIGHT,
          color='#bfd0e8', bold=True).draw()


def _context_hint(win, selected_urn, sequence, trial_results,
                  title, explanation, pattern_length=None):
    """Same dark modal style as the newer training version."""
    _draw_hint_background(win, selected_urn, sequence, trial_results)
    _draw_hint_card(win)
    if pattern_length is not None:
        length = int(pattern_length)
        _text(win, f'Pattern length: {length}', 0.190,
              height=TITLE_HEIGHT, color='#f1f5f9', bold=True).draw()
        radius = 0.030
        spacing = 0.072
        start = -(length - 1) * spacing / 2
        for i in range(length):
            visual.Circle(win, pos=(start + i * spacing, 0.065),
                          radius=radius, fillColor='#253f62',
                          lineColor='#bdc8d7', lineWidth=1.6).draw()
        text = f'The pattern repeats every {length} ball' + ('.' if length == 1 else 's.')
    else:
        _text(win, 'Pattern length (less than 4)', 0.190,
              height=TITLE_HEIGHT, color='#f1f5f9', bold=True).draw()
        for x in (-0.080, 0.0, 0.080):
            visual.Circle(win, pos=(x, 0.065), radius=0.028,
                          fillColor=params.BACKGROUND_COLOR, lineColor='#bdc8d7',
                          lineWidth=1.6).draw()
            _text(win, "?", y=0.065, x=x, height=0.030, color="#253f62", bold=True).draw()
        text = 'The pattern has 1, 2, or 3 positions. Its exact length is not revealed.'
    _text(win, text, -0.071, height=BODY_HEIGHT,
          wrap_width=0.87, color='#f1f5f9').draw()
    _text(win, 'This hint will not appear in the main task.', -0.170,
          height=NAV_HEIGHT, wrap_width=0.88, color='#cbd5e1').draw()
    win.flip()
    _wait_space(win)


def _surprise_hint(win, selected_urn, sequence, trial_results,
                   prediction, outcome):
    """Explain a surprise ball using the pattern-length popup style."""

    # Normal game screen, darkened behind the popup
    _draw_hint_background(
        win, selected_urn, sequence, trial_results
    )

    # Same card as the pattern-length explanation
    _draw_hint_card(
        win, footer="Press SPACE to reveal"
    )

    # Title
    _text(
        win,
        "Surprise ball!",
        0.190,
        height=TITLE_HEIGHT,
        color="#f1f5f9",
        bold=True
    ).draw()

    # Original pattern ball
    _ball(
        win, prediction,
        x=-0.19, y=0.048,
        radius=0.035,
        tag="surprise_popup_pattern"
    )

    # Arrow
    _text(
        win, "→", 0.048,
        height=BODY_HEIGHT,
        color="#f1f5f9"
    ).draw()

    # Surprise ball
    _ball(
        win, outcome,
        x=0.19, y=0.048,
        radius=0.035,
        tag="surprise_popup_outcome"
    )

    # Magician's hat
    _draw_surprise_hat(
        win,
        pos=(0.19, 0.048),
        radius=0.035,
        tag="surprise_popup_hat"
    )

    # Explanation
    _text(
        win,
        "A surprise ball has the opposite color\n"
        "from the pattern.",
        -0.095,
        height=BODY_HEIGHT,
        wrap_width=0.88,
        color="#f1f5f9"
    ).draw()

    # Small note
    _text(
        win,
        "The pattern continues normally after the surprise ball.",
        -0.186,
        height=NAV_HEIGHT,
        color="#cbd5e1"
    ).draw()

    win.flip()
    _wait_space(win)

def _hint_for_trial(selected_urn, condition, trial_number):
    if trial_number != 1:
        return None
    return ('Pattern length', '',
            int(selected_urn['ambiguous_k']) if condition == 'known' else None)


def _surprise_explanation(win, urn, sequence, results, prediction, outcome):
    """Teach a changed-color ball, with the same top hat used in draw history."""
    _exp_title(win, 'Surprise ball!', 0.366).draw()
    _exp_body(win, 'Sometimes a ball has the opposite color', 0.259).draw()
    _exp_body(win, 'from the pattern.', 0.205).draw()
    _exp_body(win, 'Pattern', 0.078, x=-0.250, wrap=0.40).draw()
    _exp_body(win, 'Surprise', 0.078, x=0.250, wrap=0.40).draw()
    _ball(win, prediction, -0.250, -0.040, radius=0.046, tag='surprise_before')
    _text(win, '→', -0.040, height=TITLE_HEIGHT, x=0).draw()
    _ball(win, outcome, 0.250, -0.040, radius=0.046, tag='surprise_after')
    _draw_surprise_hat(win, (0.250, -0.040), 0.046, tag='surprise_explanation')
    _exp_body(win, 'The underlying pattern stays the same.', -0.222).draw()
    _footer(win, 'Press SPACE to reveal the surprise ball')
    win.flip()
    _wait_space(win)


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
    """Cache existing urn textures, never recolor urns."""
    if scale <= 0.001:
        return
    image = str(urn['opened_image'] if opened else urn['closed_image'])
    size = (params.URN_IMAGE_SIZE[0] * scale,
            params.URN_IMAGE_SIZE[1] * scale)
    key = (id(win), 'reward_urn', image, size)
    stim = _IMAGE_CACHE.get(key)
    if stim is None:
        stim = visual.ImageStim(win=win, image=image, size=size,
                                interpolate=True)
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


def _match_urn_rules(assignment):
    """Both rewards have identical k and underlying cycle; only payoff differs."""
    ambiguous = next(u for u in assignment.values() if u['urn_type'] == 'ambiguous')
    fixed = next(u for u in assignment.values() if u['urn_type'] == 'deterministic')
    fixed['ambiguous_k'] = ambiguous['ambiguous_k']
    fixed['participant_knows_k'] = ambiguous['participant_knows_k']
    fixed['cycle'] = list(ambiguous['cycle'])
    return assignment


def _urn_comparison(win, assignment):
    """Step 6: same two-urn names, labels, reward text and colors as new task."""
    _exp_title(win, 'Choose how to earn points', y=0.412).draw()
    _exp_body(win, 'Both urns use the same game. Only the rewards differ.',
              y=0.330, wrap=1.50).draw()
    for side in ('left', 'right'):
        urn = assignment[side]
        x = (params.URN_LEFT_POS[0] if side == 'left'
             else params.URN_RIGHT_POS[0])
        _draw_reward_urn(win, urn, x, REWARD_CHOICE_URN_SCALE)
        task.draw_selection_condition_text(win, urn, x)
    _text(win, 'Press SPACE to start the practice rounds', -0.437,
          height=NAV_HEIGHT, color=MUTED).draw()
    win.flip()
    _wait_space(win)


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
        _exp_title(win, tutorial_heading or 'Try it out', y=0.430).draw()
    elif not hide_urn_type:
        _left_text(win, 'Urn type', PRACTICE_INFO_LABEL_X,
                   PRACTICE_URN_TYPE_Y, color=PRACTICE_INFO_COLOR).draw()
        _left_text(win, reward_type, PRACTICE_INFO_BALL_START_X - 0.01,
                   PRACTICE_URN_TYPE_Y, color=PRACTICE_INFO_COLOR,
                   bold=True).draw()

    pattern_label = (
        f"Pattern length ({visible_length})" if known else "Pattern length (less than 4)"
    )
    # All conditions show the same surprise-ball label as the newer version.
    info_rows = [
        (pattern_label, visible_length),
        (f"Surprise balls ({PRACTICE_FLIPS})", PRACTICE_FLIPS),
    ]
    for row_index, (label, filled) in enumerate(info_rows):
        y = PRACTICE_INFO_ROW_Y[row_index]
        _left_text(win, label, PRACTICE_INFO_LABEL_X, y,
                   height=PRACTICE_INFO_TEXT_HEIGHT,
                   color=PRACTICE_INFO_COLOR).draw()
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
            
            # Question marks only for unknown pattern length
            if row_index == 0 and not known:
                _text(
                    win,
                    "?",
                    y=y,
                    x=x,
                    height=0.012,
                    color=PRACTICE_INFO_COLOR,
                    bold=True
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
    _left_text(win, f'{points:g} pts', bar_left + 0.018, bar_y,
               height=0.021, bold=True,
               color='#ffffff' if fill_width >= 0.10 else PRACTICE_INFO_COLOR).draw()
    _right_text(win, f'{accuracy:.0f}% correct', PRACTICE_SCORE_RIGHT_X, bar_y,
                height=0.020, color=PRACTICE_INFO_COLOR).draw()

    _practice_draw_history(win, sequence, surprise_indices=surprise_indices)
    task.draw_selected_open_urn(win, selected_urn)

    if tutorial_prompt:
        # Same caption position for the pattern, magician and continuation.
        size = BODY_HEIGHT if tutorial_intro else 0.024
        _text(win, tutorial_prompt, -0.115,
              height=size,
              bold=True, color=INSTRUCTION_NAVY,
              wrap_width=1.40).draw()
    if tutorial_intro:
        _text(win, 'Press B for blue or M for magenta', -0.202,
              height=NAV_HEIGHT, color='#66758b').draw()

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

    if (reminder or tutorial_first_guess) and not tutorial_intro:
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
        fillColor=hidden_grey, lineColor=None, lineWidth=2,
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


def _run_guessing_example(win):
    """Step 5: actual B/M guessing, one surprise on guess 7, no real points."""
    _simple_page(win, 'Try it out',
                 'Guess the next ball. Press B for blue or M for magenta.')
    urn = task.create_ambiguous_urn(
        params.PRETTY_URN_NAMES[0], 'Example urn', 'known', EXAMPLE_K,
        cycle=list(EXAMPLE_CYCLE))
    urn['_tutorial_step'] = 1
    sequence = list(task.generate_latent_sequence(
        list(EXAMPLE_CYCLE), params.N_INITIAL_DRAWS))
    trials = []
    surprise_indices = []
    for trial_number in range(1, EXAMPLE_TRIALS + 1):
        previous = [entry['correct'] for entry in trials]
        prompt = ('Make your guess' if trial_number == 1 else
                  'Keep guessing')
        guess, rt = _practice_collect_prediction(
            win, urn, sequence, previous,
            tutorial_intro=True, tutorial_prompt=prompt,
            surprise_indices=surprise_indices,
            tutorial_first_guess=(trial_number == 1))
        pred_index = params.N_INITIAL_DRAWS + trial_number - 1
        surprise = (trial_number == EXAMPLE_SURPRISE_TRIAL)
        outcome, predicted = task.generate_next_outcome(
            selected_urn=urn, prediction_index=pred_index,
            is_noise_trial=surprise)
        if surprise:
            _surprise_explanation(win, urn, sequence, previous,
                                  predicted, outcome)
            surprise_indices.append(trial_number - 1)
        sequence.append(outcome)
        correct = (guess == outcome)
        trials.append({
            'trial_number': trial_number, 'guess': guess,
            'outcome': outcome, 'correct': correct,
            'response_time': rt, 'is_noise_trial': surprise,
            'pattern_prediction': predicted,
            'prediction_index': pred_index,
        })
        _practice_show_outcome(
            win, urn, sequence, [t['correct'] for t in trials],
            guess, outcome, correct,
            final_trial=(trial_number == EXAMPLE_TRIALS),
            trial_number=trial_number,
            is_surprise=surprise,
            surprise_indices=surprise_indices,
            tutorial_intro=True)
    return {
        'k': EXAMPLE_K, 'cycle': list(EXAMPLE_CYCLE),
        'trial_data': trials, 'full_sequence': list(sequence),
        'surprise_trial': EXAMPLE_SURPRISE_TRIAL,
    }


def _practice_block(win, block_number, condition, k,
                    prepared_assignment=None, skip_fixation=False):
    """Four ordinary rounds: same choices, guessing, scoring, and RTs as before."""
    assignment = prepared_assignment
    if assignment is None:
        assignment = task.assign_urns_to_sides(
            deterministic_value=random.choice(PRACTICE_DETERMINISTIC_VALUES),
            ambiguous_condition=condition, k=k)
    _match_urn_rules(assignment)
    if not skip_fixation:
        _fixation(win)
    side = _standard_urn_selection(win, assignment)
    selected_urn = assignment[side]
    task.animate_selected_urn_transition(win, selected_urn, side, assignment)
    sequence = list(task.generate_latent_sequence(
        selected_urn['cycle'], params.N_INITIAL_DRAWS))
    flips = [False] * PRACTICE_TRIALS
    possible_flips = range(max(0, PRACTICE_TRIALS-PRACTICE_FLIP_LAST_N),
                           PRACTICE_TRIALS)
    for i in random.sample(list(possible_flips), PRACTICE_FLIPS):
        flips[i] = True
    trials = []
    surprise_indices = []
    for trial_number, surprise in enumerate(flips, start=1):
        previous = [t['correct'] for t in trials]
        #if trial_number == 1:
            #hint = _hint_for_trial(selected_urn, condition, trial_number)
            #if hint:
            #    _context_hint(win, selected_urn, sequence, previous, *hint)
        guess, rt = _practice_collect_prediction(
            win, selected_urn, sequence, previous,
            surprise_indices=surprise_indices)
        pred_index = params.N_INITIAL_DRAWS + trial_number - 1
        outcome, predicted = task.generate_next_outcome(
            selected_urn=selected_urn,
            prediction_index=pred_index,
            is_noise_trial=surprise)
        if surprise:
            #if block_number == 1:
                #_surprise_hint(
                #    win,
                #    selected_urn,
                #    sequence,
                #    previous,
                #    predicted,
                #    outcome
                #)
            surprise_indices.append(trial_number - 1)
        sequence.append(outcome)
        correct = guess == outcome
        trials.append({
            'trial_number': trial_number,
            'guess': guess, 'outcome': outcome,
            'correct': correct, 'response_time': rt,
            'is_noise_trial': surprise,
            'pattern_prediction': predicted,
            'prediction_index': pred_index,
        })
        _practice_show_outcome(
            win, selected_urn, sequence,
            [entry['correct'] for entry in trials],
            guess, outcome, correct,
            final_trial=(trial_number == PRACTICE_TRIALS),
            trial_number=trial_number,
            is_surprise=surprise,
            surprise_indices=surprise_indices)
    correct_count = sum(t['correct'] for t in trials)
    points = (correct_count * params.REWARD_PER_CORRECT_GUESS
              if selected_urn['urn_type'] == 'ambiguous'
              else selected_urn['value'])
    _round_summary(win, block_number, points, correct_count)
    return {
        'practice_block': block_number,
        'condition': condition, 'k': k,
        'selected_side': side,
        'selected_urn_type': selected_urn['urn_type'],
        'surprise_trial_numbers': [i + 1 for i in surprise_indices],
        'trial_data': trials,
        'number_correct': correct_count,
        'accuracy': correct_count / PRACTICE_TRIALS,
        'hypothetical_points': points,
        'full_sequence': list(sequence),
    }


def run_training(win=None, conditions=None):
    """Run the six-step tutorial, followed by ROUND_N ordinary practice rounds.

    An optional existing PsychoPy window must use units='height'.
    Conditions start known, unknown; remaining trials are balanced and shuffled.
    No experimental parameters or staircase state are permanently changed.
    """
    if not isinstance(ROUND_N, int) or isinstance(ROUND_N, bool) or ROUND_N < 2:
        raise ValueError('ROUND_N must be at least 2')
    if conditions is None:
        remaining = ROUND_N - 2
        remaining_conditions = (['known'] * (remaining // 2) +
                                ['unknown'] * (remaining - remaining // 2))
        random.shuffle(remaining_conditions)
        conditions = ['known', 'unknown'] + remaining_conditions
    else:
        conditions = list(conditions)
        if (len(conditions) != ROUND_N or
                conditions[:2] != ['known', 'unknown'] or
                any(c not in ('known', 'unknown') for c in conditions)):
            raise ValueError('conditions must have ROUND_N values, starting known, unknown')

    owns_window = win is None
    if owns_window:
        win = visual.Window(size=params.WINDOW_SIZE, fullscr=params.FULLSCREEN,
                            color=params.BACKGROUND_COLOR, units='height',
                            monitor=params.MONITOR_NAME,
                            gammaErrorPolicy='warn')
    try:
        
        with _practice_header_values():

            # First four explanation pages
            _run_intro_pages(win)

            # Start the actual practice
            _simple_page(
                win,
                "\n\nYou will now practice the task\n\n"
                "During practice, you will see reminders of the rules.\n\n" 
                "Surprise balls will be marked with a hat.\n\n"
                "In the main task, these reminders and hats will no longer appear.\n\n",
                "\n\n\n\nPoints earned during practice do not count towards your final score.\n\n"
                "You will be told when practice ends and points start counting.",
                footer="Press SPACE to start practicing",
                title_y=0.09, #before 145
                body_y=-0.2, #before 075
                title_wrap=1.1,
                title_height=0.045,
            )

            results = []

            k_options = tuple(
                getattr(params, 'AMBIGUOUS_K_OPTIONS', (1, 2, 3))
            )

            for block_number, condition in enumerate(
                conditions, start=1
            ):
                k = random.choice(k_options)

                results.append(
                    _practice_block(
                        win,
                        block_number,
                        condition,
                        k,
                        skip_fixation=(block_number == 1)
                    )
                )


        _simple_page(win, 'Practice completed',
                     'The main task starts now. From here on, points count.\n\n'
                     'Surprise balls will not be marked with hats.',
                     footer='Press SPACE to begin the main task')
        return {'tutorial': None, 'practice_blocks': results,
                'condition_order': list(conditions)}
    finally:
        _TEXT_CACHE.clear()
        _IMAGE_CACHE.clear()
        _SHAPE_CACHE.clear()
        if owns_window:
            if hasattr(task, '_clear_visual_cache'):
                task._clear_visual_cache(win)
            win.close()


if __name__ == '__main__':
    run_training()


