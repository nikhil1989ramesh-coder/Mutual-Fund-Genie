'use client';

import { useState, useRef, useEffect } from 'react';
import { sendChatMessage } from '../lib/apiService';

const FALLBACK_PATTERNS = [
    /^(hi|hello|hey|howdy|hola|sup|what'?s up|greetings|good (morning|evening|afternoon|day))[!.,\s]*$/i,
    /extraction scope/i,
    /data targets/i,
    /amc.*scrape/i,
    /corpus.*url/i,
    /ingest phase/i,
    /retrieve phase/i,
    /generate phase/i,
];

const FALLBACK_MSG =
    "If you have any questions or need assistance with HDFC Mutual Fund, feel free to ask!";

function isFallbackQuery(text) {
    return FALLBACK_PATTERNS.some((re) => re.test(text.trim()));
}

/** Convert plain URLs to clickable blue links */
function linkify(text) {
    const urlRegex = /(https?:\/\/[^\s),\]]+)/g;
    const parts = text.split(urlRegex);
    return parts.map((part, i) => {
        if (urlRegex.test(part)) {
            urlRegex.lastIndex = 0;
            return (
                <a key={i} href={part} target="_blank" rel="noopener noreferrer" className="answer-link">
                    {part}
                </a>
            );
        }
        return part;
    });
}

function parseAnswer(raw) {
    const sourcesSeparator = /Last updated from sources?:\s*/i;
    const parts = raw.split(sourcesSeparator);
    let body = parts[0].trim();
    const sourceLine = parts[1] ? parts[1].trim() : null;

    const trailingMsg = "If you have any questions or need assistance with HDFC Mutual Fund, feel free to ask!";
    let hasTrailingMsg = false;
    if (body.includes(trailingMsg) && body !== trailingMsg) {
        hasTrailingMsg = true;
        body = body.replace(trailingMsg, '').trim();
    }

    // New logic: Detect groupings by Scheme name headers (ending in :)
    const lines = body.split(/\n+/).map(l => l.trim()).filter(l => l.length > 0);
    const groups = [];
    let currentGroup = null;

    lines.forEach(line => {
        // If line is a header (e.g. "HDFC Flexi Cap Fund:") or looks like one
        const isHeader = (line.includes('HDFC') || line.includes('Fund')) && line.endsWith(':');

        if (isHeader) {
            if (currentGroup) groups.push(currentGroup);
            currentGroup = { header: line.replace(/:$/, ''), items: [] };
        } else if (currentGroup) {
            currentGroup.items.push(line.replace(/^[-•*]\s*/, ''));
        } else {
            // Lines before any header or general text
            groups.push({ header: null, items: [line.replace(/^[-•*]\s*/, '')] });
        }
    });
    if (currentGroup) groups.push(currentGroup);

    return { groups, sourceLine, hasTrailingMsg };
}

