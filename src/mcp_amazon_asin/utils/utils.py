import os
import tempfile
from typing import Optional

import mcp_amazon_asin


def load_prompt_template(template_name: str) -> str:
    """
    Load a prompt template from the prompt folder.

    Args:
        template_name: Name of the template file (without extension)

    Returns:
        The template content as a string
    """
    # Use package-relative path for prompt files
    package_dir = os.path.dirname(mcp_amazon_asin.__file__)
    prompt_path = os.path.join(package_dir, "prompt", f"{template_name}.txt")

    try:
        with open(prompt_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        raise FileNotFoundError(
            f"Prompt template '{template_name}.txt' not found in the prompt folder"
        )


def get_amazon_detail_page_url(asin: str) -> str:
    """Construct the Amazon product detail page URL for a given ASIN"""
    return f"https://www.amazon.com/dp/{asin}"


def get_amazon_search_page_url(query: str) -> str:
    """Construct the Amazon search result page URL for a given query"""
    return f"https://www.amazon.com/s?k={query.replace(' ', '+')}"


def get_amazon_page_url(page_type: str, value: str) -> str:
    """Unified page URL builder for supported Amazon page types"""
    page_type = page_type.lower()
    if page_type == "dp":
        return get_amazon_detail_page_url(value)
    elif page_type == "search":
        return get_amazon_search_page_url(value)
    else:
        raise ValueError(
            f"Unsupported page_type '{page_type}'. Expected 'dp' or 'search'."
        )


def save_to_temp_file(content: str, suffix: str = ".txt", prefix: Optional[str] = None) -> str:
    """
    Save content to a temporary file.
    
    Args:
        content: The text content to save
        suffix: File extension (default: .txt)
        prefix: Optional prefix for the filename
        
    Returns:
        The path to the temporary file
    """
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=suffix, prefix=prefix) as tmp_file:
        tmp_file.write(content)
        return tmp_file.name
