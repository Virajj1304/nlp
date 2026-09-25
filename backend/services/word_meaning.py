"""
TaskLens — Context-Aware Word Meaning Service
===============================================
Performs Word Sense Disambiguation (WSD) using WordNet and the Lesk algorithm.

Given an input sentence and a target word:
  1. Tokenizes the sentence and filters stopwords.
  2. Compares sentence context against the definition and examples of each
     synset of the target word in WordNet.
  3. Selects the synset with the highest overlap (Lesk score) as the detected sense.
  4. Returns the detected sense, definition, synonyms, usage examples,
     overlap keywords, and ranked alternative senses.
"""

import re
from nltk.corpus import wordnet as wn
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

_lemmatizer = WordNetLemmatizer()
_stop_words = set(stopwords.words("english"))


def _clean_tokens(text: str) -> set[str]:
    """Tokenize, lowercase, and lemmatize non-stopword tokens."""
    tokens = [t.lower() for t in word_tokenize(text) if t.isalpha()]
    cleaned = set()
    for t in tokens:
        if t not in _stop_words:
            cleaned.add(t)
            cleaned.add(_lemmatizer.lemmatize(t, pos='n'))
            cleaned.add(_lemmatizer.lemmatize(t, pos='v'))
    return cleaned


def detect_meaning(sentence: str, target_word: str) -> dict:
    """
    Disambiguates `target_word` in `sentence` using the Lesk algorithm.
    """
    target_word = target_word.strip().lower()
    if not target_word:
        return {
            "target_word": "",
            "found": False,
            "message": "Please enter a target word."
        }

    # Gather all synsets for the target word
    all_synsets = wn.synsets(target_word)
    if not all_synsets:
        # Try lemmatizing the target word itself
        target_lemma = _lemmatizer.lemmatize(target_word)
        all_synsets = wn.synsets(target_lemma)

    if not all_synsets:
        return {
            "target_word": target_word,
            "found": False,
            "message": f"'{target_word}' was not found in WordNet. Try a standard English word (e.g., bank, crane, apple, plant, mouse, match).",
            "detected_sense": None,
            "definition": None,
            "synonyms": [],
            "alternative_senses": [],
        }

    # Context tokens from sentence (excluding the target word itself)
    sentence_tokens = _clean_tokens(sentence)
    target_clean = {target_word, _lemmatizer.lemmatize(target_word)}
    context_tokens = sentence_tokens - target_clean

    # Lesk algorithm: calculate overlap for each synset
    synset_scores = []
    for syn in all_synsets:
        # Build signature: definition + examples + hypernym definitions
        sig_text = syn.definition() + " " + " ".join(syn.examples())
        sig_tokens = _clean_tokens(sig_text)

        overlap = context_tokens.intersection(sig_tokens)
        synset_scores.append({
            "synset": syn,
            "overlap_count": len(overlap),
            "overlap_words": sorted(list(overlap)),
        })

    # Sort synsets by overlap score descending; preserve WordNet frequency order as secondary sort
    synset_scores.sort(key=lambda item: item["overlap_count"], reverse=True)

    best_match = synset_scores[0]
    best_synset = best_match["synset"]
    best_overlap = best_match["overlap_words"]

    # Gather synonyms for the chosen synset
    synonyms = sorted(
        {lem.name().replace("_", " ") for lem in best_synset.lemmas()}
        - {target_word}
    )

    # Format alternative senses
    alternative_senses = []
    for item in synset_scores[1:]:
        syn = item["synset"]
        alt_synonyms = sorted(
            {lem.name().replace("_", " ") for lem in syn.lemmas()}
            - {target_word}
        )
        alternative_senses.append({
            "sense": syn.name(),
            "definition": syn.definition(),
            "pos": _pos_label(syn.pos()),
            "overlap_count": item["overlap_count"],
            "overlap_words": item["overlap_words"],
            "synonyms": alt_synonyms[:6],
            "examples": syn.examples()[:2],
        })

    explanation = (
        f"The Lesk algorithm selected '{best_synset.name()}' because the sentence context "
        f"shared {len(best_overlap)} concept word(s) ({', '.join(best_overlap) if best_overlap else 'none - defaulted to primary sense'}) "
        f"with the WordNet definition and examples."
    )

    return {
        "target_word": target_word,
        "found": True,
        "sentence": sentence,
        "detected_sense": best_synset.name(),
        "definition": best_synset.definition(),
        "pos": _pos_label(best_synset.pos()),
        "synonyms": synonyms,
        "examples": best_synset.examples()[:3],
        "overlap_words": best_overlap,
        "lesk_score": best_match["overlap_count"],
        "explanation": explanation,
        "total_senses": len(all_synsets),
        "alternative_senses": alternative_senses,
    }


def _pos_label(pos_code: str) -> str:
    """Convert a WordNet POS tag to a readable label."""
    mapping = {
        "n": "Noun",
        "v": "Verb",
        "a": "Adjective",
        "r": "Adverb",
        "s": "Adjective (satellite)"
    }
    return mapping.get(pos_code, pos_code)
