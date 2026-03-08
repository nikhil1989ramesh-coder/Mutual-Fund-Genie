/**
 * API Service Layer
 * Communicates with the FastAPI backend at /api/* routes.
 * When NEXT_PUBLIC_API_URL is empty, calls same-origin /api/* (Next.js stub routes on Vercel).
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

/**
 * Parse error body from a failed response; always return an object with detail.
 * For 404 on same-origin in production, suggests Vercel Root Directory fix.
 */
async function parseErrorResponse(response, requestUrl = '') {
  const contentType = (response && typeof response.headers?.get === 'function')
    ? (response.headers.get('content-type') || '')
    : '';
  const status = response?.status;
  const isSameOrigin = typeof window !== 'undefined' && requestUrl.startsWith('/');
  const isProd = typeof window !== 'undefined' && window.location.hostname !== 'localhost';

  try {
    if (contentType.includes('application/json')) {
      const data = await response.json();
      return { detail: data.detail || data.message || `Server error: ${status}` };
    }
    const text = typeof response?.text === 'function' ? await response.text() : '';
    if (text && text.length < 200) return { detail: text };
    if (status === 404 && isSameOrigin && isProd) {
      return {
        detail: "API routes not found (404). In Vercel: set Root Directory to 'frontend', then redeploy. See README or ROOT_CAUSE_ANALYSIS.md.",
      };
    }
    return { detail: status ? `Server error: ${status}. Please try again.` : 'Request failed.' };
  } catch {
    const msg = status === 404 && isSameOrigin && isProd
      ? "API routes not found (404). In Vercel: set Root Directory to 'frontend', then redeploy."
      : status === 405
        ? 'Request method not allowed (405). Please refresh and try again.'
        : status === 500
          ? 'Server error. Please try again.'
          : status
            ? `Request failed: ${status}`
            : 'Request failed.';
    return { detail: msg };
  }
}

/**
 * Send a chat message to the RAG backend (or Next.js stub).
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
      const errorData = await parseErrorResponse(response, `${API_BASE_URL}/api/chat`);
      throw new Error(errorData.detail || `Server error: ${response.status}`);
    }

    return await response.json();
  } catch (err) {
    if (API_BASE_URL.includes('localhost') && typeof window !== 'undefined' && window.location.hostname !== 'localhost') {
      throw new Error("⚠️ Mobile Connection Blocked: You are viewing this site from a mobile device, but the backend is set to localhost.");
    }

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
    const errorData = await parseErrorResponse(response, `${API_BASE_URL}/api/faq`);
    throw new Error(errorData.detail || `Failed to load FAQs: HTTP ${response.status}`);
  }

  return response.json();
}
