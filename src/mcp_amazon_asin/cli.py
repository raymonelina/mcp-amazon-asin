#!/usr/bin/env python3
"""
CLI for local testing of Amazon ASIN utilities
"""

import asyncio
import inspect
import json
import logging
import os
import sys

import click

from .utils.dp import extract_dp
from .utils.prompt import chat_with_gemini
from .utils.search import (
    extract_refinements,
    extract_search_asin,
    extract_themed_products,
)
from .utils.setup import setup_playwright
from .utils.utils import load_prompt_template


@click.group()
@click.option(
    "--log-level",
    type=click.Choice(
        ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False
    ),
    default="INFO",
    help="Set the logging level",
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
@click.option(
    "--cache-folder",
    default="cache",
    help="Cache folder for JSON data (use 'none' to disable)",
)
async def product(asin: str, cache_folder: str):
    """Get product information by ASIN"""
    try:
        # Convert 'none' string to None to disable caching
        cache_param = (
            None if cache_folder and cache_folder.lower() == "none" else cache_folder
        )
        result = await extract_dp(asin, cache_folder=cache_param)
        # Always output as JSON
        click.echo(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("query")
@click.option("--limit", default=1000, help="Number of results to return")
@click.option(
    "--cache-folder",
    default="cache",
    help="Cache folder for JSON data (use 'none' to disable)",
)
async def search(query: str, limit: int, cache_folder: str):
    """Search Amazon products"""
    try:
        # Convert 'none' string to None to disable caching
        cache_param = (
            None if cache_folder and cache_folder.lower() == "none" else cache_folder
        )
        results = await extract_search_asin(query, limit, cache_param)
        # Always output as JSON
        click.echo(json.dumps(results, indent=2, ensure_ascii=False))
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
async def theme(query: str, limit: int, batch_size: int, cache_folder: str):
    """Get themed product recommendations"""
    try:
        # Call the extract_themed_products function from search.py
        products = await extract_themed_products(query, limit, batch_size, cache_folder)

        # Output the list of detailed products
        click.echo(json.dumps(products, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("query")
@click.option(
    "--cache-folder",
    default="cache",
    help="Cache folder for JSON data (use 'none' to disable)",
)
async def refinements(query: str, cache_folder: str):
    """Get available refinement categories for search query"""
    try:
        # Convert 'none' string to None to disable caching
        cache_param = (
            None if cache_folder and cache_folder.lower() == "none" else cache_folder
        )
        categories = await extract_refinements(query)
        # Always output as JSON
        click.echo(json.dumps(categories, indent=2, ensure_ascii=False))
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("query")
@click.option("--product-limit", default=10, help="Number of products to analyze")
@click.option(
    "--batch-size", default=5, help="Number of products to process in parallel"
)
@click.option(
    "--cache-folder",
    default="cache",
    help="Cache folder for JSON data (use 'none' to disable)",
)
async def seller_recommendation(
    query: str, product_limit: int, batch_size: int, cache_folder: str
):
    """Get seller recommendations based on the query"""
    try:
        # Run both API calls in parallel
        click.echo(
            "Fetching product information and category refinements in parallel...",
            err=True,
        )

        # Use asyncio.gather to run both API calls concurrently
        products, categories = await asyncio.gather(
            extract_themed_products(query, product_limit, batch_size, cache_folder),
            extract_refinements(query),
        )

        # Process and display the results
        products_str = json.dumps(products, indent=2, ensure_ascii=False)
        refinements_str = json.dumps(categories, indent=2, ensure_ascii=False)

        click.echo("Themed product recommendations:")
        click.echo(products_str)

        click.echo("\nCategory refinements:")
        click.echo(refinements_str)

        # Load the prompt template and format it with the data
        prompt_template = load_prompt_template("seller_recommendation")
        enhanced_prompt = prompt_template.format(
            query=query, refinements_str=refinements_str, products_str=products_str
        )
        click.echo("\nLoading prompt: seller_recommendation")

        # Send the enhanced prompt to genAI
        click.echo("\nGenerating seller recommendations...", err=True)
        response = await chat_with_gemini(enhanced_prompt)

        # Always output raw text
        click.echo(response)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


def main():
    # Convert async commands to sync
    for _, cmd in cli.commands.items():
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
