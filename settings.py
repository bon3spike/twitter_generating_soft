"""Editable defaults for the simplified content toolkit."""

# OpenAI API key (or set OPENAI_API_KEY in .env)
OPENAI_API_KEY = None

# Target handle/project mention inserted into prompts
TARGET_HANDLE = "@projecthandle"

# Default model + sampling settings
OPENAI_MODEL = "gpt-4o-mini"
OPENAI_TEMPERATURE = 0.4
OPENAI_TOP_P = 0.9
OPENAI_MAX_TOKENS = 600
OPENAI_PRESENCE_PENALTY = 0.1
OPENAI_FREQUENCY_PENALTY = 0.1

# Generation-specific sampling overrides
GENERATION_TEMPERATURE = 0.95
GENERATION_TOP_P = 0.9
GENERATION_PRESENCE_PENALTY = 0.6
GENERATION_FREQUENCY_PENALTY = 0.4
GENERATION_MAX_TOKENS = 180

# Default number of posts to generate from the CLI menu
POSTS_COUNT = 5

# Optional custom project description path (relative to repo root)
PROJECT_DESCRIPTION_PATH = "project_description.txt"

# Output locations
OUTPUT_DIR = "outputs"
LOG_FILE = "logs/soft_twitter.log"

