#!/usr/bin/env python3
"""
Quick test runner at project root
"""

import asyncio
from src.mcp_amazon_asin.test_runner import run_all_tests

if __name__ == "__main__":
    asyncio.run(run_all_tests())