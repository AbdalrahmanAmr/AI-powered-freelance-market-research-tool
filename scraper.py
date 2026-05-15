"""
scraper.py — Scrapes competitor services from Khamsat and Mostaql
Uses Playwright for browser automation
"""

import asyncio
import json
import re
from playwright.async_api import async_playwright

# ─── CONFIG ───────────────────────────────────────────────
KHAMSAT_SEARCH_QUERIES = [
    "تطوير مواقع",
    "تطبيق ويب",
    "برمجة باك اند",
    "spring boot",
    "react",
]

MOSTAQL_SEARCH_QUERIES = [
    "تطوير موقع",
    "برمجة تطبيق ويب",
    "full stack",
]

MAX_SERVICES_PER_QUERY = 10  # how many results to scrape per search
OUTPUT_FILE = "output/raw_services.json"
# ──────────────────────────────────────────────────────────


async def scrape_khamsat(page, query: str) -> list[dict]:
    """Scrape services from Khamsat for a given query."""
    services = []
    url = f"https://khamsat.com/search?q={query.replace(' ', '+')}"

    print(f"  [Khamsat] Searching: {query}")
    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    await page.wait_for_timeout(2000)

    cards = await page.query_selector_all(".service-card, .card, article.service")

    # fallback: try generic listing items
    if not cards:
        cards = await page.query_selector_all("li.service, .services-list li")

    count = 0
    for card in cards:
        if count >= MAX_SERVICES_PER_QUERY:
            break
        try:
            title_el = await card.query_selector("h3, h2, .title, .service-title")
            title = await title_el.inner_text() if title_el else "N/A"

            price_el = await card.query_selector(
                ".price, .amount, span[class*='price']"
            )
            price = await price_el.inner_text() if price_el else "N/A"

            rating_el = await card.query_selector(
                ".rating, .stars, span[class*='rate']"
            )
            rating = await rating_el.inner_text() if rating_el else "N/A"

            orders_el = await card.query_selector(
                ".orders, .sold, span[class*='order']"
            )
            orders = await orders_el.inner_text() if orders_el else "N/A"

            seller_el = await card.query_selector(".seller, .username, .user-name")
            seller = await seller_el.inner_text() if seller_el else "N/A"

            link_el = await card.query_selector("a")
            href = await link_el.get_attribute("href") if link_el else ""
            link = (
                f"https://khamsat.com{href}" if href and href.startswith("/") else href
            )

            services.append(
                {
                    "platform": "khamsat",
                    "query": query,
                    "title": title.strip(),
                    "price": price.strip(),
                    "rating": rating.strip(),
                    "orders": orders.strip(),
                    "seller": seller.strip(),
                    "link": link,
                }
            )
            count += 1
        except Exception as e:
            print(f"    [warn] Failed to parse card: {e}")
            continue

    print(f"    → Found {len(services)} services")
    return services


async def scrape_mostaql(page, query: str) -> list[dict]:
    """Scrape projects/services from Mostaql for a given query."""
    services = []
    url = f"https://mostaql.com/projects?q={query.replace(' ', '+')}&category=&budget_from=&budget_to="

    print(f"  [Mostaql] Searching: {query}")
    await page.goto(url, wait_until="domcontentloaded", timeout=30000)
    await page.wait_for_timeout(2000)

    cards = await page.query_selector_all(
        ".project-card, .table--projects tbody tr, .project-row"
    )

    count = 0
    for card in cards:
        if count >= MAX_SERVICES_PER_QUERY:
            break
        try:
            title_el = await card.query_selector("h3, h2, .project-title, a.title")
            title = await title_el.inner_text() if title_el else "N/A"

            budget_el = await card.query_selector(
                ".budget, .price, span[class*='budget']"
            )
            budget = await budget_el.inner_text() if budget_el else "N/A"

            desc_el = await card.query_selector("p, .description, .project-desc")
            description = await desc_el.inner_text() if desc_el else "N/A"

            link_el = await card.query_selector("a")
            href = await link_el.get_attribute("href") if link_el else ""
            link = (
                f"https://mostaql.com{href}" if href and href.startswith("/") else href
            )

            services.append(
                {
                    "platform": "mostaql",
                    "query": query,
                    "title": title.strip(),
                    "budget": budget.strip(),
                    "description": description.strip()[:300],
                    "link": link,
                }
            )
            count += 1
        except Exception as e:
            print(f"    [warn] Failed to parse card: {e}")
            continue

    print(f"    → Found {len(services)} services")
    return services


async def run_scraper():
    all_services = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
            locale="ar-EG",
        )
        page = await context.new_page()

        print("\n📦 Scraping Khamsat...")
        for query in KHAMSAT_SEARCH_QUERIES:
            results = await scrape_khamsat(page, query)
            all_services.extend(results)
            await asyncio.sleep(1.5)  # polite delay

        print("\n📦 Scraping Mostaql...")
        for query in MOSTAQL_SEARCH_QUERIES:
            results = await scrape_mostaql(page, query)
            all_services.extend(results)
            await asyncio.sleep(1.5)

        await browser.close()

    # Save raw output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_services, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Scraped {len(all_services)} services → saved to {OUTPUT_FILE}")
    return all_services


if __name__ == "__main__":
    asyncio.run(run_scraper())
