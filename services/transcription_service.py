import os
import tempfile
from pathlib import Path
from typing import Optional, Tuple
from faster_whisper import WhisperModel

class WhisperTranscriptionService:
    def __init__(self, model_size: Optional[str] = None, device: Optional[str] = None, compute_type: Optional[str] = None):
        self.model_size = model_size or os.getenv("WHISPER_MODEL","small")
        self.device = device or os.getenv("WHISPER_DEVICE","cpu")
        self.compute_type = compute_type or os.getenv("WHISPER_COMPUTE_TYPE","int8")
        self.model = None

    def _load_model(self):
        if self.model is None:
            self.model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
        return self.model

    def transcribe_file(self, file_path: str) -> Tuple[str,str]:
        path = Path(file_path)
        if not path.exists(): raise FileNotFoundError(file_path)
        model = self._load_model()
        segments, info = model.transcribe(str(path), beam_size=5, vad_filter=True)
        transcript = " ".join(s.text.strip() for s in segments if s.text.strip()).strip()
        if not transcript:
            raise ValueError("Whisper generated an empty transcript.")
        return transcript, getattr(info,"language","unknown")

    def transcribe(self, file_path: str):
        transcript, language = self.transcribe_file(file_path)
        return {"transcript": transcript, "language": language}

    def transcribe_audio(self, file_path: str):
        return self.transcribe_file(file_path)

    def transcribe_uploaded_file(self, uploaded_file):
        suffix = Path(uploaded_file.name).suffix or ".wav"
        tmp = None
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as f:
                f.write(uploaded_file.getbuffer()); tmp = f.name
            return self.transcribe_file(tmp)
        finally:
            if tmp:
                try: os.remove(tmp)
                except OSError: pass
