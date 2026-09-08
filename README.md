# Ambiguity Task

A PsychoPy prototype for piloting an experiment on learning and choice under ambiguity.

Participants choose between a **deterministic urn** with a fixed monetary value and an **ambiguous urn** whose payoff depends on prediction performance.

For the ambiguous urn, the next ball depends on a repeating hidden sequence. In one condition, participants are told how many previous draws are relevant (`k`); in the other condition, `k` is unkown.

After making predictions, participants reconstruct the hidden sequence and answer questions about confidence, liking, difficulty, and mental effort.


## Current experiment flow

The main experiment is run from `main.py`.

In each block:

1. One deterministic urn and one ambiguous urn are created.
2. The deterministic urn has a fixed monetary value.
3. The ambiguous urn belongs to one of two conditions:
   - **Known `k`**: the participant is told how many previous draws are relevant.
   - **Unknown `k`**: the participant is not told how many previous draws are relevant.
4. The two urns are randomly assigned to the left and right sides of the screen.
5. The participant chooses one urn.
6. The participant completes 20 blue/magenta prediction trials using the selected urn.
7. Most outcomes follow the hidden sequence, while a proportion of trials contain noise.
8. After the final prediction, the participant can inspect the complete observed sequence before continuing.
9. The participant receives feedback about the completed block.
10. Post-block questions are presented.

The deterministic value is adjusted across blocks using a staircase procedure.

Separate staircases are maintained for the known-`k` and unknown-`k` ambiguous conditions.

---

## Training task

A separate training version is available in:

`training_task.py`

The training task follows the same general structure as the main experiment but contains only **5 blocks**.

The training phase is intended to familiarize participants with:

- choosing between the two urns
- making blue/magenta predictions
- observing the sequence history
- reconstructing the hidden sequence
- answering the post-block questions

Performance during the training phase does **not** contribute to the participant's final earnings.

---

## Requirements

- Windows, macOS, or Linux
- Python 3.10
- PsychoPy
- A keyboard
- A display with OpenGL support

The current development environment uses:

```text
Python 3.10.20
```
---
## Running the experiment

To run the experiment locally:

1. Open the repository in **Visual Studio Code**.
2. Open a terminal in VS Code.
3. Create a Conda environment with Python 3.10:

```bash
conda create -n ambiguity-task python=3.10
```
4. Activate the environment:
```bash
conda activate ambiguity-task
```

5.Install the required packages:
```bash
pip install -r requirements.txt
```
6. Run the main experiment:
```bash
python main.py
```

Important: The current main experiment runs 5 blocks, with 20 prediction trials per block. To change this, go to urn_params.py and change N_TRIALS_PER_BLOCK and N_BLOCKS
## Running the training task

python training_task.py