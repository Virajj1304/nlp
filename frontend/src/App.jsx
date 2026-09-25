import { useState, useEffect } from "react";
import TaskExtractor from "./tools/TaskExtractor";
import WordMeaning from "./tools/WordMeaning";
import SmartCompletion from "./tools/SmartCompletion";
import TextInsights from "./tools/TextInsights";
import { api, API_BASE } from "./api";

const NAV_ITEMS = [
  { id: "task-extractor", label: "Task Extractor", shortcut: "1" },
  { id: "word-meaning", label: "Word Meaning", shortcut: "2" },
  { id: "smart-completion", label: "Smart Completion", shortcut: "3" },
  { id: "text-insights", label: "Text Insights", shortcut: "4" },
];

const COMPONENTS = {
  "task-extractor": TaskExtractor,
  "word-meaning": WordMeaning,
  "smart-completion": SmartCompletion,
  "text-insights": TextInsights,
};

export default function App() {
  const [activeTab, setActiveTab] = useState("task-extractor");
  const [backendOnline, setBackendOnline] = useState(null);

  useEffect(() => {
    let mounted = true;
    api.checkHealth().then((isOk) => {
      if (mounted) setBackendOnline(isOk);
    });

    const interval = setInterval(() => {
      api.checkHealth().then((isOk) => {
        if (mounted) setBackendOnline(isOk);
      });
    }, 15000);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const ActiveComponent = COMPONENTS[activeTab] || TaskExtractor;

  return (
    <div className="app-container">
      {/* Top Navigation Bar - Minimal Linear/Notion aesthetic */}
      <header className="app-header">
        <div className="header-left">
          <div className="brand" onClick={() => setActiveTab("task-extractor")}>
            <span className="brand-logo">⌘</span>
            <div className="brand-text">
              <span className="brand-name">TaskLens</span>
              <span className="brand-tag">Classical NLP</span>
            </div>
          </div>

          <nav className="nav-tabs" aria-label="Main Navigation">
            {NAV_ITEMS.map((item) => (
              <button
                key={item.id}
                type="button"
                className={`nav-tab ${activeTab === item.id ? "active" : ""}`}
                onClick={() => setActiveTab(item.id)}
              >
                <span>{item.label}</span>
                <span className="tab-shortcut">{item.shortcut}</span>
              </button>
            ))}
          </nav>
        </div>

        <div className="header-right">
          <div
            className="status-indicator"
            title={
              backendOnline
                ? `Connected to ${API_BASE}`
                : `Connecting to ${API_BASE}... (Note: Render free tier cold start may take 30-45s on first visit)`
            }
          >
            <span className={`status-dot ${backendOnline ? "online" : backendOnline === false ? "offline" : "checking"}`} />
            <span className="status-text">
              {backendOnline
                ? "FastAPI Connected"
                : backendOnline === false
                ? "Backend Offline"
                : "Connecting..."}
            </span>
          </div>
          <span className="tech-badge">NLTK + WordNet</span>
        </div>
      </header>

      {/* Main Workspace Area */}
      <main className="app-main">
        <div className="app-content-wrapper">
          <ActiveComponent />
        </div>
      </main>

      {/* Subtle Minimal Footer */}
      <footer className="app-footer">
        <div className="footer-left">
          <span>TaskLens</span>
          <span className="footer-sep">·</span>
          <span>Zero LLMs · Pure Rule-Based & Statistical NLP</span>
        </div>
        <div className="footer-right">
          <span>Sentence Segmentation · POS Tagging · Lemmatization · Lesk WSD · N-Gram LM</span>
        </div>
      </footer>
    </div>
  );
}
