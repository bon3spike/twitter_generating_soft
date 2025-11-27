"""Configuration management for the simplified content toolkit."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

try:
    sys.path.insert(0, str(BASE_DIR))
    import settings
except ImportError:  # pragma: no cover
    settings = None


@dataclass(slots=True)
class OpenAIConfig:
    """OpenAI API settings shared by analysis and generation flows."""

    api_key: Optional[str] = None
    model: str = "gpt-4o-mini"
    temperature: float = 0.4
    top_p: float = 0.9
    max_tokens: int = 600
    presence_penalty: float = 0.1
    frequency_penalty: float = 0.1
    generation_temperature: float = 0.95
    generation_top_p: float = 0.9
    generation_presence_penalty: float = 0.6
    generation_frequency_penalty: float = 0.4
    generation_max_tokens: int = 180
    posts_count: int = 5
    project_description_path: Path = BASE_DIR / "project_description.txt"
    target_handle: str = "@projecthandle"


@dataclass(slots=True)
class OutputConfig:
    output_dir: Path = BASE_DIR / "outputs"
    log_file: Path = BASE_DIR / "logs" / "soft_twitter.log"

    def ensure_directories(self) -> None:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)


@dataclass(slots=True)
class AppConfig:
    openai: OpenAIConfig = field(default_factory=OpenAIConfig)
    output: OutputConfig = field(default_factory=OutputConfig)


def _getattr(module, name: str, default):
    return getattr(module, name, default) if module else default


def load_config() -> AppConfig:
    """Populate configuration from settings.py, then environment variables."""
    config = AppConfig()

    if settings:
        config.openai.api_key = _getattr(settings, "OPENAI_API_KEY", config.openai.api_key)
        config.openai.model = _getattr(settings, "OPENAI_MODEL", config.openai.model)
        config.openai.temperature = float(_getattr(settings, "OPENAI_TEMPERATURE", config.openai.temperature))
        config.openai.top_p = float(_getattr(settings, "OPENAI_TOP_P", config.openai.top_p))
        config.openai.max_tokens = int(_getattr(settings, "OPENAI_MAX_TOKENS", config.openai.max_tokens))
        config.openai.presence_penalty = float(_getattr(settings, "OPENAI_PRESENCE_PENALTY", config.openai.presence_penalty))
        config.openai.frequency_penalty = float(_getattr(settings, "OPENAI_FREQUENCY_PENALTY", config.openai.frequency_penalty))
        config.openai.generation_temperature = float(_getattr(settings, "GENERATION_TEMPERATURE", config.openai.generation_temperature))
        config.openai.generation_top_p = float(_getattr(settings, "GENERATION_TOP_P", config.openai.generation_top_p))
        config.openai.generation_presence_penalty = float(_getattr(settings, "GENERATION_PRESENCE_PENALTY", config.openai.generation_presence_penalty))
        config.openai.generation_frequency_penalty = float(_getattr(settings, "GENERATION_FREQUENCY_PENALTY", config.openai.generation_frequency_penalty))
        config.openai.generation_max_tokens = int(_getattr(settings, "GENERATION_MAX_TOKENS", config.openai.generation_max_tokens))
        config.openai.posts_count = int(_getattr(settings, "POSTS_COUNT", config.openai.posts_count))
        config.openai.target_handle = _getattr(settings, "TARGET_HANDLE", config.openai.target_handle)
        project_description_path = _getattr(settings, "PROJECT_DESCRIPTION_PATH", None)
        if project_description_path:
            config.openai.project_description_path = BASE_DIR / project_description_path

        output_dir = _getattr(settings, "OUTPUT_DIR", None)
        if output_dir:
            config.output.output_dir = BASE_DIR / output_dir
        log_file = _getattr(settings, "LOG_FILE", None)
        if log_file:
            config.output.log_file = BASE_DIR / log_file

    env_api_key = os.getenv("OPENAI_API_KEY")
    if env_api_key:
        config.openai.api_key = env_api_key
    config.openai.model = os.getenv("OPENAI_MODEL", config.openai.model)
    config.openai.temperature = float(os.getenv("OPENAI_TEMPERATURE", config.openai.temperature))
    config.openai.top_p = float(os.getenv("OPENAI_TOP_P", config.openai.top_p))
    config.openai.max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", config.openai.max_tokens))
    config.openai.presence_penalty = float(os.getenv("OPENAI_PRESENCE_PENALTY", config.openai.presence_penalty))
    config.openai.frequency_penalty = float(os.getenv("OPENAI_FREQUENCY_PENALTY", config.openai.frequency_penalty))
    config.openai.generation_temperature = float(os.getenv("GENERATION_TEMPERATURE", config.openai.generation_temperature))
    config.openai.generation_top_p = float(os.getenv("GENERATION_TOP_P", config.openai.generation_top_p))
    config.openai.generation_presence_penalty = float(os.getenv("GENERATION_PRESENCE_PENALTY", config.openai.generation_presence_penalty))
    config.openai.generation_frequency_penalty = float(os.getenv("GENERATION_FREQUENCY_PENALTY", config.openai.generation_frequency_penalty))
    config.openai.generation_max_tokens = int(os.getenv("GENERATION_MAX_TOKENS", config.openai.generation_max_tokens))
    config.openai.posts_count = int(os.getenv("POSTS_COUNT", config.openai.posts_count))
    config.openai.target_handle = os.getenv("TARGET_HANDLE", config.openai.target_handle)

    project_description_path = os.getenv("PROJECT_DESCRIPTION_PATH")
    if project_description_path:
        config.openai.project_description_path = Path(project_description_path)

    output_dir = os.getenv("OUTPUT_DIR")
    if output_dir:
        config.output.output_dir = Path(output_dir)
    log_file = os.getenv("LOG_FILE")
    if log_file:
        config.output.log_file = Path(log_file)

    config.output.ensure_directories()
    return config

