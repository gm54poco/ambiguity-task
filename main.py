import urn_task
import urn_params as params


def main():

    all_block_results = []

    ambiguous_condition_schedule = (
        urn_task.create_ambiguous_condition_schedule(
            params.N_BLOCKS
        )
    )

    staircases = {
        "known": {
            "value": 2.00,
            "step_index": 0,
            "previous_choice": None,
            "reversals": [],
        },

        "unknown": {
            "value": 2.00,
            "step_index": 0,
            "previous_choice": None,
            "reversals": [],
        },
    }

    for block_number in range(
        1,
        params.N_BLOCKS + 1,
    ):

        condition = (
            ambiguous_condition_schedule[
                block_number - 1
            ]
        )

        deterministic_value = (
            staircases[
                condition
            ][
                "value"
            ]
        )

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
            )
        )

        selected_type = (
            block_results[
                "selected_urn_type"
            ]
        )

        staircases[
            condition
        ] = urn_task.update_staircase(
            staircase=staircases[
                condition
            ],
            choice=selected_type,
        )

        block_results[
            "block_number"
        ] = block_number

        all_block_results.append(
            block_results
        )

    return all_block_results

if __name__ == "__main__":
    main()