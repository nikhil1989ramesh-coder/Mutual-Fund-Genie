import { NextResponse } from 'next/server';

/**
 * Stub GET /api/faq for Vercel when no external backend is set.
 */

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

// Allow CORS preflight (OPTIONS) to avoid 405 on Vercel.
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Max-Age': '86400',
    },
  });
}

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
