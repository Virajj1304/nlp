"""
Text Statistics Service
========================
Computes word-level and N-gram statistics from raw text using NLTK.
"""

from collections import Counter
from nltk.tokenize import sent_tokenize, word_tokenize


def compute(text: str) -> dict:
    """Return comprehensive text statistics."""
    sentences = sent_tokenize(text)
    all_tokens = word_tokenize(text)
    words = [t.lower() for t in all_tokens if t.isalpha()]

    if not words:
        return {
            "word_count": 0,
            "sentence_count": len(sentences),
            "unique_words": 0,
            "average_word_length": 0,
            "most_frequent_words": [],
            "common_bigrams": [],
        }

    freq = Counter(words)
    avg_len = round(sum(len(w) for w in words) / len(words), 2)

    # Bigrams
    bigrams = [(words[i], words[i + 1]) for i in range(len(words) - 1)]
    bigram_freq = Counter(bigrams)

    return {
        "word_count": len(words),
        "sentence_count": len(sentences),
        "unique_words": len(set(words)),
        "average_word_length": avg_len,
        "most_frequent_words": [
            {"word": w, "count": c} for w, c in freq.most_common(10)
        ],
        "common_bigrams": [
            {"bigram": f"{b[0]} {b[1]}", "count": c}
            for b, c in bigram_freq.most_common(10)
        ],
    }
