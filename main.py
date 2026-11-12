"""Run thesis experiment in order, using one PsychoPy window throughout.

Order: demographics -> consent -> baseline fatigue -> practice -> 18 urn rounds
       -> final fatigue -> IQ -> TAS-20 -> closing message.

Integration requirements:
- iq_task.run_iq_task(win=win, participant=info, test_mode=test_mode)
- tas20_task.run_tas20(participant=info, win=win, test_mode=test_mode)
Both tasks must return without closing the shared window or calling core.quit().
"""

from psychopy import event, visual

import urn_params as params
import participant_info
import consent_task
import fatigue_task
import training_task
import experiment_schedule
import urn_task
import save_data


def show_welcome_screen(win):
    """Display a neutral introduction to the experiment."""
    event.clearEvents()

    visual.TextStim(
        win=win,
        text="Welcome!",
        pos=(0, 0.16),
        height=0.055,
        bold=True,
        color="#172b49",
    ).draw()

    visual.TextStim(
        win=win,
        text=(
            "Thank you for participating in this study.\n\n"
            "You will complete a series of computer-based tasks "
            "involving choices, guessing, and questionnaires.\n\n"
            "Please read the instructions carefully and "
            "complete the tasks."
        ),
        pos=(0, -0.015),
        height=0.027,
        wrapWidth=1.25,
        color="#576a82",
        alignText="center",
    ).draw()

    visual.TextStim(
        win=win,
        text="Press SPACE to continue.",
        pos=(0, -0.32),
        height=0.025,
        color="#576a82",
    ).draw()

    win.flip()
    event.waitKeys(keyList=["space"])

def show_closing_screen(win):
    """Display the end-of-experiment message until the participant presses SPACE."""
    event.clearEvents()
    visual.TextStim(
        win=win,
        text="This concludes our experiment. Thank you for participating!",
        pos=(0, 0.05), height=0.045, wrapWidth=1.30,
        bold=True, color="#172b49", alignText="center",
    ).draw()
    visual.TextStim(
        win=win,
        text="Press SPACE to finish.",
        pos=(0, -0.24), height=0.025, color="#576a82",
    ).draw()
    win.flip()
    event.waitKeys(keyList=["space"])


def run_main_urn_rounds(win, participant_id, writer):
    """Run the balanced 18-round design, updating one shared staircase."""
    schedule = experiment_schedule.create_balanced_schedule()
    
    staircase = {
        "value": params.STAIRCASE_INITIAL_VALUE,
        "previous_choice": None,
    }

    results = []

    for assigned in schedule:

        # Compatibility with the current experiment_schedule.py:
        # its "block_number" currently identifies an individual round.
        round_number = assigned["block_number"]

        # Convert rounds 1–18 into blocks 1–3.
        block_number = (
            (round_number - 1) // params.ROUNDS_PER_BLOCK
        ) + 1

        offered = staircase["value"]

        result = urn_task.run_urn_visual_test(
            round_number=round_number,
            total_rounds=params.N_ROUNDS,
            deterministic_value=offered,
            ambiguous_condition=assigned["condition"],
            k=assigned["k"],
            win=win,
        )

        # Save both identifiers in the internal results.
        result["round_number"] = round_number
        result["block_number"] = block_number

        selected = result["selected_urn_type"]

        # Update the deterministic offer for the next round.
        urn_task.update_staircase(
            staircase,
            selected,
            round_number,
            k_value=assigned["k"],
        )

        # Build the three raw-data CSV outputs.
        choice_row, guessing_rows, post_row = (
            save_data.build_csv_rows(
                result,
                assigned,
                participant_id,
                staircase,
            )
        )

        writer.write_rows("urn_reward_choice", [choice_row])
        writer.write_rows("guessing_balls", guessing_rows)
        writer.write_rows("post_block_questions", [post_row])

        results.append(result)

        print(
            f"Completed block {block_number}/{params.N_BLOCKS}, "
            f"round {round_number}/{params.N_ROUNDS} | "
            f"condition={assigned['condition']} | "
            f"k={assigned['k']} | "
            f"choice={selected} | "
            f"D={offered} -> {staircase['value']}"
        )

    return results



