"""
Configuration utilities for loading environment variables and API keys.

This module uses python-dotenv to load configuration from a .env file located
in the project root directory. The .env file should contain key-value pairs in
the format KEY=VALUE, with each pair on a new line.

Example .env file:
```
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_API_URL=https://generativelanguage.googleapis.com/v1beta
GEMINI_MODEL=gemini-pro-vision
```

Place the .env file in the root directory of your project (same level as the
pyproject.toml file).
"""

import os

from dotenv import load_dotenv

# Path to the .env file (relative to the project root)
DEFAULT_ENV_FILE = ".env"


def get_gemini_api_key() -> str:
    """
    Load API key from environment variables.

    Returns:
        The API key as a string

    Raises:
        ValueError: If the API key is not found in environment variables
    """
    # Load from environment (via .env file)
    load_dotenv(DEFAULT_ENV_FILE)
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key or api_key == "your_api_key_here":
        raise ValueError(
            "Gemini API key not found. Please set the GEMINI_API_KEY "
            "environment variable in your .env file."
        )

    return api_key


def get_gemini_api_url() -> str:
    """
    Get the Gemini API URL from environment variables.

    Returns:
        The API URL as a string, defaults to the standard endpoint if not set
    """
    load_dotenv(DEFAULT_ENV_FILE)
    return os.getenv(
        "GEMINI_API_URL", "https://generativelanguage.googleapis.com/v1beta"
    )


def get_gemini_model() -> str:
    """
    Get the Gemini model name from environment variables.

    Returns:
        The model name as a string, defaults to gemini-pro if not set
    """
    load_dotenv(DEFAULT_ENV_FILE)
    return os.getenv("GEMINI_MODEL", "gemini-pro")
