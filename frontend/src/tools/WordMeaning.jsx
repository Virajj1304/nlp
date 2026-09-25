import { useState } from "react";
import { api } from "../api";

const SAMPLES = [
  { sentence: "I went to the bank to deposit money.", word: "bank" },
  { sentence: "I sat near the bank of the river.", word: "bank" },
  { sentence: "The bat flew out of the cave at night.", word: "bat" },
  { sentence: "He picked up the bat and hit the ball.", word: "bat" },
  { sentence: "She set the table for dinner.", word: "set" },
];

export default function WordMeaning() {
  const [sentence, setSentence] = useState("");
  const [targetWord, setTargetWord] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleDetect() {
    if (!sentence.trim() || !targetWord.trim()) {
      setError("Please enter both a sentence and a target word.");
      return;
    }
    setError("");
    setLoading(true);
    setResult(null);
    try {
      const data = await api.wordMeaning(sentence.trim(), targetWord.trim());
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }

  function loadSample(s) {
    setSentence(s.sentence);
    setTargetWord(s.word);
    setResult(null);
  }

  return (
    <div>
      <div className="tool-header">
        <h1 className="tool-title">Word Meaning Detector</h1>
        <p className="tool-description">
          Determine the meaning of an ambiguous word from its surrounding context
          using WordNet and the Lesk algorithm for Word Sense Disambiguation.
        </p>
      </div>

      <div className="card">
        <div className="card-title">Input</div>
        <div className="input-group">
          <label>Sentence</label>
          <textarea
            value={sentence}
            onChange={(e) => setSentence(e.target.value)}
            placeholder="Enter a sentence containing an ambiguous word…"
            rows={3}
          />
        </div>
        <div className="input-group">
          <label>Target Word</label>
          <input
            type="text"
            value={targetWord}
            onChange={(e) => setTargetWord(e.target.value)}
            placeholder="e.g., bank"
          />
        </div>
        <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
          <button className="btn btn-primary" onClick={handleDetect} disabled={loading}>
            {loading ? "Detecting…" : "Detect Meaning"}
          </button>
          <span style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>Try a sample →</span>
          {SAMPLES.map((s, i) => (
            <button
              key={i}
              className="btn"
              style={{ color: "var(--text-muted)", background: "var(--bg-secondary)", border: "1px solid var(--border)", padding: "6px 12px", fontSize: "0.78rem" }}
              onClick={() => loadSample(s)}
            >
              "{s.word}" ({i + 1})
            </button>
          ))}
        </div>
      </div>

      {error && <div className="error-msg">{error}</div>}
      {loading && <div className="loading"><div className="spinner" /> Analyzing senses…</div>}

      {result && (
        <div className="results-section">
          {!result.found ? (
            <div className="card">
              <p style={{ color: "var(--text-secondary)" }}>{result.message}</p>
            </div>
          ) : (
            <>
              {/* Detected sense */}
              <div className="card">
                <div className="card-title">Detected Meaning</div>
                <p style={{ fontSize: "1.05rem", fontWeight: 600, color: "var(--text-primary)", marginBottom: 6 }}>
                  {result.target_word}
                  <span style={{ color: "var(--accent)", fontSize: "0.8rem", marginLeft: 10 }}>{result.pos}</span>
                </p>
                <p style={{ fontSize: "0.9rem", color: "var(--text-secondary)", marginBottom: 4 }}>
                  {result.definition}
                </p>
                <p className="note" style={{ fontFamily: "var(--font-mono)", fontSize: "0.75rem" }}>
                  Synset: {result.detected_sense}
                </p>
                {result.note && <p className="note" style={{ marginTop: 8 }}>{result.note}</p>}
              </div>

              {/* Synonyms */}
              {result.synonyms.length > 0 && (
                <div className="card">
                  <div className="card-title">Synonyms</div>
                  <div className="word-list">
                    {result.synonyms.map((s, i) => (
                      <span key={i} className="tag tag-accent">{s}</span>
                    ))}
                  </div>
                </div>
              )}

              {/* Alternative senses */}
              {result.alternative_senses.length > 0 && (
                <div className="card">
                  <div className="card-title">Alternative Senses</div>
                  {result.alternative_senses.map((s, i) => (
                    <div key={i} className="sense-card">
                      <div className="sense-name">
                        {s.sense}
                        <span className="sense-pos">{s.pos}</span>
                      </div>
                      <div className="sense-def">{s.definition}</div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      )}

      <div className="how-it-works">
        <h4>How it works</h4>
        <ul>
          <li><strong>WordNet</strong> — A lexical database that organizes words into sets of synonyms (synsets), each with a definition.</li>
          <li><strong>Word Sense Disambiguation</strong> — The task of determining which sense (meaning) of a word is used in a given context.</li>
          <li><strong>Lesk Algorithm</strong> — Compares the context words surrounding the target word with the definitions (glosses) of each sense in WordNet, selecting the best-matching sense.</li>
        </ul>
      </div>
    </div>
  );
}
