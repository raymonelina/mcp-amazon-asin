#!/usr/bin/env python3
"""
Amazon ASIN MCP Server

This server provides tools to fetch product information from Amazon using ASIN.
"""

import asyncio
from typing import Any

import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from pydantic import BaseModel, Field
from playwright.async_api import async_playwright

from .utils.setup import setup_playwright

class ASINInput(BaseModel):
    """Input for ASIN product lookup"""

    asin: str = Field(..., description="Amazon Standard Identification Number (ASIN)")


# Create server instance
server: Server = Server("mcp-amazon-product")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="get_product_info",
            description="Get product information from Amazon using ASIN",
            inputSchema={
                "type": "object",
                "properties": {
                    "asin": {
                        "type": "string",
                        "description": "Amazon Standard Identification Number (ASIN) - the unique product identifier",
                    }
                },
                "required": ["asin"],
            },
        )
    ]


async def get_asin_details(input: ASINInput) -> dict:
    """Fetch product details from Amazon using ASIN"""
    asin = input.asin
    url = f"https://www.amazon.com/dp/{asin}"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Set user agent to avoid blocking
        await page.set_extra_http_headers(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )

        await page.goto(url, timeout=60000)

        # Wait for page to load
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

        await browser.close()

    return {
        "asin": asin,
        "url": url,
        "title": title.strip() if title else None,
        "price": price.strip() if price else None,
        "rating": rating.strip() if rating else None,
        "features": [b.strip() for b in bullets if b.strip()],
        "image": images,
    }


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent]:
    """Handle tool calls"""
    if name == "get_product_info":
        if not arguments:
            raise ValueError("Missing arguments")

        try:
            asin_input = ASINInput(**arguments)
            product_data = await get_asin_details(asin_input)

            # Format the response
            response = f"""**Product Information for ASIN: {product_data['asin']}**

**Title:** {product_data['title'] or 'Not available'}

**Price:** {product_data['price'] or 'Not available'}

**Rating:** {product_data['rating'] or 'Not available'}

**Product URL:** {product_data['url']}

**Key Features:**
"""

            if product_data["features"]:
                for feature in product_data["features"][
                    :5
                ]:  # Limit to first 5 features
                    response += f"• {feature}\n"
            else:
                response += "No features available\n"

            if product_data["image"]:
                response += f"\n**Product Image:** {product_data['image']}"

            return [types.TextContent(type="text", text=response)]

        except Exception as e:
            return [
                types.TextContent(
                    type="text", text=f"Error fetching product information: {str(e)}"
                )
            ]
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Main entry point"""
    # Run the server using stdin/stdout streams
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="mcp-amazon-product",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    setup_playwright()

    asyncio.run(main())
