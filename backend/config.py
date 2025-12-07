"""Configuration for the LLM Council.

This version uses CLI tools (Gemini CLI, Codex CLI, Claude CLI) instead of
external APIs. No API keys required - uses local CLI subscriptions.
"""

# =============================================================================
# CLI-Based Council Configuration
# =============================================================================

# Council members - CLI identifiers
# Each member will be queried via its respective CLI tool:
# - gemini: Google Gemini CLI (https://github.com/google-gemini/gemini-cli)
# - codex: OpenAI Codex CLI (https://github.com/openai/codex)
# - claude: Anthropic Claude CLI (https://github.com/anthropics/claude-code)
COUNCIL_MODELS = [
    "gemini",   # Google Gemini via Gemini CLI
    "codex",    # OpenAI GPT via Codex CLI
    "claude",   # Anthropic Claude via Claude CLI
]

# Chairman model - synthesizes final response
# Uses Gemini as default chairman (fast and good at synthesis)
CHAIRMAN_MODEL = "gemini"

# =============================================================================
# Storage Configuration
# =============================================================================

# Data directory for conversation storage
DATA_DIR = "data/conversations"
