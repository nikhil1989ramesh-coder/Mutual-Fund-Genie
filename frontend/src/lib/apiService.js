/**
 * API Service Layer
 * Communicates with the FastAPI backend at /api/* routes.
 * On Vercel, traffic is proxied. Locally, we talk directly to localhost:8000.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

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
        'Bypass-Tunnel-Reminder': 'true',
        'User-Agent': 'Mozilla/5.0'
      },
      body: JSON.stringify({ message }),
      cache: 'no-store',
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Unknown server error' }));
      throw new Error(errorData.detail || `Server error: ${response.status}`);
    }

    return await response.json();
  } catch (err) {
    if (API_BASE_URL.includes('localhost') && typeof window !== 'undefined' && window.location.hostname !== 'localhost') {
      throw new Error("⚠️ Mobile Connection Blocked: You are viewing this site from a mobile device, but the backend is set to localhost.");
    }

    // Pass the actual error message up, but wrap it if it's a generic "Failed to fetch"
    if (err.message === 'Failed to fetch' || err.name === 'TypeError') {
      const isProduction = typeof window !== 'undefined' && window.location.hostname !== 'localhost';
      throw new Error(isProduction
        ? "⚠️ Unable to connect to the AI server. Please check your internet connection or try again later."
        : "⚠️ Could not reach the backend. Ensure FastAPI is running on port 8000.");
    }
    throw err;
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
