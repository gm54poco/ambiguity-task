import random

import urn_task
import urn_params as params


def create_k_schedule(total_blocks):
    """
    Create a roughly balanced randomized schedule of k values.

    Example:
        total_blocks = 9
        -> three blocks with k=1
        -> three blocks with k=2
        -> three blocks with k=3
    """

    k_values = [1, 2, 3]

    repetitions = (
        total_blocks
        // len(k_values)
    )

    remainder = (
        total_blocks
        % len(k_values)
    )

    schedule = (
        k_values * repetitions
    )

    schedule += (
        k_values[:remainder]
    )

    random.shuffle(
        schedule
    )

    return schedule


def main():

    all_block_results = []

    # -------------------------------------------------------------
    # Known / unknown ambiguity-condition schedule
    # -------------------------------------------------------------

    ambiguous_condition_schedule = (
        urn_task.create_ambiguous_condition_schedule(
            params.N_BLOCKS
        )
    )

    # -------------------------------------------------------------
    # k schedule
    # -------------------------------------------------------------

    k_schedule = create_k_schedule(
        params.N_BLOCKS
    )

    # -------------------------------------------------------------
    # Separate monetary staircase for each k
    # -------------------------------------------------------------

    staircases = {
        1: {
            "k": 1,
            "value": params.STAIRCASE_INITIAL_VALUE,
            "step_index": 0,
            "previous_choice": None,
            "reversals": [],
        },

        2: {
            "k": 2,
            "value": params.STAIRCASE_INITIAL_VALUE,
            "step_index": 0,
            "previous_choice": None,
            "reversals": [],
        },

        3: {
            "k": 3,
            "value": params.STAIRCASE_INITIAL_VALUE,
            "step_index": 0,
            "previous_choice": None,
            "reversals": [],
        },
    }

    # -------------------------------------------------------------
    # Run blocks
    # -------------------------------------------------------------

    for block_number in range(
        1,
        params.N_BLOCKS + 1,
    ):

        # ---------------------------------------------------------
        # Condition for this block
        # ---------------------------------------------------------

        condition = (
            ambiguous_condition_schedule[
                block_number - 1
            ]
        )

        # ---------------------------------------------------------
        # k for this block
        # ---------------------------------------------------------

        current_k = (
            k_schedule[
                block_number - 1
            ]
        )

        # ---------------------------------------------------------
        # Current deterministic value for this k
        # ---------------------------------------------------------

        deterministic_value = (
            staircases[
                current_k
            ][
                "value"
            ]
        )

        print(
            "\n"
            + "=" * 60
        )

        print(
            f"Starting block {block_number}"
        )

        print(
            f"k = {current_k}"
        )

        print(
            f"Ambiguous condition = {condition}"
        )

        print(
            f"Deterministic value = {deterministic_value:.2f}"
        )

        print(
            "=" * 60
            + "\n"
        )

        # ---------------------------------------------------------
        # Run block
        # ---------------------------------------------------------

        block_results = (
            urn_task.run_urn_visual_test(
                block_number=block_number,
                total_blocks=params.N_BLOCKS,

                deterministic_value=(
                    deterministic_value
                ),

                ambiguous_condition=(
                    condition
                ),

                k=current_k,
            )
        )

        # ---------------------------------------------------------
        # Participant choice
        # ---------------------------------------------------------

        selected_type = (
            block_results[
                "selected_urn_type"
            ]
        )

        # ---------------------------------------------------------
        # Save value BEFORE staircase update
        # ---------------------------------------------------------

        block_results[
            "staircase_value_before"
        ] = deterministic_value

        # ---------------------------------------------------------
        # Update only the staircase corresponding to current k
        # ---------------------------------------------------------

        staircases[
            current_k
        ] = urn_task.update_staircase(
            staircase=staircases[
                current_k
            ],
            choice=selected_type,
            k_value=current_k,
        )

        # ---------------------------------------------------------
        # Save value AFTER staircase update
        # ---------------------------------------------------------

        block_results[
            "staircase_value_after"
        ] = (
            staircases[
                current_k
            ][
                "value"
            ]
        )

        block_results[
            "staircase_step_index"
        ] = (
            staircases[
                current_k
            ][
                "step_index"
            ]
        )

        block_results[
            "staircase_reversals"
        ] = list(
            staircases[
                current_k
            ][
                "reversals"
            ]
        )

        # ---------------------------------------------------------
        # Save block information
        # ---------------------------------------------------------

        block_results[
            "block_number"
        ] = block_number

        block_results[
            "k"
        ] = current_k

        block_results[
            "ambiguous_condition"
        ] = condition

        all_block_results.append(
            block_results
        )

        # ---------------------------------------------------------
        # Debug output
        # ---------------------------------------------------------

        print(
            "\n"
            + "-" * 60
        )

        print(
            f"Finished block {block_number}"
        )

        print(
            f"k = {current_k}"
        )

        print(
            f"Choice = {selected_type}"
        )

        print(
            "Value before choice = "
            f"{deterministic_value:.2f}"
        )

        print(
            "Value for next k="
            f"{current_k} block = "
            f"{staircases[current_k]['value']:.2f}"
        )

        print(
            "-" * 60
            + "\n"
        )

    # -------------------------------------------------------------
    # Final staircase information
    # -------------------------------------------------------------

    print(
        "\n"
        + "=" * 70
    )

    print(
        "FINAL STAIRCASES"
    )

    print(
        "=" * 70
    )

    for k_value in [
        1,
        2,
        3,
    ]:

        staircase = (
            staircases[
                k_value
            ]
        )

        print(
            f"\nk = {k_value}"
        )

        print(
            "Final value:",
            f"{staircase['value']:.2f}",
        )

        print(
            "Reversals:",
            staircase[
                "reversals"
            ],
        )

        print(
            "Step index:",
            staircase[
                "step_index"
            ],
        )

    print(
        "\n"
        + "=" * 70
    )

    return all_block_results


if __name__ == "__main__":
    main()