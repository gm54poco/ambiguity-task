"""Main urn task: practice-style graphics, one shared fixed-stage staircase.

Works with training_task.py's public calls: assign_urns_to_sides,
animate_selected_urn_transition, draw_sequence_feedback, etc.
Post-block questions are supplied by the existing questions_task.py.
"""

import math
import random
from psychopy import visual, event, core

import urn_params as params
from questions_task import run_post_block_questions

_VISUAL_CACHE = {}


def _cached(win, key, factory):
    full_key = (id(win), key)
    if full_key not in _VISUAL_CACHE:
        _VISUAL_CACHE[full_key] = factory()
    return _VISUAL_CACHE[full_key]


def _clear_visual_cache(win):
    ident = id(win)
    for key in [k for k in _VISUAL_CACHE if k[0] == ident]:
        del _VISUAL_CACHE[key]


def draw_text(win, text, pos, height=0.05, wrap_width=1.4,
              bold=False, color=None, align_text="center"):
    text = str(text)
    key = ("text", text, tuple(pos), height, wrap_width, bold, color, align_text)
    return _cached(win, key, lambda: visual.TextStim(
        win=win, text=text, pos=pos, height=height, wrapWidth=wrap_width,
        bold=bold, color=params.TEXT_COLOR if color is None else color,
        alignText=align_text, anchorHoriz=align_text, font="Arial"))


def _image(win, image_path, pos, size):
    path = str(image_path)
    size = tuple(size)
    stim = _cached(win, ("image", path, size),
                   lambda: visual.ImageStim(win=win, image=path, size=size))
    stim.pos = pos
    return stim


def get_urn_image_path(urn_name, state):
    if state not in ("closed", "opened"):
        raise ValueError("state must be 'closed' or 'opened'")
    return str(params.PRETTY_URNS_DIR / f"{urn_name}_{state}.png")


def create_image_urn(win, pos, label_text, image_path, size=None,
                     show_label=True, bottom_text=None):
    size = params.URN_IMAGE_SIZE if size is None else size
    parts = [_image(win, image_path, pos, size)]
    if show_label:
        parts.append(draw_text(win, label_text,
                               (pos[0], pos[1] + size[1] / 2 + 0.07),
                               height=params.LABEL_HEIGHT, bold=True))
    if bottom_text is not None:
        parts.append(draw_text(win, bottom_text,
                               (pos[0], pos[1] - size[1] / 2 - 0.06),
                               height=0.028, bold=True))
    return parts


def draw_all(parts):
    for stimulus in parts:
        stimulus.draw()


def draw_selected_open_urn(win, selected_urn):
    _image(win, selected_urn["opened_image"],
           params.SELECTED_URN_POS, params.SELECTED_URN_SIZE).draw()


def quit_experiment(win):
    win.close()
    core.quit()


# -----------------------------------------------------------------------------
# Latent pattern, urn assignments, and outcome generation.
# -----------------------------------------------------------------------------

def has_smaller_period(sequence):
    n = len(sequence)
    for period in range(1, n):
        if n % period == 0 and all(sequence[i] == sequence[i % period]
                                    for i in range(n)):
            return True
    return False


def generate_k_cycle(k):
    if k not in params.AMBIGUOUS_K_OPTIONS:
        raise ValueError(f"Unsupported k={k}")
    while True:
        cycle = [random.choice(params.BALL_COLORS) for _ in range(k)]
        if not has_smaller_period(cycle):
            return cycle


def serialise_cycle(cycle):
    return "-".join(cycle) if cycle is not None else ""


def cycles_match(true_cycle, response_cycle):
    """Cyclic rotations are equivalent reconstructions."""
    if not true_cycle or not response_cycle or len(true_cycle) != len(response_cycle):
        return False
    doubled = list(true_cycle) + list(true_cycle)
    return any(doubled[i:i + len(true_cycle)] == list(response_cycle)
               for i in range(len(true_cycle)))


def generate_latent_sequence(cycle, n_draws):
    return [cycle[i % len(cycle)] for i in range(n_draws)]


