# params.py

# -----------------------------
# General experiment settings
# -----------------------------

EXPERIMENT_NAME = "ambiguity-task"

WINDOW_SIZE = [1200, 800]
FULLSCREEN = False
BACKGROUND_COLOR = "white"
TEXT_COLOR = "black"

DATA_FOLDER = "data"


# -----------------------------
# TAS-20 settings
# -----------------------------
TAS20_KEYS = [
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
TAS20_SCALE = {
    1: "Strongly disagree",
    2: "Disagree",
    3: "Neither agree nor disagree",
    4: "Agree",
    5: "Strongly agree",
}

# TAS-20 has 20 items.
TAS20_ITEMS = [
    {"id": 1, "text": "I am often confused about what emotion I am feeling.", "reverse": False},
    {"id": 2, "text": "It is difficult for me to find the right words for my feelings.", "reverse": False},
    {"id": 3, "text": "I have physical sensations that even doctors don\'t understand.", "reverse": False},
    {"id": 4, "text": "I am able to describe my feelings easily.", "reverse": True},
    {"id": 5, "text": "I prefer to analyze problems rather than just describe them.", "reverse": True},
    {"id": 6, "text": "When I am upset, I don\'t know if I am sad, frightened, or angry.", "reverse": False},
    {"id": 7, "text": "I am often puzzled by sensations in my body.", "reverse": False},
    {"id": 8, "text": "I prefer to just let things happen rather than to understand why they turned out that way.", "reverse": False},
    {"id": 9, "text": "I have feelings that I can\'t quite identify.", "reverse": False},
    {"id": 10, "text": "Being in touch with emotions is essential.", "reverse": True},
    {"id": 11, "text": "I find it hard to describe how I feel about people.", "reverse": False},
    {"id": 12, "text": "People tell me to describe my feelings more.", "reverse": False},
    {"id": 13, "text": "I don\'t know what\'s going on inside me.", "reverse": False},
    {"id": 14, "text": "I often don\'t know why I am angry.", "reverse": False},
    {"id": 15, "text": "I prefer talking to people about their daily activities rather than their feelings.", "reverse": False},
    {"id": 16, "text": "I prefer to watch \"light\" entertainment shows rather than psychological dramas.", "reverse": False},
    {"id": 17, "text": "It is difficult for me to reveal my innermost feelings, even to close friends.", "reverse": False},
    {"id": 18, "text": "I can feel close to someone, even in moments of silence.", "reverse": True},
    {"id": 19, "text": "I find examination of my feelings useful in solving personal problems.", "reverse": True},
    {"id": 20, "text": "Looking for hidden meanings in movies or plays distracts from my enjoyment.", "reverse": False},
]


# -----------------------------
# TAS-20 subscales
# -----------------------------

TAS20_SUBSCALES = {
    "difficulty_identifying_feelings": [1, 3, 6, 7, 9, 13, 14],
    "difficulty_describing_feelings": [2, 4, 11, 12, 17],
    "externally_oriented_thinking": [5, 8, 10, 15, 16, 18, 19, 20],
}


# -----------------------------
# Scoring categories
# -----------------------------

TAS20_CUTOFFS = {
    "non_alexithymic_max": 51,
    "borderline_min": 52,
    "borderline_max": 60,
    "alexithymic_min": 61,
}