def show_total_reward(win, total_points):
    """Show accumulated reward after the urn task."""
    event.clearEvents()

    visual.TextStim(
        win=win,
        text="Urn task completed!",
        pos=(0, 0.20),
        height=0.050,
        bold=True,
        color="#172b49",
    ).draw()

    visual.TextStim(
        win=win,
        text="Your total reward",
        pos=(0, 0.06),
        height=0.030,
        color="#576a82",
    ).draw()

    visual.TextStim(
        win=win,
        text=f"{total_points:g} points",
        pos=(0, -0.04),
        height=0.065,
        bold=True,
        color="#172b49",
    ).draw()

    visual.TextStim(
        win=win,
        text="Press SPACE to continue.",
        pos=(0, -0.30),
        height=0.025,
        color="#576a82",
    ).draw()

    win.flip()
    event.waitKeys(keyList=["space"])

def main():
    info = participant_info.collect_participant_info()
    participant_id = str(info["participant_id"])
    test_mode = bool(info["test_run"])

    # Refuse to overwrite an earlier session before opening the window.
    if not test_mode:
        folder = params.BASE_DIR / params.DATA_FOLDER / participant_id
        expected = [folder / f"{stem}.csv" for stem in save_data.CSV_COLUMNS]
        expected += [folder / "consent.json", folder / "fatigue.json"]
        if any(path.exists() for path in expected):
            raise FileExistsError(f"Existing experiment data for participant {participant_id}")
    else:
        print("TEST MODE — participant info:", info)

    # Uses the same display settings as your existing main. Optional parameters
    # below should be defined in urn_params.py when needed.
    window_options = {
        "size": params.WINDOW_SIZE,
        "fullscr": params.FULLSCREEN,
        "color": params.BACKGROUND_COLOR,
        "units": "height",
        "gammaErrorPolicy": "warn",
    }
    if hasattr(params, "MONITOR_NAME"):
        window_options["monitor"] = params.MONITOR_NAME
    if hasattr(params, "SCREEN_INDEX"):
        window_options["screen"] = params.SCREEN_INDEX

    win = visual.Window(**window_options)
    try:
        show_welcome_screen(win)
        # 1. Consent
        consent = consent_task.run_consent(win)
        if not consent["consented"]:
            print("Consent declined; no study files were saved.")
            return []

        if not test_mode:
            participant_info.save_participant_info(info)
        consent_task.save_consent_record(info, consent, test_mode=test_mode)
        writer = save_data.ResultWriter(participant_id, test_mode)

        # 2. Baseline fatigue
        fatigue_before = fatigue_task.ask_fatigue(win)
        fatigue_task.save_fatigue_response(
            participant_id, "before_practice", fatigue_before, test_mode
        )

        # 3. Practice
        if params.RUN_PRACTICE_BEFORE_MAIN:
            training_task.run_training(win=win)

        # 4. Main experiment
        results = run_main_urn_rounds(win, participant_id, writer)
        total_points = sum(result["block_earnings"] for result in results)
        show_total_reward(win, total_points)
        # 5. Post-experiment fatigue
        fatigue_after = fatigue_task.ask_fatigue(win)
        fatigue_task.save_fatigue_response(
            participant_id, "after_main", fatigue_after, test_mode
        )

        # 6. IQ questionnaire (must accept and reuse win, participant, test_mode)
        import iq_task
        iq_task.run_iq_task(win=win, participant=info, test_mode=test_mode)

        # 7. TAS-20 (must accept and reuse win, participant, test_mode)
        import tas20_task
        tas20_task.run_tas20(participant=info, win=win, test_mode=test_mode)

        # 8. Thank-you screen
        show_closing_screen(win)
        print(f"Experiment completed for participant {participant_id}.")
        if not test_mode:
            print("Urn-task CSV files saved to:", writer.data_dir)
        return results
    finally:
        urn_task._clear_visual_cache(win)
        win.close()


if __name__ == "__main__":
    main()