def _make_urn(urn_name, label, kind, condition, k, cycle, value=None):
    return {
        "urn_type": kind,
        "urn_name": urn_name,
        "label": label,
        "closed_image": get_urn_image_path(urn_name, "closed"),
        "opened_image": get_urn_image_path(urn_name, "opened"),
        "condition": (params.CONDITION_KNOWN_X_UNKNOWN_F if condition == "known"
                      else params.CONDITION_UNKNOWN_X_UNKNOWN_F),
        "condition_description": (params.KNOWN_X_DESCRIPTION if condition == "known"
                                  else params.UNKNOWN_X_DESCRIPTION),
        "participant_knows_k": condition == "known",
        "ambiguous_k": k,
        "cycle": list(cycle),
        "payoff_type": "performance" if kind == "ambiguous" else "fixed",
        "value": value,
    }


def create_ambiguous_urn(urn_name, label, ambiguous_condition, k, cycle=None):
    if ambiguous_condition not in ("known", "unknown"):
        raise ValueError("unknown condition")
    if cycle is None:
        cycle = generate_k_cycle(k)
    return _make_urn(urn_name, label, "ambiguous", ambiguous_condition, k, cycle)


def create_deterministic_urn(urn_name, label, value, k=None,
                             ambiguous_condition="known", cycle=None):
    if k is None:
        k = random.choice(params.AMBIGUOUS_K_OPTIONS)
    if ambiguous_condition not in ("known", "unknown"):
        raise ValueError("unknown condition")
    if cycle is None:
        cycle = generate_k_cycle(k)
    return _make_urn(urn_name, label, "deterministic", ambiguous_condition,
                     k, cycle, value=value)


def assign_urns_to_sides(deterministic_value, ambiguous_condition, k):
    """The two urns have the same task parameters; only payoff differs."""
    names = random.sample(params.PRETTY_URN_NAMES, 2)
    deterministic_side = random.choice(("left", "right"))
    ambiguous_side = "right" if deterministic_side == "left" else "left"
    sides = {"left": names[0], "right": names[1]}
    labels = {"left": params.LEFT_URN_LABEL, "right": params.RIGHT_URN_LABEL}
    common_cycle = generate_k_cycle(k)
    return {
        deterministic_side: create_deterministic_urn(
            sides[deterministic_side], labels[deterministic_side],
            deterministic_value, k=k, ambiguous_condition=ambiguous_condition,
            cycle=common_cycle),
        ambiguous_side: create_ambiguous_urn(
            sides[ambiguous_side], labels[ambiguous_side],
            ambiguous_condition, k, cycle=common_cycle),
    }


def create_noise_schedule(n_trials, pattern_probability):
    n_rule = round(n_trials * pattern_probability)
    schedule = [False] * n_rule + [True] * (n_trials - n_rule)
    random.shuffle(schedule)
    return schedule


def get_pattern_prediction(cycle, prediction_index):
    return cycle[prediction_index % len(cycle)]


def opposite_color(color):
    if color == "blue":
        return "magenta"
    if color == "magenta":
        return "blue"
    raise ValueError(f"Unknown color: {color}")


def generate_next_outcome(selected_urn, prediction_index, is_noise_trial):
    pattern_prediction = get_pattern_prediction(selected_urn["cycle"], prediction_index)
    outcome = (opposite_color(pattern_prediction) if is_noise_trial
               else pattern_prediction)
    return outcome, pattern_prediction


# -----------------------------------------------------------------------------
# Choice screen: matching training_task.py's reward cards.
# -----------------------------------------------------------------------------

def _indicators(win, x, y, filled, total=3, radius=0.008, spacing=0.026):
    for i in range(total):
        active = i < filled
        circle = _cached(win, ("card_indicator", x, y, i, radius, spacing),
                         lambda: visual.Circle(
                             win=win, radius=radius,
                             pos=(x + i * spacing, y), edges=32,
                             lineWidth=1.2))
        circle.fillColor = "#334155" if active else None
        circle.lineColor = "#334155" if active else "#94a3b8"
        circle.draw()


