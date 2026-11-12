"""Six-page informed consent for the urn experiment.

The participant information below reproduces the wording supplied by the
researcher. Review and obtain approval before collecting participant data.

SPACE or ENTER advances information pages; BACKSPACE goes back.
On the final page, SPACE or mouse click toggles the checkbox, and ENTER
confirms only when checked. ESC declines at any point.
"""

import json
from datetime import datetime, timezone

from psychopy import core, event, visual

import urn_params as params

CONSENT_VERSION = "draft-2026-11-10-six-pages-colored-subtitles"

# Text is divided at paragraph / section boundaries; wording is unchanged.
# HTML space entities and Markdown emphasis from the supplied message are
# represented as ordinary displayed spaces/text.
CONSENT_PAGES = [
    "We kindly ask you to read the following explanations carefully and to sign the present declaration of consent before you take part in the study.\n\nStudy Information\n\nThis study is being conducted as part of a Bachelor's thesis at the Department of Humanwissenschaft at Technical University of Darmstadt (TU Darmstadt), under the supervision of Angela Yu and Anais Mignot.\n\nResearcher: Giovana Mota Moraes\n\nSupervisor: Angela Yu\n\nDepartment: Humanwissenschaft\n\nInstitution: TU Darmstadt\n\nSubject of the experiment\n\nThis study investigates how people make decisions and process information in different situations. Participants will complete a series of computer-based tasks involving choices and guesses, followed by questionnaires assessing emotional processing and reasoning abilities. The study aims to better understand decision-making processes and how they may relate to individual differences.",
    "Process of the study/the experiment\n\nThe experiment will be conducted on a computer and consists of four main parts.\n\n•  First, participants will receive instructions explaining the experimental task, followed by practice trials to familiarize themselves with the procedure.\n\n•  Next, participants will complete the main experimental task, which involves making repeated choices and guesses based on information presented on the screen. Participants will observe sequences of colored balls and predict subsequent outcomes. They will receive feedback on their performance and the points earned throughout the task.\n\n•  After completing the main task, participants will answer questions about their subjective experience during the experiment, including their perceived effort, confidence in their performance, and perceived difficulty of the task.\n\n•  Finally, participants will complete two questionnaires. The first consists of questions assessing cognitive reasoning abilities. The second is the Toronto Alexithymia Scale (TAS-20), which assesses aspects of emotional processing.\n\n•  Throughout the experiment, participants' choices, guesses, questionnaire responses, and reaction times will be recorded for subsequent analysis.",
    "Duration and compensation for participation\n\nParticipation in the experiment will require approximately 75-90 minutes. Each participant will be compensated with an amount of x Euro resp. x hours as a test subject will be testified.\n\nPossible benefit of the study/the experiment\n\nThis study aims to contribute to a better understanding of how people make decisions and process information in different situations. By examining participants' responses to computer-based tasks and questionnaires, the study seeks to explore general aspects of decision-making and individual differences. The findings may contribute to future research on human behavior, cognitive processes, and decision-making.\n\nExperiences and risks which are associated with the participation in the study/the experiment\n\nThe participants of the study do not face any risks which are greater than risks they face in general life.\n\nPrivacy Statement\n\nData processing in the context of this study is performed according to the privacy regulations of the General Data Protection Regulation (GDPR) and the Privacy and Freedom of Information law of the State of Hessen (HDSIG). All data will only be used for the purposes described on the Information Sheet.",
    'In the context of this study, the following information will be collected:\n\nParticipants’ choices, guesses, reaction times, task performance, perceived effort, confidence, perceived difficulty, and responses to the TAS-20 and cognitive reasoning questionnaire.\n\nPersonal data collected are:\n\nParticipant’s age, sex and field of study.\n\nConfidentiality\n\nAll data collected in course of the study are naturally confidential and will only be used in anonymized form. Demographic data like age or sex do not allow deducing unambiguous information about your person. You will be asked at no point of the study to disclose your name or other unambiguous information about yourself.',
    'Data storage\n\nCollected data will be stored in the university’s computer and the raw data will be deleted by November 2031. Data will be stored anonymously. Each participant will be assigned a unique numerical code (participant ID), which cannot be traced back to their identity. No directly identifying personal information will be collected.\n\nThis declaration of consent will be stored separately from the data which is collected during the study and will be destroyed by November 2031.\n\nVoluntariness & Rights of the test persons\n\nYour participation in this study is voluntary. You can withdraw from participation at any point of time or withdraw your consent without facing any disadvantages (withdrawal). If you withdraw from participation, no data connected to your person will be stored and already collected data will be deleted.',
    'You have the right to request which data about your person have been stored and – if necessary – demand that they are either corrected or deleted. You also have the right to restrict processing, the right to object to processing and the right to data portability in a commonly used, structured and machine-readable form.\n\nIn case of dissent you have the right to lodge a complaint with the Data Protection Officer of Hessen (address will be given to you after the experiment).\n\nDeclaration of Consent\n\nI have read the explanations regarding the experiment und I hereby agree to participate in [the above-named study/the above-named experiment.]\n\nI agree that any data which is collected in the course of the experiment will be analyzed for scientific purposes and will be stored in anonymized form. I am aware that my participation is voluntary and that I can withdraw from participation at any time and without giving reasons.',
]

