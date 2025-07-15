"""
Cache utilities for storing and retrieving data.
"""

import json
import logging
import os
import time
from typing import Any, TypeVar

# Configure logger
logger = logging.getLogger(__name__)

# Cache expiration time in seconds (1 hour)
CACHE_EXPIRATION_SECONDS = 3600

# Type for cached data
T = TypeVar("T", bound=dict[str, Any])


def get_from_cache(
    key: str,
    cache_folder: str,
    required_fields: list[str] | None = None,
) -> dict[str, Any] | None:
    """
    Retrieve data from cache if it exists and is valid.

    Args:
        key: The cache key (e.g., ASIN)
        cache_folder: Folder where cache is stored
        required_fields: List of fields that must be present for cache to be valid

    Returns:
        The cached data if valid, None otherwise
    """
    if not cache_folder:
        return None

    os.makedirs(cache_folder, exist_ok=True)
    json_path = f"{cache_folder}/{key}.json"

    if not os.path.exists(json_path):
        return None

    try:
        with open(json_path) as f:
            cached_data = json.load(f)

        # Check if timestamp exists and is within expiration period
        if "timestamp" in cached_data:
            cache_time = cached_data["timestamp"]
            current_time = int(time.time())

            if current_time - cache_time <= CACHE_EXPIRATION_SECONDS:
                # Validate all required fields are present if specified
                if required_fields:
                    for field in required_fields:
                        if field not in cached_data or cached_data[field] is None:
                            logger.debug(
                                f"Cache invalid for {key}: missing field {field}"
                            )
                            return None

                logger.debug(
                    f"Using cached data for {key} (age: {current_time - cache_time} seconds)"
                )
                return cached_data
            else:
                logger.debug(
                    f"Cache expired for {key} (age: {current_time - cache_time} seconds)"
                )

    except Exception as e:
        logger.error(f"Error reading cache for {key}: {e!s}")

    return None


def save_to_cache(
    key: str,
    data: dict[str, Any],
    cache_folder: str,
) -> bool:
    """
    Save data to cache.

    Args:
        key: The cache key (e.g., ASIN)
        data: The data to cache
        cache_folder: Folder where cache should be stored

    Returns:
        True if saved successfully, False otherwise
    """
    if not cache_folder:
        return False

    os.makedirs(cache_folder, exist_ok=True)
    json_path = f"{cache_folder}/{key}.json"

    try:
        with open(json_path, "w") as f:
            json.dump(data, f, indent=2)
        logger.debug(f"Saved {key} to cache")
        return True
    except Exception as e:
        logger.error(f"Error saving cache for {key}: {e!s}")
        return False
