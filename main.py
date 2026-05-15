"""
main.py — Full pipeline: scrape → analyze → generate service listings
Usage: python main.py
"""

import asyncio
import os
import sys
from scraper import run_scraper
from analyzer import run_analyzer


def check_env():
    """Make sure ANTHROPIC_API_KEY is set."""
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ ERROR: ANTHROPIC_API_KEY environment variable not set.")
        print("\nFix it by running:")
        print("  export ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)


def check_deps():
    """Check required packages are installed."""
    missing = []
    try:
        import playwright
    except ImportError:
        missing.append("playwright")
    try:
        import anthropic
    except ImportError:
        missing.append("anthropic")

    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("\nInstall them with:")
        print(f"  pip install {' '.join(missing)}")
        if "playwright" in missing:
            print("  playwright install chromium")
        sys.exit(1)


async def main():
    print("=" * 55)
    print("  Freelance Market Research Pipeline")
    print("  Khamsat + Mostaql → Claude Analysis")
    print("=" * 55)

    check_env()
    check_deps()

    # Step 1: Scrape
    print("\n[1/2] Starting scraper...")
    await run_scraper()

    # Step 2: Analyze
    print("\n[2/2] Starting analyzer...")
    run_analyzer()

    print("\n" + "=" * 55)
    print("  Pipeline complete! Files in output/:")
    print("  - raw_services.json   (raw scraped data)")
    print("  - analysis.md         (market analysis)")
    print("  - my_service.md       (your ready listings)")
    print("=" * 55)


if __name__ == "__main__":
    asyncio.run(main())
