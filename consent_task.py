"""Four-page informed consent for the urn experiment.

The participant-information and declaration wording below are supplied by the
researcher; only paragraph grouping and on-screen layout have been changed.

SPACE / ENTER advances information pages, BACKSPACE goes back.
On the final page, ENTER confirms participation; ESC declines at any point.
No mouse interaction or checkbox is required.
"""

import json
from datetime import datetime, timezone

from psychopy import core, event, visual

import urn_params as params

CONSENT_VERSION = "draft-2026-11-14-four-pages-enter-confirmation"

# The declaration is deliberately kept in its own variable, so the exact
# agreement acknowledged by ENTER can be identified and saved separately.
DECLARATION_AGREEMENT_TEXT = (
    "I have read the explanations regarding the experiment and I hereby agree "
    "to participate in the \"Guess the ball\" experiment."
)

DECLARATION_DATA_TEXT = (
    "I agree that any data which is collected in the course of the experiment "
    "will be analysed for scientific purposes and will be stored in anonymized "
    "form. I am aware that my participation is voluntary and that I can "
    "withdraw from participation at any time and without giving reasons.\n\n\n"
    "Press ENTER to confirm your agreement and continue with the experiment."
)

# The four pages use the exact wording supplied by the researcher. Line wraps
# from the source have been removed for easier reading, but words have not been
# rewritten. Text blocks are separated by blank lines for the display layout.
CONSENT_PAGES = [
    "\n\n".join([
        "Information Sheet",
        (
            "We kindly ask you to read the following explanations carefully and "
            "to consent to the procedure of the experiment as well as the "
            "Privacy Statement before you take part in the study."
        ),
        "Subject of the study/the experiment",
        (
            "The planned experiments aim to study the computational mechanisms "
            "of cognition. With the help of these experiments, we will gain "
            "knowledge about key cognitive functions, such as vision, attention, "
            "learning, decision-making and social cognition and model the "
            "processes the brain uses to support intelligent behaviour."
        ),
        "Process of the study/the experiment",
        (
            "During the experiments, participants will be seated in front of a "
            "computer. The experiments will consist of questionnaires and "
            "experiments. For each of these participants will receive a brief "
            "introduction and a detailed explanation of the rules in written "
            "form on the computer. Participants’ responses via the computer’s "
            "mouse and keyboard will be recorded. Every 5-10 minutes participants "
            "can take a short break."
        ),
        "Duration and compensation for participation",
        (
            "Participation in the study/experiment will require approximately "
            "60 minutes. Participants can either receive monetary compensation "
            "or VP-hours. The amount depends on the length of the experiment."
        ),
        "Possible benefit of the study/the experiment",
        (
            "The experiment is intended to contribute to a better understanding "
            "of the computational mechanisms giving rise to intelligent "
            "behaviour in humans."
        ),
        (
            "Experiences and risks which are associated with the participation "
            "in the study/the experiment"
        ),
        (
            "Participation in this study will not expose the subject to any "
            "risk beyond the risks of everyday life."
        ),
    ]),
    "\n\n".join([
        "Privacy Statement",
        (
            "Data processing in the context of this study is performed according "
            "to the privacy regulations of the General Data Protection "
            "Regulation (GDPR) and the Privacy and Freedom of Information law of "
            "the State of Hessen (HDSIG). All data will only be used for the "
            "purposes described in the Information Sheet."
        ),
        "In the context of this study, the following information will be collected:",
        (
            "Behavioural data in the form of keystrokes or mouse (or trackpad) "
            "trajectories and clicks, responses to questionnaires"
        ),
        "Personal data collected are:",
        (
            "Age, gender, subject of study/profession, and depending on the "
            "study prior diagnosis of ADHD (Attention-deficit/hyperactivity "
            "disorder) or ASD (Autism spectrum disorder)"
        ),
        "Confidentiality",
        (
            "All data collected in the course of the study are naturally "
            "confidential and will only be used in anonymized form. Demographic "
            "data like age or sex do not allow deducing unambiguous information "
            "about your person. You will be asked at no point of the study to "
            "disclose your name or other unambiguous information about yourself."
        ),
        "Data storage",
        (
            "The data collected with this study are stored on servers of the "
            "TU Darmstadt, and/or other secure virtual platforms such as "
            "Hessenbox and GitLab. If it is an online experiment they can also "
            "be stored temporarily on the experiment hosting platform. Data "
            "storage takes place in a form which does not allow conclusions "
            "about your person, meaning that all data will be anonymized. In "
            "the context of scientific publications, the recorded (anonymised) "
            "data may also be published. This happens, for example, via the "
            "servers of the Open Science Foundation (osf.io). In this case, "
            "the data would be publicly accessible on the Internet."
        ),
        (
            "This declaration of consent will be stored separately from the "
            "data which is collected during the study and is destroyed after "
            "5 years."
        ),
    ]),
    "\n\n".join([
        "Voluntariness & Rights of the test persons",
        (
            "Your participation in this study is voluntary. You can withdraw "
            "from participation at any point of time or withdraw your consent "
            "without facing any disadvantages (withdrawal). If you withdraw "
            "from participation, no data connected to your person will be "
            "stored and already collected data will be deleted. You have the "
            "right to request which data about your person have been stored "
            "and – if necessary – demand that they are either corrected or "
            "deleted. In case of dissent you have the right to lodge a "
            "complaint with the Data Protection Officer of Hessen (see below "
            "for address)."
        ),
        "The people in charge of data handling of this study:",
        "Prof. Dr. Angela Yu\nEmail: angela.yu@tu-darmstadt.de",
        (
            "For questions about data protection issues please contact the "
            "data protection officer of TU Darmstadt:"
        ),
        "Jan Hansen\nEmail: datenschutz@tu-darmstadt.de",
        "Data Protection Officer of Hessen in case of data protection issues:",
        "Email: Poststelle@datenschutz.hessen.de",
        (
            "If you have any questions, suggestions or complaints, you are "
            "welcome to contact either the present supervisor or the "
            "responsible head of the study:"
        ),
        (
            "Prof. Dr. Angela Yu\n"
            "Professor for Centre of Cognitive Science & Hessian AI Institute\n"
            "Phone: +49 6151 16-23964\n"
            "Email: angela.yu@tu-darmstadt.de"
        ),
    ]),
    "\n\n".join([
        "Declaration of Consent",
        DECLARATION_AGREEMENT_TEXT,
        DECLARATION_DATA_TEXT,
    ]),
]

