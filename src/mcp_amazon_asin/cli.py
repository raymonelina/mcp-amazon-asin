#!/usr/bin/env python3
"""
CLI for local testing of Amazon ASIN utilities
"""

import asyncio
import json
import sys
import logging

import click

from .utils.setup import setup_playwright
from .utils.search import extract_search_asin, extract_refinements
from .utils.dp import extract_dp


@click.group()
@click.option(
    "--log-level",
    type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False),
    default="INFO",
    help="Set the logging level"
)
def cli(log_level):
    """Amazon ASIN CLI for local testing"""
    # Configure logging based on specified level
    numeric_level = getattr(logging, log_level.upper())
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    setup_playwright()


@cli.command()
@click.argument("asin")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option(
    "--cache-folder",
    default="cache",
    help="Cache folder for JSON data (use 'none' to disable)",
)
async def product(asin: str, output_json: bool, cache_folder: str):
    """Get product information by ASIN"""
    try:
        # Convert 'none' string to None to disable caching
        cache_param = (
            None if cache_folder and cache_folder.lower() == "none" else cache_folder
        )
        result = await extract_dp(asin, cache_folder=cache_param)
        if output_json:
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"Title: {result['title']}")
            click.echo(f"Price: {result['price']}")
            click.echo(f"Rating: {result['rating']}")
            click.echo(f"Sold by: {result['sold_by']}")
            click.echo(f"Delivery date: {result['delivery_date']}")
            click.echo(f"Delivering to: {result['delivering_to']}")
            click.echo(f"URL: {result['url']}")
            if result["features"]:
                click.echo("Features:")
                for feature in result["features"][:5]:
                    click.echo(f"  • {feature}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("query")
@click.option("--limit", default=1000, help="Number of results to return")
@click.option("--json", "output_json", is_flag=True, help="Output as JSON")
@click.option(
    "--cache-folder",
    default="cache",
    help="Cache folder for JSON data (use 'none' to disable)",
)
async def search(
    query: str, limit: int, output_json: bool, cache_folder: str
):
    """Search Amazon products"""
    try:
        # Convert 'none' string to None to disable caching
        cache_param = (
            None if cache_folder and cache_folder.lower() == "none" else cache_folder
        )
        results = await extract_search_asin(query, limit, cache_param)
        if output_json:
            click.echo(json.dumps(results, indent=2))
        else:
            for result in results:
                click.echo(f"{result['asin']}: {result['title']}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("query")
@click.option("--limit", default=50, help="Number of products to fetch details for")
@click.option(
    "--batch-size",
    default=10,
    help="Number of products to process in parallel per batch",
)
@click.option(
    "--cache-folder",
    default="cache",
    help="Cache folder for JSON data (use 'none' to disable)",
)
async def theme(
    query: str, limit: int, batch_size: int, cache_folder: str
):
    """Get themed product recommendations"""
    try:
        # Convert 'none' string to None to disable caching
        cache_param = (
            None if cache_folder and cache_folder.lower() == "none" else cache_folder
        )

        # Step 1: Get search results using the limit parameter
        search_results = await extract_search_asin(
            query, limit, cache_param
        )

        # Step 2: Get all ASINs and process them in batches
        asins = [
            result["asin"] for result in search_results if result and result["asin"]
        ]

        products = []
        if asins:
            # Calculate total number of batches
            total_batches = (len(asins) + batch_size - 1) // batch_size

            # Process ASINs in batches
            for i in range(0, len(asins), batch_size):
                batch = asins[i : i + batch_size]
                batch_asins = ", ".join(batch)
                current_batch = i // batch_size + 1
                click.echo(
                    f"Processing batch {current_batch}/{total_batches}: {len(batch)} ASINs [{batch_asins}]",
                    err=True,
                )
                batch_products = await asyncio.gather(
                    *[
                        extract_dp(asin, cache_folder=cache_param)
                        for asin in batch
                    ]
                )
                products.extend(batch_products)

        # Step 3: Output the list of detailed products
        click.echo(json.dumps(products, indent=2))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("query")
async def refinements(query: str):
    """Get available refinement categories for search query"""
    try:
        categories = await extract_refinements(query)
        for category in categories:
            click.echo(category)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def main():
    """Async wrapper for CLI"""
    import inspect

    # Convert async commands to sync
    for name, cmd in cli.commands.items():
        if inspect.iscoroutinefunction(cmd.callback):
            original_callback = cmd.callback
            cmd.callback = (
                lambda *args, callback=original_callback, **kwargs: asyncio.run(
                    callback(*args, **kwargs)
                )
            )

    cli()


if __name__ == "__main__":
    main()
