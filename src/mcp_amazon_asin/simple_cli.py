#!/usr/bin/env python3
"""
Simple CLI without external dependencies
"""

import asyncio
import json
import sys

from .utils.setup import setup_playwright
from .utils.search import extract_search
from .utils.dp import extract_dp


async def test_product(asin: str):
    """Test product lookup"""
    result = await extract_dp(asin)
    print(json.dumps(result, indent=2))


async def test_search(query: str, limit: int = 5):
    """Test search"""
    results = await extract_search(query, limit)
    print(json.dumps(results, indent=2))


def main():
    """Simple CLI"""
    setup_playwright()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python -m mcp_amazon_asin.simple_cli product <ASIN>")
        print("  python -m mcp_amazon_asin.simple_cli search <query>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "product" and len(sys.argv) >= 3:
        asyncio.run(test_product(sys.argv[2]))
    elif command == "search" and len(sys.argv) >= 3:
        asyncio.run(test_search(sys.argv[2]))
    else:
        print("Invalid command or missing arguments")
        sys.exit(1)


if __name__ == "__main__":
    main()