def draw_selection_condition_text(win, urn, x_pos):
    
    ambiguous = urn["urn_type"] == "ambiguous"
    y, width = -0.280, 0.53

    # Same colors for both urns
    fill = "#EDF1F5"
    border = "#C4CDD8"
    accent = "#172B49"

    rect = _cached(
        win,
        ("card", ambiguous, x_pos),
        lambda: visual.Rect(
            win,
            pos=(x_pos, y),
            width=width,
            height=0.190,
            fillColor=fill,
            lineColor=border,
            lineWidth=1.2
        )
    )
    rect.draw()

    heading = "MAXIMUM REWARD" if ambiguous else "GUARANTEED REWARD"
    amount = (f"+4 pts (max {params.MAX_AMBIGUOUS_REWARD:g})" if ambiguous
              else f"{urn['value']:g} pts")
    subtitle = ("earn points per correct guess"
                if ambiguous else "Fixed reward")
    draw_text(win, heading, (x_pos, y + 0.067), 0.018,
              color="#475569", bold=True).draw()
    draw_text(win, amount, (x_pos, y + 0.020), 0.042,
              color=accent, bold=True).draw()
    draw_text(win, subtitle, (x_pos, y - 0.020), 0.020,
              color=accent).draw()
    draw_text(win, "Pattern length", (x_pos - 0.075, y - 0.060),
              0.020, wrap_width=0.18, color="#334155").draw()
    count = int(urn["ambiguous_k"]) if urn["participant_knows_k"] else 0
    _indicators(win, x_pos + 0.015, y - 0.060, count)


def collect_urn_choice(win, urn_assignment):
    draw_text(win, "Choose an urn", (0, 0.405),
              height=0.047, bold=True, color="#172b49").draw()
    draw_text(win, "Press ← or → to choose", (0, 0.325),
              height=0.026, color="#576a82").draw()
    for side in ("left", "right"):
        urn = urn_assignment[side]
        x = params.URN_LEFT_POS[0] if side == "left" else params.URN_RIGHT_POS[0]
        _image(win, urn["closed_image"],
               (x, params.URN_LEFT_POS[1]),
               (params.URN_IMAGE_SIZE[0] * 1.3, params.URN_IMAGE_SIZE[1] * 1.3)).draw()
        draw_selection_condition_text(win, urn, x)

    event.clearEvents()
    clock = core.Clock()
    win.callOnFlip(clock.reset)
    win.flip()
    keys = event.waitKeys(keyList=["left", "right", "escape"], timeStamped=clock)
    key, reaction_time = keys[0]
    if key == "escape":
        quit_experiment(win)
    return key, float(reaction_time)


def animate_selected_urn_transition(win, selected_urn, selected_side,
                                    urn_assignment, highlight_duration=0.10,
                                    move_duration=0.24):
    """Reuse images while selected urn moves to the prediction position."""
    start = (params.URN_LEFT_POS if selected_side == "left"
             else params.URN_RIGHT_POS)
    other_side = "right" if selected_side == "left" else "left"
    other = urn_assignment[other_side]
    other_pos = (params.URN_LEFT_POS if other_side == "left"
                 else params.URN_RIGHT_POS)

    # Reuse two stimuli throughout the movement, not recreate each frame.
    moving = _image(win, selected_urn["opened_image"], start, params.URN_IMAGE_SIZE)
    other_stim = _image(win, other["closed_image"], other_pos, params.URN_IMAGE_SIZE)
    off_x = -0.80 if other_side == "left" else 0.80
    n_frames = max(2, int(move_duration * 30))
    for i in range(n_frames + 1):
        t = i / n_frames
        t = t * t * (3 - 2 * t)
        moving.pos = (start[0] + (params.SELECTED_URN_POS[0] - start[0]) * t,
                      start[1] + (params.SELECTED_URN_POS[1] - start[1]) * t)
        moving.size = tuple(params.URN_IMAGE_SIZE[j]
                            + (params.SELECTED_URN_SIZE[j] - params.URN_IMAGE_SIZE[j]) * t
                            for j in range(2))
        other_stim.pos = (other_pos[0] + (off_x - other_pos[0]) * t, other_pos[1])
        other_stim.draw()
        moving.draw()
        win.flip()
    # Restore the shared cached stimulus's size if used on later screens.
    moving.size = params.URN_IMAGE_SIZE


# -----------------------------------------------------------------------------
# Prediction screen: matching practice (left indicators + rounded score bar).
# -----------------------------------------------------------------------------

