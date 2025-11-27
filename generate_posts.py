#!/usr/bin/env python3
"""Generate short social posts from a reusable prompt template."""

from __future__ import annotations

import argparse
import csv
import sys
from datetime import UTC, datetime
from pathlib import Path

# Add parent directory to path
BASE_DIR = Path(__file__).parent
sys.path.insert(0, str(BASE_DIR))

from content_utils import (
    add_diversity_controls,
    is_similar,
    matches_unwanted_pattern,
    pick_profiles,
    substitute_profiles,
    validate_post,
)
from twitter_tool.config import load_config
from twitter_tool.logger import setup_logger
from twitter_tool.openai_client import OpenAIClient


def replace_handle_placeholders(text: str, handle: str | None) -> str:
    """Replace generic placeholders with the configured handle."""
    if not handle:
        handle = "@projecthandle"
    return text.replace("{TARGET_HANDLE}", handle).replace("{{TARGET_HANDLE}}", handle)


def load_project_description(path: Path | None) -> str | None:
    if path and path.exists():
        return path.read_text(encoding="utf-8").strip() or None
    return None


def save_posts(posts: list[str], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["post"])
        for post in posts:
            writer.writerow([post])


def build_user_prompt(
    template: str,
    *,
    profiles_dir: Path,
    target_handle: str | None,
    project_description: str | None,
) -> str:
    prompt_body = replace_handle_placeholders(template, target_handle)

    if profiles_dir.exists():
        profiles = pick_profiles(profiles_dir)
        prompt_body = substitute_profiles(prompt_body, profiles)

    prompt_body = add_diversity_controls(prompt_body)

    if project_description:
        prompt_body = (
            f"PROJECT DESCRIPTION:\n{project_description}\n\n---\n\n{prompt_body}"
        )

    return prompt_body


def generate_posts(
    *,
    template: str,
    count: int,
    client: OpenAIClient,
    profiles_dir: Path,
    target_handle: str | None,
    project_description: str | None,
    logger,
) -> list[str]:
    system_prompt = (
        "You craft concise social media posts. "
        "Always follow the provided template and keep every post under 280 characters."
    )

    posts: list[str] = []
    max_attempts = count * 8
    attempts = 0

    while len(posts) < count and attempts < max_attempts:
        attempts += 1
        user_prompt = build_user_prompt(
            template,
            profiles_dir=profiles_dir,
            target_handle=target_handle,
            project_description=project_description,
        )
        response = client.generate(system_prompt, user_prompt).strip()

        is_valid, reason = validate_post(response, handle=target_handle)
        if not is_valid:
            logger.debug("Discarded post (validation): %s", reason)
            continue
        
        if matches_unwanted_pattern(response):
            logger.debug("Discarded post (unwanted pattern): %s", response)
            continue
        
        if is_similar(response, posts):
            logger.debug("Discarded post (too similar)")
            continue
        
        posts.append(response)
        logger.info("Generated %s/%s posts", len(posts), count)
    
    if len(posts) < count:
        logger.warning("Only generated %s posts out of %s requested", len(posts), count)
    
    return posts


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate short posts and save them to CSV",
    )
    parser.add_argument(
        "--prompt-file",
        "-f",
        type=Path,
        default=BASE_DIR / "prompt.txt",
        help="Path to the prompt template (default: prompt.txt)",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Path to output CSV file (default: outputs/generated_posts_TIMESTAMP.csv)",
    )
    parser.add_argument(
        "--count",
        "-c",
        type=int,
        help="Number of posts to generate (default: value from settings.py)",
    )
    parser.add_argument(
        "--profiles-dir",
        type=Path,
        default=BASE_DIR / "unique",
        help="Directory with style/tone/punctuation profiles",
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

    if not args.prompt_file.exists():
        raise SystemExit(f"Prompt file not found: {args.prompt_file}")

    prompt_template = args.prompt_file.read_text(encoding="utf-8").strip()
    if not prompt_template:
        raise SystemExit("Prompt file is empty")

    config = load_config()
    logger = setup_logger(config.output.log_file, verbose=args.verbose)
    
    count = args.count or config.openai.posts_count

    if not config.openai.api_key:
        raise SystemExit("OPENAI_API_KEY is not configured")
    
    client = OpenAIClient(
        api_key=config.openai.api_key,
        model=config.openai.model,
        temperature=config.openai.generation_temperature,
        max_tokens=config.openai.generation_max_tokens,
        top_p=config.openai.generation_top_p,
        presence_penalty=config.openai.generation_presence_penalty,
        frequency_penalty=config.openai.generation_frequency_penalty,
    )

    project_description = load_project_description(config.openai.project_description_path)

    posts = generate_posts(
        template=prompt_template,
        count=count,
        client=client,
        profiles_dir=args.profiles_dir,
        target_handle=config.openai.target_handle,
        project_description=project_description,
        logger=logger,
    )

    if not posts:
        raise SystemExit("Generation failed. Adjust your prompt and try again.")

    if args.output:
        output_path = args.output
    else:
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        output_path = config.output.output_dir / f"generated_posts_{timestamp}.csv"

    save_posts(posts, output_path)
    logger.info("Saved %s posts to %s", len(posts), output_path)
    print(f"✓ Generated {len(posts)} posts -> {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

