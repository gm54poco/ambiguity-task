from pathlib import Path


# -----------------------------------------------------------------------------
# Trial settings
# -----------------------------------------------------------------------------
MONITOR_NAME="wahrnehmen_monitor"
# 20 ball-color predictions in each round
N_TRIALS_PER_ROUND = 20

# 18 rounds in the main experiment
N_ROUNDS = 2

# 3 staircase blocks, each containing 6 rounds
ROUNDS_PER_BLOCK = 6
N_BLOCKS = N_ROUNDS // ROUNDS_PER_BLOCK

#Explanation sizes
TITLE_HEIGHT = 0.055
BODY_HEIGHT = 0.032

# -----------------------------------------------------------------------------
# Monetary rewards
# -----------------------------------------------------------------------------

REWARD_PER_CORRECT_GUESS = 4 #if euros: 0.20

MAX_AMBIGUOUS_REWARD = (
    N_TRIALS_PER_ROUND
    * REWARD_PER_CORRECT_GUESS
)

# Always show the same number of initial balls, regardless of k.
#
# This prevents the participant from inferring k simply from the number
# of balls visible before prediction trial 1.
N_INITIAL_DRAWS = 0


# The latent rule is followed on exactly this proportion of prediction trials.
PATTERN_PROBABILITY = 0.85 # 3 random

RANDOM_PROBABILITY = (
    1.0 - PATTERN_PROBABILITY
)

N_RANDOM_DRAWS =(
    N_TRIALS_PER_ROUND
    - int(
        N_TRIALS_PER_ROUND
        * PATTERN_PROBABILITY
    )
)
GUESS_KEYS = {
    "b": "blue",
    "m": "magenta",
}


GUESS_PROMPT = "Guess the next ball:"

REVEAL_DURATION = 0.01
INTER_TRIAL_INTERVAL = 0.01


# -----------------------------------------------------------------------------
# Cycle / ambiguity settings
# -----------------------------------------------------------------------------

BALL_COLORS = [
    "blue",
    "magenta",
]
# Colors displayed to participants
BALL_BLUE = "#5379B8"
BALL_MAGENTA = "#B966A8"

BALL_DISPLAY_COLORS = {
    "blue": BALL_BLUE,
    "magenta": BALL_MAGENTA,
}

def ball_display_color(color):
    return BALL_DISPLAY_COLORS.get(color, color)


# For now the experiment uses 1-, 2- and 3-cycle rules.
AMBIGUOUS_K_OPTIONS = [
    1,
    2,
    3,
]


CONDITION_KNOWN_X_UNKNOWN_F = "known_k"
CONDITION_UNKNOWN_X_UNKNOWN_F = "unknown_k"


# k refers to how many previous draws are relevant for predicting
# the next ball.
#
# Participants are NOT explicitly told that the latent structure
# is a repeating k-cycle.


KNOWN_X_DESCRIPTION = (
    "Sequence length: {k}"
)


UNKNOWN_X_DESCRIPTION = (
    "Sequence length: less than 4"
)


# -----------------------------------------------------------------------------
# Experiment settings
# -----------------------------------------------------------------------------

EXPERIMENT_NAME = "k-cycle-pretty-urn-task"

WINDOW_SIZE = [1920, 1080]
FULLSCREEN = True
SCREEN_INDEX = 0

BACKGROUND_COLOR = "lightgrey"

TEXT_COLOR = "black"

CORRECT_TEXT_COLOR = "darkgreen"
INCORRECT_TEXT_COLOR = "darkred"

DATA_FOLDER = "data"


BASE_DIR = Path(__file__).resolve().parent

PRETTY_URNS_DIR = (
    BASE_DIR
    / "assets"
    / "pretty_urns"
)


# -----------------------------------------------------------------------------
# Urn display settings
# -----------------------------------------------------------------------------

URN_LEFT_POS = (
    -0.35,
    0.02,
)

URN_RIGHT_POS = (
    0.35,
    0.02,
)


URN_IMAGE_SIZE = (
    0.32,
    0.32,
)


CLICK_AREA_WIDTH = 0.38
CLICK_AREA_HEIGHT = 0.38