def _draw_info(win, selected_urn):
    # ---------------------------------------------------------
    # Urn type (top row)
    # ---------------------------------------------------------

    reward_type = (
        "Fixed reward"
        if selected_urn["urn_type"] == "deterministic"
        else "Performance-dependent reward"
    )

    # Left-aligned label
    draw_text(
        win,
        "Urn type",
        (params.INFO_LABEL_X, params.URN_TYPE_Y),
        height=params.INFO_TEXT_HEIGHT,
        color=params.INFO_COLOR,
        align_text="left"
    ).draw()
    # Left-aligned reward description
    draw_text(
        win,
        reward_type,
        (
            params.INFO_BALL_START_X + params.URN_TYPE_VALUE_OFFSET_X,
            params.URN_TYPE_Y
        ),
        height=params.INFO_TEXT_HEIGHT,
        color=params.INFO_COLOR,
        bold=True,
        align_text="left"
    ).draw()

    known = bool(selected_urn["participant_knows_k"])
    k_count = int(selected_urn["ambiguous_k"]) if known else 0

    # Show the number directly next to the pattern-length label.
    pattern_label = (
        f"Pattern length ({k_count})"
        if known else "Pattern length (?)"
    )

    for row, (label, count) in enumerate((
        (pattern_label, k_count),
        (f"Flipped balls ({params.N_RANDOM_DRAWS})", params.N_RANDOM_DRAWS)
    )):

        y = params.INFO_ROW_Y[row]
        draw_text(win, label, (params.INFO_LABEL_X, y),
                  height=params.INFO_TEXT_HEIGHT, color=params.INFO_COLOR,
                  align_text="left").draw()
        for i in range(3):
            circle = _cached(win, ("info_ball", row, i),
                             lambda: visual.Circle(win=win,
                                                   pos=(params.INFO_BALL_START_X
                                                        + i * params.INFO_BALL_SPACING, y),
                                                   radius=params.INFO_BALL_RADIUS,
                                                   edges=32, lineWidth=1.3))
            active = i < count
            circle.fillColor = params.INFO_COLOR if active else None
            circle.lineColor = params.INFO_COLOR if active else params.INFO_EMPTY_COLOR
            circle.draw()


def _draw_pill(win, left, right, y, height, color, key):
    r = height / 2
    inner_width = max(0, right - left - height)
    if inner_width > 0:
        rect = _cached(win, ("bar_rect", key), lambda: visual.Rect(
            win=win, pos=((left + right) / 2, y), width=inner_width,
            height=height, fillColor=color, lineColor=None))
        rect.pos = ((left + right) / 2, y)
        rect.width = inner_width
        rect.draw()
    for idx, x in enumerate((left + r, right - r)):
        disk = _cached(win, ("bar_cap", key, idx), lambda: visual.Circle(
            win=win, radius=r, pos=(x, y), edges=32,
            fillColor=color, lineColor=None))
        disk.pos = (x, y)
        disk.draw()


def draw_score_progress(win, trial_results, total_trials, selected_urn=None):
    """Bar tracks correct predictions; points track the chosen urn's payoff."""
    correct = sum(bool(x) for x in trial_results)
    complete = len(trial_results)
    fraction = correct / total_trials if total_trials else 0
    accuracy = 100 * correct / complete if complete else 0
    if selected_urn is not None and selected_urn["urn_type"] == "deterministic":
        points = selected_urn["value"]
    else:
        points = correct * params.REWARD_PER_CORRECT_GUESS
    left, right, y, height = (params.SCORE_BAR_LEFT_X, params.SCORE_BAR_RIGHT_X,
                              params.SCORE_BAR_Y, params.SCORE_BAR_HEIGHT)
    _draw_pill(win, left, right, y, height, "#d6dce5", "track")
    filled_width = (right - left) * fraction
    if filled_width >= height:
        _draw_pill(win, left, left + filled_width, y, height, "#789bc0", "fill")
    draw_text(win, f"{points:g} pts", (left + 0.018, y), height=0.021,
              color="#ffffff" if filled_width >= 0.10 else params.INFO_COLOR,
              bold=True, align_text="left").draw()
    draw_text(win, f"{accuracy:.0f}% correct", (params.SCORE_ACCURACY_X, y),
              height=0.020, color=params.INFO_COLOR, align_text="right").draw()


