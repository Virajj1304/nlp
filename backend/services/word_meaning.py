"""
Context-Aware Word Meaning Detector
=====================================
Uses NLTK WordNet + a simplified Lesk algorithm to perform
Word Sense Disambiguation (WSD).
"""

from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
from nltk.wsd import lesk


def detect_meaning(sentence: str, target_word: str) -> dict:
    """
    Disambiguate *target_word* in *sentence* using the Lesk algorithm.
    Returns the best sense, its definition, synonyms, and alternative senses.
    """
    target_word = target_word.strip().lower()
    tokens = word_tokenize(sentence)

    # ── Run Lesk ──────────────────────────────────────────────
    best_synset = lesk(tokens, target_word)

    # ── Gather all senses for the target word ─────────────────
    all_synsets = wn.synsets(target_word)

    if not all_synsets:
        return {
            "target_word": target_word,
            "found": False,
            "message": f"'{target_word}' was not found in WordNet. "
                       "Try a common English word.",
            "detected_sense": None,
            "definition": None,
            "synonyms": [],
            "alternative_senses": [],
        }

    # ── Build result ──────────────────────────────────────────
    if best_synset is None:
        # Lesk couldn't decide → fall back to the most common sense
        best_synset = all_synsets[0]
        note = ("The Lesk algorithm could not confidently disambiguate this "
                "word in the given context. Showing the most common sense.")
    else:
        note = None

    synonyms = sorted(
        {lem.name().replace("_", " ") for lem in best_synset.lemmas()}
        - {target_word}
    )

    alternative_senses = []
    for syn in all_synsets:
        if syn != best_synset:
            alternative_senses.append({
                "sense": syn.name(),
                "definition": syn.definition(),
                "pos": _pos_label(syn.pos()),
            })

    return {
        "target_word": target_word,
        "found": True,
        "note": note,
        "detected_sense": best_synset.name(),
        "definition": best_synset.definition(),
        "pos": _pos_label(best_synset.pos()),
        "synonyms": synonyms,
        "alternative_senses": alternative_senses,
    }


def _pos_label(pos_code: str) -> str:
    """Convert a WordNet POS code to a human-readable label."""
    mapping = {"n": "Noun", "v": "Verb", "a": "Adjective",
               "r": "Adverb", "s": "Adjective (satellite)"}
    return mapping.get(pos_code, pos_code)
