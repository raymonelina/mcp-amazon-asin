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

### 3. Install dependencies

**Option A: Using uv sync (recommended)**
```bash
uv sync
```

**Option B: Using pip-style installation**
```bash
uv pip install -e .
```

**Key differences:**
- `uv sync`: Modern uv workflow that creates/updates lockfile and installs exact versions
- `uv pip install -e .`: Traditional pip-style that installs latest compatible versions

Both will:
- Create a virtual environment
- Install all dependencies from `pyproject.toml`
- Enable editable imports for the `mcp_amazon_asin` module

---

## ▶️ Testing the MCP Server (Optional)

To test the server manually from command line:

```bash
uv run -m mcp_amazon_asin.server
```

This will:
- Ensure `playwright` is set up (via `setup_playwright()`)
- Launch the MCP server on stdin/stdout
- Register the `get_product_info` tool for use by Claude or any agent framework

---

## 🧠 Claude Desktop Integration

To use this MCP in Claude Desktop, add the following to your `~/.claude/desktop/settings.json`:

```json
{
  "mcpServers": {
    "asin": {
      "command": "/Users/zhurunz/.local/bin/uv",
      "args": [
        "--directory",
        "/Users/zhurunz/Zhurun Zhang/git-hub/mcp-amazon-asin",
        "run",
        "-m",
        "mcp_amazon_asin.server"
      ]
    }
  }
}
```

**Important:** Update the paths for your system:
- Replace `/Users/zhurunz/.local/bin/uv` with your uv installation path
- Replace `/Users/zhurunz/Zhurun Zhang/git-hub/mcp-amazon-asin` with your project's absolute path

**Find your uv path:**
```bash
which uv
```

**Find your project path:**
```bash
pwd  # run this inside your mcp-amazon-asin directory
```

After updating the config, restart Claude Desktop to load the MCP server.

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

## 🖥️ CLI Usage (Optional)

For local testing, you can use the CLI directly:

**Commands:**
- `product` - Get product information by ASIN
- `search` - Search Amazon products
- `refinements` - Get available refinement categories for search query
- `theme` - Get themed product recommendations

**Common Options:**
- `--cache-folder` - Cache folder for JSON data (default: "cache", use 'none' to disable)
- `--log-level` - Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL, default: INFO)

### Option A: Using uv run (Recommended)
```bash
# No activation needed - uv automatically manages the environment
uv run amazon-asin-cli product B0CGXY13QW
uv run amazon-asin-cli search "wireless headphones"
uv run amazon-asin-cli refinements "wireless headphones"
uv run amazon-asin-cli theme "gaming setup" --limit 10 --batch-size 5

# Use custom cache folder
uv run amazon-asin-cli search "wireless headphones" --limit 5 --cache-folder ./my-cache
```

### Option B: Activate virtual environment first
```bash
# Step 1: Activate the virtual environment
source .venv/bin/activate

# Step 2: Use CLI commands directly
amazon-asin-cli product B0CGXY13QW
amazon-asin-cli search "wireless headphones"
amazon-asin-cli refinements "wireless headphones"
amazon-asin-cli theme "gaming setup" --limit 10 --batch-size 5

# Use custom cache folder
amazon-asin-cli search "wireless headphones" --limit 5 --cache-folder ./my-cache

# Step 3: Deactivate when done
deactivate
```

### Cache and Verbose Options
```bash
# Use default cache folder ("cache")
amazon-asin-cli search "wireless headphones" --limit 5

# Disable caching
amazon-asin-cli search "wireless headphones" --cache-folder none

# Use custom cache folder
amazon-asin-cli search "wireless headphones" --cache-folder ./my-cache

# Set logging level for detailed output
amazon-asin-cli --log-level DEBUG search "wireless headphones"

# Set logging level for minimal output
amazon-asin-cli --log-level WARNING search "wireless headphones"
```

**Note:** If `amazon-asin-cli` command is not found, make sure you've activated the virtual environment or use `uv run`.

---

## 🧪 Playwright Setup Notes

If Playwright fails to launch Chromium:
```bash
playwright install chromium
```

---