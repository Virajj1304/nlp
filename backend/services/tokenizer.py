"""
Tokenization & Lemmatization Service
=====================================
Uses NLTK for:
  - Sentence segmentation   (sent_tokenize)
  - Word tokenization        (word_tokenize)
  - Lemmatization            (WordNetLemmatizer)
"""

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer

_lemmatizer = WordNetLemmatizer()


def analyze(text: str) -> dict:
    """Tokenize and lemmatize the input text, return statistics."""
    sentences = sent_tokenize(text)
    words = word_tokenize(text)

    # Keep only alphabetic tokens for meaningful stats
    alpha_words = [w for w in words if w.isalpha()]

    lemmas = []
    for word in alpha_words:
        lemma = _lemmatizer.lemmatize(word.lower())
        lemmas.append({"original": word, "lemma": lemma})

    unique = set(w.lower() for w in alpha_words)

    return {
        "sentences": sentences,
        "tokens": words,
        "lemmas": lemmas,
        "total_words": len(alpha_words),
        "unique_words": len(unique),
        "sentence_count": len(sentences),
    }
