"""
Smart Sentence Predictor — N-Gram Language Model
==================================================
Builds unigram, bigram and trigram frequency tables from a built-in
corpus at import time.  Predicts the next word using trigram → bigram →
unigram fallback with add-one (Laplace) smoothing.
"""

from collections import Counter, defaultdict
from nltk.tokenize import word_tokenize

# ── Built-in corpus ──────────────────────────────────────────────────
# Covers: technology, AI, programming, education, college, general English.

_CORPUS_SENTENCES = [
    # Technology
    "Artificial intelligence is transforming the world of technology.",
    "Machine learning algorithms can learn from data and make predictions.",
    "Deep learning is a subset of machine learning that uses neural networks.",
    "Natural language processing helps computers understand human language.",
    "Computers can process large amounts of data very quickly.",
    "The internet has connected people across the world.",
    "Cloud computing allows users to store data on remote servers.",
    "Cybersecurity is important to protect data from hackers.",
    "Blockchain technology ensures secure and transparent transactions.",
    "Quantum computing is the future of computation.",
    "The development of artificial intelligence has been rapid in recent years.",
    "Technology is changing the way we live and work every day.",
    "Smart devices are becoming more common in everyday life.",
    "Virtual reality creates immersive experiences for users.",
    "Augmented reality overlays digital content on the real world.",
    "Data science combines statistics and programming to extract insights from data.",
    "Big data analytics helps organizations make better decisions.",
    "The field of robotics is advancing rapidly with new innovations.",
    "Autonomous vehicles use sensors and algorithms to navigate roads.",
    "Internet of things connects everyday objects to the internet.",

    # AI
    "Artificial intelligence can be used to solve complex problems.",
    "Neural networks are inspired by the structure of the human brain.",
    "Supervised learning requires labeled training data.",
    "Unsupervised learning discovers patterns in unlabeled data.",
    "Reinforcement learning trains agents through rewards and penalties.",
    "Transfer learning allows models to apply knowledge from one task to another.",
    "Computer vision enables machines to interpret visual information.",
    "Speech recognition converts spoken language into text.",
    "Sentiment analysis determines the emotional tone of text.",
    "Chatbots use natural language processing to communicate with users.",
    "AI research is focused on creating more intelligent systems.",
    "Ethics in artificial intelligence is an important area of study.",
    "Bias in machine learning models can lead to unfair outcomes.",
    "Generative models can create new content such as images and text.",
    "Recurrent neural networks are designed to process sequential data.",

    # Programming
    "Python is a popular programming language for data science.",
    "Python is widely used in machine learning and web development.",
    "Java is used for building enterprise applications.",
    "JavaScript is essential for web development.",
    "Programming requires logical thinking and problem solving skills.",
    "Open source software allows developers to collaborate freely.",
    "Version control systems like Git help manage code changes.",
    "Debugging is an important part of the software development process.",
    "Software testing ensures that applications work correctly.",
    "Agile methodology promotes iterative development and collaboration.",
    "Object oriented programming organizes code into reusable classes.",
    "Functional programming uses pure functions and immutable data.",
    "Algorithms and data structures are fundamental to computer science.",
    "Web frameworks like Django and Flask simplify web development in Python.",
    "APIs allow different software systems to communicate with each other.",
    "Code review is a best practice for maintaining code quality.",

    # Education & College
    "Students learn about algorithms and data structures in college.",
    "Education is the key to a successful career in technology.",
    "College provides students with opportunities to learn and grow.",
    "Research is an important part of higher education.",
    "Professors guide students through complex topics in their courses.",
    "Exams test the knowledge and understanding of students.",
    "Projects help students apply theoretical knowledge to real problems.",
    "The curriculum includes courses on programming and mathematics.",
    "Students should practice coding every day to improve their skills.",
    "Internships provide valuable industry experience for college students.",
    "Group projects teach students how to work in teams.",
    "Academic conferences are great for networking and learning.",
    "Online courses have made education more accessible to everyone.",
    "Libraries are essential resources for research and study.",
    "The university offers programs in computer science and engineering.",
    "Students learn to write programs in Python and Java.",
    "Critical thinking is an important skill for college students.",
    "Time management helps students balance studies and activities.",
    "Scholarships support students who excel in their studies.",

    # General English / NLP topics
    "Language is the primary means of human communication.",
    "Words can have multiple meanings depending on context.",
    "Grammar rules help us construct correct sentences.",
    "Reading books improves vocabulary and comprehension skills.",
    "Writing is an essential skill for effective communication.",
    "Communication skills are important in both personal and professional life.",
    "The English language has a rich history and diverse vocabulary.",
    "Sentences are made up of words that follow grammatical rules.",
    "Paragraphs organize ideas into coherent blocks of text.",
    "Punctuation marks help clarify the meaning of sentences.",
    "A dictionary provides definitions and usage of words.",
    "Synonyms are words that have similar meanings.",
    "Antonyms are words that have opposite meanings.",
    "Context determines the meaning of ambiguous words.",
    "The study of language is called linguistics.",
    "Phonetics deals with the sounds of speech.",
    "Morphology studies the structure and formation of words.",
    "Syntax refers to the arrangement of words in a sentence.",
    "Semantics is the study of meaning in language.",
    "Pragmatics studies how context affects interpretation.",

    # NLP-specific
    "Tokenization is the first step in natural language processing.",
    "Lemmatization reduces words to their base or dictionary form.",
    "Part of speech tagging assigns grammatical categories to words.",
    "Named entity recognition identifies names of people places and organizations.",
    "Word embeddings represent words as dense numerical vectors.",
    "The bag of words model represents text as word frequency vectors.",
    "TF-IDF measures the importance of a word in a document.",
    "N-gram models predict the next word based on previous words.",
    "Language models estimate the probability of word sequences.",
    "Text classification assigns categories to documents.",
    "Information retrieval systems help users find relevant documents.",
    "Machine translation converts text from one language to another.",
    "Text summarization creates concise summaries of longer documents.",
    "Word sense disambiguation determines the correct meaning of a word.",
    "Corpus linguistics studies language through large collections of text.",
    "Stop words are common words that are often filtered out in NLP.",
    "Stemming reduces words to their root form by removing suffixes.",

    # Extra variety
    "I want to learn Python programming.",
    "I want to learn machine learning and artificial intelligence.",
    "I want to learn natural language processing.",
    "I want to learn data science and deep learning.",
    "I want to learn web development with JavaScript.",
    "The students are working on their final year project.",
    "The professor explained the concept of neural networks clearly.",
    "We need to study hard for the upcoming examinations.",
    "The lab session covered natural language processing techniques.",
    "This semester we are learning about compiler design.",
    "Algorithms play a critical role in modern software development.",
    "Data is the new oil in the digital economy.",
    "Innovation drives progress in science and technology.",
    "Collaboration between teams leads to better software products.",
    "Understanding mathematics is essential for machine learning.",
]


