"""
config.py — All search queries organized by service category.
Edit the queries here if you want to add/remove search terms.
"""

RAW_DATA_FILE = "data/raw/raw_services.json"
METRICS_LOG_FILE = "data/logs/run_metrics.log"
ANALYSIS_FILE = "data/reports/analysis.md"
SERVICE_FILE = "data/reports/my_service.md"

# ─── SEARCH QUERY BANK ────────────────────────────────────
# Each category has:
#   "label"    : display name shown in the menu
#   "khamsat"  : Arabic/English queries for Khamsat
#   "mostaql"  : Arabic/English queries for Mostaql

CATEGORIES = [
    {
        "id": "backend",
        "label": "Backend API (Spring Boot / REST)",
        "khamsat": [
            "برمجة باك اند",
            "spring boot",
            "rest api",
            "برمجة API",
        ],
        "mostaql": [
            "برمجة باك اند",
            "تطوير API",
            "spring boot",
        ],
    },
    {
        "id": "fullstack",
        "label": "Web App / Full Stack (React + Spring Boot)",
        "khamsat": [
            "تطوير مواقع",
            "تطبيق ويب",
            "full stack",
            "react spring boot",
        ],
        "mostaql": [
            "تطوير موقع",
            "برمجة تطبيق ويب",
            "full stack developer",
        ],
    },
    {
        "id": "frontend",
        "label": "Frontend Only (React / UI)",
        "khamsat": [
            "تصميم واجهات",
            "react",
            "frontend",
            "واجهة مستخدم",
        ],
        "mostaql": [
            "تصميم واجهة",
            "react developer",
            "frontend",
        ],
    },
]

# ─── MODEL REGISTRY ───────────────────────────────────────
# Add / remove models here as needed.

MODELS = [
    {
        "id": "gemini",
        "label": "Gemini 1.5 Flash  (Free tier)",
        "env": "GEMINI_API_KEY",
        "pkg": "google-genai",
    },
    {
        "id": "groq",
        "label": "Groq — LLaMA 3.3 70B  (Free tier, fast)",
        "env": "GROQ_API_KEY",
        "pkg": "groq",
    },
    {
        "id": "openrouter",
        "label": "OpenRouter — Mistral 7B  (Free tier)",
        "env": "OPENROUTER_API_KEY",
        "pkg": "openai",  # OpenRouter uses OpenAI-compatible SDK
    },
    {
        "id": "claude",
        "label": "Claude Sonnet 4   (Paid)",
        "env": "ANTHROPIC_API_KEY",
        "pkg": "anthropic",
    },
]

# ─── LIMITS ───────────────────────────────────────────────
FREE_TPM_LIMITS = {
    "gemini": 250_000,
    "groq": 6_000,  # Groq free: ~6k TPM on LLaMA 3.3 70B
    "openrouter": None,  # OpenRouter free tier has no hard TPM cap
    "claude": None,  # Paid — no hard cap shown
}

MAX_SERVICES_PER_QUERY = 10
