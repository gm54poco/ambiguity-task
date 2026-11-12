"""Write raw urn-task data with block/round/trial identifiers.

Terminology:
- Block: six consecutive urn-choice rounds with one staircase step size.
- Round: urn choice, guessing trials, and post-round questions.
- Trial: one ball-color prediction.

The CSVs deliberately exclude derived accuracy, reconstruction-correctness,
staircase reversals, and duplicate questionnaire response columns.
"""

import csv
import io
import json

import urn_params as params


CSV_COLUMNS = {
    "urn_reward_choice": [
        "participant_id",
        "block_number",
        "round_number",
        "k_condition",
        "k_value",
        "chosen_urn",
        "reward_deterministic",
        "reaction_time",
        "chosen_side",
        "chosen_earnings",
        "selected_cycle",
    ],
    "guessing_balls": [
        "participant_id",
        "block_number",
        "round_number",
        "trial_number",
        "k_condition",
        "k_value",
        "ball_color",
        "guess",
        "noise",
        "reaction_time",
        "chosen_urn",
        "latent_pattern_color",
        "latent_cycle",
        "prediction_index",
    ],
    "post_block_questions": [
        "participant_id",
        "block_number",
        "round_number",
        "k_condition",
        "chosen_urn",
        "confidence_response",
        "liking_response",
        "difficulty_response",
        "mental_effort_response",
        "estimated_k",
        "estimated_cycle",
        "actual_k",
        "actual_cycle",
        "other_responses_json",
    ],
}

# Compatibility with main.py versions that still call write_rows("learning", ...).
# The actual filename is always guessing_balls.csv.
_STEM_ALIASES = {"learning": "guessing_balls"}


def _cycle_text(value):
    """Store sequence colors consistently without changing their order."""
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return "-".join(str(color) for color in value)
    return str(value)


def _binary(value):
    """Represent whether the experimental noise flip occurred as 0 or 1."""
    return int(bool(value))


class ResultWriter:
    """Save CSV rows after each completed round, or print them in test mode."""

    def __init__(self, participant_id, test_mode=False):
        self.participant_id = str(participant_id)
        self.test_mode = bool(test_mode)
        self.data_dir = (
            params.BASE_DIR / params.DATA_FOLDER / self.participant_id
        )

        if self.test_mode:
            print("\nTEST RUN: no urn-task CSV files will be saved.\n")
            for stem, fields in CSV_COLUMNS.items():
                print(f"\n--- {stem}.csv: columns ---")
                print(",".join(fields))
            return

        existing = [
            self.data_dir / f"{stem}.csv"
            for stem in CSV_COLUMNS
            if (self.data_dir / f"{stem}.csv").exists()
        ]
        if existing:
            raise FileExistsError(
                "Data already exists for participant "
                + self.participant_id
                + ": "
                + ", ".join(str(path) for path in existing)
            )

        self.data_dir.mkdir(parents=True, exist_ok=True)
        for stem, fields in CSV_COLUMNS.items():
            with (self.data_dir / f"{stem}.csv").open(
                "x", newline="", encoding="utf-8-sig"
            ) as handle:
                csv.DictWriter(handle, fieldnames=fields).writeheader()

    def write_rows(self, stem, rows):
        """Write only schema columns; reject accidentally misspelled fields."""
        stem = _STEM_ALIASES.get(stem, stem)
        if stem not in CSV_COLUMNS:
            raise KeyError(f"Unknown CSV output: {stem}")

        if not rows:
            return

        fields = CSV_COLUMNS[stem]
        extra_fields = set().union(*(set(row) for row in rows)) - set(fields)
        if extra_fields:
            raise ValueError(
                f"Unexpected fields for {stem}.csv: {sorted(extra_fields)}"
            )

        if self.test_mode:
            print(f"\n--- {stem}.csv: {len(rows)} row(s) ---")
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=fields)
            writer.writerows(rows)
            print(output.getvalue().strip())
        else:
            with (self.data_dir / f"{stem}.csv").open(
                "a", newline="", encoding="utf-8"
            ) as handle:
                csv.DictWriter(handle, fieldnames=fields).writerows(rows)
                handle.flush()


def build_csv_rows(result, assignment, participant_id,
                   staircase=None, reversed_choice=None):
    """Convert one completed round into choice, trial, and question rows.

    Compatible with the older main.py call signature. The older schedule's
    assignment["block_number"] actually refers to an urn-choice ROUND.
    The staircase and reversal arguments are intentionally not saved.
    """
    round_number = int(
        result.get("round_number", assignment["block_number"])
    )
    rounds_per_block = params.ROUNDS_PER_BLOCK
    block_number = (round_number - 1) // rounds_per_block + 1

    condition = assignment["condition"]
    k_value = assignment["k"]
    chosen_urn = result["selected_urn_type"]
    actual_cycle = _cycle_text(result["selected_cycle"])
    participant_id = str(participant_id)

    choice_row = {
        "participant_id": participant_id,
        "block_number": block_number,
        "round_number": round_number,
        "k_condition": condition,
        "k_value": k_value,
        "chosen_urn": chosen_urn,
        "reward_deterministic": result["deterministic_value"],
        "reaction_time": result["urn_choice_rt"],
        "chosen_side": result["selected_side"],
        "chosen_earnings": result["block_earnings"],
        "selected_cycle": actual_cycle,
    }

    guessing_rows = []
    for trial in result["trial_data"]:
        guessing_rows.append({
            "participant_id": participant_id,
            "block_number": block_number,
            "round_number": round_number,
            "trial_number": trial["trial_number"],
            "k_condition": condition,
            "k_value": k_value,
            "ball_color": trial["outcome"],
            "guess": trial["guess"],
            "noise": _binary(trial["is_noise_trial"]),
            "reaction_time": trial["response_time"],
            "chosen_urn": chosen_urn,
            "latent_pattern_color": trial["pattern_prediction"],
            "latent_cycle": actual_cycle,
            "prediction_index": trial["prediction_index"],
        })

    questions = result.get("question_results") or {}
    post_row = {
        "participant_id": participant_id,
        "block_number": block_number,
        "round_number": round_number,
        "k_condition": condition,
        "chosen_urn": chosen_urn,
        "confidence_response": questions.get("confidence"),
        "liking_response": questions.get("liking"),
        "difficulty_response": questions.get("difficulty"),
        "mental_effort_response": questions.get("mental_effort"),
        "estimated_k": questions.get("estimated_k"),
        "estimated_cycle": _cycle_text(questions.get("estimated_cycle")),
        "actual_k": k_value,
        "actual_cycle": actual_cycle,
        "other_responses_json": json.dumps(
            questions, ensure_ascii=False, default=str
        ),
    }

    return choice_row, guessing_rows, post_row
