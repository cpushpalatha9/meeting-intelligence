import json
import re
import time

from google import genai

from prompts.meeting_prompt import MEETING_PROMPT

from schemas.meeting_schema import (
    MeetingIntelligence,
    ActionItem,
    Participant
)

from services.meeting_service import (
    clean_action_items,
    clean_participants
)


class LLMService:

    def __init__(
        self,
        api_key,
        model
    ):

        if not api_key:

            raise ValueError(
                "Gemini API key is missing."
            )

        if not model:

            raise ValueError(
                "Gemini model is missing."
            )

        self.client = genai.Client(
            api_key=api_key
        )

        self.model = model

    # =====================================
    # INPUT VALIDATION
    # =====================================

    def validate_transcript(
        self,
        transcript
    ):

        if transcript is None:

            raise ValueError(
                "Transcript cannot be empty."
            )

        transcript = transcript.strip()

        if not transcript:

            raise ValueError(
                "Transcript cannot be empty."
            )

        if len(transcript) < 10:

            raise ValueError(
                "Transcript is too short."
            )

        return transcript

    # =====================================
    # PROMPT
    # =====================================

    def create_prompt(
        self,
        transcript
    ):

        return MEETING_PROMPT.format(
            transcript=transcript
        )

    # =====================================
    # GEMINI
    # =====================================

    def call_llm(
        self,
        prompt
    ):

        print(
            "\nCalling Gemini..."
        )

        response = (
            self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )
        )

        print(
            "Gemini response received."
        )

        if not response.text:

            raise ValueError(
                "Gemini returned an empty response."
            )

        return response.text

    # =====================================
    # CLEAN JSON
    # =====================================

    def clean_json_response(
        self,
        response_text
    ):

        text = response_text.strip()

        # Remove ```json
        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE
        )

        # Remove ```
        text = re.sub(
            r"\s*```$",
            "",
            text
        )

        text = text.strip()

        # Extract JSON object if extra text exists
        first_brace = text.find("{")
        last_brace = text.rfind("}")

        if (
            first_brace != -1
            and last_brace != -1
            and last_brace > first_brace
        ):

            text = text[
                first_brace:last_brace + 1
            ]

        return text.strip()

    # =====================================
    # PROCESS ONE TRANSCRIPT
    # =====================================

    def process_once(
        self,
        transcript
    ):

        prompt = self.create_prompt(
            transcript
        )

        response_text = self.call_llm(
            prompt
        )

        cleaned = (
            self.clean_json_response(
                response_text
            )
        )

        data = json.loads(
            cleaned
        )

        result = (
            MeetingIntelligence
            .model_validate(data)
        )

        return result

    # =====================================
    # PROCESS NORMAL TRANSCRIPT
    # =====================================

    def process(
        self,
        transcript
    ):

        transcript = (
            self.validate_transcript(
                transcript
            )
        )

        max_retries = 3

        last_error = None

        for attempt in range(
            max_retries
        ):

            try:

                print(
                    f"\nAttempt "
                    f"{attempt + 1}/"
                    f"{max_retries}"
                )

                result = self.process_once(
                    transcript
                )

                print(
                    "\nPydantic validation "
                    "successful."
                )

                return result

            except Exception as error:

                last_error = error

                print(
                    "\nLLM processing error:"
                )

                print(error)

                error_text = str(error)

                transient_error = any(
                    code in error_text
                    for code in [
                        "429",
                        "500",
                        "502",
                        "503",
                        "504"
                    ]
                )

                if not transient_error:

                    raise

                if (
                    attempt
                    < max_retries - 1
                ):

                    wait_time = (
                        2 ** attempt
                    )

                    print(
                        f"Retrying in "
                        f"{wait_time} seconds..."
                    )

                    time.sleep(
                        wait_time
                    )

        raise RuntimeError(
            "LLM processing failed after "
            f"{max_retries} attempts: "
            f"{last_error}"
        )

    # =====================================
    # LONG TRANSCRIPT CHUNKING
    # =====================================

    def split_transcript(
        self,
        transcript,
        max_chars=18000
    ):

        transcript = (
            self.validate_transcript(
                transcript
            )
        )

        chunks = []

        start = 0

        while start < len(
            transcript
        ):

            end = min(
                start + max_chars,
                len(transcript)
            )

            # Prefer a newline boundary
            if end < len(transcript):

                boundary = (
                    transcript.rfind(
                        "\n",
                        start,
                        end
                    )
                )

                if boundary > (
                    start
                    + int(
                        max_chars * 0.6
                    )
                ):

                    end = boundary

            chunk = transcript[
                start:end
            ].strip()

            if chunk:

                chunks.append(
                    chunk
                )

            start = end

        return chunks

    # =====================================
    # LONG TRANSCRIPT PROCESSING
    # =====================================

    def process_long_transcript(
        self,
        transcript,
        max_chars=18000
    ):

        transcript = (
            self.validate_transcript(
                transcript
            )
        )

        # Normal meeting
        if len(transcript) <= max_chars:

            return self.process(
                transcript
            )

        print(
            "\nLong transcript detected."
        )

        chunks = (
            self.split_transcript(
                transcript,
                max_chars
            )
        )

        print(
            f"Transcript split into "
            f"{len(chunks)} chunks."
        )

        results = []

        for index, chunk in enumerate(
            chunks,
            start=1
        ):

            print(
                f"\nProcessing chunk "
                f"{index}/{len(chunks)}"
            )

            result = self.process(
                chunk
            )

            results.append(
                result
            )

        return self.merge_results(
            results
        )

    # =====================================
    # MERGE CHUNK RESULTS
    # =====================================

    def merge_results(
        self,
        results
    ):

        if not results:

            raise ValueError(
                "No results to merge."
            )

        summaries = []

        key_points = []
        decisions = []
        action_items = []
        participants = []

        for result in results:

            if result.summary:

                summaries.append(
                    result.summary
                )

            key_points.extend(
                result.key_points
            )

            decisions.extend(
                result.decisions
            )

            action_items.extend(
                result.action_items
            )

            participants.extend(
                result.participants
            )

        # Remove duplicate strings
        key_points = list(
            dict.fromkeys(
                key_points
            )
        )

        decisions = list(
            dict.fromkeys(
                decisions
            )
        )

        # Clean duplicate actions
        cleaned_actions = (
            clean_action_items(
                action_items
            )
        )

        # Clean duplicate participants
        cleaned_participants = (
            clean_participants(
                participants
            )
        )

        return MeetingIntelligence(

            summary=" ".join(
                summaries
            ),

            key_points=key_points,

            decisions=decisions,

            action_items=[
                ActionItem.model_validate(
                    item
                )
                for item in cleaned_actions
            ],

            participants=[
                Participant.model_validate(
                    item
                )
                for item in cleaned_participants
            ]
        )