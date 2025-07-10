When a shopper searches for a product on Amazon, identify the top 3 most relevant decision factors they should consider based on the shopping context and product category. For example, factors like price or delivery speed may be relevant, but tailor your suggestions to the specific query.

Return your output in this format:

[
  {
    "keyword": "<search keyword>",
    "theme": "<short description of the factor (max 10 words)>"
  },
  ...
]
keyword should be a deterministic, specific search phrase under the theme. 

theme explains what to consider, while keyword reflects a pre-selected user intent.
Display this to the user to explain you are working on these themes.

Next, for the original search query:

Retrieve a list of ASINs and keep the first 2.

For each of the 2 extended queries (from the keywords above), retrieve the first 2 ASINs.

Then, for each ASIN (from both steps), fetch product title and image link.

Keep the product that is relevant to the corresponding theme. This is a must. For example, if the theme is price, then ASIN price must be compliant.

Return the results grouped by theme + keyword, showing product title and image link.