LABEL_Y_OFFSET = 0.24
LABEL_HEIGHT = 0.04


LEFT_URN_LABEL = "LEFT"
RIGHT_URN_LABEL = "RIGHT"


# During prediction trials the selected urn is enlarged and moved down.
SELECTED_URN_POS = (
    0.0,
    -0.50,
)

SELECTED_URN_SIZE = (
    0.62,
    0.62,
)


PRETTY_URN_NAMES = [
    "urn_blue",
    "urn_dark_green",
    "urn_flower",
    "urn_green",
    "urn_pink",
    "urn_tree",
    "urn_yellow",
]


# -----------------------------------------------------------------------------
# General instructions
# -----------------------------------------------------------------------------
TRAINING_INSTRUCTIONS = (
    "Training Phase\n\n"
    "You will now complete practice rounds.\n\n"
    "Practice results do not affect your final earnings.\n\n"
    "Press SPACE to begin."
)

URN_INSTRUCTIONS = (
    f"Each round has {N_TRIALS_PER_ROUND} balls that are either blue (B) or magenta (M).\n"
    f"Exactly {N_RANDOM_DRAWS} are surprise balls; the others follow a sequence.\n\n\n\n"
    "Press SPACE to continue."
)


SELECT_INSTRUCTIONS = (
    "Choose an urn"
)


SELECTION_BOTTOM_TEXT = (
    "Press ESC to quit."
)


SELECTED_URN_TEXT = (
    "You selected {urn_label}."
)


SELECTED_URN_CONTINUE_TEXT = (
    "Press SPACE to continue."
)


# -----------------------------------------------------------------------------
# Condition-specific trial instructions
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Trial instructions
# -----------------------------------------------------------------------------

# Deterministic urn
REWARD_LABEL = ("Reward:")
DETERMINISTIC_REWARD_VALUE = (
    "{value} points"
)

RANDOM_BALLS_LABEL = (
    "Random balls:"
)

GUESS_KEYS_TEXT = ( 
    "[B] BLUE            [M] MAGENTA"
)


# Ambiguous urn
AMBIGUOUS_REWARD_VALUE = (
    "{reward_per_correct} pts/correct • max {max_reward} pts"
)

SEQUENCE_LENGTH_LABEL = (
    "Sequence length:"
)

KNOWN_SEQUENCE_LENGTH_VALUE = (
    "{k}"
)

UNKNOWN_SEQUENCE_LENGTH_VALUE = (
    "less than 4"
)


# -----------------------------------------------------------------------------
# Appearance Likert rating
# -----------------------------------------------------------------------------

LIKERT_VALUES = [
    1,
    2,
    3,
    4,
    5,
]


LIKERT_KEYS = [
    "1",
    "2",
    "3",
    "4",
    "5",
    "num_1",
    "num_2",
    "num_3",
    "num_4",
    "num_5",
]


LIKERT_TITLE_POS = (
    0,
    0.42,
)

LIKERT_TITLE_HEIGHT = 0.045


LIKERT_URN_POS = (
    0.0,
    0.12,
)


LIKERT_X_POSITIONS = [
    -0.48,
    -0.24,
    0.00,
    0.24,
    0.48,
]


LIKERT_CIRCLE_Y = -0.18
LIKERT_CIRCLE_RADIUS = 0.055


LIKERT_CIRCLE_COLOR = "#1f6fb2"
LIKERT_CIRCLE_LINE_COLOR = "black"


LIKERT_NUMBER_COLOR = "white"
LIKERT_NUMBER_HEIGHT = 0.055


LIKERT_LABEL_Y = -0.32
LIKERT_LABEL_HEIGHT = 0.028
LIKERT_LABEL_WRAP_WIDTH = 0.20


LIKERT_LABELS = [
    "Do not like\nit at all",
    "Slightly\nlike it",
    "Moderately\nlike it",
    "Like it\nvery much",
    "Like it\nextremely",
]


LIKERT_BOTTOM_TEXT = (
    "Click one circle or press a number from 1 to 5. "
    "Press ESC to quit."
)


