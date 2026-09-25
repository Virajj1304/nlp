"""
TaskLens — Dynamic Task Extractor Service
==========================================
Converts arbitrary everyday messages, emails, and project notes into
structured actionable tasks using classical NLP:
  1. Sentence segmentation (NLTK Punkt)
  2. Universal Dynamic Assignee Extraction:
     - Handles ANY name: single names, full names, international names, usernames, lowercase
     - Vocative with punctuation: "Rahul, finish...", "rohan: check...", "Sarah Jenkins -"
     - Addressee with politeness/modals: "Viraj please finish...", "kavya need to make..."
     - Leading subject followed directly by action verb: "Michael finish the frontend...", "Alex deploy..."
     - Mentions: "@elena please check..." -> "Elena"
     - Prefixed assignments: "Assigned to Zhang:", "Task for Ananya:", "For David:"
  3. Action Verb Detection & Base Normalization:
     - Leverages NLTK POS Tagging (VB, VBP, VBZ, VBD, VBG) + WordNet verb morphology
     - Handles modal leading chains: "need to make", "needs to create", "must test", "has to review"
     - Normalizes to base lemma via WordNetLemmatizer
  4. Direct Object Noun Phrase Chunking
  5. Prepositional / Adverbial Temporal Phrase Extraction for Deadlines
  6. Urgency Scoring & Domain Classification
"""

import re
import nltk
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn

_lemmatizer = WordNetLemmatizer()

# Words that should not be mistaken for person names
NON_PERSON_WORDS = {
    "the", "a", "an", "this", "that", "these", "those", "it", "its", "they", "we", "you", "i", "he", "she",
    "please", "kindly", "also", "and", "then", "plus", "urgent", "asap", "note", "task", "meeting", "reminder",
    "today", "tomorrow", "tonight", "yesterday", "monday", "tuesday", "wednesday", "thursday", "friday",
    "saturday", "sunday", "mon", "tue", "wed", "thu", "fri", "sat", "sun", "hi", "hey", "hello", "dear",
    "can", "could", "should", "must", "will", "would", "may", "might", "do", "does", "did", "is", "are", "was", "were",
    "need", "needs", "have", "has", "had", "here", "there", "where", "when", "why", "how", "what", "which", "who",
    "all", "everyone", "team", "folks", "action", "update", "status", "deadline", "priority"
}

AUXILIARY_VERBS = {
    "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had",
    "do", "does", "did",
    "can", "could", "should", "would", "may", "might", "must", "will", "shall"
}

DAYS_MAP = {
    "monday": "Monday", "tuesday": "Tuesday", "wednesday": "Wednesday",
    "thursday": "Thursday", "friday": "Friday", "saturday": "Saturday", "sunday": "Sunday",
    "mon": "Monday", "tue": "Tuesday", "wed": "Wednesday", "thu": "Thursday",
    "fri": "Friday", "sat": "Saturday", "sun": "Sunday"
}

RELATIVE_TIMES = {
    "today": "Today", "tomorrow": "Tomorrow", "tonight": "Tonight", "yesterday": "Yesterday",
    "eod": "End of Day (EOD)", "eow": "End of Week (EOW)",
    "asap": "ASAP", "morning": "Morning", "afternoon": "Afternoon",
    "evening": "Evening", "noon": "Noon", "midnight": "Midnight"
}

PREPOSITIONS_TIME = {"by", "before", "until", "till", "due", "on", "at"}

DOMAIN_KEYWORDS = {
    "Tech / Engineering": {
        "backend", "frontend", "api", "bug", "code", "deploy", "database", "test",
        "pr", "commit", "docker", "server", "git", "release", "build", "endpoint",
        "refactor", "repo", "pipeline", "auth", "schema", "ui", "ux", "ui/ux", "css"
    },
    "Academic / College": {
        "assignment", "lab", "submission", "exam", "professor", "syllabus", "project",
        "lecture", "marks", "seminar", "viva", "campus", "homework", "class",
        "college", "course", "grade", "quiz", "department", "ppt"
    },
    "Product / Meeting": {
        "meeting", "sync", "client", "demo", "presentation", "slides", "notes",
        "roadmap", "sprint", "stakeholder", "minutes", "standup", "agenda", "call"
    },
    "Operations / Admin": {
        "invoice", "email", "budget", "contract", "hire", "onboarding", "approval",
        "documentation", "schedule", "report", "doc", "sheet", "policy", "form"
    }
}


