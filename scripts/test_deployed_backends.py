#!/usr/bin/env python3
"""
Test deployed backends: Streamlit app, Vercel frontend, and optional FastAPI API.
Run after deployment to verify live URLs.

Usage:
  python scripts/test_deployed_backends.py
  python scripts/test_deployed_backends.py --streamlit-url URL --vercel-url URL [--backend-url URL]

Environment variables (optional):
  STREAMLIT_URL   Default: https://nikhil-ramesh-ai-mfgenie.streamlit.app
  VERCEL_URL      Default: https://mutual-fund-genie-nikhil1989ramesh-5219s-projects.vercel.app
  BACKEND_API_URL Optional FastAPI base URL (e.g. https://xxx.up.railway.app)
"""

import argparse
import json
import os
import sys

try:
    import requests
except ImportError:
    print("Install requests: pip install requests")
    sys.exit(1)

# Defaults (override with env or CLI)
DEFAULT_STREAMLIT = "https://nikhil-ramesh-ai-mfgenie.streamlit.app"
# Vercel production URL: project mutual-fund-genie, scope nikhil1989ramesh-5219s-projects
DEFAULT_VERCEL = "https://mutual-fund-genie-nikhil1989ramesh-5219s-projects.vercel.app"
TIMEOUT = 15


def test_streamlit(url: str) -> tuple:
    """GET Streamlit app; expect 200 and check for expected content."""
    try:
        r = requests.get(url, timeout=TIMEOUT)
        ok = r.status_code == 200
        if not ok:
            return False, f"HTTP {r.status_code}"
        text = (r.text or "").lower()
        if "streamlit" in text or "mutual" in text or "genie" in text or "hdfc" in text:
            return True, "OK (200, expected content found)"
        return True, "OK (200, page loaded)"
    except requests.RequestException as e:
        return False, str(e)


def test_vercel(url: str) -> tuple:
    """GET Vercel frontend; expect 200."""
    try:
        r = requests.get(url, timeout=TIMEOUT)
        ok = r.status_code == 200
        if not ok:
            return False, f"HTTP {r.status_code}"
        text = (r.text or "").lower()
        if "mutual" in text or "genie" in text or "next" in text or "react" in text:
            return True, "OK (200, expected content found)"
        return True, "OK (200, page loaded)"
    except requests.RequestException as e:
        return False, str(e)


def test_fastapi_docs(base_url: str) -> tuple:
    """GET FastAPI /docs."""
    url = base_url.rstrip("/") + "/docs"
    try:
        r = requests.get(url, timeout=TIMEOUT)
        if r.status_code == 200:
            return True, "OK (200)"
        return False, f"HTTP {r.status_code}"
    except requests.RequestException as e:
        return False, str(e)


def test_fastapi_chat(base_url: str) -> tuple:
    """POST /api/chat with a test message."""
    url = base_url.rstrip("/") + "/api/chat"
    try:
        r = requests.post(
            url,
            json={"message": "What is NAV?"},
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT,
        )
        if r.status_code != 200:
            return False, f"HTTP {r.status_code}"
        data = r.json()
        if not isinstance(data.get("answer"), str):
            return False, "Response missing 'answer'"
        if "sources" not in data:
            return False, "Response missing 'sources'"
        return True, "OK (200, answer + sources)"
    except requests.RequestException as e:
        return False, str(e)
    except json.JSONDecodeError as e:
        return False, "Invalid JSON: " + str(e)


def test_fastapi_faq(base_url: str) -> tuple:
    """GET /api/faq."""
    url = base_url.rstrip("/") + "/api/faq"
    try:
        r = requests.get(url, headers={"Content-Type": "application/json"}, timeout=TIMEOUT)
        if r.status_code != 200:
            return False, f"HTTP {r.status_code}"
        data = r.json()
        if "faqs" not in data:
            return False, "Response missing 'faqs'"
        return True, "OK (200, faqs list)"
    except requests.RequestException as e:
        return False, str(e)
    except json.JSONDecodeError as e:
        return False, "Invalid JSON: " + str(e)


def main():
    parser = argparse.ArgumentParser(description="Test deployed Streamlit, Vercel, and optional FastAPI backend.")
    parser.add_argument("--streamlit-url", default=os.environ.get("STREAMLIT_URL", DEFAULT_STREAMLIT), help="Streamlit app URL")
    parser.add_argument("--vercel-url", default=os.environ.get("VERCEL_URL", DEFAULT_VERCEL), help="Vercel frontend URL")
    parser.add_argument("--backend-url", default=os.environ.get("BACKEND_API_URL", ""), help="Optional FastAPI backend base URL")
    args = parser.parse_args()

    streamlit_url = (args.streamlit_url or "").strip()
    vercel_url = (args.vercel_url or "").strip()
    backend_url = (args.backend_url or "").strip()

    results = []
    failed = 0

    # 1. Streamlit backend (RAG chat UI)
    if streamlit_url:
        ok, msg = test_streamlit(streamlit_url)
        results.append(("Streamlit app (RAG chat)", streamlit_url, ok, msg))
        if not ok:
            failed += 1
    else:
        results.append(("Streamlit app", "(not set)", None, "skipped"))

    # 2. Vercel frontend
    if vercel_url:
        ok, msg = test_vercel(vercel_url)
        results.append(("Vercel frontend", vercel_url, ok, msg))
        if not ok:
            failed += 1
    else:
        results.append(("Vercel frontend", "(not set)", None, "skipped"))

    # 3. Optional FastAPI backend
    if backend_url:
        for name, test_fn in [
            ("FastAPI /docs", test_fastapi_docs),
            ("FastAPI POST /api/chat", test_fastapi_chat),
            ("FastAPI GET /api/faq", test_fastapi_faq),
        ]:
            ok, msg = test_fn(backend_url)
            results.append((name, backend_url, ok, msg))
            if not ok:
                failed += 1
    else:
        results.append(("FastAPI backend", "(not set)", None, "skipped (set BACKEND_API_URL or --backend-url)"))

    # Report
    print("\n--- Deployed backends test ---\n")
    for name, url, ok, msg in results:
        if ok is True:
            status = "PASS"
        elif ok is False:
            status = "FAIL"
        else:
            status = "SKIP"
        print("  [{}] {}".format(status, name))
        print("         URL: {}".format(url))
        print("         {}\n".format(msg))
    print("---\n")
    if failed > 0:
        print("Total: {} failed.".format(failed))
        sys.exit(1)
    print("All checks passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
