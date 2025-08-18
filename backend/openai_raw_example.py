"""
Simplest possible OpenAI API call using GPT-5 with web search:
- Sends required fields: model + a single user message
- Enables web search so the model can browse and cite current info
- Prints both the assistant's text and the raw JSON response

Usage:
  OPENAI_API_KEY=your_openai_api_key_here \
  python backend/openai_raw_example.py --question "What is Haldiram's latest news?"

Optional:
  --model gpt-5  # override model if needed
"""

import argparse
import json
import os
import asyncio

import httpx
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

CHAT_API_URL = "https://api.openai.com/v1/chat/completions"
RESPONSES_API_URL = "https://api.openai.com/v1/responses"


async def run(question: str, model: str = "gpt-5") -> None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY env var")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        # 1) Try Chat Completions with web search tool (for supported models)
        chat_payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": question}
            ],
            # Enable web search using the tools parameter
            "tools": [{"type": "web_search"}]
        }
        
        try:
            resp = await client.post(CHAT_API_URL, headers=headers, json=chat_payload)
            if resp.status_code >= 400:
                # Print server error details and fall back
                print(f"Web search attempt failed ({resp.status_code}):")
                try:
                    error_data = resp.json()
                    print(json.dumps(error_data, indent=2))
                except Exception:
                    print(resp.text)
                print("\nFalling back to standard chat...")
                raise httpx.HTTPStatusError("Web search unsupported", request=resp.request, response=resp)
            
            data = resp.json()
            
            # Extract assistant text
            try:
                assistant_text = data["choices"][0]["message"]["content"]
                print("\n--- Assistant Reply (with web search) ---\n")
                print(assistant_text)
                print("\n-----------------------------------------\n")
            except Exception:
                pass

            print(json.dumps(data, indent=2, ensure_ascii=False))
            return
            
        except httpx.HTTPStatusError:
            # Fall through to standard chat
            pass

        # 2) Fall back to Chat Completions without web search
        fallback_payload = {
            "model": model,
            "messages": [
                {"role": "user", "content": question}
            ]
        }
        
        try:
            resp = await client.post(CHAT_API_URL, headers=headers, json=fallback_payload)
            resp.raise_for_status()
            data = resp.json()
        except httpx.HTTPStatusError as e:
            # If GPT-5 fails, try gpt-4o as final fallback
            if model == "gpt-5":
                print(f"GPT-5 failed, trying gpt-4o...")
                fallback_payload["model"] = "gpt-4o"
                resp = await client.post(CHAT_API_URL, headers=headers, json=fallback_payload)
                resp.raise_for_status()
                data = resp.json()
            else:
                raise

        # Print assistant text and full JSON
        try:
            assistant_text = data["choices"][0]["message"]["content"]
            print("\n--- Assistant Reply ---\n")
            print(assistant_text)
            print("\n-----------------------\n")
        except Exception:
            pass

        print(json.dumps(data, indent=2, ensure_ascii=False))


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Minimal OpenAI GPT-5 example with web search fallback")
    p.add_argument("--question", required=True, help="Question to ask")
    p.add_argument("--model", default="gpt-5", help="Model (default: gpt-5)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    asyncio.run(run(args.question, model=args.model))


if __name__ == "__main__":
    main()
