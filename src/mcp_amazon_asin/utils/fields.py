"""
Common field definitions for product data
"""


class ProductFields:
    """Class to define product field names as attributes"""

    asin = "asin"
    url = "url"
    title = "title"
    price = "price"
    rating = "rating"
    features = "features"
    image = "image"
    sold_by = "sold_by"
    delivery_date = "delivery_date"
    delivering_to = "delivering_to"


# Create an instance for easy access
PRODUCT_FIELDS = ProductFields()

# List of all fields for validation
ALL_PRODUCT_FIELDS = [
    PRODUCT_FIELDS.asin,
    PRODUCT_FIELDS.url,
    PRODUCT_FIELDS.title,
    PRODUCT_FIELDS.price,
    PRODUCT_FIELDS.rating,
    PRODUCT_FIELDS.features,
    PRODUCT_FIELDS.image,
    PRODUCT_FIELDS.sold_by,
    PRODUCT_FIELDS.delivery_date,
    PRODUCT_FIELDS.delivering_to,
]

# List of fields that are strictly required (must not be None for valid cache)
REQUIRED_PRODUCT_FIELDS = [
    PRODUCT_FIELDS.asin,
    PRODUCT_FIELDS.url,
    PRODUCT_FIELDS.title,
    PRODUCT_FIELDS.price,
    PRODUCT_FIELDS.rating,
    PRODUCT_FIELDS.features,
    PRODUCT_FIELDS.image,
]

# Fields that are optional (can be None but should be logged)
OPTIONAL_PRODUCT_FIELDS = [
    PRODUCT_FIELDS.sold_by,
    PRODUCT_FIELDS.delivery_date,
    PRODUCT_FIELDS.delivering_to,
]