def clean_name(name_str: str) -> str:
    """Normalize capitalization for any extracted name."""
    parts = [p.capitalize() for p in name_str.strip().split() if p]
    return " ".join(parts)


def is_action_verb(word: str, tag: str = "") -> bool:
    """Check dynamically if a token represents an actionable verb using POS tags and WordNet."""
    w_low = word.lower()
    if w_low in AUXILIARY_VERBS or w_low in {"please", "kindly", "need", "needs", "to"}:
        return False
    if tag.startswith("VB"):
        return True
    if wn.synsets(w_low, pos=wn.VERB):
        return True
    return False


def parse_assignee_from_sentence(sentence: str) -> tuple[str | None, str]:
    """
    Universally extracts ANY person's name (Western, Indian, international, usernames, lowercase)
    from live conversational messages and notes.
    """
    cleaned = sentence.strip()

    # 1. Prefixed assignment: 'Task for X:', 'Assigned to X:', 'For X:'
    m_pref = re.match(
        r'^(?:task\s+for|assigned\s+to|for)\s+([A-Za-z0-9_]+(?:\s+[A-Za-z0-9_]+)?)\s*[:,\-]\s*(.*)$',
        cleaned,
        re.I
    )
    if m_pref:
        cand = m_pref.group(1).strip()
        if cand.lower() not in NON_PERSON_WORDS:
            return clean_name(cand), m_pref.group(2)

    # 2. Mention: @username
    m_men = re.match(
        r'^(?:(?:hey|hi|hello|dear)\s+)?@([A-Za-z0-9_]+)\s*[,:\-]?\s*(.*)$',
        cleaned,
        re.I
    )
    if m_men:
        cand = m_men.group(1).strip()
        if cand.lower() not in NON_PERSON_WORDS:
            return clean_name(cand), m_men.group(2)

    # 3. Vocative with punctuation: 'Rahul,' or 'rohan,' or 'Sarah Jenkins:'
    m_voc = re.match(
        r'^(?:(?:hey|hi|hello|dear|also)\s+)?([A-Za-z0-9_]+(?:\s+[A-Za-z0-9_]+)?)\s*[,:\-]\s*(.*)$',
        cleaned,
        re.I
    )
    if m_voc:
        cand = m_voc.group(1).strip()
        if cand.lower() not in NON_PERSON_WORDS:
            return clean_name(cand), m_voc.group(2)

    # 4. Name + modal/politeness: 'Viraj please...', 'Vaidehi need to...', 'Aarav Sharma will...'
    m_lead = re.match(
        r'^(?:(?:hey|hi|hello|dear|also)\s+)?([A-Za-z0-9_]+(?:\s+(?!please|kindly|needs?|has|have|must|should|will|to)[A-Za-z0-9_]+)?)\s+(?:please|kindly|needs?|has|have|must|should|will|is\s+to|to)\s*(?:to\s+)?(.*)$',
        cleaned,
        re.I
    )
    if m_lead:
        cand = m_lead.group(1).strip()
        if cand.lower() not in NON_PERSON_WORDS:
            return clean_name(cand), m_lead.group(2)

    # 5. Name + action verb directly: 'Viraj finish the UI/UX...', 'rohan deploy...'
    tokens = cleaned.split()
    if len(tokens) >= 2:
        first = tokens[0]
        if first.lower() not in NON_PERSON_WORDS and is_action_verb(tokens[1]):
            remainder = " ".join(tokens[1:])
            return clean_name(first), remainder

    return None, cleaned


