from urllib.parse import quote_plus

def get_amazon_search_page_url(query: str) -> str:
    return f"https://www.amazon.com/s?k={quote_plus(query)}"

def get_amazon_detail_page_url(asin: str) -> str:
    return f"https://www.amazon.com/dp/{asin}"