# Keep the complete text as an independent, verbatim record in consent.json.
FULL_CONSENT_TEXT = "\n\n".join(CONSENT_PAGES)

# Wider side margins than the original version (height-based PsychoPy units).
# The original text started at x=-0.72 with wrap width 1.44.
CONSENT_TEXT_LEFT_X = -0.60
CONSENT_TEXT_WIDTH = 1.20

# Only section titles are highlighted. All participant-facing content above is
# unchanged from the source; this set controls visual styling only.
SUBTITLE_COLOR = "#76232C"
BODY_COLOR = "#253F62"
SECTION_SUBTITLES = {
    "Information Sheet",
    "Subject of the study/the experiment",
    "Process of the study/the experiment",
    "Duration and compensation for participation",
    "Possible benefit of the study/the experiment",
    "Experiences and risks which are associated with the participation in the study/the experiment",
    "Privacy Statement",
    "Confidentiality",
    "Data storage",
    "Voluntariness & Rights of the test persons",
    "Declaration of Consent",
}


def _page_blocks(page_text):
    """Identify section headings without modifying any supplied wording."""
    return [(paragraph, paragraph in SECTION_SUBTITLES)
            for paragraph in page_text.split("\n\n")]


def _draw_page_body(win, page_text, final_page=False):
    """Draw the consent in separate text blocks and fit them on one screen.

    Larger side margins are used throughout. Text size is reduced only when
    necessary to fit a denser page; nothing is omitted from a page.
    """
    blocks = _page_blocks(page_text)
    start_y = 0.340
    bottom_y = -0.225 if final_page else -0.382
    x = CONSENT_TEXT_LEFT_X
    text_width = CONSENT_TEXT_WIDTH

    for body_font_size in (0.025, 0.024, 0.023, 0.022, 0.021, 0.020, 0.019, 0.018):
        rendered = []
        y = start_y
        for index, (paragraph, is_heading) in enumerate(blocks):
            height = body_font_size * 1.06 if is_heading else body_font_size
            stim = visual.TextStim(
                win=win, text=paragraph, pos=(x, y),
                height=height, wrapWidth=text_width,
                color=SUBTITLE_COLOR if is_heading else BODY_COLOR,
                bold=is_heading, alignText="left",
                anchorHoriz="left", anchorVert="top",
            )
            # PsychoPy reports the bounding box in pixels. Convert to the
            # height-based window coordinates used by the experiment.
            measured_height = stim.boundingBox[1] / float(win.size[1])
            rendered.append(stim)
            y -= measured_height
            if index < len(blocks) - 1:
                y -= body_font_size * (0.60 if is_heading else 0.85)
        if y >= bottom_y:
            break

    for stim in rendered:
        stim.draw()


