import { useState } from "react";
import Tokenizer from "./tools/Tokenizer";
import WordMeaning from "./tools/WordMeaning";
import Grammar from "./tools/Grammar";
import Predictor from "./tools/Predictor";
import Statistics from "./tools/Statistics";

const TOOLS = [
  { id: "tokenizer",    label: "Tokenizer & Lemmatizer", icon: "✂" },
  { id: "word-meaning", label: "Word Meaning",           icon: "🔍" },
  { id: "grammar",      label: "Grammar Analyzer",       icon: "📝" },
  { id: "predictor",    label: "Sentence Predictor",     icon: "⚡" },
  { id: "statistics",   label: "Text Statistics",        icon: "📊" },
];

const TOOL_COMPONENTS = {
  tokenizer:       Tokenizer,
  "word-meaning":  WordMeaning,
  grammar:         Grammar,
  predictor:       Predictor,
  statistics:      Statistics,
};

export default function App() {
  const [activeTool, setActiveTool] = useState("tokenizer");
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const ActiveComponent = TOOL_COMPONENTS[activeTool];

  function selectTool(id) {
    setActiveTool(id);
    setSidebarOpen(false);
  }

  return (
    <div className="app-layout">
      {/* Mobile menu button */}
      <button
        className="mobile-menu-btn"
        onClick={() => setSidebarOpen(!sidebarOpen)}
        aria-label="Toggle menu"
      >
        {sidebarOpen ? "✕" : "☰"}
      </button>

      {/* Overlay for mobile */}
      <div
        className={`sidebar-overlay ${sidebarOpen ? "visible" : ""}`}
        onClick={() => setSidebarOpen(false)}
      />

      {/* Sidebar */}
      <aside className={`sidebar ${sidebarOpen ? "open" : ""}`}>
        <div className="sidebar-header">
          <div className="sidebar-logo">
            NLP <span>Studio</span>
          </div>
          <div className="sidebar-subtitle">
            Interactive NLP Toolkit
          </div>
        </div>

        <nav className="sidebar-nav">
          {TOOLS.map((tool) => (
            <button
              key={tool.id}
              className={`sidebar-link ${activeTool === tool.id ? "active" : ""}`}
              onClick={() => selectTool(tool.id)}
            >
              <span className="icon">{tool.icon}</span>
              {tool.label}
            </button>
          ))}
        </nav>

        <div className="sidebar-footer">
          NLP Studio · College Mini-Project
        </div>
      </aside>

      {/* Main content */}
      <main className="main-content">
        <ActiveComponent key={activeTool} />
      </main>
    </div>
  );
}