def parse_deadline(tokens: list[str], start_idx: int) -> tuple[str, str]:
    """Extract and format temporal expression for deadline."""
    dl_tokens = []
    for j in range(start_idx, len(tokens)):
        t = tokens[j]
        t_low = t.lower()
        if t in {",", ";", "!", "?"} or t_low in {"urgent", "asap", "immediately", "critical", "please"}:
            break
        dl_tokens.append(t)

    raw_dl = " ".join(dl_tokens).strip(" .,!?:;")
    if not raw_dl:
        return "No deadline", "None"

    m_prep = re.match(r'^(?:by|on|at|due\s+on|due\s+by|due|before)\s+(.*)$', raw_dl, re.I)
    if m_prep and m_prep.group(1).strip():
        clean_dl = m_prep.group(1).strip(" .,!?:;")
    else:
        clean_dl = raw_dl

    # Capitalize cleanly if standard weekday/relative day
    if clean_dl.lower() in DAYS_MAP:
        clean_dl = DAYS_MAP[clean_dl.lower()]
    elif clean_dl.lower() in RELATIVE_TIMES:
        clean_dl = RELATIVE_TIMES[clean_dl.lower()]

    return clean_dl, raw_dl


def parse_clause(
    clause: str,
    full_sentence: str,
    default_assignee: str | None = None,
    default_priority: str | None = None,
) -> dict | None:
    """
    Parse a single action clause using POS tagging and rule-based chunking.
    """
    tokens = word_tokenize(clause)
    if not tokens:
        return None

    pos_tags = nltk.pos_tag(tokens)

    # 1. Determine Priority
    priority = default_priority or "Normal"
    if re.search(r'\b(urgent|asap|immediately|critical|emergency|high\s*priority|priority:\s*high)\b|!', clause, re.I):
        priority = "High"
    elif re.search(r'\b(low\s*priority|priority:\s*low|no\s*rush|whenever|when\s*free|optional)\b', clause, re.I):
        priority = "Low"

    # 2. Identify the Action Verb
    verb_idx = -1
    action_verb = None
    action_lemma = None

    for i, (w, tag) in enumerate(pos_tags):
        w_low = w.lower()
        if w_low in {"please", "kindly", "can", "could", "you", "we", "i", "also", "just", "need", "needs", "to", "must", "should", "make_sure"}:
            continue
        lemma = _lemmatizer.lemmatize(w_low, pos='v')
        if is_action_verb(w, tag):
            verb_idx = i
            action_verb = w
            action_lemma = lemma
            break

    if verb_idx == -1:
        # Fallback check on initial token
        w_first = tokens[0].lower()
        lemma = _lemmatizer.lemmatize(w_first, pos='v')
        if is_action_verb(tokens[0], pos_tags[0][1]):
            verb_idx = 0
            action_verb = tokens[0]
            action_lemma = lemma

    if verb_idx == -1:
        return None

    # 3. Identify Deadline
    deadline = None
    raw_deadline = None
    deadline_start_idx = -1

    for i in range(verb_idx + 1, len(pos_tags)):
        w, _ = pos_tags[i]
        w_low = w.lower()
        if w_low in PREPOSITIONS_TIME or w_low in DAYS_MAP or w_low in RELATIVE_TIMES or re.match(r'^\d{1,2}(?::\d{2})?(?:am|pm)?$', w_low):
            deadline_start_idx = i
            deadline, raw_deadline = parse_deadline(tokens, i)
            break

    # 4. Extract Task / Object
    if deadline_start_idx != -1:
        obj_tokens = tokens[verb_idx + 1:deadline_start_idx]
    else:
        obj_tokens = tokens[verb_idx + 1:]

    clean_obj_tokens = [
        t for t in obj_tokens
        if t.lower() not in {"urgent", "asap", "immediately", "please", "kindly"}
        and t not in {".", ",", "!", "?", ";", ":"}
    ]
    task_object = " ".join(clean_obj_tokens).strip()
    if not task_object:
        task_object = "Task details"

    # 5. Domain / Context Classification
    context = "General Task"
    clause_words = {t.lower() for t in tokens}
    for dom, kws in DOMAIN_KEYWORDS.items():
        if clause_words.intersection(kws):
            context = dom
            break

    action_display = (action_lemma or action_verb).capitalize()

    # Clean display title (e.g. "FINISH BACKEND")
    clean_title_obj = re.sub(r'^(the|a|an)\s+', '', task_object, flags=re.I).strip()
    title = f"{action_display.upper()} {clean_title_obj.upper()}"

    deadline_display = deadline if deadline else "No deadline"
    assignee_display = default_assignee if default_assignee else "Unassigned"

    nlp_breakdown = {
        "tokens": [{"token": t, "tag": tag} for t, tag in pos_tags],
        "action_lemma": action_lemma,
        "action_verb": action_verb,
        "raw_object": task_object,
        "detected_deadline": deadline or "None",
        "clause_text": clause,
        "full_sentence": full_sentence,
        "pos_tags_summary": " ".join(f"{t}/{tag}" for t, tag in pos_tags),
        "steps": [
            f"Assignee dynamically resolved to '{assignee_display}' from sentence subject/vocative analysis.",
            f"Action verb identified as '{action_verb}' tagged '{pos_tags[verb_idx][1]}', lemmatized to '{action_lemma}'.",
            f"Direct object noun phrase extracted: '{task_object}'.",
            f"Temporal expression parsed as '{deadline_display}'.",
            f"Priority computed as '{priority}'."
        ]
    }

    return {
        "title": title,
        "action": action_display,
        "task_object": task_object,
        "assignee": assignee_display,
        "deadline": deadline_display,
        "priority": priority,
        "context": context,
        "nlp_breakdown": nlp_breakdown
    }