class NGramModel:
    """Simple N-gram language model with Laplace smoothing."""

    def __init__(self):
        self.unigrams: Counter = Counter()
        self.bigrams: Counter = Counter()
        self.trigrams: Counter = Counter()
        self.bigram_context: dict[tuple, Counter] = defaultdict(Counter)
        self.trigram_context: dict[tuple, Counter] = defaultdict(Counter)
        self.vocab: set = set()
        self._build()

    # ── Build ─────────────────────────────────────────────────
    def _build(self):
        for sentence in _CORPUS_SENTENCES:
            tokens = [t.lower() for t in word_tokenize(sentence) if t.isalpha()]
            self.vocab.update(tokens)
            self.unigrams.update(tokens)

            for i in range(len(tokens) - 1):
                bg = (tokens[i], tokens[i + 1])
                self.bigrams[bg] += 1
                self.bigram_context[(tokens[i],)][tokens[i + 1]] += 1

            for i in range(len(tokens) - 2):
                tg = (tokens[i], tokens[i + 1], tokens[i + 2])
                self.trigrams[tg] += 1
                self.trigram_context[(tokens[i], tokens[i + 1])][tokens[i + 2]] += 1

        self.total_unigrams = sum(self.unigrams.values())

    # ── Predict ───────────────────────────────────────────────
    def predict(self, text: str, top_k: int = 5) -> dict:
        tokens = [t.lower() for t in word_tokenize(text) if t.isalpha()]

        if not tokens:
            return self._empty_result(text)

        V = len(self.vocab)

        # Try trigram first
        if len(tokens) >= 2:
            ctx = (tokens[-2], tokens[-1])
            counts = self.trigram_context.get(ctx)
            if counts:
                total = sum(counts.values())
                predictions = self._top_predictions(counts, total, V, top_k)
                return {
                    "input": text,
                    "context_used": " ".join(ctx),
                    "model": "trigram",
                    "predictions": predictions,
                }

        # Bigram fallback
        ctx = (tokens[-1],)
        counts = self.bigram_context.get(ctx)
        if counts:
            total = sum(counts.values())
            predictions = self._top_predictions(counts, total, V, top_k)
            return {
                "input": text,
                "context_used": " ".join(ctx),
                "model": "bigram",
                "predictions": predictions,
            }

        # Unigram fallback
        predictions = self._top_predictions(self.unigrams, self.total_unigrams, V, top_k)
        return {
            "input": text,
            "context_used": "(none — unigram fallback)",
            "model": "unigram",
            "predictions": predictions,
        }

    # ── Helpers ───────────────────────────────────────────────
    @staticmethod
    def _top_predictions(counts: Counter | dict, total: int, V: int, k: int) -> list:
        """Return top-k predictions with Laplace-smoothed probabilities."""
        results = []
        for word, count in Counter(counts).most_common(k):
            prob = (count + 1) / (total + V)   # Laplace smoothing
            results.append({
                "word": word,
                "count": count,
                "probability": round(prob, 6),
            })
        return results

    @staticmethod
    def _empty_result(text: str) -> dict:
        return {
            "input": text,
            "context_used": None,
            "model": None,
            "predictions": [],
            "message": "No valid words found in the input. "
                       "Please enter some English text.",
        }

    # ── Corpus stats (for the /predict info panel) ────────────
    def corpus_stats(self) -> dict:
        return {
            "total_sentences": len(_CORPUS_SENTENCES),
            "vocabulary_size": len(self.vocab),
            "total_tokens": self.total_unigrams,
            "unique_bigrams": len(self.bigrams),
            "unique_trigrams": len(self.trigrams),
        }


# Singleton — instantiated once at import time
ngram_model = NGramModel()
