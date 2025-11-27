#!/usr/bin/env python3
"""Analyze existing posts to extract tone, style, and prompt hints."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Dict, List

BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from content_utils import ensure_json_object
from twitter_tool.config import load_config
from twitter_tool.logger import setup_logger
from twitter_tool.openai_client import OpenAIClient


def load_posts(path: Path) -> list[str]:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        raise ValueError("Input file is empty")
    if "\n\n" in content:
        posts = [block.strip() for block in content.split("\n\n") if block.strip()]
    else:
        posts = [line.strip() for line in content.splitlines() if line.strip()]
    if not posts:
        raise ValueError("No posts found in input file")
    return posts


def analyze_post(client: OpenAIClient, post: str) -> Dict[str, Any]:
    system_prompt = (
        "You are a linguistic analyst. "
        "Given a social media post, you explain its tone, writing style, "
        "narrative angle, and provide a short hint for recreating it."
    )
    user_prompt = (
        "Analyze the post below.\n\n"
        "Return ONLY JSON with keys: "
        "style_label, style_description, "
        "tone_label, tone_description, "
        "narrative_summary, prompt_hint.\n\n"
        f"POST:\n{post}"
    )
    response = client.generate(system_prompt, user_prompt)
    payload = json.loads(ensure_json_object(response))
    payload["post"] = post
    return payload


def analyze_posts(posts: list[str], client: OpenAIClient, logger) -> List[Dict[str, Any]]:
    results = []
    for idx, post in enumerate(posts, start=1):
        try:
            logger.info("Analyzing post %s/%s", idx, len(posts))
            results.append(analyze_post(client, post))
        except Exception as exc:  # noqa: BLE001
            logger.error("Failed to analyze post %s: %s", idx, exc)
    return results


def write_markdown(results: List[Dict[str, Any]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Post Analysis Report", ""]
    for idx, item in enumerate(results, start=1):
        lines.append(f"## Post {idx}")
        lines.append(item["post"])
        lines.append("")
        lines.append(f"- **Style:** {item.get('style_label', 'n/a')} — {item.get('style_description', '').strip()}")
        lines.append(f"- **Tone:** {item.get('tone_label', 'n/a')} — {item.get('tone_description', '').strip()}")
        lines.append(f"- **Narrative:** {item.get('narrative_summary', '').strip()}")
        lines.append(f"- **Prompt hint:** {item.get('prompt_hint', '').strip()}")
        lines.append("")
    path.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze existing posts for tone and style patterns",
    )
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        default=BASE_DIR / "analysis_input.txt",
        help="Text file with posts to analyze (separate posts by blank lines)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Path to save the Markdown report (default: outputs/analysis_report_TIMESTAMP.md)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    posts = load_posts(args.input)
    config = load_config()
    logger = setup_logger(config.output.log_file, verbose=args.verbose)

    if not config.openai.api_key:
        raise SystemExit("OPENAI_API_KEY is not configured")

    client = OpenAIClient(
        api_key=config.openai.api_key,
        model=config.openai.model,
        temperature=config.openai.temperature,
        max_tokens=config.openai.max_tokens,
        top_p=config.openai.top_p,
        presence_penalty=config.openai.presence_penalty,
        frequency_penalty=config.openai.frequency_penalty,
    )

    results = analyze_posts(posts, client, logger)
    if not results:
        raise SystemExit("No analysis results were produced.")

    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        output_path = config.output.output_dir / f"analysis_report_{timestamp}.md"

    write_markdown(results, output_path)
    print(f"✓ Analysis saved to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

