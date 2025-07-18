#!/usr/bin/env python3
"""
Amazon ASIN MCP Server

This server provides tools to fetch product information from Amazon using ASIN.
"""

import asyncio
import json
from typing import Any

import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
from pydantic import BaseModel, Field


from .utils.setup import setup_playwright
from .utils.search import extract_search_asin, get_seller_recommendations
from .utils.dp import extract_dp


class ASINInput(BaseModel):
    """Input for ASIN product lookup"""

    asin: str = Field(..., description="Amazon Standard Identification Number (ASIN)")


class SearchInput(BaseModel):
    """Input for Amazon product search"""

    query: str = Field(..., description="Search query for Amazon products")


# Create server instance
server: Server = Server("mcp-amazon-product")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="get_product_info_from_asin",
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
        ),
        types.Tool(
            name="search_amazon",
            description="Search for products on Amazon and get a list of ASINs",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The product search query",
                    }
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="get_recommendations",
            description="Get a list of product sub category, refinements, and recommended products for a given Amazon search query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The Amazon product search query",
                    }
                },
                "required": ["query"],
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent]:
    """Handle tool calls"""
    if not arguments:
        raise ValueError("Missing arguments")

    if name == "get_product_info_from_asin":
        try:
            asin_input = ASINInput(**arguments)
            product_data = await extract_dp(asin_input.asin)

            # Format the response
            response = f"""**Product Information for ASIN: {product_data['asin']}**

**Title:** {product_data['title'] or 'Not available'}

**Price:** {product_data['price'] or 'Not available'}

**Rating:** {product_data['rating'] or 'Not available'}

**Product URL:** {product_data['url']}

**Sold By:** {product_data['sold_by'] or 'Not available'}

**Delivery Date:** {product_data['delivery_date'] or 'Not available'}

**Delivering To:** {product_data['delivering_to'] or 'Not available'}

**Key Features:**
"""

            if product_data["features"]:
                for feature in product_data["features"]:
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
    elif name == "search_amazon":
        try:
            search_input = SearchInput(**arguments)
            results = await extract_search_asin(search_input.query)

            if not results:
                return [
                    types.TextContent(
                        type="text", text="No products found for your query."
                    )
                ]

            # Format the response with more detailed product information
            response = "**Found the following products:**\n"
            for result in results:
                if result["asin"]:
                    response += f"- ASIN: {result['asin']}\n"
                    response += f"  Title: {result.get('title', 'N/A')}\n"
                    response += (
                        f"  Sponsored: {'Yes' if result.get('sponsored') else 'No'}\n\n"
                    )

            return [types.TextContent(type="text", text=response)]
        except Exception as e:
            return [
                types.TextContent(
                    type="text", text=f"Error searching for products: {str(e)}"
                )
            ]
    elif name == "get_recommendations":
        try:
            search_input = SearchInput(**arguments)
            results = await get_seller_recommendations(search_input.query)

            if not results:
                return [
                    types.TextContent(
                        type="text", text="No recommendations found for your query."
                    )
                ]

            # Just return the recommendations directly
            return [types.TextContent(type="text", text=results["recommendations"])]
        except Exception as e:
            return [
                types.TextContent(
                    type="text", text=f"Error getting recommendations: {str(e)}"
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
