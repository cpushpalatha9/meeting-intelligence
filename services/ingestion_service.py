from pathlib import Path

SUPPORTED_FORMATS = {"mp3","wav","m4a","mp4","webm","ogg","flac","aac"}

def validate_uploaded_file(uploaded_file, max_mb=500):
    if uploaded_file is None:
        raise ValueError("No file was uploaded.")
    ext = Path(uploaded_file.name).suffix.lower().lstrip(".")
    if ext not in SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported format: {ext}")
    if getattr(uploaded_file, "size", 0) > max_mb * 1024 * 1024:
        raise ValueError(f"File exceeds {max_mb} MB limit.")
    return True

def validate_transcript(text, min_chars=10):
    text = (text or "").strip()
    if len(text) < min_chars:
        return False, f"Transcript is too short. Minimum {min_chars} characters."
    words = text.split()
    if len(words) < 3:
        return False, "Transcript must contain at least three words."
    return True, "Valid transcript."

def read_text_input(text):
    valid, msg = validate_transcript(text)
    if not valid:
        raise ValueError(msg)
    return text.strip()
