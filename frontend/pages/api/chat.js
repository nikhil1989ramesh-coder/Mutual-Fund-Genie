/**
 * Next.js Pages API: /api/chat
 * Stub when NEXT_PUBLIC_API_URL is unset. On Vercel: friendly message + link to full RAG chat. Locally: dev hint.
 */

const STREAMLIT_RAG_URL = 'https://nikhil-ramesh-ai-mfgenie.streamlit.app';

function getStubAnswer() {
  if (process.env.VERCEL === '1') {
    return (
      'For full AI answers with sources on HDFC Mutual Fund schemes, use the dedicated chat here: ' +
      STREAMLIT_RAG_URL +
      '\n\nYou can ask questions there and get instant answers with citations. Last updated from sources: ' +
      STREAMLIT_RAG_URL
    );
  }
  return (
    'Running without RAG backend. Start Phase-4_Backend_API (port 8000) and set NEXT_PUBLIC_API_URL=http://localhost:8000 in frontend/.env.local for full answers.\n\nLast updated from sources: https://www.indmoney.com/mutual-funds/amc/hdfc-mutual-fund'
  );
}

function getStubSources() {
  if (process.env.VERCEL === '1') {
    return [STREAMLIT_RAG_URL];
  }
  return ['https://www.indmoney.com/mutual-funds/amc/hdfc-mutual-fund'];
}

export const config = {
  api: {
    bodyParser: { sizeLimit: '256kb' },
    responseLimit: false,
  },
};

export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.setHeader('Access-Control-Max-Age', '86400');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ detail: 'Method not allowed' });

  try {
    const body = req.body;
    const message = (body && typeof body === 'object' && body !== null && 'message' in body)
      ? (typeof body.message === 'string' ? body.message.trim() : '')
      : '';
    if (!message) return res.status(400).json({ detail: 'Empty message received.' });

    return res.status(200).json({
      answer: getStubAnswer(),
      sources: getStubSources(),
    });
  } catch (err) {
    console.error('[pages/api/chat]', err);
    return res.status(500).json({ detail: 'Server error while processing your message. Please try again.' });
  }
}
