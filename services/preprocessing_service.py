import re

def preprocess_text(text: str) -> str:
    text = text or ""
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"[^\w\s.,!?%:/@#&'()\-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def tokenize(text: str):
    return re.findall(r"\b[\w']+\b", (text or "").lower())

def remove_stopwords(tokens):
    stops = {"the","a","an","is","are","was","were","to","of","and","or","in","on","for","with","this","that","it"}
    return [t for t in tokens if t not in stops]
