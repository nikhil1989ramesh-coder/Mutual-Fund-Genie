import { NextResponse } from 'next/server';

/**
 * Stub POST /api/chat for Vercel when no external backend is set.
 * When NEXT_PUBLIC_API_URL is set, the client calls that URL instead.
 */

export const dynamic = 'force-dynamic';
export const runtime = 'nodejs';

// Allow CORS preflight (OPTIONS) so browsers don't get 405 on same-origin POST.
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Max-Age': '86400',
    },
  });
}

export async function POST(request) {
  try {
    const body = await request.json().catch(() => ({}));
    const message = body?.message?.trim();
    if (!message) {
      return NextResponse.json(
        { detail: 'Empty message received.' },
        { status: 400 }
      );
    }

    return NextResponse.json({
      answer: 'This deployment is running without the RAG backend. For full answers, run the FastAPI backend locally (see README) or set NEXT_PUBLIC_API_URL to your backend URL.\n\nLast updated from sources: https://www.indmoney.com/mutual-funds/amc/hdfc-mutual-fund',
      sources: ['https://www.indmoney.com/mutual-funds/amc/hdfc-mutual-fund'],
    });
  } catch (err) {
    console.error('[api/chat]', err);
    return NextResponse.json(
      { detail: 'Server error while processing your message. Please try again.' },
      { status: 500 }
    );
  }
}
