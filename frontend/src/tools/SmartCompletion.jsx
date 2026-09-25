import { useState, useEffect } from "react";
import { api } from "../api";

const PRESET_PROMPTS = [
  "Please send the",
  "Finish the",
  "Submit the",
  "Review the",
  "Schedule a",
  "Deploy the",
  "Write the",
];

export default function SmartCompletion() {
  const [text, setText] = useState("Please send the");
  const [topK, setTopK] = useState(5);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  async function fetchPrediction(currentText = text, k = topK) {
    if (!currentText.trim()) {
      setResult(null);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const data = await api.predict(currentText.trim(), k);
      setResult(data);
    } catch (err) {
      setError(err.message || "Failed to fetch prediction.");
    } finally {
      setLoading(false);
    }
  }

  // Initial fetch on mount
  useEffect(() => {
    let ignore = false;
    api.predict("Please send the", 5)
      .then((data) => {
        if (!ignore) {
          setResult(data);
        }
      })
      .catch((err) => {
        if (!ignore) {
          setError(err.message || "Failed to fetch prediction.");
        }
      });

    return () => {
      ignore = true;
    };
  }, []);

  function handleWordClick(word) {
    const updated = text.trim() + " " + word;
    setText(updated);
    fetchPrediction(updated, topK);
  }

  return (
    <div className="tool-view">
      <div className="view-header">
        <div>
          <h1 className="view-title">Smart Sentence & Task Completion</h1>
          <p className="view-subtitle">
            Statistical N-Gram Language Model with Laplace smoothing trained on everyday task messages and project notes.
          </p>
        </div>
      </div>

      {/* Input Card */}
      <div className="card input-card">
        <div className="input-toolbar">
          <span className="input-label">Task Prefix Input</span>
          <div className="presets-group">
            <span className="presets-label">Starters:</span>
            {PRESET_PROMPTS.map((starter, i) => (
              <button
                key={i}
                type="button"
                className="preset-btn"
                onClick={() => {
                  setText(starter);
                  fetchPrediction(starter, topK);
                }}
              >
                "{starter}"
              </button>
            ))}
          </div>
        </div>

        <div className="completion-input-wrap">
          <textarea
            className="textarea font-mono"
            rows={2}
            value={text}
            onChange={(e) => {
              setText(e.target.value);
            }}
            placeholder="Type your task sentence (e.g., 'Please send the')..."
          />
        </div>

        <div className="card-actions">
          <div className="k-selector">
            <span className="meta-label">Top Candidates:</span>
            <div className="k-pills">
              {[3, 5, 8].map((k) => (
                <button
                  key={k}
                  type="button"
                  className={`k-pill ${topK === k ? "active" : ""}`}
                  onClick={() => {
                    setTopK(k);
                    fetchPrediction(text, k);
                  }}
                >
                  {k}
                </button>
              ))}
            </div>
          </div>

          <div className="btn-group">
            {text && (
              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => {
                  setText("");
                  setResult(null);
                }}
              >
                Clear
              </button>
            )}
            <button
              type="button"
              className="btn btn-primary"
              onClick={() => fetchPrediction(text, topK)}
              disabled={loading || !text.trim()}
            >
              {loading ? (
                <>
                  <span className="spinner-sm" />
                  Predicting...
                </>
              ) : (
                "Suggest Next Words"
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

      {/* Predictions Display */}
      {result && result.predictions && (
        <div className="prediction-results">
          {/* Quick Click-to-Append Pills */}
          <div className="card next-words-card">
            <div className="next-words-header">
              <div className="model-badge-group">
                <span className="badge badge-primary">{result.model}</span>
                {result.context_used && (
                  <span className="badge badge-context">
                    Context: "{result.context_used}"
                  </span>
                )}
                {result.formula && (
                  <span className="badge badge-formula font-mono">
                    {result.formula}
                  </span>
                )}
              </div>
              <span className="click-hint">Click word to append & continue</span>
            </div>

            <div className="suggested-chips-container">
              {result.predictions.map((p, idx) => (
                <button
                  key={idx}
                  type="button"
                  className="suggestion-chip"
                  onClick={() => handleWordClick(p.word)}
                >
                  <span className="chip-word font-mono">{p.word}</span>
                  <span className="chip-prob">{p.percentage}%</span>
                </button>
              ))}
            </div>
          </div>

          {/* Probability Distribution Table */}
          <div className="card table-card">
            <h3 className="section-title">Statistical Distribution</h3>
            <table className="stats-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Candidate Word</th>
                  <th>Corpus Count</th>
                  <th>Laplace Probability</th>
                  <th>Relative Likelihood</th>
                </tr>
              </thead>
              <tbody>
                {result.predictions.map((p, idx) => (
                  <tr key={idx}>
                    <td className="font-mono text-muted">#{idx + 1}</td>
                    <td className="font-mono font-bold text-highlight">{p.word}</td>
                    <td className="font-mono">{p.count}</td>
                    <td className="font-mono">{p.probability}</td>
                    <td className="prob-bar-cell">
                      <div className="prob-bar-bg">
                        <div
                          className="prob-bar-fill"
                          style={{
                            width: `${Math.min(100, p.percentage * 25)}%`,
                          }}
                        />
                      </div>
                      <span className="prob-bar-label font-mono">{p.percentage}%</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Local Corpus Stats */}
          {result.corpus_stats && (
            <div className="corpus-stats-grid">
              <div className="stat-card">
                <span className="stat-num">{result.corpus_stats.total_sentences}</span>
                <span className="stat-name">Corpus Sentences</span>
              </div>
              <div className="stat-card">
                <span className="stat-num">{result.corpus_stats.vocabulary_size}</span>
                <span className="stat-name">Vocabulary Words</span>
              </div>
              <div className="stat-card">
                <span className="stat-num">{result.corpus_stats.total_tokens}</span>
                <span className="stat-name">Total Tokens</span>
              </div>
              <div className="stat-card">
                <span className="stat-num">{result.corpus_stats.unique_trigrams}</span>
                <span className="stat-name">Unique Trigrams</span>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
