import { NextResponse } from 'next/server';

/**
 * Stub GET /api/faq for Vercel when no external backend is set.
 */
export async function GET() {
  try {
    return NextResponse.json({
      faqs: [
        'What is the exit load for HDFC Flexi Cap?',
        'What is a mutual fund?',
        'What is the AUM of the HDFC Liquid Fund?',
      ],
    });
  } catch (err) {
    console.error('[api/faq]', err);
    return NextResponse.json(
      { detail: 'Server error while loading FAQs. Please try again.' },
      { status: 500 }
    );
  }
}
