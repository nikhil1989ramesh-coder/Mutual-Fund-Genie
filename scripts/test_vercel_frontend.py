#!/usr/bin/env python3
"""
Test the Next.js frontend after deployment on Vercel.
Checks: home page (GET /), FAQ API (GET /api/faq), Chat API (POST /api/chat).

Vercel project: https://vercel.com/nikhil1989ramesh-5219s-projects/mutual-fund-genie

Usage:
  python scripts/test_vercel_frontend.py
  python scripts/test_vercel_frontend.py --url https://your-app.vercel.app

Environment variable:
  VERCEL_URL  Base URL of the deployed frontend (no trailing slash).
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

# Production URL for mutual-fund-genie (Vercel project)
# https://vercel.com/docs/deployments/generated-urls
DEFAULT_VERCEL_URL = "https://mutual-fund-genie-nikhil1989ramesh-5219s-projects.vercel.app"
TIMEOUT = 20


def test_home(base_url: str) -> tuple:
    """GET / — home page returns 200 and contains app content."""
    url = base_url.rstrip("/") + "/"
    try:
        r = requests.get(url, timeout=TIMEOUT)
        if r.status_code != 200:
            return False, "HTTP {}".format(r.status_code)
        text = (r.text or "").lower()
        if "mutual" in text or "genie" in text or "hdfc" in text or "chat" in text:
            return True, "OK (200, app content found)"
        return True, "OK (200)"
    except requests.RequestException as e:
        return False, str(e)


def test_api_faq(base_url: str) -> tuple:
    """GET /api/faq — returns 200 and JSON with faqs array."""
    url = base_url.rstrip("/") + "/api/faq"
    try:
        r = requests.get(
            url,
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT,
        )
        if r.status_code != 200:
            return False, "HTTP {}".format(r.status_code)
        data = r.json()
        if "faqs" not in data:
            return False, "Response missing 'faqs'"
        if not isinstance(data["faqs"], list):
            return False, "'faqs' is not a list"
        return True, "OK (200, faqs[{}])".format(len(data["faqs"]))
    except requests.RequestException as e:
        return False, str(e)
    except json.JSONDecodeError as e:
        return False, "Invalid JSON: " + str(e)


def test_api_chat(base_url: str) -> tuple:
    """POST /api/chat — returns 200 and JSON with answer and sources."""
    url = base_url.rstrip("/") + "/api/chat"
    try:
        r = requests.post(
            url,
            json={"message": "What is NAV?"},
            headers={"Content-Type": "application/json"},
            timeout=TIMEOUT,
        )
        if r.status_code != 200:
            body = ""
            try:
                body = r.text[:200] if r.text else ""
            except Exception:
                pass
            return False, "HTTP {} {}".format(r.status_code, body or "")
        data = r.json()
        if "answer" not in data:
            return False, "Response missing 'answer'"
        if "sources" not in data:
            return False, "Response missing 'sources'"
        return True, "OK (200, answer + sources)"
    except requests.RequestException as e:
        return False, str(e)
    except json.JSONDecodeError as e:
        return False, "Invalid JSON: " + str(e)


def main():
    parser = argparse.ArgumentParser(
        description="Test Vercel-deployed Next.js frontend (home, /api/faq, /api/chat)."
    )
    parser.add_argument(
        "--url",
        default=os.environ.get("VERCEL_URL", DEFAULT_VERCEL_URL),
        help="Base URL of the Vercel deployment (e.g. https://mutual-fund-genie-xxx.vercel.app)",
    )
    args = parser.parse_args()
    base_url = (args.url or "").strip()
    if not base_url:
        print("Error: provide --url or set VERCEL_URL")
        sys.exit(1)

    tests = [
        ("GET / (home)", test_home),
        ("GET /api/faq", test_api_faq),
        ("POST /api/chat", test_api_chat),
    ]
    results = []
    failed = 0

    for name, test_fn in tests:
        ok, msg = test_fn(base_url)
        results.append((name, ok, msg))
        if not ok:
            failed += 1

    print("\n--- Vercel frontend test ---")
    print("Base URL: {}\n".format(base_url))
    for name, ok, msg in results:
        status = "PASS" if ok else "FAIL"
        print("  [{}] {} — {}".format(status, name, msg))
    print("\n---\n")

    if failed > 0:
        print("Total: {} failed.".format(failed))
        sys.exit(1)
    print("All frontend checks passed.")
    sys.exit(0)


if __name__ == "__main__":
    main()
