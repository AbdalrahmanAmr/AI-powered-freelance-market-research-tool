"""
analyzer.py — Builds prompts and runs AI analysis.
Resolves output paths relative to project root (works from src/ layout).
"""

import json
import os
import sys
from datetime import datetime

# ── .env support ─────────────────────────────────────────
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

# ── path fix ─────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ai_backends import call_ai


# ─── RESOLVE OUTPUT PATHS ─────────────────────────────────
def _root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _resolve(subfolder: str, filename: str) -> str:
    """Find the right output folder whether project uses data/ or output/."""
    root = _root()
    candidates = [
        os.path.join(root, "data", subfolder, filename),
        os.path.join(root, "output", filename),
    ]
    for path in candidates:
        if os.path.isdir(os.path.dirname(path)):
            return path
    return candidates[0]


RAW_DATA_FILE = _resolve("raw", "raw_services.json")
ANALYSIS_FILE = _resolve("reports", "analysis.md")
SERVICE_FILE = _resolve("reports", "my_service.md")

# ─── YOUR SKILLS ──────────────────────────────────────────
MY_SKILLS = """
- Backend: Spring Boot (REST APIs, Spring Data JPA, Spring Security, Thymeleaf)
- Frontend: React.js, TypeScript, Tailwind CSS
- Database: MySQL
- Tools: Git, GitHub, Maven
- 3rd year CS student at AAST, Cairo, Egypt
- Projects: Clinic Management System (Spring Boot), Supermarket System (Python/PyQt6),
  Wardity luxury shop (React/TypeScript, live on Vercel)
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

I scraped {len(services)} competitor services from {MY_TARGET_PLATFORMS}.

<competitor_services>
{services_text}
</competitor_services>

<my_skills>
{MY_SKILLS}
</my_skills>

Produce a comprehensive markdown report:

# Freelance Market Analysis Report
*Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}*

## 1. Market Overview
- Services analyzed per platform
- Most common service types
- Price range (min / avg / max)
- Most saturated niches

## 2. Competitor Breakdown
- Top 5 strongest sellers and why
- Patterns in winning titles
- Patterns in pricing strategies
- What most sellers are doing WRONG

## 3. Market Gaps & Opportunities
- Underserved niches I can target
- Price points with least competition
- Service combos rarely offered together

## 4. Keyword Analysis
- Most used Arabic keywords in titles
- Keywords I should use
- Keywords to AVOID (oversaturated)

## 5. Pricing Strategy
- Starting price given my level
- When to raise (milestone: X orders / X rating)
- Package structure (basic / standard / premium)

## 6. Strategic Recommendation
- Which 2-3 services to offer first (based on MY skills)
- Which platform to prioritize and why
- What differentiator to build my brand around

Be specific, data-driven, honest. If data is limited, say so.
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

Create ACTUAL copy-paste-ready service listings:

# My Freelance Service Listings

## Service 1 — [Primary Service]

### Khamsat (Arabic)
**العنوان:** ...
**الوصف:** (3-4 paragraphs, persuasive, specific)
**الحزم:**
- أساسي: [deliverables] — [price] ريال
- متقدم: [deliverables] — [price] ريال
- احترافي: [deliverables] — [price] ريال

### Upwork (English)
**Title:** ...
**Description:** (3-4 paragraphs)
**Packages:**
- Basic:    [deliverables] — $[price]
- Standard: [deliverables] — $[price]
- Premium:  [deliverables] — $[price]

---

## Service 2 — [Secondary Service]
[same structure]

---

## Profile Bio

### Arabic (Khamsat / Mostaql)
...

### English (Upwork)
...

---

## Quick-Win: First Order in 30 Days
3 concrete actions to land the first client fast.

Be specific on prices, timelines, deliverables. Everything copy-paste ready.
"""


def run_analyzer(model_id: str = "gemini") -> None:
    print(f"\n🔍 Loading scraped data...")
    services = load_services()
    print(f"  → {len(services)} services loaded")

    print(f"\n🤖 Market analysis via {model_id.upper()}...")
    analysis = call_ai(
        build_analysis_prompt(services),
        model_id=model_id,
        step="Market Analysis Generation",
    )
    os.makedirs(os.path.dirname(ANALYSIS_FILE), exist_ok=True)
    with open(ANALYSIS_FILE, "w", encoding="utf-8") as f:
        f.write(analysis)
    print(f"  → Saved to {ANALYSIS_FILE}")

    print(f"\n🤖 Service listings via {model_id.upper()}...")
    service_content = call_ai(
        build_service_prompt(analysis, services),
        model_id=model_id,
        step="Service Copywriting Listings",
    )
    with open(SERVICE_FILE, "w", encoding="utf-8") as f:
        f.write(service_content)
    print(f"  → Saved to {SERVICE_FILE}")

    print("\n✅ Analysis complete.")


if __name__ == "__main__":
    print("Which model? (1) Gemini  (2) Groq  (3) OpenRouter  (4) Claude")
    c = input("Choice: ").strip()
    ids = {"1": "gemini", "2": "groq", "3": "openrouter", "4": "claude"}
    run_analyzer(model_id=ids.get(c, "gemini"))