function MessageBubble({ role, text, sources, isLatestBot, topRef }) {
    if (role === 'user') {
        return (
            <div className="message-row user">
                <div className="message-avatar user-av">🙋</div>
                <div className="message-bubble user-bubble">{text}</div>
            </div>
        );
    }

    const { groups, sourceLine, hasTrailingMsg } = parseAnswer(text);
    const inlineSourceUrls = sourceLine
        ? [...sourceLine.matchAll(/(https?:\/\/[^\s),\]]+)/g)].map((m) => m[1])
        : [];
    const allSources = [...new Set([...inlineSourceUrls, ...(sources || [])])];

    return (
        <div className="message-row bot" ref={isLatestBot ? topRef : null}>
            <div className="message-avatar bot-av">🏦</div>
            <div className="message-bubble bot-bubble">
                {groups.map((group, gIdx) => (
                    <div key={gIdx} className={group.header ? "scheme-result-group" : ""}>
                        {group.header && (
                            <div className="scheme-result-header">{group.header}</div>
                        )}
                        <ul className="answer-bullets">
                            {group.items.map((item, iIdx) => (
                                <li key={iIdx}>{linkify(item)}</li>
                            ))}
                        </ul>
                    </div>
                ))}

                {hasTrailingMsg && (
                    <p className="bot-closing-msg" style={{ fontStyle: 'italic', fontSize: '0.9em', opacity: 0.9, marginTop: '12px' }}>
                        If you have any questions or need assistance with HDFC Mutual Fund, feel free to ask!
                    </p>
                )}

                {allSources.length > 0 && (
                    <div className="sources-list">
                        <div className="sources-label">📎 Sources</div>
                        {allSources.map((src, i) => {
                            const label = src.replace(/https?:\/\/(www\.)?/, '').split('/').slice(0, 3).join('/');
                            return (
                                <a
                                    key={i}
                                    href={src}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="source-chip"
                                    title={src}
                                >
                                    🔗 {label}
                                </a>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
}

function TypingBubble() {
    return (
        <div className="message-row bot">
            <div className="message-avatar bot-av">🏦</div>
            <div className="message-bubble bot-bubble">
                <div className="typing-indicator">
                    <span /><span /><span />
                </div>
            </div>
        </div>
    );
}

export default function ChatInterface({ externalQuery, onExternalQueryHandled }) {
    const [messages, setMessages] = useState([]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [latestBotIdx, setLatestBotIdx] = useState(-1);
    const [hasInteracted, setHasInteracted] = useState(false);
    const bottomRef = useRef(null);
    const latestBotRef = useRef(null);
    const textareaRef = useRef(null);

    // Initial Welcome Message
    useEffect(() => {
        const welcome = {
            role: 'bot',
            text: `💬 Welcome to Mutual Fund Genie AI Assistant

You can explore the app in multiple ways:
• Click questions under Mutual Fund Basics on the right
• Try the Suggested Questions to quickly explore fund details
• Select any scheme from "Schemes in Scope" to ask about it
• Or type your own question in the chat box below

👇 Get started by clicking a question!`,
            sources: []
        };
        setMessages([welcome]);
        setLatestBotIdx(0);
    }, []);

    // Scroll to results/question focus
    useEffect(() => {
        if (messages.length > 0) {
            // If user just sent a message, scroll to bottom to show typing or user bubble
            if (messages[messages.length - 1].role === 'user') {
                bottomRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
            }
            // If bot just responded, scroll to top of that response
            else if (latestBotIdx >= 0 && latestBotRef.current) {
                latestBotRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        }
    }, [messages, latestBotIdx]);

    // Secondary scroll to bottom for typing indicator
    useEffect(() => {
        if (isLoading) {
            bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
        }
    }, [isLoading]);

    useEffect(() => {
        if (externalQuery) {
            setInputValue(externalQuery);
            onExternalQueryHandled?.();
            // Trigger auto-send if not loading
            if (!isLoading) {
                const autoSubmit = async () => {
                    // Small delay to let state update
                    await new Promise(r => setTimeout(r, 0));
                    handleSend(externalQuery);
                };
                autoSubmit();
            }
        }
    }, [externalQuery, onExternalQueryHandled, isLoading]);

    const handleSend = async (overrideQuery) => {
        const query = (overrideQuery || inputValue).trim();
        if (!query || isLoading) return;

        setInputValue('');
        setError(null);
        setHasInteracted(true);
        setMessages((prev) => [...prev, { role: 'user', text: query }]);
        setIsLoading(true);

        if (isFallbackQuery(query)) {
            await new Promise((r) => setTimeout(r, 400));
            setMessages((prev) => {
                const next = [...prev, { role: 'bot', text: FALLBACK_MSG, sources: [] }];
                setLatestBotIdx(next.length - 1);
                return next;
            });
            setIsLoading(false);
            return;
        }

        try {
            const data = await sendChatMessage(query);
            setMessages((prev) => {
                const next = [...prev, { role: 'bot', text: data.answer, sources: data.sources }];
                setLatestBotIdx(next.length - 1);
                return next;
            });
        } catch (err) {
            setError('⚠️ Could not reach the server. Make sure the backend is running on port 8000.');
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            handleSend();
        }
    };

    const handleReset = () => {
        setMessages([]);
        setError(null);
        setInputValue('');
        setLatestBotIdx(-1);
    };

    return (
        <div className="chat-section">
            <div className="chat-window">
                {messages.length === 0 && !isLoading && (
                    <div className="welcome-screen">
                        <div className="welcome-card">
                            <div className="welcome-card-header">
                                <span>🏦</span>
                                <span>Mutual Fund Genie AI Assistant</span>
                            </div>
                            <div className="welcome-card-content">
                                <h2>Get Started with HDFC Mutual Fund</h2>
                                <p>Discover scheme details, NAV, AUM, and investment basics using our official data-backed assistant.</p>

                                <div className="welcome-instruction-list">
                                    <div className="welcome-instruction-item">
                                        <span>📘</span>
                                        <span>Click **Mutual Fund Basics** on the right to learn key concepts.</span>
                                    </div>
                                    <div className="welcome-instruction-item">
                                        <span>💬</span>
                                        <span>Try **Suggested Questions** to explore specific fund details.</span>
                                    </div>
                                    <div className="welcome-instruction-item">
                                        <span>📋</span>
                                        <span>Select from **Schemes in Scope** to ask about specific funds.</span>
                                    </div>
                                    <div className="welcome-instruction-item">
                                        <span>⌨️</span>
                                        <span>Or simply **type your question** in the chat box below.</span>
                                    </div>
                                </div>

                                <p style={{ color: 'var(--brand-gold)', fontWeight: '600', marginTop: '4px' }}>
                                    👇 Start by clicking a question!
                                </p>
                            </div>
                        </div>
                    </div>
                )}

                {messages.map((msg, idx) => (
                    <MessageBubble
                        key={idx}
                        role={msg.role}
                        text={msg.text}
                        sources={msg.sources}
                        isLatestBot={idx === latestBotIdx}
                        topRef={latestBotRef}
                    />
                ))}

                {isLoading && <TypingBubble />}

                {error && (
                    <div className="error-banner">{error}</div>
                )}

                <div ref={bottomRef} />
            </div>

            <div className="input-bar">
                <textarea
                    ref={textareaRef}
                    className="input-textarea"
                    placeholder="Ask about HDFC Mutual Fund schemes…"
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={handleKeyDown}
                    rows={1}
                    disabled={isLoading}
                />
                <button
                    className="reset-button"
                    title="Start a new session"
                    onClick={handleReset}
                    disabled={isLoading}
                >
                    🔄
                </button>
                <button
                    className="send-button"
                    title="Send message"
                    onClick={handleSend}
                    disabled={isLoading || !inputValue.trim()}
                >
                    {isLoading ? <span className="spinner" /> : '➤'}
                </button>
            </div>
        </div>
    );
}
