from pathlib import Path


# -----------------------------------------------------------------------------
# Trial settings
# -----------------------------------------------------------------------------

# Number of prediction trials after the initial displayed draws.
N_TRIALS_PER_BLOCK = 20
N_BLOCKS = 5
# -----------------------------------------------------------------------------
# Monetary rewards
# -----------------------------------------------------------------------------

REWARD_PER_CORRECT_GUESS = 0.20

MAX_AMBIGUOUS_REWARD = (
    N_TRIALS_PER_BLOCK
    * REWARD_PER_CORRECT_GUESS
)

# Always show the same number of initial balls, regardless of k.
#
# This prevents the participant from inferring k simply from the number
# of balls visible before prediction trial 1.
N_INITIAL_DRAWS = 0


# The latent rule is followed on exactly this proportion of prediction trials.
PATTERN_PROBABILITY = 0.80

RANDOM_PROBABILITY = (
    1.0 - PATTERN_PROBABILITY
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


# For now the experiment uses 2- and 3-cycle rules.
AMBIGUOUS_K_OPTIONS = [
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
    "The next ball depends on the previous {k} draws."
)


UNKNOWN_X_DESCRIPTION = (
    "The next ball depends on previous draws.\n"
    "You are not told how many draws are relevant."
)


# -----------------------------------------------------------------------------
# Experiment settings
# -----------------------------------------------------------------------------

EXPERIMENT_NAME = "k-cycle-pretty-urn-task"

WINDOW_SIZE = [1200, 800]
FULLSCREEN = False

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


LEFT_URN_LABEL = "Urn A"
RIGHT_URN_LABEL = "Urn B"


# During prediction trials the selected urn is enlarged and moved down.
SELECTED_URN_POS = (
    0.0,
    -0.50,
)

SELECTED_URN_SIZE = (
    0.72,
    0.72,
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
    "You will now complete 5 practice blocks.\n\n"
    "Your performance in these blocks "
    "will NOT affect your final score or earnings.\n\n"
    "Press SPACE to begin."
)

URN_INSTRUCTIONS = (
    "You will play a game in which you will repeatedly draw balls from an urn you have previously chosen.\n\n"
    "Each urn contains 20 balls that are either blue or magenta.\n\n"
    "Your draws should mostly follow a sequence, but occasionally "
    "a random color will come up.\n\n\n\n"#add correct/incorrect explanation here?

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

KNOWN_X_TRIAL_INSTRUCTION = (
    "The next ball depends on the previous {k} draws.\n"
    "The exact rule is unknown.\n"
    "(B = Blue, M = Magenta)"
)


UNKNOWN_X_TRIAL_INSTRUCTION = (
    "The next ball depends on previous draws.\n"
    "You are not told how many previous draws are relevant.\n"
    "The exact rule is unknown.\n"
    "(B = Blue, M = Magenta)"
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
    0.035,
)

GUESS_PROMPT_HEIGHT = 0.037


OUTCOME_BALL_POS = (
    0,
    -0.06,
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

TOP_DIVIDER_Y = 0.275
BOTTOM_DIVIDER_Y = 0.115

DIVIDER_WIDTH = 0.72

DIVIDER_LINE_COLOR = "#b5b5b5"
DIVIDER_LINE_WIDTH = 1.5


# -----------------------------------------------------------------------------
# Sequence feedback
# -----------------------------------------------------------------------------

SEQUENCE_TITLE = "Draw history:"


SEQUENCE_TITLE_POS = (
    -0.25,
    0.195,
)

SEQUENCE_TITLE_HEIGHT = 0.028


FEEDBACK_START_X = -0.15
FEEDBACK_START_Y = 0.242


FEEDBACK_SPACING_X = 0.05
FEEDBACK_SPACING_Y = 0.050


FEEDBACK_BALL_RADIUS = 0.02

FEEDBACK_BALLS_PER_ROW = 10