"""Create balanced, randomized known/unknown-k block assignments."""

import random
import urn_params as params


def create_balanced_schedule():
    """
    Create an experimental schedule for any number of rounds.

    - Approximately 50% known k and 50% unknown k.
    - Balance k = 1, 2, 3 as evenly as possible.
    - Randomize the order of conditions.
    """

    import random
    import urn_params as params

    n_rounds = params.N_ROUNDS

    if n_rounds < 1:
        raise ValueError("N_ROUNDS must be at least 1.")

    conditions = [
        ("known", 1),
        ("known", 2),
        ("known", 3),
        ("unknown", 1),
        ("unknown", 2),
        ("unknown", 3),
    ]

    # Generate complete sets of six balanced rounds.
    schedule_pairs = conditions * (n_rounds // 6)

    # Add any remaining rounds, as evenly as possible.
    remainder = n_rounds % 6

    if remainder:
        extra = conditions.copy()
        random.shuffle(extra)
        schedule_pairs.extend(extra[:remainder])

    random.shuffle(schedule_pairs)
    # Five effective staircase updates per condition.
    # Balance the 4-point and 8-point steps across both staircases.

    extra_step = random.choice(params.STAIRCASE_STEP_SIZES)

    steps_by_condition = {
        "known": [4, 4, 8, 8, extra_step],
        "unknown": [4, 4, 8, 8, 12 - extra_step],
    }

    for steps in steps_by_condition.values():
        random.shuffle(steps)

    condition_counter = {"known": 0, "unknown": 0}
    schedule = []

    for index, (condition, k) in enumerate(schedule_pairs):

        condition_counter[condition] += 1
        occurrence = condition_counter[condition]

        # No update after the sixth and final occurrence.
        step = (
            steps_by_condition[condition][occurrence - 1]
            if occurrence <= 5
            else None
        )

        schedule.append({
            "block_number": index + 1,
            "condition": condition,
            "k": k,
            "step": step,
        })

    return schedule
