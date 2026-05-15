"""
analyzer.py — Sends scraped services to Claude API for deep analysis
Outputs: analysis.md + service_recommendations.md
"""

import json
import os
import anthropic
from datetime import datetime

# ─── CONFIG ───────────────────────────────────────────────
RAW_DATA_FILE = "output/raw_services.json"
ANALYSIS_FILE = "output/analysis.md"
SERVICE_FILE = "output/my_service.md"

# YOUR SKILLS — edit this before running
MY_SKILLS = """
- Backend: Spring Boot (REST APIs, Spring Data JPA, Spring Security basics, Thymeleaf)
- Frontend: React.js, basic TypeScript, Tailwind CSS
- Database: MySQL, basic SQL
- Tools: Git, GitHub, Maven
- Currently in 3rd year Computer Science at AAST, Cairo
- Side projects: Clinic management system (Spring Boot), Supermarket system (Python/PyQt6), 
  Wardity luxury shop (React/TypeScript, deployed on Vercel)
- Not yet senior level — building toward job-ready
"""

MY_TARGET_PLATFORMS = "Khamsat (خمسات) and Mostaql (مستقل)"
# ──────────────────────────────────────────────────────────


def load_services() -> list[dict]:
    with open(RAW_DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def build_analysis_prompt(services: list[dict]) -> str:
    services_text = json.dumps(services, ensure_ascii=False, indent=2)
    return f"""
You are a freelance market strategist specializing in Arabic freelancing platforms.

I have scraped {len(services)} competitor services from {MY_TARGET_PLATFORMS}.
Here is the raw data:

<competitor_services>
{services_text}
</competitor_services>

My skills:
<my_skills>
{MY_SKILLS}
</my_skills>

Perform a DEEP analysis and produce a comprehensive markdown report with these exact sections:

# Freelance Market Analysis Report
*Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}*

## 1. Market Overview
- Total services analyzed per platform
- Most common service types
- Price range breakdown (min / avg / max)
- Most saturated niches

## 2. Competitor Breakdown
- Top 5 most competitive sellers and what makes them strong
- Common patterns in winning titles
- Common patterns in pricing strategies
- What most sellers are doing WRONG (gaps/weaknesses)

## 3. Market Gaps & Opportunities
- Underserved niches I can target
- Price points with least competition
- Service combinations that are rarely offered together

## 4. Keyword Analysis
- Most used Arabic keywords in titles
- Keywords I should use in my profile/services
- Keywords to AVOID (oversaturated)

## 5. Pricing Strategy Recommendation
- What price to start at given my level
- When to raise prices (milestone: X orders / X rating)
- Package structure recommendation (basic / standard / premium)

## 6. Strategic Recommendation
- Based on MY SKILLS specifically, which 2-3 services should I offer first?
- Which platform to prioritize first and why?
- What differentiator should I build my brand around?

Be specific, data-driven, and honest. If the data is limited, say so and reason from what you have.
"""


def build_service_prompt(analysis: str, services: list[dict]) -> str:
    return f"""
Based on this market analysis:
<analysis>
{analysis}
</analysis>

And my skills:
<my_skills>
{MY_SKILLS}
</my_skills>

Now create the ACTUAL service listings I should post. Produce a markdown file with:

# My Freelance Service Listings

## Service 1 — [Primary Service]

### Khamsat Listing (Arabic)
**العنوان:** ...
**الوصف:** (3-4 paragraphs, persuasive, specific)
**الحزم:**
- أساسي: [what's included] — [price] ريال
- متقدم: [what's included] — [price] ريال  
- احترافي: [what's included] — [price] ريال

### Upwork Listing (English)
**Title:** ...
**Description:** (3-4 paragraphs)
**Packages:**
- Basic: [what's included] — $[price]
- Standard: [what's included] — $[price]
- Premium: [what's included] — $[price]

---

## Service 2 — [Secondary Service]
[same structure]

---

## Profile Bio

### Arabic (for Khamsat/Mostaql)
...

### English (for Upwork)
...

---

## Quick-Win Strategy
3 specific actions to get the first order within 30 days.

Make everything COPY-PASTE READY. Be specific about prices, deliverables, and timelines.
"""


def call_claude(prompt: str, max_tokens: int = 4000) -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text


def run_analyzer():
    print("\n🔍 Loading scraped data...")
    services = load_services()
    print(f"  → {len(services)} services loaded")

    print("\n🤖 Sending to Claude for market analysis...")
    analysis_prompt = build_analysis_prompt(services)
    analysis = call_claude(analysis_prompt, max_tokens=4000)

    with open(ANALYSIS_FILE, "w", encoding="utf-8") as f:
        f.write(analysis)
    print(f"  → Analysis saved to {ANALYSIS_FILE}")

    print("\n🤖 Generating your service listings...")
    service_prompt = build_service_prompt(analysis, services)
    service_content = call_claude(service_prompt, max_tokens=4000)

    with open(SERVICE_FILE, "w", encoding="utf-8") as f:
        f.write(service_content)
    print(f"  → Service listings saved to {SERVICE_FILE}")

    print("\n✅ Done! Check the output/ folder.")


if __name__ == "__main__":
    run_analyzer()
