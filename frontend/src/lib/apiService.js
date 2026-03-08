/**
 * API Service Layer
 * Communicates with the FastAPI backend at /api/* routes.
 * On Vercel, traffic is proxied. Locally, we talk directly to localhost:8000.
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Send a chat message to the RAG backend.
 * @param {string} message - The user query.
 * @returns {Promise<{answer: string, sources: string[]}>}
 */
export async function sendChatMessage(message) {
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

  return response.json();
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
