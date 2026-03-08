/**
 * Unit Tests for apiService.js
 * Tests the frontend API service layer that communicates with the FastAPI backend.
 * Run with: npx jest (after installing jest + @testing-library/react)
 */

// Mock the global fetch
global.fetch = jest.fn();

// Import after mock is set up
const { sendChatMessage, fetchFAQs } = require('./apiService');

const MOCK_API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

beforeEach(() => {
    fetch.mockClear();
});

// ----------  sendChatMessage  ----------
describe('sendChatMessage', () => {
    test('returns answer and sources on success', async () => {
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ answer: 'HDFC Flexi Cap has 2% exit load.', sources: ['https://example.com'] }),
        });

        const result = await sendChatMessage('What is the exit load?');
        expect(result.answer).toBe('HDFC Flexi Cap has 2% exit load.');
        expect(result.sources).toHaveLength(1);
        expect(fetch).toHaveBeenCalledWith(
            expect.stringMatching(/\/api\/chat$/),
            expect.objectContaining({ method: 'POST' })
        );
    });

    test('throws on non-ok HTTP response', async () => {
        fetch.mockResolvedValueOnce({
            ok: false,
            status: 500,
            headers: { get: () => 'application/json' },
            json: async () => ({ detail: 'Internal server error' }),
        });

        await expect(sendChatMessage('test')).rejects.toThrow('Internal server error');
    });

    test('throws on network failure', async () => {
        fetch.mockRejectedValueOnce(new Error('Network unreachable'));

        await expect(sendChatMessage('test')).rejects.toThrow('Network unreachable');
    });

    test('throws on empty message body', async () => {
        // The backend returns 400 for empty messages; simulate that response
        fetch.mockResolvedValueOnce({
            ok: false,
            status: 400,
            headers: { get: () => 'application/json' },
            json: async () => ({ detail: 'Empty message received.' }),
        });

        await expect(sendChatMessage('')).rejects.toThrow('Empty message received.');
    });
});

// ----------  fetchFAQs  ----------
describe('fetchFAQs', () => {
    test('returns faqs array on success', async () => {
        fetch.mockResolvedValueOnce({
            ok: true,
            json: async () => ({ faqs: ['What is NAV?', 'What is a SIP?', 'What is exit load?'] }),
        });

        const result = await fetchFAQs();
        expect(result.faqs).toHaveLength(3);
        expect(result.faqs[0]).toBe('What is NAV?');
    });

    test('throws on non-ok HTTP response', async () => {
        fetch.mockResolvedValueOnce({
            ok: false,
            status: 500,
            headers: { get: () => 'application/json' },
            json: async () => ({ detail: 'Failed to load FAQs' }),
        });

        await expect(fetchFAQs()).rejects.toThrow('Failed to load FAQs');
    });
});