def get_feedback_ball_position(ball_index):
    row, col = divmod(ball_index, params.FEEDBACK_BALLS_PER_ROW)
    return (params.FEEDBACK_START_X + col * params.FEEDBACK_SPACING_X,
            params.FEEDBACK_START_Y - row * params.FEEDBACK_SPACING_Y)


def draw_sequence_feedback(win, sequence):
    draw_text(win, params.SEQUENCE_TITLE, params.SEQUENCE_TITLE_POS,
              height=params.SEQUENCE_TITLE_HEIGHT, wrap_width=0.30,
              bold=True, color="#172b49", align_text="left").draw()
    for i, color in enumerate(sequence):
        pos = get_feedback_ball_position(i)
        dot = _cached(win, ("history_ball", i),
                    lambda: visual.Circle(win, pos=pos,
                                            radius=params.FEEDBACK_BALL_RADIUS,
                                            fillColor=params.ball_display_color(color),
                                            lineColor="black", lineWidth=1.5, edges=32))
        dot.pos = pos
        dot.fillColor = params.ball_display_color(color)
        dot.draw()


def draw_trial_instruction(win, selected_urn):
    _draw_info(win, selected_urn)


def draw_trial_dividers(win):
    """Retained for compatibility. Practice screen has no dividers."""
    return None


def draw_prediction_choices(win):
    """Keyboard-only input. A reminder appears after the delay."""
    return None


def _prediction_frame(win, selected_urn, sequence, trial_results, reminder=False):
    draw_trial_instruction(win, selected_urn)
    draw_score_progress(win, trial_results, params.N_TRIALS_PER_ROUND, selected_urn)
    draw_sequence_feedback(win, sequence)
    draw_selected_open_urn(win, selected_urn)
    if reminder:
        draw_text(win, "Press B for blue or M for magenta", (0, -0.145),
                  height=0.023, color="#66758b").draw()


def collect_prediction(win, selected_urn, sequence, trial_number,
                       total_trials=None, number_correct=0, trial_results=None):
    trial_results = trial_results if trial_results is not None else []
    event.clearEvents()
    clock = core.Clock()
    win.callOnFlip(clock.reset)
    _prediction_frame(win, selected_urn, sequence, trial_results)
    win.flip()
    reminder_shown = False
    while True:
        keys = event.getKeys(keyList=list(params.GUESS_KEYS.keys()) + ["escape"],
                             timeStamped=clock)
        if keys:
            key, rt = keys[0]
            if key == "escape":
                quit_experiment(win)
            return params.GUESS_KEYS[key], float(rt)
        if not reminder_shown and clock.getTime() >= params.REMINDER_AFTER:
            reminder_shown = True
            _prediction_frame(win, selected_urn, sequence, trial_results, reminder=True)
            win.flip()
        core.wait(0.005)


def animate_ball_reveal(win, selected_urn, sequence, trial_number,
                        total_trials, guess, outcome, trial_results=None,
                        rise_duration=None, reveal_duration=None,
                        pause_duration=None, history_duration=None):
    """Match the practice: grey ball rises, flips, shrinks into history."""
    before = sequence[:-1]
    trial_results = trial_results if trial_results is not None else []
    start = (params.SELECTED_URN_POS[0],
             params.SELECTED_URN_POS[1]
             + params.SELECTED_URN_SIZE[1] * params.REVEAL_START_HEIGHT_FRACTION)
    reveal = params.OUTCOME_BALL_POS
    finish = get_feedback_ball_position(len(sequence) - 1)
    max_r = params.REVEAL_BALL_RADIUS
    min_r = params.FEEDBACK_BALL_RADIUS
    circle = visual.Circle(win=win, pos=start, radius=max_r,
                           fillColor="#94a3b8", lineColor="black",
                           edges=48, lineWidth=2)

    def frame(pos, color, radius, width_scale=1.0):
        _prediction_frame(win, selected_urn, before, trial_results)
        circle.pos = pos
        circle.fillColor = params.ball_display_color(color)
        circle.size = (radius * 2 * max(0.01, width_scale), radius * 2)
        circle.draw()
        win.flip()

    def lerp(a, b, t):
        return tuple(a[j] + (b[j] - a[j]) * t for j in range(2))

    def ease(t):
        return t * t * (3 - 2 * t)

    rise_n = max(1, int(params.RISE_FRAMES))
    half_n = max(1, int(params.FLIP_HALF_FRAMES))
    history_n = max(1, int(params.HISTORY_FRAMES))
    for i in range(rise_n + 1):
        frame(lerp(start, reveal, ease(i / rise_n)), "#94a3b8", max_r)
    for i in range(half_n + 1):
        frame(reveal, "#94a3b8", max_r, 1 - i / half_n)
    for i in range(half_n + 1):
        frame(reveal, outcome, max_r, i / half_n)
    for i in range(history_n + 1):
        t = ease(i / history_n)
        frame(lerp(reveal, finish, t), outcome, max_r + (min_r - max_r) * t)


