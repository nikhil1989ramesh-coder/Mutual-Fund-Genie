/**
 * Pages Router API: /api/chat
 * Handles POST /api/chat for Vercel (Pages API is well-supported).
 * When NEXT_PUBLIC_API_URL is set, the client calls that URL instead.
 */

export const config = {
  api: {
    bodyParser: {
      sizeLimit: '256kb',
    },
    responseLimit: false,
  },
};

export default function handler(req, res) {
  // CORS: allow all origins in production for same-origin and cross-origin
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.setHeader('Access-Control-Max-Age', '86400');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ detail: 'Method not allowed' });
  }

  try {
    const body = req.body;
    const message = (body && typeof body === 'object' && body !== null && 'message' in body)
      ? (typeof body.message === 'string' ? body.message.trim() : '')
      : '';
    if (!message) {
      return res.status(400).json({ detail: 'Empty message received.' });
    }
    return res.status(200).json({
      answer: 'This deployment is running without the RAG backend. For full answers, run the FastAPI backend locally (see README) or set NEXT_PUBLIC_API_URL to your backend URL.\n\nLast updated from sources: https://www.indmoney.com/mutual-funds/amc/hdfc-mutual-fund',
      sources: ['https://www.indmoney.com/mutual-funds/amc/hdfc-mutual-fund'],
    });
  } catch (err) {
    console.error('[pages/api/chat]', err);
    return res.status(500).json({ detail: 'Server error while processing your message. Please try again.' });
  }
}