# Only section subtitles are highlighted; all paragraph wording remains unchanged.
SUBTITLE_COLOR = "#76232C"
BODY_COLOR = "#253F62"
SECTION_SUBTITLES = {
    "Study Information",
    "Subject of the experiment",
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
    """Identify headings without editing the supplied text."""
    return [(paragraph, paragraph in SECTION_SUBTITLES)
            for paragraph in page_text.split("\n\n")]


def _draw_page_body(win, page_text, final_page=False):
    """Draw each heading and paragraph separately, preserving the source wording.

    Use PsychoPy's measured text bounds to place consecutive blocks without
    overlapping. Slightly reduce spacing/font only if necessary on long pages.
    """
    blocks = _page_blocks(page_text)
    start_y = 0.330
    bottom_y = -0.295 if final_page else -0.390
    x = -0.72
    text_width = 1.44

    # Cache the calculated stimuli for the current draw so a page fits without
    # relying on approximate character counts or hand-written line breaks.
    for body_font_size in (0.025, 0.024, 0.023, 0.022, 0.021):
        rendered = []
        y = start_y
        for index, (paragraph, is_heading) in enumerate(blocks):
            height = body_font_size if not is_heading else body_font_size * 1.06
            stim = visual.TextStim(
                win=win, text=paragraph, pos=(x, y),
                height=height, wrapWidth=text_width,
                color=SUBTITLE_COLOR if is_heading else BODY_COLOR,
                bold=is_heading, alignText="left",
                anchorHoriz="left", anchorVert="top",
            )
            # boundingBox is expressed in screen pixels, so convert to
            # height-units using the shared PsychoPy window dimensions.
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
    """Return consent event record; an unchecked final page cannot be confirmed."""
    page = 0
    checked = False
    last_pressed = False

    heading = visual.TextStim(
        win, text="", pos=(0, 0.445), height=0.038,
        color="#172b49", bold=True,
    )
    footer = visual.TextStim(
        win, text="", pos=(0, -0.45), height=0.021,
        wrapWidth=1.35, color="#576a82",
    )
    box = visual.Rect(
        win, pos=(-0.59, -0.355), width=0.043, height=0.043,
        fillColor=None, lineColor="#253f62", lineWidth=2,
    )
    tick = visual.TextStim(
        win, text="✓", pos=(-0.59, -0.355), height=0.034,
        color="#253f62", bold=True,
    )
    checkbox_label = visual.TextStim(
        win, text="I have read the information and agree to participate.",
        pos=(-0.55, -0.355), height=0.023, wrapWidth=1.18,
        color="#172b49", alignText="left", anchorHoriz="left",
    )

    mouse = event.Mouse(win=win)
    mouse.clickReset()
    last_page = len(CONSENT_PAGES) - 1

    def consent_result(consented):
        return {
            "consented": consented,
            "consent_version": CONSENT_VERSION,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        }

    def render(message=None):
        heading.text = f"Participant information ({page + 1}/{len(CONSENT_PAGES)})"
        if message is not None:
            footer.text = message
        elif page == last_page:
            footer.text = (
                "SPACE / click: checkbox     ENTER: agree     "
                "BACKSPACE: back     ESC: decline"
            )
        else:
            footer.text = (
                "SPACE / ENTER: next     BACKSPACE: back     ESC: decline"
            )
        heading.draw()
        _draw_page_body(win, CONSENT_PAGES[page], final_page=(page == last_page))
        if page == last_page:
            box.draw()
            if checked:
                tick.draw()
            checkbox_label.draw()
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
                event.clearEvents()
                render()
        else:
            if "backspace" in keys:
                page -= 1
                event.clearEvents()
                render()
            elif "space" in keys:
                checked = not checked
                render()
            elif any(k in keys for k in ("return", "num_enter")):
                if checked:
                    return consent_result(True)
                render("Please check the box before pressing ENTER. ESC: decline")

            pressed = bool(mouse.getPressed()[0])
            if pressed and not last_pressed:
                mx, my = mouse.getPos()
                if -0.63 <= mx <= 0.62 and -0.39 <= my <= -0.32:
                    checked = not checked
                    render()
            last_pressed = pressed

        core.wait(0.01)


def save_consent_record(participant_info, consent, test_mode=False):
    """Save minimal participant fields with consent proof, or print in test mode."""
    record = {
        "participant_id": str(participant_info["participant_id"]),
        "age": participant_info.get("age"),
        "field_of_study": participant_info.get("field_of_study"),
        "consented": bool(consent["consented"]),
        "consent_version": consent["consent_version"],
        "consent_timestamp_utc": consent["timestamp_utc"],
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
