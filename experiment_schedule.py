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

    schedule = []

    for index, (condition, k) in enumerate(schedule_pairs):

        # Assign staircase stages by block position.
        stage_index = min(
            index // params.ROUNDS_PER_BLOCK,
            len(params.STAIRCASE_STEP_SIZES) - 1
        )

        schedule.append({
            "block_number": index + 1,
            "condition": condition,
            "k": k,
            "stage": stage_index + 1,
            "step": params.STAIRCASE_STEP_SIZES[stage_index],
        })

    return schedule
