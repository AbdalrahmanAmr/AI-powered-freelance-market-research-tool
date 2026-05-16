"""
main.py — Pipeline entry point.
Supports src/ layout: adds src/ to path so imports resolve correctly.
"""

import asyncio
import sys
import os

# ── Support src/ project layout ──────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from menu import pick_model, pick_categories, check_env, check_deps
from scraper import run_scraper
from analyzer import run_analyzer


async def main():
    # Step 1: Model selection
    model = pick_model()
    check_env(model)
    check_deps(model)

    # Step 2: Category + query selection
    selected_categories = pick_categories()

    # Step 3: Scrape
    print("\n" + "═" * 56)
    print("  [1/2] Scraping...")
    print("═" * 56)
    await run_scraper(selected_categories)

    # Step 4: Analyze
    print("\n" + "═" * 56)
    print("  [2/2] Analyzing...")
    print("═" * 56)
    run_analyzer(model_id=model["id"])

    # Done
    print("\n" + "═" * 56)
    print("  Pipeline complete! Files in output/:")
    print("    raw_services.json   — scraped competitor data")
    print("    analysis.md         — market analysis report")
    print("    my_service.md       — your copy-paste listings")
    print("    run_metrics.log     — token usage history")
    print("═" * 56 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
