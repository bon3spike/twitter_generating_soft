"""Shared helpers for prompt-driven post generation and analysis."""

from __future__ import annotations

import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence, Tuple


UNWANTED_PHRASES = [
    r"please provide",
    r"i(?:'| a)m (?:happy|glad) to",
    r"i'?ll generate",
    r"it seems like",
    r"your request",
    r"got cut off",
    r"there was an error",
]

UNWANTED_PATTERNS = [re.compile(pattern, re.IGNORECASE) for pattern in UNWANTED_PHRASES]

OPENERS = [
    "Start with a question",
    "Start with a bold statement",
    "Start with a personal observation",
    "Start with a fact or statistic",
    "Start with a comparison",
]

ANGLES = [
    "Focus on community benefits",
    "Focus on technical innovation",
    "Focus on real-world use cases",
    "Focus on user experience",
    "Focus on market potential",
]

STRUCTURES = [
    "Use a single clear message",
    "Use a problem-solution format",
    "Use a before-after comparison",
    "Use a numbered list format",
    "Use a story-telling approach",
]


@dataclass(slots=True)
class ProfileSet:
    """Container for randomly selected writing profiles."""

    style: str = ""
    tone: str = ""
    punctuation: str = ""


def load_profiles_from_file(file_path: Path) -> list[str]:
    """Load profiles from a text file."""
    if not file_path.exists():
        return []

    content = file_path.read_text(encoding="utf-8").strip()
    if not content:
        return []

    if "\n\n" in content:
        profiles = [part.strip() for part in content.split("\n\n") if part.strip()]
    else:
        profiles = [line.strip() for line in content.splitlines() if line.strip()]

    return profiles


def pick_profiles(profiles_dir: Path) -> ProfileSet:
    """Return a randomly selected set of profiles."""
    profiles = ProfileSet()

    style_profiles = load_profiles_from_file(profiles_dir / "style.txt")
    if style_profiles:
        profiles.style = random.choice(style_profiles)

    tone_profiles = load_profiles_from_file(profiles_dir / "tone.txt")
    if tone_profiles:
        profiles.tone = random.choice(tone_profiles)

    punctuation_profiles = load_profiles_from_file(profiles_dir / "punctuation.txt")
    if punctuation_profiles:
        profiles.punctuation = random.choice(punctuation_profiles)

    return profiles


def substitute_profiles(
    template: str,
    profiles: ProfileSet,
    placeholders: tuple[str, str, str] = ("{STYLE_PROFILE}", "{TONE_PROFILE}", "{PUNCTUATION_PROFILE}"),
) -> str:
    """Insert selected profiles into a prompt template."""
    style_placeholder, tone_placeholder, punctuation_placeholder = placeholders

    filled = template
    if profiles.style:
        filled = filled.replace(style_placeholder, profiles.style)
    if profiles.tone:
        filled = filled.replace(tone_placeholder, profiles.tone)
    if profiles.punctuation:
        filled = filled.replace(punctuation_placeholder, profiles.punctuation)

    return filled


def add_diversity_controls(prompt: str) -> str:
    """Append randomness directives to a prompt."""
    opener = random.choice(OPENERS)
    angle = random.choice(ANGLES)
    structure = random.choice(STRUCTURES)

    diversity_section = (
        "\nDIVERSITY CONTROLS:\n"
        f"- {opener}\n"
        f"- {angle}\n"
        f"- {structure}\n"
    )
    return f"{prompt.rstrip()}\n{diversity_section}"


def _ngrams(text: str, n: int = 3) -> set[str]:
    words = text.lower().split()
    if len(words) < n:
        return {text.lower()}
    return {" ".join(words[i : i + n]) for i in range(len(words) - n + 1)}


def is_similar(candidate: str, existing: Iterable[str], threshold: float = 0.82) -> bool:
    """Return True if candidate is too similar to any existing entry."""
    candidate_ngrams = _ngrams(candidate)
    for text in existing:
        existing_ngrams = _ngrams(text)
        intersection = len(candidate_ngrams & existing_ngrams)
        union = len(candidate_ngrams | existing_ngrams) or 1
        similarity = intersection / union
        if similarity >= threshold:
            return True
    return False


def matches_unwanted_pattern(text: str, extra_patterns: Sequence[re.Pattern[str]] | None = None) -> bool:
    """Return True if text matches any unwanted pattern."""
    patterns = list(UNWANTED_PATTERNS)
    if extra_patterns:
        patterns.extend(extra_patterns)

    return any(pattern.search(text) for pattern in patterns)


def validate_post(text: str, handle: str | None = None, *, max_length: int = 280) -> Tuple[bool, str]:
    """Basic validation for generated posts."""
    if len(text) > max_length:
        return False, f"Length {len(text)} exceeds {max_length} characters"

    if handle:
        handle = handle.strip()
        if handle:
            mention_count = text.count(handle)
            if mention_count != 1:
                return False, f"{handle} mentions: {mention_count} (expected exactly 1)"

    return True, ""


def ensure_json_object(raw: str) -> str:
    """Best-effort extraction of a JSON object from model output."""
    raw = raw.strip()
    if raw.startswith("{") and raw.endswith("}"):
        return raw

    if "```" in raw:
        segments = raw.split("```")
        for segment in segments:
            segment = segment.strip()
            if segment.lower().startswith("json"):
                segment = segment[4:].strip()
            if segment.startswith("{") and "}" in segment:
                return segment[: segment.rfind("}") + 1]

    start = raw.find("{")
    end = raw.rfind("}")
    if start != -1 and end != -1 and end > start:
        return raw[start : end + 1]

    return raw

