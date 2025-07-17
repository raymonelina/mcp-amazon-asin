"""
Utilities for interacting with the Google Gemini API.
"""

import asyncio
import json
from typing import Dict, Any

import aiohttp

from mcp_amazon_asin import config


async def chat_with_gemini(prompt: str) -> str:
    """
    Send a prompt to the Gemini API and get a response.
    Uses the model specified in the config.

    Args:
        prompt: The text prompt to send to the model

    Returns:
        The text response from the model

    Raises:
        ValueError: If the API request fails
    """
    api_key = config.get_gemini_api_key()
    api_url = config.get_gemini_api_url()
    model = config.get_gemini_model()

    # Construct the full API URL
    url = f"{api_url}/models/{model}:generateContent?key={api_key}"

    # Prepare the request payload with maximized settings
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 8192,  # Maximum allowed for most models
        },
        "safetySettings": [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_ONLY_HIGH"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_ONLY_HIGH"},
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH",
            },
        ],
    }

    # Send the request to the API
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as response:
            if response.status != 200:
                error_text = await response.text()
                raise ValueError(
                    f"API request failed with status {response.status}: {error_text}"
                )

            response_data = await response.json()

            # Extract the response text from the API response
            try:
                return response_data["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError) as e:
                raise ValueError(
                    f"Failed to parse API response: {e}\nResponse: {json.dumps(response_data)}"
                )
