"""
scraper.py — Scrapes competitor services from Khamsat and Mostaql.
Accepts selected categories from menu.py instead of hardcoded queries.
"""

import asyncio
import json
import os
from playwright.async_api import async_playwright
from src.config import MAX_SERVICES_PER_QUERY

OUTPUT_FILE = "output/raw_services.json"


async def scrape_khamsat(page, query: str) -> list[dict]:
    services = []
    url = f"https://khamsat.com/search?q={query.replace(' ', '+')}"
    print(f"  [Khamsat] {query}")

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)
    except Exception as e:
        print(f"    [error] Could not load page: {e}")
        return []

    cards = await page.query_selector_all(".service-card, .card, article.service")
    if not cards:
        cards = await page.query_selector_all("li.service, .services-list li")

    for card in cards[:MAX_SERVICES_PER_QUERY]:
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
        except Exception as e:
            print(f"    [warn] card parse failed: {e}")

    print(f"    → {len(services)} services found")
    return services


async def scrape_mostaql(page, query: str) -> list[dict]:
    services = []
    url = f"https://mostaql.com/projects?q={query.replace(' ', '+')}"
    print(f"  [Mostaql] {query}")

    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        await page.wait_for_timeout(2000)
    except Exception as e:
        print(f"    [error] Could not load page: {e}")
        return []

    cards = await page.query_selector_all(
        ".project-card, .table--projects tbody tr, .project-row"
    )

    for card in cards[:MAX_SERVICES_PER_QUERY]:
        try:
            title_el = await card.query_selector("h3, h2, .project-title, a.title")
            title = await title_el.inner_text() if title_el else "N/A"

            budget_el = await card.query_selector(
                ".budget, .price, span[class*='budget']"
            )
            budget = await budget_el.inner_text() if budget_el else "N/A"

            desc_el = await card.query_selector("p, .description, .project-desc")
            desc = await desc_el.inner_text() if desc_el else "N/A"

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
                    "description": desc.strip()[:300],
                    "link": link,
                }
            )
        except Exception as e:
            print(f"    [warn] card parse failed: {e}")

    print(f"    → {len(services)} services found")
    return services


async def run_scraper(selected_categories: list[dict]) -> list[dict]:
    all_services = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
            ),
            locale="ar-EG",
        )
        page = await context.new_page()

        for cat in selected_categories:
            print(f"\n📦 [{cat['label']}]")

            if cat.get("khamsat"):
                print("  Khamsat queries:")
                for q in cat["khamsat"]:
                    results = await scrape_khamsat(page, q)
                    all_services.extend(results)
                    await asyncio.sleep(1.5)

            if cat.get("mostaql"):
                print("  Mostaql queries:")
                for q in cat["mostaql"]:
                    results = await scrape_mostaql(page, q)
                    all_services.extend(results)
                    await asyncio.sleep(1.5)

        await browser.close()

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_services, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Scraped {len(all_services)} total services → {OUTPUT_FILE}")
    return all_services


if __name__ == "__main__":
    # Standalone run: scrape all categories
    from src.config import CATEGORIES

    asyncio.run(run_scraper(CATEGORIES))
