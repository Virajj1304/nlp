"""
Grammar & Sentence Analyzer
=====================================
Uses NLTK POS tagging + simple rule-based heuristics for
basic grammar suggestions (subject-verb agreement, article usage, etc.).
"""

import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn

_lemmatizer = WordNetLemmatizer()

# Map Penn Treebank tags to WordNet POS for lemmatization
_TAG_MAP = {
    "J": wn.ADJ,
    "V": wn.VERB,
    "N": wn.NOUN,
    "R": wn.ADV,
}

# Human-readable POS category descriptions
POS_DESCRIPTIONS = {
    "CC": "Coordinating conjunction",
    "CD": "Cardinal number",
    "DT": "Determiner",
    "EX": "Existential there",
    "FW": "Foreign word",
    "IN": "Preposition / subordinating conjunction",
    "JJ": "Adjective",
    "JJR": "Adjective, comparative",
    "JJS": "Adjective, superlative",
    "LS": "List item marker",
    "MD": "Modal",
    "NN": "Noun, singular or mass",
    "NNS": "Noun, plural",
    "NNP": "Proper noun, singular",
    "NNPS": "Proper noun, plural",
    "PDT": "Predeterminer",
    "POS": "Possessive ending",
    "PRP": "Personal pronoun",
    "PRP$": "Possessive pronoun",
    "RB": "Adverb",
    "RBR": "Adverb, comparative",
    "RBS": "Adverb, superlative",
    "RP": "Particle",
    "SYM": "Symbol",
    "TO": "to",
    "UH": "Interjection",
    "VB": "Verb, base form",
    "VBD": "Verb, past tense",
    "VBG": "Verb, gerund / present participle",
    "VBN": "Verb, past participle",
    "VBP": "Verb, non-3rd person singular present",
    "VBZ": "Verb, 3rd person singular present",
    "WDT": "Wh-determiner",
    "WP": "Wh-pronoun",
    "WP$": "Possessive wh-pronoun",
    "WRB": "Wh-adverb",
    ".": "Punctuation",
    ",": "Comma",
    ":": "Colon / semicolon",
    "(": "Opening bracket",
    ")": "Closing bracket",
    "``": "Opening quotation mark",
    "''": "Closing quotation mark",
    "#": "Hash / pound sign",
    "$": "Dollar sign",
}


def _get_wordnet_pos(tag: str) -> str:
    """Map Penn Treebank tag to WordNet POS constant."""
    return _TAG_MAP.get(tag[0].upper(), wn.NOUN)


def analyze(sentence: str) -> dict:
    """POS-tag, lemmatize, categorize, and run basic grammar checks."""
    tokens = word_tokenize(sentence)
    tagged = nltk.pos_tag(tokens)

    word_analysis = []
    nouns, verbs, adjectives, adverbs = [], [], [], []

    for word, tag in tagged:
        wn_pos = _get_wordnet_pos(tag)
        lemma = _lemmatizer.lemmatize(word.lower(), pos=wn_pos)
        desc = POS_DESCRIPTIONS.get(tag, tag)

        word_analysis.append({
            "word": word,
            "pos_tag": tag,
            "pos_description": desc,
            "lemma": lemma,
        })

        if tag.startswith("NN"):
            nouns.append(word)
        elif tag.startswith("VB"):
            verbs.append(word)
        elif tag.startswith("JJ"):
            adjectives.append(word)
        elif tag.startswith("RB"):
            adverbs.append(word)

    suggestions = _grammar_check(tokens, tagged)

    return {
        "tokens": tokens,
        "word_analysis": word_analysis,
        "nouns": nouns,
        "verbs": verbs,
        "adjectives": adjectives,
        "adverbs": adverbs,
        "suggestions": suggestions,
    }


# ── Rule-based grammar heuristics ────────────────────────────────────


# Common plural subjects that require a plural verb
_PLURAL_PRONOUNS = {"they", "we", "these", "those"}

# Singular subjects that require singular verb form
_SINGULAR_PRONOUNS = {"he", "she", "it", "this", "that"}

# "be" irregular forms lookup
_BE_SINGULAR = {"is", "was"}
_BE_PLURAL = {"are", "were"}

# Common irregular verbs: { base: third_person_singular }
_IRREGULAR_3SG = {
    "have": "has",
    "do": "does",
    "go": "goes",
}


