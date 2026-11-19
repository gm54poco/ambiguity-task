# -----------------------------------------------------------------------------
# Response keys
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


K_RESPONSE_KEYS = {
    "1": 1,
    "2": 2,
    "3": 3,
    "num_1": 1,
    "num_2": 2,
    "num_3": 3,
}


# -----------------------------------------------------------------------------
# Estimated-k question
# -----------------------------------------------------------------------------

K_QUESTION = (
    "What is the length of the sequence?\n\n"
)


K_QUESTION_POS = (
    0,
    0.18,
)

K_QUESTION_HEIGHT = 0.038

K_QUESTION_WRAP_WIDTH = 1.10


# -----------------------------------------------------------------------------
# Cycle reconstruction
# -----------------------------------------------------------------------------

CYCLE_QUESTION = (
    "What was the sequence?"
)


CYCLE_INSTRUCTION_KNOWN = (
    "[B] Blue        [M] Magenta        [⌫] Delete last        [SPACE] Done"
)


CYCLE_INSTRUCTION_UNKNOWN = (
    "[B] Blue        [M] Magenta        [⌫] Delete last        [SPACE] Done"
)


# Maximum number of balls that can be entered when k was not disclosed.
MAX_CYCLE_RESPONSE_LENGTH = 4


CYCLE_QUESTION_POS = (
    0,
    0.30,
)

CYCLE_QUESTION_HEIGHT = 0.040

CYCLE_QUESTION_WRAP_WIDTH = 1.20


CYCLE_BALL_Y = 0.02

CYCLE_BALL_RADIUS = 0.04

CYCLE_BALL_SPACING = 0.12


CYCLE_INSTRUCTION_POS = (
    0,
    -0.22,
)

CYCLE_INSTRUCTION_HEIGHT = 0.026


CYCLE_ERROR_POS = (
    0,
    -0.34,
)

CYCLE_ERROR_HEIGHT = 0.025


# -----------------------------------------------------------------------------
# Remaining questions
# -----------------------------------------------------------------------------

CONFIDENCE_QUESTION = (
    "How confident are you in the pattern you just gave?"
)


LIKING_QUESTION = (
    "How much did you like this round?"
)


DIFFICULTY_QUESTION = (
    "How difficult was it to understand this round?"
)


EFFORT_QUESTION = (
    "How mentally demanding was this round?"
)


# -----------------------------------------------------------------------------
# Likert labels
# -----------------------------------------------------------------------------

CONFIDENCE_LABELS = [
    "Not at all\nconfident",
    "Slightly\nconfident",
    "Moderately\nconfident",
    "Very\nconfident",
    "Extremely\nconfident",
]


LIKING_LABELS = [
    "Did not like\nit at all",
    "Slightly\nliked it",
    "Moderately\nliked it",
    "Liked it\nvery much",
    "Liked it\nextremely",
]


DIFFICULTY_LABELS = [
    "Very easy",
    "Easy",
    "Moderate",
    "Difficult",
    "Very difficult",
]


EFFORT_LABELS = [
    "Not at all\ndemanding",
    "Slightly\ndemanding",
    "Moderately\ndemanding",
    "Very\ndemanding",
    "Extremely\ndemanding",
]


# -----------------------------------------------------------------------------
# General Likert layout
# -----------------------------------------------------------------------------

QUESTION_POS = (
    0,
    0.30,
)

QUESTION_HEIGHT = 0.040

QUESTION_WRAP_WIDTH = 1.20


LIKERT_Y = -0.05


LIKERT_X_POSITIONS = [
    -0.40,
    -0.20,
    0.00,
    0.20,
    0.40,
]


LIKERT_RADIUS = 0.045


LABEL_Y = -0.18

LABEL_HEIGHT = 0.026

LABEL_WRAP_WIDTH = 0.16


# -----------------------------------------------------------------------------
# Bottom text
# -----------------------------------------------------------------------------

BOTTOM_TEXT_POS = (
    0,
    -0.38,
)

BOTTOM_TEXT_HEIGHT = 0.028