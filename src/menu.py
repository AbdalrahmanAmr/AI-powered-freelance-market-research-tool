"""
menu.py — Interactive CLI menus for model and category selection.
Called by main.py before scraping starts.
"""

import os
import sys
from src.config import MODELS, CATEGORIES


def _divider():
    print("─" * 56)


def pick_model() -> dict:
    """Step 1: Let user pick which AI model to use."""
    print("\n╔══════════════════════════════════════════════════════╗")
    print("║     Freelance Market Research Pipeline               ║")
    print("╚══════════════════════════════════════════════════════╝")
    print("\n  Step 1 of 2 — Choose AI Model\n")

    for i, m in enumerate(MODELS, 1):
        print(f"  {i}. {m['label']}")

    print()
    while True:
        try:
            choice = int(input("  Enter number: "))
            if 1 <= choice <= len(MODELS):
                selected = MODELS[choice - 1]
                print(f"\n  ✅ Model: {selected['label']}\n")
                return selected
            print(f"  Enter a number between 1 and {len(MODELS)}.")
        except ValueError:
            print("  Please enter a number.")


def pick_categories() -> list[dict]:
    """Step 2: Let user pick which service categories to scrape."""
    _divider()
    print("\n  Step 2 of 2 — Choose Service Categories to Scrape\n")

    for i, cat in enumerate(CATEGORIES, 1):
        print(f"  {i}. {cat['label']}")

    print()
    print("  Enter numbers separated by commas  (e.g. 1,3)")
    print("  Or press Enter to select ALL categories")
    print()

    raw = input("  Your choice: ").strip()

    if not raw:
        selected = CATEGORIES
        print(f"\n  ✅ All {len(selected)} categories selected.")
        return selected

    selected = []
    for part in raw.split(","):
        part = part.strip()
        if part.isdigit():
            idx = int(part) - 1
            if 0 <= idx < len(CATEGORIES):
                selected.append(CATEGORIES[idx])

    if not selected:
        print("  No valid selection — defaulting to ALL categories.")
        return CATEGORIES

    print(f"\n  ✅ Selected categories:")
    for cat in selected:
        print(f"     • {cat['label']}")

    # Per-category: let user pick which queries to include
    refined = []
    for cat in selected:
        _divider()
        print(f"\n  Queries for: {cat['label']}")
        all_queries = list(dict.fromkeys(cat["khamsat"] + cat["mostaql"]))
        print("  (Enter numbers to include, or press Enter for ALL)\n")
        for i, q in enumerate(all_queries, 1):
            print(f"    {i}. {q}")
        print()

        raw_q = input("  Your choice: ").strip()
        if not raw_q:
            refined.append(cat)
            print(f"  ✅ All queries kept.")
            continue

        chosen_khamsat = []
        chosen_mostaql = []
        for part in raw_q.split(","):
            part = part.strip()
            if part.isdigit():
                idx = int(part) - 1
                if 0 <= idx < len(all_queries):
                    q = all_queries[idx]
                    if q in cat["khamsat"]:
                        chosen_khamsat.append(q)
                    if q in cat["mostaql"]:
                        chosen_mostaql.append(q)

        refined.append(
            {
                **cat,
                "khamsat": chosen_khamsat or cat["khamsat"],
                "mostaql": chosen_mostaql or cat["mostaql"],
            }
        )
        print(f"  ✅ Custom queries saved.")

    return refined


def check_env(model: dict) -> None:
    """Verify the API key for the chosen model is set."""
    key = os.environ.get(model["env"])
    if not key:
        print(f"\n❌ Missing environment variable: {model['env']}")
        print(f"\n  Set it before running:")
        print(f"    Windows CMD : set {model['env']}=your_key_here")
        print(f"    Windows PS  : $env:{model['env']}='your_key_here'")
        print(f"    Linux/Mac   : export {model['env']}=your_key_here")
        print(f"\n  See README.md → API Keys section for where to get it.")
        sys.exit(1)


def check_deps(model: dict) -> None:
    """Verify the required Python package is installed."""
    pkg = model["pkg"]
    try:
        if pkg == "google-genai":
            from google import genai  # noqa
        elif pkg == "groq":
            import groq  # noqa
        elif pkg == "openai":
            import openai  # noqa
        elif pkg == "anthropic":
            import anthropic  # noqa
    except ImportError:
        print(f"\n❌ Missing package: {pkg}")
        install_name = pkg
        print(f"\n  pip install {install_name}")
        sys.exit(1)
