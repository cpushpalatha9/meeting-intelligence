import os
from pathlib import Path


class WhisperTranscriptionService:

    def __init__(self, model_size=None):

        self.model_size = (
            model_size
            or os.getenv("WHISPER_MODEL", "small")
        )

        self.model = None

    def load_model(self):

        if self.model is None:

            from faster_whisper import WhisperModel

            print(
                f"Loading Whisper model: "
                f"{self.model_size}"
            )

            self.model = WhisperModel(
                self.model_size,
                device="cpu",
                compute_type="int8"
            )

            print("Whisper model loaded.")

    def transcribe(self, audio_path):

        audio_path = Path(audio_path)

        if not audio_path.exists():

            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )

        self.load_model()

        print("Starting Whisper transcription...")

        segments, info = self.model.transcribe(
            str(audio_path),
            beam_size=5,
            vad_filter=True
        )

        text_parts = []

        for segment in segments:

            text = segment.text.strip()

            if text:

                text_parts.append(text)

        transcript = " ".join(
            text_parts
        ).strip()

        if not transcript:

            raise ValueError(
                "Whisper could not detect speech "
                "in the audio."
            )

        print("Whisper transcription completed.")

        return transcript, info.language