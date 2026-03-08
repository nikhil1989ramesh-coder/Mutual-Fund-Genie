/**
 * @jest-environment jsdom
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';

// Mock the apiService module used inside ChatInterface
jest.mock('../lib/apiService', () => ({
  sendChatMessage: jest.fn(),
}));

import { sendChatMessage } from '../lib/apiService';
import ChatInterface from './ChatInterface';

describe('ChatInterface failure modes', () => {
  beforeAll(() => {
    // jsdom doesn't implement scrollIntoView; mock it so effects don't crash.
    if (!HTMLElement.prototype.scrollIntoView) {
      HTMLElement.prototype.scrollIntoView = jest.fn();
    }
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  function typeAndSend(question) {
    render(<ChatInterface />);
    const textarea = screen.getByPlaceholderText(/Ask about HDFC Mutual Fund schemes/i);
    fireEvent.change(textarea, { target: { value: question } });
    const sendButton = screen.getByTitle(/Send message/i);
    fireEvent.click(sendButton);
  }

  test('shows busy engine banner when backend returns rate-limit friendly message', async () => {
    sendChatMessage.mockResolvedValueOnce({
      answer: 'The AI server is currently receiving too many requests. Please wait a moment and try again.',
      sources: ['https://example.com'],
    });

    typeAndSend('What is the expense ratio of HDFC Small Cap Fund?');

    await waitFor(() => {
      expect(
        screen.getByText(/The AI engine is temporarily busy/i)
      ).toBeInTheDocument();
    });

    // Busy text from backend should not appear as a chat bubble
    expect(
      screen.queryByText(/currently receiving too many requests/i)
    ).not.toBeInTheDocument();
  });

  test('shows generic backend error banner when apiService rejects', async () => {
    sendChatMessage.mockRejectedValueOnce(new Error('Network unreachable'));

    typeAndSend('Tell me about HDFC Flexi Cap');

    await waitFor(() => {
      // ChatInterface displays err.message in the error banner
      expect(
        screen.getByText(/Network unreachable/i)
      ).toBeInTheDocument();
    });
  });

  test('renders normal bot response when backend succeeds', async () => {
    sendChatMessage.mockResolvedValueOnce({
      answer: 'HDFC Flexi Cap has an expense ratio of 1%.',
      sources: [],
    });

    typeAndSend('What is the expense ratio of HDFC Flexi Cap?');

    await waitFor(() => {
      expect(
        screen.getByText(/HDFC Flexi Cap has an expense ratio of 1%./i)
      ).toBeInTheDocument();
    });

    // No error banners should be shown
    expect(
      screen.queryByText(/The AI engine is temporarily busy/i)
    ).not.toBeInTheDocument();
    expect(
      screen.queryByText(/Could not reach the server/i)
    ).not.toBeInTheDocument();
  });
});