LIKERT_BOTTOM_TEXT_POS = (
    0,
    -0.44,
)

LIKERT_BOTTOM_TEXT_HEIGHT = 0.03


# -----------------------------------------------------------------------------
# Selection-screen condition text
# -----------------------------------------------------------------------------

CONDITION_TEXT_Y = -0.28
CONDITION_TEXT_HEIGHT = 0.024
CONDITION_TEXT_WRAP_WIDTH = 0.42


# -----------------------------------------------------------------------------
# Prediction-trial display
# -----------------------------------------------------------------------------

TRIAL_COUNTER_POS = (
    0.58,
    0.44,
)

TRIAL_COUNTER_HEIGHT = 0.032


TRIAL_INSTRUCTION_POS = (
    0,
    0.35,
)

TRIAL_INSTRUCTION_HEIGHT = 0.027
TRIAL_INSTRUCTION_WRAP_WIDTH = 1.15


GUESS_PROMPT_POS = (
    0,
    0.025,
)

GUESS_PROMPT_HEIGHT = 0.037


OUTCOME_BALL_POS = (
    0,
    -0.10,
)

OUTCOME_BALL_RADIUS = 0.055


RESULT_TEXT_POS = (
    0,
    0.035,
)

RESULT_TEXT_HEIGHT = 0.040


# -----------------------------------------------------------------------------
# Horizontal divider lines
# -----------------------------------------------------------------------------

TOP_DIVIDER_Y = 0.225
BOTTOM_DIVIDER_Y = 0.065

DIVIDER_WIDTH = 0.72

DIVIDER_LINE_COLOR = "#b5b5b5"
DIVIDER_LINE_WIDTH = 1.5


# -----------------------------------------------------------------------------
# Sequence feedback
# -----------------------------------------------------------------------------

SEQUENCE_TITLE = "Draw history:"


SEQUENCE_TITLE_POS = (
    -0.55,
    0.2,
)

SEQUENCE_TITLE_HEIGHT = 0.028


FEEDBACK_START_X = -0.22
FEEDBACK_START_Y = 0.195


FEEDBACK_SPACING_X = 0.048
FEEDBACK_SPACING_Y = 0.050


FEEDBACK_BALL_RADIUS = 0.02

FEEDBACK_BALLS_PER_ROW = 10

#####STAIRCASE PARAMETERS#####
# ONE shared staircase for all known/unknown conditions.
# 20 trials x 4 points = 80-point maximum possible variable reward.
STAIRCASE_INITIAL_VALUE = round(MAX_AMBIGUOUS_REWARD*0.7)
STAIRCASE_MIN_VALUE = 0
STAIRCASE_MAX_VALUE = MAX_AMBIGUOUS_REWARD
STAIRCASE_STEP_SIZES = (4,8)

# Opt in to the separate guided practice before the 18 actual blocks.
RUN_PRACTICE_BEFORE_MAIN = True

# Practice-style animation parameters for the MAIN urn task.
REVEAL_BALL_RADIUS = 0.12
REVEAL_START_HEIGHT_FRACTION = 0.35
RISE_FRAMES = 1
FLIP_HALF_FRAMES = 2
HISTORY_FRAMES = 1

# Practice-style minimalist display.

# Practice-style minimalist display.
INFO_LABEL_X = -0.66
INFO_BALL_START_X = -0.46

# Row positions
URN_TYPE_Y = 0.422
INFO_ROW_Y = (0.374, 0.326)

# Urn type description alignment
URN_TYPE_VALUE_OFFSET_X = -0.01

INFO_TEXT_HEIGHT = 0.019
INFO_BALL_RADIUS = 0.007
INFO_BALL_SPACING = 0.023
INFO_COLOR = "#253f62"
INFO_EMPTY_COLOR = "#536e8c"

SCORE_BAR_LEFT_X = -0.62
SCORE_BAR_RIGHT_X = 0.45
SCORE_BAR_Y = 0.26
SCORE_BAR_HEIGHT = 0.035
SCORE_ACCURACY_X = 0.58
REMINDER_AFTER = 3.0