def _grammar_check(tokens: list, tagged: list) -> list:
    """
    Apply simple rule-based grammar heuristics.
    Returns a list of suggestion dicts.
    """
    suggestions = []

    lower_tokens = [t.lower() for t in tokens]

    for i, (word, tag) in enumerate(tagged):
        lw = word.lower()

        # ── Rule 1: Plural noun + singular "be" verb ──────────
        if tag in ("NNS", "NNPS") and i + 1 < len(tagged):
            next_word = tokens[i + 1].lower()
            if next_word in _BE_SINGULAR:
                correction = "are" if next_word == "is" else "were"
                suggestions.append({
                    "type": "Subject-Verb Agreement",
                    "message": (
                        f"Plural subject \"{word}\" followed by singular "
                        f"verb \"{tokens[i+1]}\". Consider using "
                        f"\"{correction}\"."
                    ),
                    "position": i + 1,
                })

        # ── Rule 1b: Likely-plural noun tagged as NN + singular "be" ──
        # NLTK sometimes mis-tags plural nouns (e.g. "boys") as NN.
        if tag == "NN" and lw.endswith("s") and not lw.endswith("ss") and i + 1 < len(tagged):
            next_word = tokens[i + 1].lower()
            if next_word in _BE_SINGULAR:
                correction = "are" if next_word == "is" else "were"
                suggestions.append({
                    "type": "Subject-Verb Agreement",
                    "message": (
                        f"Possible plural subject \"{word}\" followed by "
                        f"singular verb \"{tokens[i+1]}\". If \"{word}\" "
                        f"is plural, consider using \"{correction}\"."
                    ),
                    "position": i + 1,
                })

        # ── Rule 2: Singular noun + plural "be" verb ──────────
        if tag in ("NN", "NNP") and i + 1 < len(tagged):
            next_word = tokens[i + 1].lower()
            if next_word in _BE_PLURAL:
                correction = "is" if next_word == "are" else "was"
                suggestions.append({
                    "type": "Subject-Verb Agreement",
                    "message": (
                        f"Singular subject \"{word}\" followed by plural "
                        f"verb \"{tokens[i+1]}\". Consider using "
                        f"\"{correction}\"."
                    ),
                    "position": i + 1,
                })

        # ── Rule 3: Pronoun–be agreement ──────────────────────
        if tag == "PRP" and i + 1 < len(tagged):
            next_word = tokens[i + 1].lower()
            if lw in _PLURAL_PRONOUNS and next_word in _BE_SINGULAR:
                correction = "are" if next_word == "is" else "were"
                suggestions.append({
                    "type": "Subject-Verb Agreement",
                    "message": (
                        f"Plural pronoun \"{word}\" followed by singular "
                        f"verb \"{tokens[i+1]}\". Consider using "
                        f"\"{correction}\"."
                    ),
                    "position": i + 1,
                })
            elif lw in _SINGULAR_PRONOUNS and next_word in _BE_PLURAL:
                correction = "is" if next_word == "are" else "was"
                suggestions.append({
                    "type": "Subject-Verb Agreement",
                    "message": (
                        f"Singular pronoun \"{word}\" followed by plural "
                        f"verb \"{tokens[i+1]}\". Consider using "
                        f"\"{correction}\"."
                    ),
                    "position": i + 1,
                })

        # ── Rule 4: "a" before a vowel-starting word ──────────
        if lw == "a" and tag == "DT" and i + 1 < len(tagged):
            next_word = tokens[i + 1].lower()
            if next_word and next_word[0] in "aeiou":
                suggestions.append({
                    "type": "Article Usage",
                    "message": (
                        f"Consider using \"an\" instead of \"a\" before "
                        f"\"{tokens[i+1]}\" (starts with a vowel sound)."
                    ),
                    "position": i,
                })

        # ── Rule 5: "an" before a consonant-starting word ────
        if lw == "an" and tag == "DT" and i + 1 < len(tagged):
            next_word = tokens[i + 1].lower()
            if next_word and next_word[0] not in "aeiou":
                suggestions.append({
                    "type": "Article Usage",
                    "message": (
                        f"Consider using \"a\" instead of \"an\" before "
                        f"\"{tokens[i+1]}\" (starts with a consonant sound)."
                    ),
                    "position": i,
                })

        # ── Rule 6: Double negative ──────────────────────────
        if lw in ("not", "n't") and tag == "RB":
            for j in range(i + 1, min(i + 4, len(tagged))):
                if tagged[j][0].lower() in (
                    "no", "nothing", "nobody", "nowhere",
                    "neither", "never", "none",
                ):
                    suggestions.append({
                        "type": "Double Negative",
                        "message": (
                            f"Possible double negative: \"{word}\" and "
                            f"\"{tagged[j][0]}\". This may be unintentional."
                        ),
                        "position": i,
                    })
                    break

    return suggestions
