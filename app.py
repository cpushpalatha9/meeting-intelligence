import os
import tempfile

import streamlit as st
from dotenv import load_dotenv

from services.llm_service import LLMService

from services.transcription_service import (
    WhisperTranscriptionService
)

from services.meeting_service import (
    clean_action_items,
    clean_participants
)

from services.database_service import (
    init_database,
    save_meeting,
    get_all_meetings,
    get_meeting
)

from schemas.meeting_schema import (
    ActionItem,
    Participant
)


# ==========================================
# ENVIRONMENT
# ==========================================

load_dotenv(
    override=True
)

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.6-flash"
)

WHISPER_MODEL = os.getenv(
    "WHISPER_MODEL",
    "small"
)


# ==========================================
# PAGE
# ==========================================

st.set_page_config(
    page_title="Meeting Intelligence System",
    page_icon="🎙️",
    layout="wide"
)


# ==========================================
# DATABASE
# ==========================================

init_database()


# ==========================================
# HEADER
# ==========================================

st.title(
    "🎙️ Meeting Intelligence System"
)

st.caption(
    "Transform meeting audio or transcripts "
    "into structured meeting intelligence."
)


# ==========================================
# SIDEBAR
# ==========================================

st.sidebar.title(
    "Navigation"
)

page = st.sidebar.radio(
    "Choose:",
    [
        "Process Meeting",
        "Meeting History"
    ]
)


# ============================================================
# PROCESS MEETING
# ============================================================

if page == "Process Meeting":

    st.header(
        "📝 Process Meeting"
    )

    # --------------------------------------
    # TITLE
    # --------------------------------------

    meeting_title = st.text_input(
        "Meeting Title",
        value="Meeting"
    )

    # --------------------------------------
    # INPUT MODE
    # --------------------------------------

    input_mode = st.radio(
        "Meeting Input",
        [
            "🎙️ Upload Audio",
            "📄 Paste Transcript"
        ],
        horizontal=True
    )

    transcript = ""
    audio_file = None

    # ========================================================
    # AUDIO
    # ========================================================

    if input_mode == "🎙️ Upload Audio":

        st.info(
            "Upload an audio recording of the meeting. "
            "Whisper will automatically create the transcript."
        )

        audio_file = st.file_uploader(
            "Upload Meeting Audio",
            type=[
                "mp3",
                "wav",
                "m4a",
                "mp4",
                "webm",
                "ogg"
            ]
        )

        if audio_file:

            st.audio(
                audio_file
            )

            st.success(
                f"Audio selected: "
                f"{audio_file.name}"
            )

    # ========================================================
    # TRANSCRIPT
    # ========================================================

    else:

        transcript = st.text_area(
            "Meeting Transcript",
            height=300,
            placeholder=(
                "Paste your meeting transcript here..."
            )
        )

    # --------------------------------------
    # PROCESS
    # --------------------------------------

    process_button = st.button(
        "🚀 Process Meeting",
        type="primary"
    )

    # ========================================================
    # PROCESS BUTTON
    # ========================================================

    if process_button:

        # ----------------------------------
        # API KEY
        # ----------------------------------

        if not GEMINI_API_KEY:

            st.error(
                "GEMINI_API_KEY is missing "
                "from the .env file."
            )

            st.stop()

        # ----------------------------------
        # TITLE
        # ----------------------------------

        if not meeting_title.strip():

            st.error(
                "Please enter a meeting title."
            )

            st.stop()

        # ====================================================
        # AUDIO → WHISPER
        # ====================================================

        if (
            input_mode
            == "🎙️ Upload Audio"
        ):

            if not audio_file:

                st.error(
                    "Please upload an audio file."
                )

                st.stop()

            temp_path = None

            try:

                suffix = os.path.splitext(
                    audio_file.name
                )[1]

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix
                ) as temp_file:

                    temp_file.write(
                        audio_file.getbuffer()
                    )

                    temp_path = (
                        temp_file.name
                    )

                with st.spinner(
                    f"Transcribing audio with "
                    f"Whisper ({WHISPER_MODEL})..."
                ):

                    whisper = (
                        WhisperTranscriptionService(
                            WHISPER_MODEL
                        )
                    )

                    transcript, language = (
                        whisper.transcribe(
                            temp_path
                        )
                    )

                st.success(
                    "Whisper transcription completed."
                )

                st.info(
                    f"Detected language: "
                    f"{language}"
                )

                with st.expander(
                    "📄 View Generated Transcript"
                ):

                    st.text_area(
                        "Transcript",
                        transcript,
                        height=300,
                        disabled=True
                    )

            except Exception as error:

                st.error(
                    "Whisper transcription failed."
                )

                st.exception(
                    error
                )

                st.stop()

            finally:

                if (
                    temp_path
                    and os.path.exists(
                        temp_path
                    )
                ):

                    os.remove(
                        temp_path
                    )

        # ====================================================
        # TRANSCRIPT VALIDATION
        # ====================================================

        if not transcript.strip():

            st.error(
                "Transcript is empty."
            )

            st.stop()

        # ====================================================
        # GEMINI PROCESSING
        # ====================================================

        try:

            llm_service = LLMService(
                api_key=GEMINI_API_KEY,
                model=GEMINI_MODEL
            )

            with st.spinner(
                "Analyzing meeting with Gemini..."
            ):

                result = (
                    llm_service
                    .process_long_transcript(
                        transcript
                    )
                )

            # ----------------------------------
            # CLEAN ACTION ITEMS
            # ----------------------------------

            cleaned_actions = (
                clean_action_items(
                    result.action_items
                )
            )

            result.action_items = [
                ActionItem.model_validate(
                    item
                )
                for item in cleaned_actions
            ]

            # ----------------------------------
            # CLEAN PARTICIPANTS
            # ----------------------------------

            cleaned_participants = (
                clean_participants(
                    result.participants
                )
            )

            result.participants = [
                Participant.model_validate(
                    item
                )
                for item in cleaned_participants
            ]

            # =================================================
            # SAVE DATABASE
            # =================================================

            meeting_id = save_meeting(
                title=meeting_title.strip(),
                transcript=transcript,
                result=result,
                participants=cleaned_participants,
                action_items=cleaned_actions
            )

            st.success(
                f"Meeting processed successfully! "
                f"Meeting ID: {meeting_id}"
            )

            # =================================================
            # SUMMARY
            # =================================================

            st.subheader(
                "📌 Summary"
            )

            st.write(
                result.summary
            )

            # =================================================
            # KEY POINTS
            # =================================================

            st.subheader(
                "🔑 Key Points"
            )

            if result.key_points:

                for point in result.key_points:

                    st.markdown(
                        f"- {point}"
                    )

            else:

                st.info(
                    "No key points identified."
                )

            # =================================================
            # DECISIONS
            # =================================================

            st.subheader(
                "✅ Decisions"
            )

            if result.decisions:

                for decision in result.decisions:

                    st.markdown(
                        f"- {decision}"
                    )

            else:

                st.info(
                    "No decisions identified."
                )

            # =================================================
            # ACTION ITEMS
            # =================================================

            st.subheader(
                "📋 Action Items"
            )

            if result.action_items:

                for index, item in enumerate(
                    result.action_items,
                    start=1
                ):

                    st.markdown(
                        f"### Action Item {index}"
                    )

                    st.write(
                        f"**Task:** "
                        f"{item.task}"
                    )

                    st.write(
                        f"**Assignee:** "
                        f"{item.assignee or 'Unknown'}"
                    )

                    st.write(
                        f"**Deadline:** "
                        f"{item.deadline or 'Unknown'}"
                    )

                    st.write(
                        f"**Priority:** "
                        f"{item.priority or 'Unknown'}"
                    )

                    st.write(
                        f"**Status:** "
                        f"{item.status}"
                    )

                    st.divider()

            else:

                st.info(
                    "No genuine action items identified."
                )

            # =================================================
            # PARTICIPANTS
            # =================================================

            st.subheader(
                "👥 Participants"
            )

            if result.participants:

                for participant in (
                    result.participants
                ):

                    st.markdown(
                        f"### {participant.name}"
                    )

                    if participant.responsibilities:

                        for responsibility in (
                            participant.responsibilities
                        ):

                            st.markdown(
                                f"- {responsibility}"
                            )

                    else:

                        st.write(
                            "No responsibilities identified."
                        )

            else:

                st.info(
                    "No participants identified."
                )

            # =================================================
            # JSON
            # =================================================

            with st.expander(
                "🔍 View Structured JSON"
            ):

                st.json(
                    result.model_dump()
                )

        except Exception as error:

            st.error(
                "Meeting processing failed."
            )

            st.exception(
                error
            )


