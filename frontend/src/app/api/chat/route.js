import { NextResponse } from 'next/server';

/**
 * Stub POST /api/chat for Vercel when no external backend is set.
 * When NEXT_PUBLIC_API_URL is set, the client calls that URL instead.
 */
export async function POST(request) {
  try {
    const body = await request.json();
    const message = body?.message?.trim();
    if (!message) {
      return NextResponse.json(
        { detail: 'Empty message received.' },
        { status: 400 }
      );
    }
  } catch {
    return NextResponse.json(
      { detail: 'Invalid JSON body.' },
      { status: 400 }
    );
  }

  return NextResponse.json({
    answer: 'This deployment is running without the RAG backend. For full answers, run the FastAPI backend locally (see README) or set NEXT_PUBLIC_API_URL to your backend URL.\n\nLast updated from sources: https://www.indmoney.com/mutual-funds/amc/hdfc-mutual-fund',
    sources: ['https://www.indmoney.com/mutual-funds/amc/hdfc-mutual-fund'],
  });
}
