import asyncio
import json
import logging
import os
from playwright.async_api import async_playwright
from mcp_amazon_asin.utils import get_amazon_search_page_url
from mcp_amazon_asin.utils.dp import extract_dp
from mcp_amazon_asin.utils.prompt import chat_with_gemini
from mcp_amazon_asin.utils.utils import load_prompt_template, save_to_temp_file

# Configure logger
logger = logging.getLogger(__name__)


async def extract_search_asin(
    query: str, limit: int = 100, cache_folder: str = "cache"
) -> list[dict]:
    """Extracts search result summaries for a given Amazon search query (fast version)"""
    url = get_amazon_search_page_url(query)

    logger.debug(f"Searching Amazon for '{query}' (limit: {limit})")

    # Handle cache_folder parameter (used for screenshots)
    if cache_folder and cache_folder.lower() == "none":
        cache_folder = None

    # Create cache directory if it doesn't exist
    if cache_folder:
        os.makedirs(cache_folder, exist_ok=True)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Set user agent to avoid bot detection
        await page.set_extra_http_headers(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            }
        )

        await page.goto(url, timeout=60000)
        await page.wait_for_timeout(2000)

        results = []

        base = page.locator(
            "div.s-main-slot div[data-asin][data-index][role='listitem']"
        )
        count = await base.count()

        for i in range(min(count, limit)):
            item = base.nth(i)
            try:
                data = await item.evaluate(
                    """
                    (el) => {
                        const asin = el.getAttribute('data-asin');
                        const index = el.getAttribute('data-index');
                        const span = el.querySelector('a h2 span');
                        const title = span ? span.textContent.trim() : null;

                        // Sponsored check
                        const sponsorEl = el.querySelector("span.a-declarative span, span.a-declarative");
                        const sponsored = sponsorEl && sponsorEl.textContent.trim().startsWith("Sponsored");


                        return {
                            asin: asin?.trim() || null,
                            index: index ? parseInt(index) : null,
                            title: title,
                            sponsored: sponsored || false
                        };
                    }
                    """
                )
                if data and data.get("asin"):
                    # Save screenshot if cache_folder is specified
                    if cache_folder and data.get("asin"):
                        try:
                            await item.screenshot(
                                path=f"{cache_folder}/{data['asin']}.png"
                            )
                            logger.debug(f"Saved screenshot for {data['asin']}")
                        except Exception as e:
                            logger.debug(
                                f"Failed to save screenshot for {data['asin']}: {e}"
                            )
                            # Continue if screenshot fails

                    results.append(data)
            except Exception:
                continue

        await browser.close()
        logger.debug(f"Found {len(results)} results for '{query}'")
        return results


async def extract_refinements(query: str) -> list[dict]:
    """Extracts available refinement categories from Amazon search page sidebar"""
    logger.debug(f"Extracting refinement categories for '{query}'")

    """Extracts available refinement categories from Amazon search page sidebar (fast version)"""
    url = get_amazon_search_page_url(query)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Set user agent to avoid bot detection
        await page.set_extra_http_headers(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            }
        )

        await page.goto(url, timeout=60000)
        await page.wait_for_timeout(2000)

        try:
            refinements = await page.evaluate(
                """
                () => {
                    const refinementPairs = [];
                    const refinementSection = document.querySelector('#s-refinements');
                    
                    if (refinementSection) {
                        // Target the specific structure: #s-refinements > .a-section.a-spacing-double-large > div
                        const sections = refinementSection.querySelectorAll('.a-section.a-spacing-double-large > div');
                        
                        sections.forEach(div => {
                            const id = div.id;
                            const innerText = div.innerText?.trim();
                            if (id && id.trim().length > 0 && innerText) {
                                const textLines = innerText.split('\\n').map(line => line.trim()).filter(line => line.length > 0);
                                refinementPairs.push({
                                    type: id.trim(),
                                    refinements: textLines
                                });
                            }
                        });
                    }
                    
                    return refinementPairs;
                }
                """
            )
        except Exception:
            refinements = []

        await browser.close()
        logger.debug(f"Found {len(refinements)} refinement categories for '{query}'")
        return refinements


async def extract_themed_products(
    query: str, limit: int = 50, batch_size: int = 10, cache_folder: str = "cache"
) -> list[dict]:
    """
    Get themed product recommendations for a search query.
    
    Args:
        query: The search query
        limit: Maximum number of products to fetch details for
        batch_size: Number of products to process in parallel per batch
        cache_folder: Cache folder for JSON data (use 'none' to disable)
        
    Returns:
        List of detailed product information
    """
    logger.debug(f"Getting themed products for '{query}' (limit: {limit}, batch_size: {batch_size})")
    
    # Convert 'none' string to None to disable caching
    cache_param = None if cache_folder and cache_folder.lower() == "none" else cache_folder

    # Step 1: Get search results using the limit parameter
    search_results = await extract_search_asin(query, limit, cache_param)

    # Step 2: Get all ASINs and process them in batches
    asins = [result["asin"] for result in search_results if result and result["asin"]]

    products = []
    if asins:
        # Calculate total number of batches
        total_batches = (len(asins) + batch_size - 1) // batch_size

        # Process ASINs in batches
        for i in range(0, len(asins), batch_size):
            batch = asins[i : i + batch_size]
            batch_asins = ", ".join(batch)
            current_batch = i // batch_size + 1
            logger.debug(f"Processing batch {current_batch}/{total_batches}: {len(batch)} ASINs [{batch_asins}]")
            batch_products = await asyncio.gather(
                *[extract_dp(asin, cache_folder=cache_param) for asin in batch]
            )
            products.extend(batch_products)

    logger.debug(f"Found {len(products)} themed products for '{query}'")
    return products


async def get_seller_recommendations(
    query: str, product_limit: int = 10, batch_size: int = 5, cache_folder: str = "cache"
) -> dict:
    """
    Get seller recommendations based on the query.
    
    Args:
        query: The search query
        product_limit: Maximum number of products to analyze
        batch_size: Number of products to process in parallel
        cache_folder: Cache folder for JSON data (use 'none' to disable)
        
    Returns:
        Dictionary containing products, categories, and AI-generated recommendations
    """
    logger.debug(f"Getting seller recommendations for '{query}'")
    
    # Convert 'none' string to None to disable caching
    cache_param = None if cache_folder and cache_folder.lower() == "none" else cache_folder
    
    # Run both API calls in parallel
    logger.debug("Fetching product information and category refinements in parallel...")
    products, categories = await asyncio.gather(
        extract_themed_products(query, product_limit, batch_size, cache_param),
        extract_refinements(query),
    )
    
    # Convert to JSON strings for the prompt
    products_str = json.dumps(products, indent=2, ensure_ascii=False)
    refinements_str = json.dumps(categories, indent=2, ensure_ascii=False)
    
    # Load the prompt template and format it with the data
    prompt_template = load_prompt_template("seller_recommendation")
    enhanced_prompt = prompt_template.format(
        query=query, refinements_str=refinements_str, products_str=products_str
    )
    logger.debug("Prompt template loaded and formatted")
    
    # Send the enhanced prompt to Gemini
    logger.debug("Generating seller recommendations...")
    response = await chat_with_gemini(enhanced_prompt)
    
    # Save the response to a temporary file
    tmp_file_path = save_to_temp_file(response, prefix="seller_recommendation_")
    logger.debug(f"Response saved to temporary file: {tmp_file_path}")
    
    # Return all the data
    return {
        "products": products,
        "categories": categories,
        "recommendations": response,
        "temp_file": tmp_file_path
    }
