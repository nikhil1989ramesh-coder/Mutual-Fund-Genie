/**
 * Pages Router API: /api/faq
 * Handles GET /api/faq for Vercel (Pages API is well-supported).
 */
export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  res.setHeader('Access-Control-Max-Age', '86400');

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'GET') {
    return res.status(405).json({ detail: 'Method not allowed' });
  }

  try {
    return res.status(200).json({
      faqs: [
        'What is the exit load for HDFC Flexi Cap?',
        'What is a mutual fund?',
        'What is the AUM of the HDFC Liquid Fund?',
      ],
    });
  } catch (err) {
    console.error('[pages/api/faq]', err);
    return res.status(500).json({ detail: 'Server error while loading FAQs. Please try again.' });
  }
}
