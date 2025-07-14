#!/usr/bin/env python3
"""
Simple test runner for manual testing
"""

import asyncio
import json
from .utils.setup import setup_playwright
from .utils.search import extract_search
from .utils.dp import extract_dp


async def test_product_info(asin: str = "B0CGXY13QW"):
    """Test product information extraction"""
    print(f"🔍 Testing product info for ASIN: {asin}")
    result = await extract_dp(asin)
    print(json.dumps(result, indent=2))
    return result


async def test_search(query: str = "wireless headphones"):
    """Test search functionality"""
    print(f"🔍 Testing search for: {query}")
    results = await extract_search(query, limit=5)
    print(json.dumps(results, indent=2))
    return results


async def test_theme(query: str = "gaming mouse"):
    """Test theme functionality"""
    print(f"🔍 Testing theme for: {query}")
    search_results = await extract_search(query, limit=3)
    
    products = []
    for result in search_results:
        if result and result['asin']:
            product = await extract_dp(result['asin'])
            products.append(product)
    
    print(json.dumps(products, indent=2))
    return products


async def run_all_tests():
    """Run all tests"""
    print("🚀 Starting all tests...\n")
    
    await test_product_info()
    print("\n" + "="*50 + "\n")
    
    await test_search()
    print("\n" + "="*50 + "\n")
    
    await test_theme()
    print("\n✅ All tests completed!")


def main():
    """Entry point for test runner"""
    setup_playwright()
    asyncio.run(run_all_tests())


if __name__ == "__main__":
    main()