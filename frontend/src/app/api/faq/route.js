import { NextResponse } from 'next/server';

/**
 * Stub GET /api/faq for Vercel when no external backend is set.
 */
export async function GET() {
  return NextResponse.json({
    faqs: [
      'What is the exit load for HDFC Flexi Cap?',
      'What is a mutual fund?',
      'What is the AUM of the HDFC Liquid Fund?',
    ],
  });
}