def run_consent(win):
    """Display four consent pages; ENTER on the final page records agreement.

    ESC declines without saving. BACKSPACE returns to the preceding page.
    """
    if not CONSENT_PAGES:
        raise ValueError("CONSENT_PAGES must contain the approved consent text")

    page = 0
    last_page = len(CONSENT_PAGES) - 1
    consent_ready_at = None

    heading = visual.TextStim(
        win, text="", pos=(0, 0.445), height=0.038,
        color="#172b49", bold=True,
    )
    footer = visual.TextStim(
        win, text="", pos=(0, -0.452), height=0.020,
        wrapWidth=1.40, color="#576a82",
    )

    # Draw a key graphic directly, so no external image file is necessary.
    # Adjust these constants if you want the key higher, lower, or larger.
    KEY_Y = -0.337
    KEY_WIDTH = 0.220
    KEY_HEIGHT = 0.060
    key_shadow = visual.Rect(
        win, pos=(0.006, KEY_Y - 0.006),
        width=KEY_WIDTH, height=KEY_HEIGHT,
        fillColor="#cbd5e1", lineColor=None,
    )
    key_face = visual.Rect(
        win, pos=(0, KEY_Y),
        width=KEY_WIDTH, height=KEY_HEIGHT,
        fillColor="#f8fafc", lineColor="#526783", lineWidth=1.6,
    )
    key_symbol = visual.TextStim(
        win, text="ENTER  ↵", pos=(0, KEY_Y),
        height=0.024, color="#172b49", bold=True,
    )

    def consent_result(consented):
        return {
            "consented": consented,
            "consent_version": CONSENT_VERSION,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }

    def render():
        heading.text = f"Participant information ({page + 1}/{len(CONSENT_PAGES)})"
        footer.text = (
            "ENTER: agree to participate     BACKSPACE: back     ESC: decline"
            if page == last_page else
            "SPACE / ENTER: next     BACKSPACE: back     ESC: decline"
        )
        heading.draw()
        _draw_page_body(win, CONSENT_PAGES[page], final_page=(page == last_page))
        if page == last_page:
            key_shadow.draw()
            key_face.draw()
            key_symbol.draw()
        footer.draw()
        win.flip()

    event.clearEvents()
    render()

    while True:
        keys = event.getKeys(
            keyList=["space", "return", "num_enter", "escape", "backspace"]
        )
        if "escape" in keys:
            return consent_result(False)

        if page < last_page:
            if "backspace" in keys and page > 0:
                page -= 1
                event.clearEvents()
                render()
            elif any(k in keys for k in ("space", "return", "num_enter")):
                page += 1
                if page == last_page:
                    # A keypress used to advance must not also register consent.
                    consent_ready_at = core.getTime() + 0.45
                event.clearEvents()
                render()
        else:
            if "backspace" in keys:
                page -= 1
                consent_ready_at = None
                event.clearEvents()
                render()
            elif any(k in keys for k in ("return", "num_enter")):
                if consent_ready_at is None or core.getTime() >= consent_ready_at:
                    return consent_result(True)
            # SPACE / mouse clicks intentionally cannot indicate agreement.

        core.wait(0.01)


def save_consent_record(participant_info, consent, test_mode=False):
    """Store the full consent wording and the confirmation in consent.json."""
    record = {
        "participant_id": str(participant_info["participant_id"]),
        "age": participant_info.get("age"),
        "field_of_study": participant_info.get("field_of_study"),
        "consented": bool(consent["consented"]),
        "consent_version": consent["consent_version"],
        "consent_timestamp_utc": consent["timestamp_utc"],
        "consent_text": FULL_CONSENT_TEXT,
        "declaration_agreement_text": DECLARATION_AGREEMENT_TEXT,
    }
    if test_mode:
        print("TEST MODE — consent record (not saved):", json.dumps(record, ensure_ascii=False))
        return None
    if not record["consented"]:
        raise ValueError("Declined consent must not be written to the participant data folder")
    folder = params.BASE_DIR / params.DATA_FOLDER / record["participant_id"]
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "consent.json"
    with path.open("x", encoding="utf-8") as handle:
        json.dump(record, handle, indent=2, ensure_ascii=False)
    return path
