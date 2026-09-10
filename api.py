import os
import tempfile

from fastapi import (
    FastAPI,
    File,
    Form,
    UploadFile
)

from dotenv import load_dotenv

from services.transcription_service import (
    WhisperTranscriptionService
)

from services.llm_service import (
    LLMService
)

from services.database_service import (
    init_database,
    save_meeting
)


load_dotenv(
    override=True
)

app = FastAPI(
    title="Meeting Intelligence API",
    description=(
        "API for meeting transcription "
        "and intelligence extraction"
    ),
    version="1.0"
)


init_database()


@app.get("/")
def home():

    return {
        "status": "running",
        "service": "Meeting Intelligence API"
    }


@app.post(
    "/process-meeting"
)
async def process_meeting(
    title: str = Form(...),
    audio: UploadFile = File(...)
):

    api_key = os.getenv(
        "GEMINI_API_KEY"
    )

    model = os.getenv(
        "GEMINI_MODEL",
        "gemini-3.6-flash"
    )

    if not api_key:

        return {
            "error":
            "GEMINI_API_KEY is missing."
        }

    temp_path = None

    try:

        suffix = os.path.splitext(
            audio.filename or ".wav"
        )[1]

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp_file:

            content = await audio.read()

            temp_file.write(
                content
            )

            temp_path = (
                temp_file.name
            )

        # ------------------------------
        # Whisper
        # ------------------------------

        whisper = (
            WhisperTranscriptionService()
        )

        transcript, language = (
            whisper.transcribe(
                temp_path
            )
        )

        # ------------------------------
        # Gemini
        # ------------------------------

        llm = LLMService(
            api_key,
            model
        )

        result = (
            llm.process_long_transcript(
                transcript
            )
        )

        # ------------------------------
        # Database
        # ------------------------------

        meeting_id = save_meeting(
            title=title,
            transcript=transcript,
            result=result,
            participants=[
                p.model_dump()
                for p in result.participants
            ],
            action_items=[
                a.model_dump()
                for a in result.action_items
            ]
        )

        return {

            "success": True,

            "meeting_id": meeting_id,

            "language": language,

            "transcript": transcript,

            "meeting_intelligence":
                result.model_dump()
        }

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