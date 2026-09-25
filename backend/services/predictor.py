"""
TaskLens — Smart Task & Sentence Predictor (N-Gram Language Model)
===================================================================
Builds statistical Unigram, Bigram, and Trigram language models from a local
corpus of task messages, project emails, meeting notes, college deadlines,
and technical workflows.

Calculates actual corpus frequencies and Laplace (Add-One) smoothed probabilities:
  P(w3 | w1, w2) = (Count(w1, w2, w3) + 1) / (Count(w1, w2) + |V|)
Fallback hierarchy:
  Trigram context (w_{t-2}, w_{t-1})
    → Bigram fallback (w_{t-1})
      → Unigram fallback (most frequent words in corpus)
"""

from collections import Counter, defaultdict
from nltk.tokenize import word_tokenize

# Local corpus tailored for everyday workplace messages, college assignments,
# task management, engineering notes, and productivity workflows.
CORPUS_SENTENCES = [
    # Workplace & Task requests (including target test phrases)
    "Please send the report to the client before noon.",
    "Please send the document to the team for review.",
    "Please send the presentation slides to the manager.",
    "Please send the file as soon as possible.",
    "Please send the report by tomorrow morning.",
    "Please send the document before the sync meeting.",
    "Please send the presentation for the client demo.",
    "Please send the file to the engineering channel.",
    "Please send the invoice to the finance department.",
    "Please send the spreadsheet with the quarterly data.",
    "Please send the project updates to all stakeholders.",
    "Please send the meeting notes after the discussion.",

    # Engineering & Development tasks
    "Rahul finish the backend by Wednesday.",
    "Please finish the backend implementation and write tests.",
    "Finish the backend API endpoints before the sprint demo.",
    "Finish the frontend components for the user dashboard.",
    "Check the documentation before Thursday.",
    "Please check the documentation for any missing endpoints.",
    "Review the pull request before merging to main.",
    "Deploy the release build to the staging server on Friday.",
    "Deploy the application to the cloud production environment.",
    "Fix the critical bug in the authentication service.",
    "Update the database schema to support new user roles.",
    "Write unit tests for the core business logic.",
    "Refactor the legacy codebase to improve performance.",
    "Configure the CI/CD pipeline for automated testing.",
    "Monitor server logs for unexpected errors or high latency.",
    "Create a new branch for the feature implementation.",
    "Merge the feature branch into development after approval.",
    "Test the user interface across mobile and desktop browsers.",

    # College & Academic project workflows
    "Hey Priya submit the assignment before five PM tomorrow.",
    "Submit the assignment on the student portal before Friday.",
    "Submit the project proposal to the professor for feedback.",
    "Prepare the presentation slides for the college seminar.",
    "Prepare the final report for the mini project evaluation.",
    "Complete the lab exercises before the end of the week.",
    "Schedule a study group session for the upcoming exam.",
    "Download the dataset for the machine learning lab.",
    "Submit the research paper draft to the advisor.",
    "Attend the guest lecture on artificial intelligence tomorrow.",
    "Review the course syllabus before the midterm examination.",

    # Meetings, Operations & Scheduling
    "Schedule a meeting with the client on Monday.",
    "Schedule a quick sync with the design team.",
    "Discuss the project timeline during the morning standup.",
    "Share the meeting agenda with the participants in advance.",
    "Take notes during the client discussion and send a summary.",
    "Follow up with the customer regarding their feedback.",
    "Confirm the delivery date with the external vendor.",
    "Organize the team files in the shared workspace drive.",
    "Update the sprint backlog with the new action items.",
    "Send the weekly status update email to the director.",

    # General Productivity & Communication
    "Make sure to test all edge cases thoroughly.",
    "Keep the communication clear and concise.",
    "Prioritize the high impact tasks first thing in the morning.",
    "Track the progress of each deliverable on the Kanban board.",
    "Document all decisions made during the architecture review.",
    "Ensure the deployment checklist is completed before launch."
]


