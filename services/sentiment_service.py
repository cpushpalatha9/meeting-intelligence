import nltk
from nltk.sentiment import SentimentIntensityAnalyzer

try:
    _sia = SentimentIntensityAnalyzer()
except LookupError:
    nltk.download("vader_lexicon", quiet=True)
    _sia = SentimentIntensityAnalyzer()

def analyze_sentiment(text: str):
    scores = _sia.polarity_scores(text or "")
    compound = scores["compound"]
    label = "positive" if compound >= 0.05 else "negative" if compound <= -0.05 else "neutral"
    return {
        "label": label,
        "positive": scores["pos"],
        "negative": scores["neg"],
        "neutral": scores["neu"],
        "compound": compound,
    }
