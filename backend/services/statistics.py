"""
TaskLens — Text Insights Service
==================================
Computes lightweight statistics, token metrics, word frequencies,
and bigram patterns from raw text using NLTK.
"""

from collections import Counter
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords

_stop_words = set(stopwords.words("english"))


def compute(text: str) -> dict:
    """Compute lexical and n-gram statistics for the given input text."""
    if not text or not text.strip():
        return {
            "word_count": 0,
            "sentence_count": 0,
            "unique_words": 0,
            "lexical_diversity": 0.0,
            "average_word_length": 0.0,
            "estimated_read_time": "0s",
            "most_frequent_words": [],
            "content_words_frequent": [],
            "common_bigrams": [],
        }

    sentences = sent_tokenize(text)
    all_tokens = word_tokenize(text)
    words = [t.lower() for t in all_tokens if t.isalpha()]

    if not words:
        return {
            "word_count": 0,
            "sentence_count": len(sentences),
            "unique_words": 0,
            "lexical_diversity": 0.0,
            "average_word_length": 0.0,
            "estimated_read_time": "0s",
            "most_frequent_words": [],
            "content_words_frequent": [],
            "common_bigrams": [],
        }

    word_count = len(words)
    unique_words = len(set(words))
    lexical_diversity = round((unique_words / word_count) * 100, 1)
    avg_len = round(sum(len(w) for w in words) / word_count, 1)

    # Reading time calculation (average 200 words per minute)
    read_seconds = max(1, round((word_count / 200) * 60))
    read_time_str = f"{read_seconds}s" if read_seconds < 60 else f"{round(read_seconds / 60, 1)}m"

    # All word frequencies
    freq = Counter(words)
    top_words = [
        {"word": w, "count": c, "percentage": round((c / word_count) * 100, 1)}
        for w, c in freq.most_common(8)
    ]

    # Content-only words (excluding stopwords)
    content_words = [w for w in words if w not in _stop_words]
    content_freq = Counter(content_words)
    top_content_words = [
        {"word": w, "count": c, "percentage": round((c / len(content_words)) * 100, 1)}
        for w, c in content_freq.most_common(8)
    ] if content_words else []

    # Common bigrams
    bigrams = [f"{words[i]} {words[i + 1]}" for i in range(len(words) - 1)]
    bigram_freq = Counter(bigrams)
    top_bigrams = [
        {"bigram": b, "count": c}
        for b, c in bigram_freq.most_common(6)
    ]

    return {
        "word_count": word_count,
        "sentence_count": len(sentences),
        "unique_words": unique_words,
        "lexical_diversity": lexical_diversity,
        "average_word_length": avg_len,
        "estimated_read_time": read_time_str,
        "most_frequent_words": top_words,
        "content_words_frequent": top_content_words,
        "common_bigrams": top_bigrams,
    }
