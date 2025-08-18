"""
Simplest possible Perplexity API call:
- Sends only required fields: model + a single user message
- Prints the raw JSON response so you can see structure

Usage:
  PERPLEXITY_API_KEY=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
  python backend/scripts/perplexity_raw_example.py --question "What is Haldiram's latest news?"
"""

import argparse
import json
import os
import asyncio

import httpx
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

API_URL = "https://api.perplexity.ai/chat/completions"


async def run(question: str, model: str = "sonar") -> None:
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise RuntimeError("Missing PERPLEXITY_API_KEY env var")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": question}
        ],
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(API_URL, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()

    print(json.dumps(data, indent=2, ensure_ascii=False))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Minimal Perplexity raw JSON example")
    p.add_argument("--question", required=True, help="Question to ask")
    p.add_argument("--model", default="sonar", help="Model (default: sonar)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(run(args.question, model=args.model))


if __name__ == "__main__":
    main()




