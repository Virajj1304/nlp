import { useState } from "react";
import { api } from "../api";

const PRESETS = [
  {
    sentence: "I went to the bank to deposit money.",
    word: "bank",
    note: "Financial sense of 'bank'",
  },
  {
    sentence: "The fisherman sat on the river bank waiting for a bite.",
    word: "bank",
    note: "River/geographical sense of 'bank'",
  },
  {
    sentence: "The construction workers operated a giant crane at the site.",
    word: "crane",
    note: "Machine/lifting equipment sense",
  },
  {
    sentence: "We saw a white crane flying gracefully over the marsh.",
    word: "crane",
    note: "Bird sense of 'crane'",
  },
  {
    sentence: "He used the wireless mouse to click the icon on the screen.",
    word: "mouse",
    note: "Computer device sense",
  },
];

export default function WordMeaning() {
  const [sentence, setSentence] = useState(PRESETS[0].sentence);
  const [targetWord, setTargetWord] = useState(PRESETS[0].word);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Extract clickable candidate words from current sentence
  const sentenceWords = sentence
    .replace(/[^\w\s-]/g, " ")
    .split(/\s+/)
    .filter((w) => w.length > 1);

  async function handleAnalyze(s = sentence, w = targetWord) {
    if (!s.trim() || !w.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const data = await api.wordMeaning(s.trim(), w.trim());
      setResult(data);
    } catch (err) {
      setError(err.message || "Failed to disambiguate word meaning.");
    } finally {
      setLoading(false);
    }
  }

  function handleSelectWord(w) {
    const cleaned = w.toLowerCase().replace(/[^a-z]/g, "");
    setTargetWord(cleaned);
    handleAnalyze(sentence, cleaned);
  }

  function applyPreset(preset) {
    setSentence(preset.sentence);
    setTargetWord(preset.word);
    handleAnalyze(preset.sentence, preset.word);
  }

  return (
    <div className="tool-view">
      <div className="view-header">
        <div>
          <h1 className="view-title">Context-Aware Word Meaning</h1>
          <p className="view-subtitle">
            Disambiguate polysemous words using the classical Simplified Lesk Algorithm and Princeton WordNet.
          </p>
        </div>
      </div>

      {/* Input Card */}
      <div className="card input-card">
        <div className="input-toolbar">
          <span className="input-label">Sentence & Target Word</span>
          <div className="presets-group">
            <span className="presets-label">Examples:</span>
            {PRESETS.map((p, i) => (
              <button
                key={i}
                type="button"
                className="preset-btn"
                onClick={() => applyPreset(p)}
                title={p.note}
              >
                {p.word}: "{p.sentence.slice(0, 24)}..."
              </button>
            ))}
          </div>
        </div>

        <div className="form-group">
          <label className="field-label">Sentence Context</label>
          <textarea
            className="textarea"
            rows={2}
            value={sentence}
            onChange={(e) => setSentence(e.target.value)}
            placeholder="Enter a sentence with an ambiguous word..."
          />
        </div>

        {/* Clickable word selector from sentence */}
        {sentenceWords.length > 0 && (
          <div className="word-selector-strip">
            <span className="helper-label">Click a word to disambiguate:</span>
            <div className="word-chips-wrap">
              {sentenceWords.map((w, idx) => {
                const cleanW = w.toLowerCase().replace(/[^a-z]/g, "");
                const isSelected = cleanW === targetWord.toLowerCase();
                return (
                  <button
                    key={idx}
                    type="button"
                    className={`word-chip ${isSelected ? "selected" : ""}`}
                    onClick={() => handleSelectWord(cleanW)}
                  >
                    {w}
                  </button>
                );
              })}
            </div>
          </div>
        )}

        <div className="input-split-row">
          <div className="form-group flex-1">
            <label className="field-label">Target Word</label>
            <input
              type="text"
              className="text-input font-mono"
              value={targetWord}
              onChange={(e) => setTargetWord(e.target.value)}
              placeholder="e.g. bank"
              onKeyDown={(e) => e.key === "Enter" && handleAnalyze()}
            />
          </div>

          <div className="form-group-btn">
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => handleAnalyze()}
              disabled={loading || !sentence.trim() || !targetWord.trim()}
            >
              {loading ? (
                <>
                  <span className="spinner-sm" />
                  Running Lesk...
                </>
              ) : (
                "Disambiguate Meaning"
              )}
            </button>
          </div>
        </div>
      </div>

      {error && (
        <div className="alert alert-error">
          <span className="alert-icon">!</span>
          <div className="alert-content">
            <strong>Error:</strong> {error}
          </div>
        </div>
      )}

      {/* Empty State */}
      {!loading && !result && !error && (
        <div className="empty-state">
          <div className="empty-icon">📖</div>
          <h3>Select a word to detect meaning</h3>
          <p>
            Choose an example preset or type a sentence and target word to view WordNet senses, definitions, and Lesk overlap scores.
          </p>
        </div>
      )}

      {/* Result Display */}
      {!loading && result && result.found && (
        <div className="meaning-results">
          {/* Detected Primary Sense Card */}
          <div className="card result-card primary-sense-card">
            <div className="card-top-row">
              <div className="sense-badge-group">
                <span className="badge badge-primary font-mono">
                  {result.detected_sense}
                </span>
                <span className="badge badge-pos">
                  {result.pos}
                </span>
                <span className="badge badge-score">
                  Lesk Overlap: {result.lesk_score} word(s)
                </span>
              </div>
              <span className="sense-counter">
                1 of {result.total_senses} senses in WordNet
              </span>
            </div>

            <div className="meaning-section">
              <h2 className="meaning-definition">
                "{result.definition}"
              </h2>
            </div>

            {/* Overlap & Explanation */}
            <div className="lesk-explanation-box">
              <span className="explanation-title">How the Lesk Algorithm chose this sense:</span>
              <p>{result.explanation}</p>
              {result.overlap_words && result.overlap_words.length > 0 && (
                <div className="overlap-pills">
                  <span className="overlap-label">Context overlap:</span>
                  {result.overlap_words.map((w, i) => (
                    <span key={i} className="badge badge-overlap">
                      {w}
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Synonyms */}
            {result.synonyms && result.synonyms.length > 0 && (
              <div className="detail-block">
                <span className="block-title">Synonyms from Synset</span>
                <div className="tags-wrap">
                  {result.synonyms.map((syn, i) => (
                    <span key={i} className="synonym-tag font-mono">
                      {syn}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Examples */}
            {result.examples && result.examples.length > 0 && (
              <div className="detail-block">
                <span className="block-title">WordNet Usage Examples</span>
                <ul className="examples-list">
                  {result.examples.map((ex, i) => (
                    <li key={i}>"{ex}"</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Alternative Senses */}
          {result.alternative_senses && result.alternative_senses.length > 0 && (
            <div className="alt-senses-section">
              <div className="alt-senses-header">
                <h3>Alternative WordNet Senses ({result.alternative_senses.length})</h3>
                <p>Other meanings of "{result.target_word}" ranked by context relevance</p>
              </div>

              <div className="alt-senses-grid">
                {result.alternative_senses.map((alt, idx) => (
                  <div key={idx} className="alt-sense-card">
                    <div className="alt-header">
                      <span className="alt-name font-mono">{alt.sense}</span>
                      <span className="badge badge-pos">{alt.pos}</span>
                      {alt.overlap_count > 0 && (
                        <span className="badge badge-score">
                          Overlap: {alt.overlap_count}
                        </span>
                      )}
                    </div>
                    <p className="alt-definition">{alt.definition}</p>
                    {alt.synonyms && alt.synonyms.length > 0 && (
                      <div className="alt-synonyms">
                        <span className="alt-meta-label">Synonyms:</span>
                        <span>{alt.synonyms.join(", ")}</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Word not found in WordNet */}
      {!loading && result && !result.found && (
        <div className="alert alert-warning">
          <span className="alert-icon">i</span>
          <div className="alert-content">
            <strong>Word Not Found:</strong> {result.message}
          </div>
        </div>
      )}
    </div>
  );
}
