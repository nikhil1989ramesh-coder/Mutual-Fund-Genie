/**
 * API Service Layer
 * Communicates with the FastAPI backend at /api/* routes.
 * On Vercel, traffic is proxied. Locally, we talk directly to localhost:8000.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://mutual-fund-genie-api.loca.lt';

/**
 * Send a chat message to the RAG backend.
 * @param {string} message - The user query.
 * @returns {Promise<{answer: string, sources: string[]}>}
 */
export async function sendChatMessage(message) {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
      cache: 'no-store', // Force Next.js to bypass all caches and hit the Python API
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
      throw new Error(errorData.detail || `HTTP error: ${response.status}`);
    }

    return await response.json();
  } catch (err) {
    if (API_BASE_URL.includes('localhost') && typeof window !== 'undefined' && window.location.hostname !== 'localhost') {
      throw new Error("⚠️ Mobile Connection Blocked: You are viewing this site from a mobile device on Vercel, but the AI engine is running locally on your computer ('localhost'). To test on mobile, access the Next.js app using your computer's Local IP address (e.g., http://192.168.x.x:3000) while on the same Wi-Fi network.");
    }
    throw new Error(err.message || "⚠️ Could not reach the server. Make sure the backend is running on port 8000.");
  }
}

/**
 * Fetch dynamically generated FAQs from the backend.
 * @returns {Promise<{faqs: string[]}>}
 */
export async function fetchFAQs() {
  const response = await fetch(`${API_BASE_URL}/api/faq`, {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to load FAQs: HTTP ${response.status}`);
  }

  return response.json();
}
