#!/usr/bin/env python3
"""
CLI for local testing of Amazon ASIN utilities
"""

import asyncio
import json
import sys
from typing import Optional

import click

from .utils.setup import setup_playwright
from .utils.search import extract_search
from .utils.dp import extract_dp


@click.group()
def cli():
    """Amazon ASIN CLI for local testing"""
    setup_playwright()


@cli.command()
@click.argument('asin')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
async def product(asin: str, output_json: bool):
    """Get product information by ASIN"""
    try:
        result = await extract_dp(asin)
        if output_json:
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"Title: {result['title']}")
            click.echo(f"Price: {result['price']}")
            click.echo(f"Rating: {result['rating']}")
            click.echo(f"URL: {result['url']}")
            if result['features']:
                click.echo("Features:")
                for feature in result['features'][:5]:
                    click.echo(f"  • {feature}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('query')
@click.option('--limit', default=10, help='Number of results to return')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
async def search(query: str, limit: int, output_json: bool):
    """Search Amazon products"""
    try:
        results = await extract_search(query, limit)
        if output_json:
            click.echo(json.dumps(results, indent=2))
        else:
            for result in results:
                click.echo(f"{result['asin']}: {result['title']}")
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument('query')
@click.option('--limit', default=5, help='Number of products to fetch details for')
async def theme(query: str, limit: int):
    """Get themed product recommendations"""
    try:
        search_results = await extract_search(query, limit)
        products = []
        for result in search_results:
            if result and result['asin']:
                product = await extract_dp(result['asin'])
                products.append(product)
        
        click.echo(json.dumps(products, indent=2))
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
            cmd.callback = lambda *args, callback=original_callback, **kwargs: asyncio.run(callback(*args, **kwargs))
    
    cli()


if __name__ == "__main__":
    main()