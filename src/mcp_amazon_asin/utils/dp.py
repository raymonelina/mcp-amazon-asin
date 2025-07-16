import logging
import time

from playwright.async_api import async_playwright

from mcp_amazon_asin.utils import get_amazon_detail_page_url
from mcp_amazon_asin.utils.cache import get_from_cache, save_to_cache
from mcp_amazon_asin.utils.fields import (
    ALL_PRODUCT_FIELDS,
    OPTIONAL_PRODUCT_FIELDS,
    PRODUCT_FIELDS,
    REQUIRED_PRODUCT_FIELDS,
)

# Configure logger
logger = logging.getLogger(__name__)


async def extract_dp(
    asin: str, cache_folder: str = "cache", verbose: bool = False
) -> dict:
    """Fetch product details from Amazon using ASIN

    Args:
        asin: Amazon Standard Identification Number
        cache_folder: Folder to store cached data (use 'none' to disable)
        verbose: Deprecated parameter, kept for backward compatibility
    """

    url = get_amazon_detail_page_url(asin)

    # Check cache if enabled
    cached_data = get_from_cache(asin, cache_folder, REQUIRED_PRODUCT_FIELDS)
    if cached_data:
        # Log if optional fields are missing in cached data
        for field in OPTIONAL_PRODUCT_FIELDS:
            if field not in cached_data or cached_data[field] is None:
                logger.debug(
                    f"Note: optional field '{field}' is empty for {asin} in cache"
                )
        return cached_data

    logger.debug(f"Fetching data for {asin} from Amazon (cache not used)")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Set user agent to avoid blocking
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
            title = await page.locator("span#productTitle").text_content()
        except Exception:
            title = None

        try:
            price = await page.locator(
                "span.a-price span.a-offscreen"
            ).first.text_content()
        except Exception:
            price = None

        try:
            rating = await page.locator("span.a-icon-alt").first.text_content()
        except Exception:
            rating = None

        try:
            bullets = await page.locator(
                "#feature-bullets ul li span"
            ).all_text_contents()
        except Exception:
            bullets = []

        try:
            images = await page.locator("img#landingImage").get_attribute("src")
        except Exception:
            images = None

        try:
            sold_by = await page.locator(
                "#merchant-info a, #sellerProfileTriggerId, [data-feature-name='merchant'] a"
            ).first.text_content()
        except Exception:
            sold_by = None

        try:
            delivery_date = await page.locator(
                "#mir-layout-DELIVERY_BLOCK span[data-csa-c-type='element']"
            ).first.text_content()
        except Exception:
            delivery_date = None

        try:
            delivering_to = await page.locator(
                "#glow-ingress-line1, #contextualIngressPt"
            ).first.text_content()
        except Exception:
            delivering_to = None

        await browser.close()

    # Prepare the data dictionary with all required fields
    product_data = {
        PRODUCT_FIELDS.asin: asin,
        PRODUCT_FIELDS.url: url,
        PRODUCT_FIELDS.title: title.strip() if title else None,
        PRODUCT_FIELDS.price: price.strip() if price else None,
        PRODUCT_FIELDS.rating: rating.strip() if rating else None,
        PRODUCT_FIELDS.features: [b.strip() for b in bullets if b.strip()],
        PRODUCT_FIELDS.image: images,
        PRODUCT_FIELDS.sold_by: sold_by.strip() if sold_by else None,
        PRODUCT_FIELDS.delivery_date: delivery_date.strip() if delivery_date else None,
        PRODUCT_FIELDS.delivering_to: delivering_to.strip() if delivering_to else None,
    }

    # Flag to determine if we should cache the data
    should_cache = True

    # Verify all fields are present (both required and optional)
    for field in ALL_PRODUCT_FIELDS:
        if field not in product_data:
            product_data[field] = None

    # Check required fields - these must not be None for caching
    for field in REQUIRED_PRODUCT_FIELDS:
        if product_data[field] is None:
            should_cache = False
            logger.debug(f"Not caching {asin}: required field '{field}' is empty")

    # Log optional fields that are empty but don't prevent caching
    for field in OPTIONAL_PRODUCT_FIELDS:
        if product_data[field] is None:
            logger.debug(
                f"Note: optional field '{field}' is empty for {asin}, but caching is still allowed"
            )

    # Add timestamp for cache expiration
    product_data["timestamp"] = int(time.time())

    # Save to cache if enabled
    if should_cache and cache_folder:
        save_to_cache(asin, product_data, cache_folder)
    else:
        logger.debug(f"Skipping cache for {asin} due to missing critical fields")

    return product_data