def show_trial_outcome(win, selected_urn, sequence, trial_number, guess,
                       outcome, total_trials=None, wait_for_continue=False,
                       trial_results=None):
    if total_trials is None:
        total_trials = params.N_TRIALS_PER_ROUND
    trial_results = trial_results if trial_results is not None else []
    animate_ball_reveal(win, selected_urn, sequence, trial_number,
                        total_trials, guess, outcome, trial_results=trial_results[:-1])
    _prediction_frame(win, selected_urn, sequence, trial_results)
    if wait_for_continue:
        draw_text(win, "Press SPACE to continue", (0, -0.18),
                  height=0.024, color="#172b49").draw()
    win.flip()
    if wait_for_continue:
        event.clearEvents()
        keys = event.waitKeys(keyList=["space", "escape"])
        if "escape" in keys:
            quit_experiment(win)
    else:
        core.wait(params.REVEAL_DURATION + params.INTER_TRIAL_INTERVAL)


# -----------------------------------------------------------------------------
# Prediction block, feedback, post-block questions.
# -----------------------------------------------------------------------------

def run_trials(win, selected_urn, n_trials=None):
    if n_trials is None:
        n_trials = params.N_TRIALS_PER_ROUND
    k = selected_urn["ambiguous_k"]
    cycle = selected_urn["cycle"]
    seed = generate_latent_sequence(cycle, params.N_INITIAL_DRAWS)
    sequence = list(seed)
    noise_schedule = create_noise_schedule(n_trials, params.PATTERN_PROBABILITY)
    trials = []
    for trial_number, noise in enumerate(noise_schedule, start=1):
        history_before = list(sequence)
        previous = [entry["correct"] for entry in trials]
        guess, reaction_time = collect_prediction(
            win, selected_urn, sequence, trial_number,
            total_trials=n_trials, trial_results=previous)
        prediction_index = params.N_INITIAL_DRAWS + trial_number - 1
        outcome, pattern_prediction = generate_next_outcome(
            selected_urn, prediction_index, noise)
        sequence.append(outcome)
        correct = guess == outcome
        trials.append({
            "trial_number": trial_number,
            "guess": guess,
            "outcome": outcome,
            "correct": correct,
            "response_time": reaction_time,
            "is_noise_trial": bool(noise),
            "pattern_prediction": pattern_prediction,
            # This is about learning the latent rule, not the noisy outcome:
            "guess_matches_pattern": guess == pattern_prediction,
            "prediction_index": prediction_index,
            "cycle_position": prediction_index % k,
            "outcome_matches_pattern": outcome == pattern_prediction,
            "history_before_draw": history_before,
            "payoff_type": selected_urn["payoff_type"],
            "prediction_affects_earnings": selected_urn["payoff_type"] == "performance",
        })
        show_trial_outcome(
            win, selected_urn, sequence, trial_number, guess, outcome,
            total_trials=n_trials, trial_results=[r["correct"] for r in trials],
            wait_for_continue=trial_number == n_trials)

    correct_count = sum(r["correct"] for r in trials)
    earnings = (correct_count * params.REWARD_PER_CORRECT_GUESS
                if selected_urn["urn_type"] == "ambiguous"
                else selected_urn["value"])
    return {
        "seed_sequence": seed,
        "full_sequence": list(sequence),
        "trial_data": trials,
        "number_correct": correct_count,
        "accuracy": correct_count / n_trials if n_trials else 0,
        "number_noise_trials": sum(r["is_noise_trial"] for r in trials),
        "number_pattern_trials": sum(not r["is_noise_trial"] for r in trials),
        "number_pattern_consistent": sum(r["outcome_matches_pattern"] for r in trials),
        "block_earnings": earnings,
        "reward_per_correct_guess": params.REWARD_PER_CORRECT_GUESS,
    }


