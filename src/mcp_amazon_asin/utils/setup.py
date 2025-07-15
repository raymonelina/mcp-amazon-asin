import importlib.util
import logging
import subprocess
import sys

# Configure logger
logger = logging.getLogger(__name__)


def setup_playwright():
    # Check if playwright is installed
    if importlib.util.find_spec("playwright") is None:
        logger.debug("📦 Playwright not found. Installing via pip...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "playwright"], check=True
        )
    else:
        logger.debug("✅ Playwright already installed.")

    # Ensure the browser binaries are installed
    try:
        subprocess.run(["playwright", "install", "chromium"], check=True)
        logger.debug("✅ Chromium browser installed.")
    except subprocess.CalledProcessError:
        logger.error("⚠️ Failed to install Chromium browser. Try manually running:")
        logger.error("   playwright install chromium")
        raise