class NGramModel:
    """Statistical N-Gram Language Model with Laplace smoothing."""

    def __init__(self):
        self.unigrams: Counter = Counter()
        self.bigrams: Counter = Counter()
        self.trigrams: Counter = Counter()
        self.bigram_context: dict[tuple, Counter] = defaultdict(Counter)
        self.trigram_context: dict[tuple, Counter] = defaultdict(Counter)
        self.vocab: set[str] = set()
        self.total_unigrams: int = 0
        self._build_model()

    def _build_model(self):
        """Tokenize corpus and construct n-gram frequency distributions."""
        for sentence in CORPUS_SENTENCES:
            tokens = [t.lower() for t in word_tokenize(sentence) if t.isalpha()]
            self.vocab.update(tokens)
            self.unigrams.update(tokens)

            # Bigrams
            for i in range(len(tokens) - 1):
                bg = (tokens[i], tokens[i + 1])
                self.bigrams[bg] += 1
                self.bigram_context[(tokens[i],)][tokens[i + 1]] += 1

            # Trigrams
            for i in range(len(tokens) - 2):
                tg = (tokens[i], tokens[i + 1], tokens[i + 2])
                self.trigrams[tg] += 1
                self.trigram_context[(tokens[i], tokens[i + 1])][tokens[i + 2]] += 1

        self.total_unigrams = sum(self.unigrams.values())

    def predict(self, text: str, top_k: int = 5) -> dict:
        """
        Predict the next word for the given input text.
        Returns top-k candidate words ranked by Laplace-smoothed probabilities.
        """
        tokens = [t.lower() for t in word_tokenize(text) if t.isalpha()]

        if not tokens:
            return {
                "input": text,
                "context_used": None,
                "model": None,
                "predictions": [],
                "message": "Enter some text to see statistical next-word suggestions.",
            }

        vocab_size = len(self.vocab)

        # 1. Trigram model (w_{t-2}, w_{t-1})
        if len(tokens) >= 2:
            ctx = (tokens[-2], tokens[-1])
            counts = self.trigram_context.get(ctx)
            if counts:
                total = sum(counts.values())
                predictions = self._top_predictions(counts, total, vocab_size, top_k)
                return {
                    "input": text,
                    "context_used": " ".join(ctx),
                    "model": "Trigram Model",
                    "formula": "P(w | w_{t-2}, w_{t-1})",
                    "predictions": predictions,
                }

        # 2. Bigram fallback (w_{t-1})
        ctx = (tokens[-1],)
        counts = self.bigram_context.get(ctx)
        if counts:
            total = sum(counts.values())
            predictions = self._top_predictions(counts, total, vocab_size, top_k)
            return {
                "input": text,
                "context_used": " ".join(ctx),
                "model": "Bigram Model (Fallback)",
                "formula": "P(w | w_{t-1})",
                "predictions": predictions,
            }

        # 3. Unigram fallback (general corpus frequency)
        predictions = self._top_predictions(self.unigrams, self.total_unigrams, vocab_size, top_k)
        return {
            "input": text,
            "context_used": "(none - unigram fallback)",
            "model": "Unigram Model (Corpus Freq)",
            "formula": "P(w)",
            "predictions": predictions,
        }

    @staticmethod
    def _top_predictions(counts: Counter | dict, total: int, vocab_size: int, k: int) -> list[dict]:
        """Rank words by Laplace smoothed probability: (c + 1) / (N + |V|)."""
        results = []
        for word, count in Counter(counts).most_common(k):
            prob = (count + 1) / (total + vocab_size)
            results.append({
                "word": word,
                "count": count,
                "probability": round(prob, 5),
                "percentage": round(prob * 100, 2),
            })
        return results

    def corpus_stats(self) -> dict:
        """Return metadata about the underlying corpus."""
        return {
            "total_sentences": len(CORPUS_SENTENCES),
            "vocabulary_size": len(self.vocab),
            "total_tokens": self.total_unigrams,
            "unique_bigrams": len(self.bigrams),
            "unique_trigrams": len(self.trigrams),
        }


# Singleton instance
ngram_model = NGramModel()
