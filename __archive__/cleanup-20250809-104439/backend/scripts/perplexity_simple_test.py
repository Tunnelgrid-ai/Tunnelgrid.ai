"""
Minimal Perplexity Sonar test caller

Purpose:
- Provide a tiny, runnable script to ping Perplexity Sonar with a question
- Keep the system prompt simple (explicit via --system or persona-based via --persona)
- Print the answer content and a deduplicated list of citation URLs for quick inspection

Usage examples:

  # Use explicit system prompt
  python backend/scripts/perplexity_simple_test.py \
    --question "What are recent updates about Haldiram Snacks Pvt?" \
    --system "You are a brand analysis assistant. Cite sources."

  # Or build a simple persona-based system prompt
  python backend/scripts/perplexity_simple_test.py \
    --question "How do customers perceive Haldiram's bhujia?" \
    --persona "Health-Conscious Parent"

Requirements:
- Environment variable PERPLEXITY_API_KEY must be set
- Endpoint: https://api.perplexity.ai/chat/completions
- Model: sonar (default)
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
from typing import Any, Dict, List, Optional

import httpx


# Perplexity Chat Completions endpoint for Sonar family models
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"


def build_persona_system_prompt(persona_description: str) -> str:
    """Build a minimal system prompt using a persona description.

    The intent is to mirror the lightweight persona framing used elsewhere in
    the project, without pulling in broader dependencies. The system prompt
    nudges the model to answer from that persona and to cite sources where
    applicable.
    """
    persona = persona_description.strip() or "a consumer researching brands online"
    return (
        f"You are {persona}.\n\n"
        "Answer the user's question naturally and concisely from this perspective. "
        "Use current, factual information. If you use information from the web, include citations with source URLs."
    )


async def call_perplexity(question: str, system_prompt: str, model: str = "sonar") -> Dict[str, Any]:
    """Call Perplexity Sonar and return a minimal structured result.

    Parameters:
    - question: The user question to send as the user message
    - system_prompt: The system role content
    - model: Perplexity model identifier (default: "sonar")

    Returns:
    - dict with keys:
      - content: model output string
      - citations: list of source URLs (deduplicated)
      - raw: the raw JSON response for debugging/inspection

    Notes on citation extraction:
    - Some Perplexity responses include citations at the top level or under
      choices[0].message.citations. We collect both if present, and then fall
      back to extracting URLs from the generated content as a safety net.
    """
    api_key = os.getenv("PERPLEXITY_API_KEY")
    if not api_key:
        raise RuntimeError("Missing PERPLEXITY_API_KEY environment variable")

    # Standard bearer auth and JSON content type expected by Perplexity API
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Minimal payload: system + user messages. Sonar performs web search
    # automatically; we keep parameters small for a quick test.
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": question},
        ],
        # Keep defaults simple/minimal; Sonar handles search automatically
        "max_tokens": 1000,
        "temperature": 0.7,
    }

    # Simple timeout to avoid hanging in CLI usage
    timeout = httpx.Timeout(60.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(PERPLEXITY_API_URL, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()

    # Extract assistant content (first choice)
    content: str = (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("content", "")
    )

    # Collect citations from known fields, with a URL regex fallback
    citations: List[str] = []

    # 1) Top-level citations (some Perplexity responses include this)
    top_level_cites = data.get("citations")
    if isinstance(top_level_cites, list):
        citations.extend([str(u) for u in top_level_cites if isinstance(u, (str,))])

    # 2) Choice-level/message citations, if present
    msg_cites = (
        data.get("choices", [{}])[0]
        .get("message", {})
        .get("citations")
    )
    if isinstance(msg_cites, list):
        citations.extend([str(u) for u in msg_cites if isinstance(u, (str,))])

    # 3) Fallback: Extract URLs from content
    url_pattern = r"https?://[^\s<>\"{}|\\^`\[\]]+"
    citations.extend(re.findall(url_pattern, content))

    # De-duplicate while preserving order
    seen = set()
    deduped: List[str] = []
    for url in citations:
        clean = re.sub(r"[.,;!?]+$", "", url)
        if clean not in seen:
            seen.add(clean)
            deduped.append(clean)

    return {
        "content": content,
        "citations": deduped,
        "raw": data,
    }


def parse_args() -> argparse.Namespace:
    """Define and parse CLI arguments for the test script.

    Supported args:
    - --question (required): user question
    - --system: explicit system prompt text
    - --persona: persona description to build a system prompt
    - --model: Perplexity model (default: sonar)
    - --pretty: pretty-print JSON output
    """
    parser = argparse.ArgumentParser(description="Minimal Perplexity Sonar test caller")
    parser.add_argument("--question", required=True, help="User question to ask Perplexity")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--system", help="Explicit system prompt text")
    group.add_argument("--persona", help="Persona description to build system prompt from")
    parser.add_argument("--model", default="sonar", help="Perplexity model (default: sonar)")
    parser.add_argument(
        "--pretty", action="store_true", help="Pretty-print JSON output"
    )
    return parser.parse_args()


def main() -> None:
    """Entry point: build system prompt, call API, and print JSON result."""
    args = parse_args()
    if args.system:
        system_prompt = args.system
    else:
        system_prompt = build_persona_system_prompt(args.persona or "a consumer researching brands online")

    result = asyncio.run(call_perplexity(args.question, system_prompt, model=args.model))

    # Minimal console output to inspect response + citations
    output = {
        "question": args.question,
        "model": args.model,
        "system_prompt": system_prompt,
        "content": result["content"],
        "citations": result["citations"],
    }

    if args.pretty:
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(output, ensure_ascii=False))


if __name__ == "__main__":
    main()


