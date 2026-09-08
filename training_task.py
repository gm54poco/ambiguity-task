import random

import urn_task
import urn_params as params


class TrainingTask:
    """
    Short training version of the urn experiment.

    The training follows the same structure as the real experiment,
    but contains only 5 blocks.

    Training staircase values are kept separate from the staircase
    used in the real experiment.
    """

    def __init__(
        self,
        n_blocks=5,
        starting_value=2.00,
    ):

        self.n_blocks = n_blocks
        self.starting_value = starting_value

        # -------------------------------------------------------------
        # Training condition schedule
        # -------------------------------------------------------------
        #
        # With 5 blocks, exact 50/50 balance is impossible.
        # Therefore one condition occurs 3 times and the other 2 times.
        #
        # Which condition gets the extra block is randomized.
        # -------------------------------------------------------------

        if random.choice(
            ["known", "unknown"]
        ) == "known":

            self.condition_schedule = [
                "known",
                "known",
                "known",
                "unknown",
                "unknown",
            ]

        else:

            self.condition_schedule = [
                "known",
                "known",
                "unknown",
                "unknown",
                "unknown",
            ]

        random.shuffle(
            self.condition_schedule
        )

        # -------------------------------------------------------------
        # Separate staircase for each ambiguous condition
        # -------------------------------------------------------------

        self.staircases = {
            "known": {
                "value": self.starting_value,
                "step_index": 0,
                "previous_choice": None,
                "reversals": [],
            },

            "unknown": {
                "value": self.starting_value,
                "step_index": 0,
                "previous_choice": None,
                "reversals": [],
            },
        }

        self.all_results = []

    # -----------------------------------------------------------------
    # Run one training block
    # -----------------------------------------------------------------

    def run_block(
        self,
        block_number,
    ):

        ambiguous_condition = (
            self.condition_schedule[
                block_number - 1
            ]
        )

        staircase = (
            self.staircases[
                ambiguous_condition
            ]
        )

        deterministic_value = (
            staircase[
                "value"
            ]
        )

        # -------------------------------------------------------------
        # Run exactly the same block as the real experiment
        # -------------------------------------------------------------

        block_results = (
            urn_task.run_urn_visual_test(
                block_number=block_number,
                total_blocks=self.n_blocks,
                deterministic_value=deterministic_value,
                ambiguous_condition=ambiguous_condition,
                training=True,
            )
        )

        # -------------------------------------------------------------
        # Update the training staircase
        # -------------------------------------------------------------

        selected_urn_type = (
            block_results[
                "selected_urn_type"
            ]
        )

        self.staircases[
            ambiguous_condition
        ] = (
            urn_task.update_staircase(
                staircase=staircase,
                choice=selected_urn_type,
            )
        )

        # -------------------------------------------------------------
        # Add training information to results
        # -------------------------------------------------------------

        block_results[
            "training_block"
        ] = True

        block_results[
            "training_block_number"
        ] = block_number

        block_results[
            "training_condition"
        ] = ambiguous_condition

        block_results[
            "training_deterministic_value"
        ] = deterministic_value

        block_results[
            "training_next_deterministic_value"
        ] = (
            self.staircases[
                ambiguous_condition
            ][
                "value"
            ]
        )

        self.all_results.append(
            block_results
        )

    # -----------------------------------------------------------------
    # Run complete training
    # -----------------------------------------------------------------

    def run(self):

        print(
            "\n"
            + "=" * 70
        )

        print(
            "STARTING TRAINING TASK"
        )

        print(
            "=" * 70
        )

        print(
            "Training condition schedule:",
            self.condition_schedule,
        )

        print(
            "=" * 70
            + "\n"
        )

        for block_number in range(
            1,
            self.n_blocks + 1,
        ):

            self.run_block(
                block_number=block_number
            )

        print(
            "\n"
            + "=" * 70
        )

        print(
            "TRAINING COMPLETE"
        )

        print(
            "=" * 70
            + "\n"
        )

        return self.all_results


# ---------------------------------------------------------------------
# Run training directly
# ---------------------------------------------------------------------

if __name__ == "__main__":

    training = TrainingTask(
        n_blocks=5,
        starting_value=2.00,
    )

    results = training.run()

    print(
        results
    )