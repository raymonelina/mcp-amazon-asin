import logging
from playwright.async_api import async_playwright
from mcp_amazon_asin.utils import get_amazon_search_page_url

# Configure logger
logger = logging.getLogger(__name__)


async def extract_search_asin(query: str, limit: int = 100, cache_folder: str = "cache") -> list[dict]:
    """Extracts search result summaries for a given Amazon search query (fast version)"""
    url = get_amazon_search_page_url(query)
    
    logger.info(f"Searching Amazon for '{query}' (limit: {limit})")
    
    # No screenshot folder in this version, using cache_folder instead
    screenshot_folder = None

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
                if data and data.get('asin'):
                    # Take screenshot if folder specified
                    if screenshot_folder:
                        try:
                            await item.screenshot(path=f"{screenshot_folder}/{data['asin']}.png")
                        except Exception:
                            pass  # Continue if screenshot fails
                    
                    results.append(data)
            except Exception:
                continue

        await browser.close()
        logger.info(f"Found {len(results)} results for '{query}'")
        return results


async def extract_refinements(query: str) -> list[dict]:
    """Extracts available refinement categories from Amazon search page sidebar"""
    logger.info(f"Extracting refinement categories for '{query}'")
    
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
                                    id: id.trim(),
                                    text: textLines
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
        logger.info(f"Found {len(refinements)} refinement categories for '{query}'")
        return refinements