def extract_tasks(text: str) -> dict:
    """
    Main entry point for task extraction from any user input in real time.
    Handles arbitrary names, compound sentences, emails, and notes.
    """
    if not text or not text.strip():
        return {"tasks": [], "count": 0, "original_text": text}

    lines = text.splitlines()
    all_sentences = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        cleaned_line = re.sub(r'^(\d+[\.\)]|[\-\*\•])\s*', '', line)
        sents = sent_tokenize(cleaned_line)
        all_sentences.extend(sents)

    tasks = []

    # Detect global priority cues across the entire text
    global_priority = None
    if re.search(r'\b(urgent|asap|immediately|critical|emergency|high\s*priority|priority:\s*high)\b|!{2,}', text, re.I):
        global_priority = "High"
    elif re.search(r'\b(low\s*priority|priority:\s*low|no\s*rush|whenever|when\s*free|optional)\b', text, re.I):
        global_priority = "Low"

    for sentence in all_sentences:
        sentence = sentence.strip()
        if not sentence:
            continue

        sent_priority = global_priority
        if re.search(r'\b(urgent|asap|immediately|critical|emergency|high\s*priority|priority:\s*high)\b|!', sentence, re.I):
            sent_priority = "High"
        elif re.search(r'\b(low\s*priority|priority:\s*low|no\s*rush|whenever|when\s*free|optional)\b', sentence, re.I):
            sent_priority = "Low"

        # Dynamically extract person name / assignee
        assignee, remainder = parse_assignee_from_sentence(sentence)

        # Coordinated clause splitting ("... and ...", ";", "also", "then")
        clauses = re.split(r'\s+(?:and\s+also|and\s+then|and|also|then|plus)\s+|[;\n]+', remainder, flags=re.I)

        for clause in clauses:
            clause = clause.strip()
            if not clause:
                continue

            task = parse_clause(
                clause,
                sentence,
                default_assignee=assignee,
                default_priority=sent_priority
            )
            if task:
                tasks.append(task)

    return {
        "tasks": tasks,
        "count": len(tasks),
        "original_text": text
    }
