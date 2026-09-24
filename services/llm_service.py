# services/llm_service.py

import json
import os
import random
import re
import time
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from google import genai

from prompts.meeting_prompt import (
    build_meeting_prompt,
    build_rag_prompt,
)
from schemas.meeting_schema import (
    MeetingIntelligence,
)


load_dotenv(override=True)


class GeminiError(Exception):
    """Base Gemini service error."""


class GeminiQuotaError(GeminiError):
    """Gemini quota/rate-limit error."""


class GeminiTemporaryError(GeminiError):
    """Temporary Gemini service error."""


class GeminiPermanentError(GeminiError):
    """Permanent Gemini configuration/request error."""


class LLMService:

    def __init__(self):

        self.api_key = os.getenv(
            "GEMINI_API_KEY",
            ""
        ).strip()

        self.model = os.getenv(
            "GEMINI_MODEL",
            "gemini-3.8-flash"
        ).strip()

        if not self.api_key:

            raise GeminiPermanentError(
                "GEMINI_API_KEY is missing. "
                "Add your Gemini API key to the .env file."
            )

        try:

            self.client = genai.Client(
                api_key=self.api_key
            )

        except Exception as exc:

            raise GeminiPermanentError(
                f"Unable to initialize Gemini client: {exc}"
            ) from exc

    # ========================================================
    # ERROR CLASSIFICATION
    # ========================================================

    @staticmethod
    def _classify_error(exc: Exception) -> str:

        message = str(exc).lower()

        # Daily/project quota
        daily_patterns = [
            "generate_content_free_tier_requests",
            "perdayperprojectpermodel",
            "per_day_per_project_per_model",
            "daily quota",
            "quota exceeded",
            "exceeded your current quota",
        ]

        if any(
            pattern in message
            for pattern in daily_patterns
        ):

            return "daily_quota"

        # Short-term rate limiting
        if (
            "429" in message
            or "rate limit" in message
            or "resource exhausted" in message
        ):

            return "quota"

        # Temporary server conditions
        temporary_patterns = [
            "500",
            "502",
            "503",
            "504",
            "unavailable",
            "timeout",
            "deadline exceeded",
            "temporarily",
        ]

        if any(
            pattern in message
            for pattern in temporary_patterns
        ):

            return "temporary"

        # Authentication
        authentication_patterns = [
            "401",
            "403",
            "api key",
            "authentication",
            "permission denied",
            "unauthorized",
        ]

        if any(
            pattern in message
            for pattern in authentication_patterns
        ):

            return "authentication"

        # Invalid model/request
        permanent_patterns = [
            "400",
            "404",
            "not found",
            "invalid argument",
            "invalid model",
            "unsupported",
        ]

        if any(
            pattern in message
            for pattern in permanent_patterns
        ):

            return "permanent"

        return "unknown"

    # ========================================================
    # JSON CLEANING
    # ========================================================

    @staticmethod
    def _extract_json(text: str) -> Dict[str, Any]:

        if not text:

            raise GeminiPermanentError(
                "Gemini returned an empty response."
            )

        cleaned = text.strip()

        # Remove Markdown code fences
        cleaned = re.sub(
            r"^```(?:json)?",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"```$",
            "",
            cleaned,
        )

        cleaned = cleaned.strip()

        # Direct JSON
        try:

            result = json.loads(
                cleaned
            )

            if isinstance(
                result,
                dict
            ):

                return result

        except json.JSONDecodeError:

            pass

        # Search for JSON object
        match = re.search(
            r"\{.*\}",
            cleaned,
            flags=re.DOTALL,
        )

        if match:

            try:

                result = json.loads(
                    match.group(0)
                )

                if isinstance(
                    result,
                    dict
                ):

                    return result

            except json.JSONDecodeError:

                pass

        raise GeminiPermanentError(
            "Gemini returned invalid JSON."
        )

    # ========================================================
    # NORMALIZE RESULT
    # ========================================================

    @staticmethod
    def _normalize_result(
        data: Dict[str, Any]
    ) -> Dict[str, Any]:

        defaults = {

            "summary": "",

            "key_points": [],

            "decisions": [],

            "action_items": [],

            "participants": [],

            "deadlines": [],

            "priorities": [],
        }

        for key, default in defaults.items():

            if key not in data:

                data[key] = default

        # Pydantic validation
        try:

            validated = (
                MeetingIntelligence(
                    **data
                )
            )

            return validated.model_dump()

        except Exception as exc:

            raise GeminiPermanentError(
                f"Gemini response validation failed: {exc}"
            ) from exc

    # ========================================================
    # SINGLE GENERATION REQUEST
    # ========================================================

    def _generate(
        self,
        prompt: str,
        max_retries: int = 4,
    ) -> str:

        last_error = None

        for attempt in range(
            1,
            max_retries + 1
        ):

            try:

                response = (
                    self.client
                    .models
                    .generate_content(
                        model=self.model,
                        contents=prompt,
                    )
                )

                text = getattr(
                    response,
                    "text",
                    None,
                )

                if not text:

                    raise GeminiPermanentError(
                        "Gemini returned no text."
                    )

                return text

            except GeminiPermanentError:

                raise

            except Exception as exc:

                last_error = exc

                category = (
                    self._classify_error(
                        exc
                    )
                )

                # Daily quota is not fixed by retrying.
                if category == "daily_quota":

                    raise GeminiQuotaError(
                        "Gemini daily/project generation quota "
                        "has been reached. A new API key in the "
                        "same Google project will not reset this "
                        "quota. Wait for the quota reset or use "
                        "a project/quota with available capacity."
                    ) from exc

                # Authentication should be shown immediately.
                if category == "authentication":

                    raise GeminiPermanentError(
                        "Gemini authentication failed. "
                        "Check GEMINI_API_KEY in .env."
                    ) from exc

                # Invalid model/request.
                if category == "permanent":

                    raise GeminiPermanentError(
                        f"Gemini rejected the request: {exc}"
                    ) from exc

                # Temporary/rate-limit errors can retry.
                if (
                    category
                    in {
                        "quota",
                        "temporary",
                        "unknown",
                    }
                ):

                    if attempt >= max_retries:

                        if category == "quota":

                            raise GeminiQuotaError(
                                "Gemini is rate-limited. "
                                "Please try again later."
                            ) from exc

                        raise GeminiTemporaryError(
                            f"Gemini temporarily failed: {exc}"
                        ) from exc

                    delay = min(
                        2 ** attempt,
                        20,
                    )

                    delay += random.uniform(
                        0,
                        1,
                    )

                    time.sleep(
                        delay
                    )

        raise GeminiTemporaryError(
            f"Gemini request failed: {last_error}"
        )

    # ========================================================
    # TRANSCRIPT PROCESSING
    # ========================================================

    def process_transcript(
        self,
        transcript: str,
    ) -> Dict[str, Any]:

        if not transcript or not transcript.strip():

            raise ValueError(
                "Transcript is empty."
            )

        prompt = build_meeting_prompt(
            transcript.strip()
        )

        response_text = self._generate(
            prompt
        )

        data = self._extract_json(
            response_text
        )

        return self._normalize_result(
            data
        )

    # ========================================================
    # COMPATIBILITY ALIASES
    # ========================================================

    def process(
        self,
        transcript: str,
    ):

        return self.process_transcript(
            transcript
        )

    def analyze(
        self,
        transcript: str,
    ):

        return self.process_transcript(
            transcript
        )

    def analyze_meeting(
        self,
        transcript: str,
    ):

        return self.process_transcript(
            transcript
        )

    # ========================================================
    # LONG TRANSCRIPTS
    # ========================================================

    def process_long_transcript(
        self,
        transcript: str,
        max_chars: int = 50000,
    ):

        transcript = (
            transcript or ""
        ).strip()

        if not transcript:

            raise ValueError(
                "Transcript is empty."
            )

        if len(transcript) <= max_chars:

            return self.process_transcript(
                transcript
            )

        # Keep the beginning and end for very long meetings.
        first_part = (
            max_chars * 2 // 3
        )

        last_part = (
            max_chars - first_part
        )

        reduced = (
            transcript[:first_part]
            + "\n\n[...middle of transcript omitted...]\n\n"
            + transcript[-last_part:]
        )

        return self.process_transcript(
            reduced
        )

    # ========================================================
    # RAG ANSWER
    # ========================================================

    def generate_rag_answer(
        self,
        question: str,
        context: str,
    ) -> str:

        if not question.strip():

            raise ValueError(
                "Question is empty."
            )

        if not context.strip():

            return (
                "The meeting repository does not contain "
                "enough evidence to answer this question."
            )

        prompt = build_rag_prompt(
            question.strip(),
            context.strip(),
        )

        return self._generate(
            prompt
        ).strip()

    # ========================================================
    # HEALTH CHECK
    # ========================================================

    def health_check(
        self,
        make_request: bool = False,
    ):

        result = {
            "status": "configured",
            "model": self.model,
            "api_key_configured": bool(
                self.api_key
            ),
        }

        # Do not consume a Gemini request just to
        # render the Streamlit dashboard.
        if not make_request:

            return result

        try:

            response = (
                self.client
                .models
                .generate_content(
                    model=self.model,
                    contents="Reply with OK.",
                )
            )

            result[
                "status"
            ] = "healthy"

            result[
                "response"
            ] = getattr(
                response,
                "text",
                "",
            )

            return result

        except Exception as exc:

            result[
                "status"
            ] = "unavailable"

            result[
                "error"
            ] = str(exc)

            return result