def show_round_earnings(win, selected_urn, round_results, round_number, total_rounds, training=False):
    """Compact circular accuracy and points like the practice-round summary."""
    correct = round_results["number_correct"]
    n = len(round_results["trial_data"])
    accuracy = 100 * correct / n if n else 0
    earned = round_results["block_earnings"]

    # Progress across experimental blocks
    draw_text(
        win,
        f"ROUND {round_number} OF {total_rounds}",
        (0, 0.44),
        height=0.022,
        color="#64748b",
    ).draw()

    
    # ---------------------------------------------------------
    # Progress indicator: 18 horizontal segments
    # ---------------------------------------------------------

    max_progress_width = 0.90
    bar_gap = 0.009

    bar_width = (
        max_progress_width - (total_rounds - 1) * bar_gap
    ) / total_rounds
    bar_height = 0.012
    bar_y = 0.39

    completed_color = "#789bc0"
    remaining_color = "#c6cbd2"

    total_width = (
        total_rounds * bar_width
        + (total_rounds - 1) * bar_gap
    )

    start_x = -total_width / 2 + bar_width / 2

    for i in range(total_rounds):
        x = start_x + i * (bar_width + bar_gap)

        color = (
            completed_color
            if i < round_number
            else remaining_color
        )

        bar = visual.Rect(
            win,
            pos=(x, bar_y),
            width=bar_width,
            height=bar_height,
            fillColor=color,
            lineColor=None
        )
        bar.draw()

    draw_text(win, "ROUND COMPLETE", (0, 0.33), height=0.025,
              bold=True, color="#64748b").draw()
    cx, cy, radius = -0.17, 0.015, 0.103
    visual.Circle(win, pos=(cx, cy), radius=radius, fillColor=None,
                  lineColor="#aab8ca", lineWidth=11, edges=120).draw()
    if accuracy > 0:
        fraction = accuracy / 100
        count = max(30, int(240 * fraction))
        vertices = [(cx + radius * math.cos(math.pi / 2 - 2 * math.pi * fraction * i / count),
                     cy + radius * math.sin(math.pi / 2 - 2 * math.pi * fraction * i / count))
                    for i in range(count + 1)]
        visual.ShapeStim(win=win, vertices=vertices, closeShape=False,
                         fillColor=None, lineColor="#2e7bd4", lineWidth=11).draw()
    draw_text(win, f"{accuracy:.0f}%", (cx, cy + 0.012),
              height=0.048, bold=True).draw()
    draw_text(win, "correct", (cx, cy - 0.038),
              height=0.022, color="#64748b").draw()
    visual.Line(win, start=(0.015, -0.145), end=(0.015, 0.05),
                lineColor="#b7c2d0", lineWidth=1.5).draw()
    draw_text(win, f"{earned:g} points", (0.205, 0.032),
              height=0.052, bold=True).draw()
    draw_text(win, "earned this round", (0.205, -0.025),
              height=0.023, color="#64748b").draw()
    draw_text(win, "Press SPACE to continue", (0, -0.35),
              height=0.024, color="#576a82").draw()
    win.flip()
    event.clearEvents()
    keys = event.waitKeys(keyList=["space", "escape"])
    if "escape" in keys:
        quit_experiment(win)


