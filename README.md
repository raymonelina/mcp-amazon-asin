# 🛍️ MCP Amazon ASIN Server

This project is a Python-based [Model Context Provider (MCP)](https://docs.anthropic.com/claude/docs/tools-intro) that fetches product information from Amazon using a given ASIN. It is designed to integrate with Claude or similar agent platforms using stdin/stdout-based communication.

Built with:

- 🧠 [`fastmcp`](https://github.com/aria-oss/fastmcp) for Claude-compatible tool serving
- 🎭 [`playwright`](https://playwright.dev/python/) for headless product page scraping
- ⚙️ `uv` for dependency and environment management


## 🚀 Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/mcp-amazon-asin.git
cd mcp-amazon-asin
```

### 2. Install `uv` (if not already installed)

```bash
curl -Ls https://astral.sh/uv/install.sh | bash
```

Verify:
```bash
uv --version
```

### 3. Install dependencies and enable editable module import

```bash
uv pip install -e .
```

This will:
- Create a `.uv/` virtual environment (if not present)
- Install all dependencies from `pyproject.toml` or `uv.lock`
- Register the `src/`-based `mcp_amazon_asin` module for relative imports

---

## ▶️ Run the ASIN MCP Server

Use `uv` with module mode from the root:

```bash
uv run -m mcp_amazon_asin.server
```

This will:
- Ensure `playwright` is set up (via `setup_playwright()`)
- Launch the MCP server on stdin/stdout
- Register the `get_product_info` tool for use by Claude or any agent framework

---

## 🧰 Tool Behavior Summary

Tool Name: `get_product_info`  
Input: `{ "asin": "<ASIN>" }`  
Returns:
- Product Title
- Price
- Rating
- Key Features
- Product Image URL
- Product URL

Example ASIN: `B0CGXY13QW` → returns formatted product information from Amazon.

---

## 🧠 Claude Desktop Integration

To use this MCP locally in Claude Desktop, add the following to your `~/.claude/desktop/settings.json`:

```json
{
  "mcpServers": {
    "asin": {
      "command": "/Users/USER_NAME/.local/bin/uv",
      "args": [
        "--directory",
        "/ABSOLUTE_PATH_TO/mcp-amazon-asin",
        "run",
        "-m",
        "mcp_amazon_asin.server"
      ]
    }
  }
}
```

> 🧩 Replace `/USER_NAME/` with your user name.
> 🧩 Replace `/ABSOLUTE_PATH_TO/` with your actual project path.

---

## 🧪 Playwright Setup Notes

If Playwright fails to launch Chromium:
```bash
playwright install chromium
```

---