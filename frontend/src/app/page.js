'use client';

import { useState, useEffect } from 'react';
import ChatInterface from '../components/ChatInterface';
import FAQSection from '../components/FAQSection';

const SCHEMES = [
  { name: 'HDFC Flexi Cap Fund', type: 'Flexi-cap Equity' },
  { name: 'HDFC ELSS Tax Saver', type: 'ELSS Equity' },
  { name: 'HDFC Mid-Cap Opportunities Fund', type: 'Mid-cap Equity' },
  { name: 'HDFC Small Cap Fund', type: 'Small-cap Equity' },
  { name: 'HDFC Liquid Fund', type: 'Liquid Debt' },
];

const MF_BASICS = [
  'What is a Mutual Fund?',
  'What is NAV (Net Asset Value)?',
  'What is AUM (Assets Under Management)?',
  'What is an Expense Ratio?',
  'What is an Exit Load?',
  'What is the difference between Equity and Debt Funds?',
  'What is a SIP (Systematic Investment Plan)?',
  'What is a Lump Sum Investment?',
  'What is a Benchmark Index?',
  'What is Fund Diversification?',
  'What is a Lock-in Period?',
  'What is a Fund Manager?',
  'What are Large Cap, Mid Cap, and Small Cap Funds?',
  'What is an ELSS Tax Saving Fund?',
  'How does risk level vary across mutual funds?',
];

function useCurrentTime() {
  const [time, setTime] = useState('');
  useEffect(() => {
    const format = () => {
      const now = new Date();
      const day = now.toLocaleDateString('en-IN', {
        day: '2-digit', month: 'short', year: 'numeric', timeZone: 'Asia/Kolkata',
      });
      const t = now.toLocaleTimeString('en-IN', {
        hour: '2-digit', minute: '2-digit', hour12: true, timeZone: 'Asia/Kolkata',
      }).toUpperCase();
      return `${day}, ${t} IST`;
    };

    // Defer initial setState to avoid ESLint sync updates error
    setTimeout(() => {
      setTime(format());
    }, 0);

    const id = setInterval(() => setTime(format()), 60000);
    return () => clearInterval(id);
  }, []);
  return time;
}

export default function Home() {
  const [pendingFAQ, setPendingFAQ] = useState(null);
  const handleSidebarClick = (q) => setPendingFAQ(q);
  const timestamp = useCurrentTime();

  return (
    <div className="app-container">
      <header className="app-header">
        <div className="header-logo" aria-hidden="true">🏦</div>
        <div className="header-info">
          <h1>Mutual Fund Genie AI Assistant</h1>
          <p>HDFC Mutual Fund | Facts-only. No investment advice.</p>
        </div>
        <div className="header-badge">
          <span className="status-dot" />
          <span>Live</span>
        </div>
      </header>

      <main className="main-content">
        {/* LEFT PANEL */}
        <aside className="sidebar-left">
          <div className="panel-card panel-flex-shrink">
            <div className="panel-header">
              <span>📋</span>
              <span>Schemes in My Scope</span>
            </div>
            <div className="schemes-list">
              {SCHEMES.map((s, i) => (
                <div
                  key={i}
                  className="scheme-row"
                  onClick={() => handleSidebarClick(`Tell me about ${s.name}`)}
                  title={`Ask about ${s.name}`}
                >
                  <span className="scheme-arrow">›</span>
                  <div>
                    <div className="scheme-name">{s.name}</div>
                    <div className="scheme-type">{s.type}</div>
                  </div>
                </div>
              ))}
            </div>
            <div className="schemes-source-note">Source: HDFC AMC · AMFI · SEBI</div>
          </div>

          <div className="panel-card panel-flex-shrink">
            <div className="panel-header">
              <span>ℹ️</span>
              <span>About</span>
            </div>
            <div className="about-grid">
              <span className="about-label">Product :</span>
              <span className="about-value">Mutual Fund Genie AI Assistant</span>

              <span className="about-label">Target AMC :</span>
              <span className="about-value">HDFC</span>

              <span className="about-label">Engine :</span>
              <span className="about-value">Groq · Llama-3.3-70b</span>

              <span className="about-label">Creator :</span>
              <span className="about-value">
                <a
                  href="https://www.linkedin.com/in/nikhil-ramesh-1b526141/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="creator-link tooltip-trigger"
                  data-tooltip="Built by Nikhil Ramesh. Click to view creator profile."
                >
                  Nikhil Ramesh
                </a>
              </span>
            </div>
          </div>
        </aside>

        {/* CENTER: Chat */}
        <div className="chat-section-wrapper">
          <ChatInterface
            externalQuery={pendingFAQ}
            onExternalQueryHandled={() => setPendingFAQ(null)}
          />
          {timestamp && (
            <div className="timestamp-bar">
              🕐 Last Updated On {timestamp}
            </div>
          )}
        </div>

        {/* RIGHT PANEL */}
        <aside className="sidebar-right">
          <div className="panel-card panel-flex-grow pulse-glow">
            <div className="panel-header">
              <span>📘</span>
              <span>Mutual Fund Basics</span>
            </div>
            <div className="basics-scroll">
              <div className="faq-list">
                {MF_BASICS.map((q, i) => (
                  <button
                    key={i}
                    className="faq-item"
                    onClick={() => handleSidebarClick(q)}
                    title="Click to ask this question"
                  >
                    <span className="faq-arrow">›</span>
                    <span>{q}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="panel-card panel-flex-shrink pulse-glow">
            <div className="panel-header">
              <span>💬</span>
              <span>Suggested Questions</span>
            </div>
            <div className="panel-content-padding" style={{ padding: '0 16px 12px' }}>
              <div className="section-intro-text">
                💡 Try these popular questions to get started.
              </div>
              <FAQSection onFAQClick={handleSidebarClick} />
            </div>
          </div>
        </aside>
      </main>

      <footer className="app-footer">
        For educational purposes only. This AI Assistant is not SEBI-registered and does not provide financial or investment advice.
      </footer>
    </div>
  );
}