def create_ambiguous_condition_schedule(total_rounds):
    """Compatibility helper: balanced known/unknown only."""
    if total_rounds % 2:
        raise ValueError("Exact 50% requires an even number of rounds")
    schedule = ["known"] * (total_rounds // 2) + ["unknown"] * (total_rounds // 2)
    random.shuffle(schedule)
    return schedule


def run_urn_visual_test(round_number=1, total_rounds=1,
                        deterministic_value=None, ambiguous_condition="known",
                        k=2, training=False, win=None):
    """Run a complete block, returning both choices and post-block responses."""
    if deterministic_value is None:
        deterministic_value = params.STAIRCASE_INITIAL_VALUE
    owns_window = win is None
    if owns_window:
        win = visual.Window(size=params.WINDOW_SIZE, fullscr=params.FULLSCREEN, screen=getattr(params, "SCREEN_INDEX", 1),
                            color=params.BACKGROUND_COLOR, units="height",monitor=params.MONITOR_NAME, gammaErrorPolicy="warn")
    try:
        if round_number == 1:
            draw_text(win,"New parameters", (0, 0.2), #before 0.13
                      height=0.050, bold=True, color="#172b49").draw()
            draw_text(win, params.URN_INSTRUCTIONS, (0, -0.025),
                      height=0.026, wrap_width=1.18, color="#334155").draw()
            win.flip()
            event.clearEvents()
            keys = event.waitKeys(keyList=["space", "escape"])
            if "escape" in keys:
                quit_experiment(win)

        # A fixation precedes every choice, matching guided practice.
        draw_text(win, "+", (0, 0), height=0.070,
                  bold=True, color="#172b49").draw()
        win.flip()
        core.wait(0.35)
        assignment = assign_urns_to_sides(deterministic_value, ambiguous_condition, k)
        side, choice_rt = collect_urn_choice(win, assignment)
        chosen = assignment[side]
        animate_selected_urn_transition(win, chosen, side, assignment)
        block = run_trials(win, chosen)
        show_round_earnings(win, chosen, block, round_number, total_rounds, training=training)

        questions = run_post_block_questions(win=win, selected_urn=chosen)
        if questions is None:
            questions = {}
        if not isinstance(questions, dict):
            raise TypeError("questions_task.run_post_block_questions must return a dict")
        estimated_cycle = questions.get("estimated_cycle")
        reconstructed = (cycles_match(chosen["cycle"], estimated_cycle)
                         if estimated_cycle is not None else None)
        result = dict(block)
        result.update({
            "round_number": round_number,
            "k": k,
            "ambiguous_condition": ambiguous_condition,
            "deterministic_value": deterministic_value,
            "selected_side": side,
            "selected_urn_type": chosen["urn_type"],
            "selected_urn_name": chosen["urn_name"],
            "selected_condition": chosen["condition"],
            "selected_ambiguous_k": k,
            "selected_cycle": serialise_cycle(chosen["cycle"]),
            "selected_participant_knows_k": chosen["participant_knows_k"],
            "selected_value": chosen["value"],
            "selected_payoff_type": chosen["payoff_type"],
            "urn_choice_rt": choice_rt,
            "left_urn_type": assignment["left"]["urn_type"],
            "left_urn_name": assignment["left"]["urn_name"],
            "right_urn_type": assignment["right"]["urn_type"],
            "right_urn_name": assignment["right"]["urn_name"],
            "estimated_k": questions.get("estimated_k"),
            "estimated_cycle": estimated_cycle,
            "estimated_cycle_serialised": serialise_cycle(estimated_cycle),
            "estimated_cycle_correct": reconstructed,
            "post_block_confidence": questions.get("confidence"),
            "post_block_liking": questions.get("liking"),
            "post_block_difficulty": questions.get("difficulty"),
            "post_block_mental_effort": questions.get("mental_effort"),
            "question_results": questions,
        })
        return result
    finally:
        if owns_window:
            _clear_visual_cache(win)
            win.close()


# -----------------------------------------------------------------------------
# ONE global staircase: step changes after 6 and 12 blocks, not on reversals.
# -----------------------------------------------------------------------------


def update_staircase(staircase, choice, round_number, k_value=None):
    """Update the deterministic reward after each round."""

    if choice not in ("ambiguous", "deterministic"):
        raise ValueError("Invalid urn choice")

    block_number = (
        (round_number - 1) // params.ROUNDS_PER_BLOCK
    ) + 1

    step = params.STAIRCASE_STEP_SIZES[block_number - 1]

    direction = 1 if choice == "ambiguous" else -1

    staircase["value"] = max(
        params.STAIRCASE_MIN_VALUE,
        min(
            params.STAIRCASE_MAX_VALUE,
            staircase["value"] + direction * step
        )
    )

    staircase["previous_choice"] = choice

    return staircase



if __name__ == "__main__":
    print(run_urn_visual_test())
