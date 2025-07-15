import os
import json
import time
import logging

from playwright.async_api import async_playwright
from mcp_amazon_asin.utils import get_amazon_detail_page_url
from mcp_amazon_asin.utils.fields import REQUIRED_PRODUCT_FIELDS, PRODUCT_FIELDS

# Configure logger
logger = logging.getLogger(__name__)


# Cache expiration time in seconds (1 hour)
CACHE_EXPIRATION_SECONDS = 3600


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
    if cache_folder:
        os.makedirs(cache_folder, exist_ok=True)
        json_path = f"{cache_folder}/{asin}.json"

        if os.path.exists(json_path):
            try:
                with open(json_path, "r") as f:
                    cached_data = json.load(f)

                # Check if timestamp exists and is within expiration period
                if "timestamp" in cached_data:
                    cache_time = cached_data["timestamp"]
                    current_time = int(time.time())

                    if current_time - cache_time <= CACHE_EXPIRATION_SECONDS:
                        # Validate all required fields are present
                        valid_cache = True
                        for field in REQUIRED_PRODUCT_FIELDS:
                            if field not in cached_data or cached_data[field] is None:
                                valid_cache = False
                                logger.debug(f"Cache invalid for {asin}: missing field {field}")
                                break

                        if valid_cache:
                            logger.info(f"Using cached data for {asin} (age: {current_time - cache_time} seconds)")
                            return cached_data
                    else:
                        logger.debug(f"Cache expired for {asin} (age: {current_time - cache_time} seconds)")
            except Exception as e:
                logger.error(f"Error reading cache for {asin}: {str(e)}")

    logger.info(f"Fetching data for {asin} from Amazon (cache not used)")
        
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
                "#mir-layout-DELIVERY_BLOCK span[data-csa-c-type='element'], #deliveryBlockMessage, [data-feature-name='delivery'] span"
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

    # Verify all required fields are present
    for field in REQUIRED_PRODUCT_FIELDS:
        if field not in product_data:
            product_data[field] = None

    # Add timestamp for cache expiration
    product_data["timestamp"] = int(time.time())

    # Save to cache if enabled
    if cache_folder:
        try:
            json_path = f"{cache_folder}/{asin}.json"
            with open(json_path, "w") as f:
                json.dump(product_data, f, indent=2)
            logger.info(f"Saved {asin} to cache")
        except Exception as e:
            logger.error(f"Error saving cache for {asin}: {str(e)}")

    return product_data
