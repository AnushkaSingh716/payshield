"""Loads the scam text model (TF-IDF + Logistic Regression)."""
import joblib
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

from app.config import SCAM_MODEL_PATH

_pipeline = None  # loaded once, then reused

# Word pieces that come from links; they make poor "reasons"
LINK_PIECES = {
    "http", "https", "www", "com", "bit", "ly", "tinyurl", "cutt",
    "xyz", "top", "info", "online",
}


def get_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = joblib.load(SCAM_MODEL_PATH)
    return _pipeline


def text_probability(text: str) -> float:
    """Chance (0 to 1) that the wording looks like a scam."""
    return float(get_pipeline().predict_proba([text])[0, 1])


def top_scam_words(text: str, n: int = 4) -> list[str]:
    """The words in this message that pushed the score toward scam the most."""
    pipeline = get_pipeline()
    tfidf = pipeline.named_steps["tfidf"]
    clf = pipeline.named_steps["clf"]

    row = tfidf.transform([text])
    contributions = row.multiply(clf.coef_[0]).tocsr()
    names = tfidf.get_feature_names_out()

    pairs = sorted(zip(contributions.data, contributions.indices), reverse=True)
    words = []
    for value, index in pairs:
        if value <= 0:
            break
        word = names[index]
        # Keep single, meaningful words (skip phrases, link pieces and filler like "to")
        if " " in word or word in LINK_PIECES or word in ENGLISH_STOP_WORDS:
            continue
        words.append(word)
        if len(words) >= n:
            break
    return words