# ============================================================
# MEETING HISTORY
# ============================================================

else:

    st.header(
        "📚 Meeting History"
    )

    meetings = (
        get_all_meetings()
    )

    if not meetings:

        st.info(
            "No meetings have been processed yet."
        )

    else:

        st.write(
            f"Total meetings: "
            f"{len(meetings)}"
        )

        meeting_options = {}

        for meeting in meetings:

            meeting_id = meeting[0]
            title = meeting[1]
            created_at = meeting[3]

            label = (
                f"{meeting_id} - "
                f"{title} - "
                f"{created_at}"
            )

            meeting_options[label] = (
                meeting_id
            )

        selected_label = st.selectbox(
            "Select a meeting:",
            list(
                meeting_options.keys()
            )
        )

        selected_id = (
            meeting_options[
                selected_label
            ]
        )

        meeting = get_meeting(
            selected_id
        )

        if meeting:

            st.subheader(
                f"📌 {meeting[1]}"
            )

            st.caption(
                f"Created: {meeting[8]}"
            )

            st.subheader(
                "Summary"
            )

            st.write(
                meeting[3]
            )

            st.subheader(
                "Key Points"
            )

            key_points = (
                __import__("json")
                .loads(meeting[4])
            )

            for point in key_points:

                st.markdown(
                    f"- {point}"
                )

            st.subheader(
                "Decisions"
            )

            decisions = (
                __import__("json")
                .loads(meeting[5])
            )

            if decisions:

                for decision in decisions:

                    st.markdown(
                        f"- {decision}"
                    )

            else:

                st.info(
                    "No decisions identified."
                )

            st.subheader(
                "Action Items"
            )

            action_items = (
                __import__("json")
                .loads(meeting[6])
            )

            for item in action_items:

                st.write(
                    f"**Task:** "
                    f"{item['task']}"
                )

                st.write(
                    f"**Assignee:** "
                    f"{item['assignee'] or 'Unknown'}"
                )

                st.write(
                    f"**Deadline:** "
                    f"{item['deadline'] or 'Unknown'}"
                )

                st.write(
                    f"**Priority:** "
                    f"{item['priority'] or 'Unknown'}"
                )

                st.write(
                    f"**Status:** "
                    f"{item['status']}"
                )

                st.divider()

            st.subheader(
                "Participants"
            )

            participants = (
                __import__("json")
                .loads(meeting[7])
            )

            for participant in participants:

                st.markdown(
                    f"### {participant['name']}"
                )

                for responsibility in (
                    participant[
                        "responsibilities"
                    ]
                ):

                    st.markdown(
                        f"- {responsibility}"
                    )

            with st.expander(
                "📄 Original Transcript"
            ):

                st.text(
                    meeting[2]
                )