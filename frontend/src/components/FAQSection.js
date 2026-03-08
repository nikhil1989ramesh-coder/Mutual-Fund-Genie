'use client';

// Static FAQ list — hardcoded per user specification
const STATIC_FAQS = [
    "What is the latest NAV of HDFC Flexi Cap Fund?",
    "What is the expense ratio of HDFC Small Cap Fund?",
    "What is the exit load for HDFC Mid-Cap Opportunities Fund?",
    "What is the AUM of HDFC Liquid Fund?",
    "What is the lock-in period for HDFC ELSS Tax Saver Fund?",
];

// Renders only the list items — the panel-card wrapper is in page.js
export default function FAQSection({ onFAQClick }) {
    return (
        <div className="faq-list">
            {STATIC_FAQS.map((faq, i) => (
                <button
                    key={i}
                    className="faq-item"
                    onClick={() => onFAQClick?.(faq)}
                    title="Click to ask this question"
                >
                    <span className="faq-arrow">›</span>
                    <span>{faq}</span>
                </button>
            ))}
        </div>
    );
}
