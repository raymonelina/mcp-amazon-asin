import importlib.util
import subprocess
import sys


def setup_playwright():
    # Check if playwright is installed
    if importlib.util.find_spec("playwright") is None:
        print("📦 Playwright not found. Installing via pip...")
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "playwright"], check=True
        )
    else:
        print("✅ Playwright already installed.")

    # Ensure the browser binaries are installed
    try:
        subprocess.run(["playwright", "install", "chromium"], check=True)
        print("✅ Chromium browser installed.")
    except subprocess.CalledProcessError:
        print("⚠️ Failed to install Chromium browser. Try manually running:")
        print("   playwright install chromium")
        raise
