"""
ai_backends.py — All AI model backends + token metrics logging.
Each backend returns response text and logs usage.
"""

import os
import sys
from datetime import datetime

# ── .env support ─────────────────────────────────────────
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv optional — env vars set manually still work

# ── path fix so config imports work from src/ ─────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import FREE_TPM_LIMITS


# ─── OUTPUT PATHS ─────────────────────────────────────────
def _resolve_log_path() -> str:
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidates = [
        os.path.join(root, "data", "logs", "run_metrics.log"),
        os.path.join(root, "output", "run_metrics.log"),
    ]
    for path in candidates:
        if os.path.isdir(os.path.dirname(path)):
            return path
    return candidates[0]


METRICS_LOG = _resolve_log_path()

# ─── GROQ TOKEN LIMIT ─────────────────────────────────────
GROQ_SAFE_INPUT = 8_000  # leave room for output (~3k tokens)

# ─── METRICS LOGGING ──────────────────────────────────────


def log_metrics(model_id: str, step: str, usage: dict) -> None:
    """Console: detailed block. Log file: compact one-liner."""
    inp = usage.get("input", 0)
    out = usage.get("output", 0)
    total = usage.get("total", inp + out)
    tpm = FREE_TPM_LIMITS.get(model_id)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n📊 [Token Metrics — {step}]")
    print(f"  → Input: {inp:,} | Output: {out:,} | Total: {total:,}")
    if tpm:
        remaining = max(0, tpm - total)
        print(f"  → Free TPM buffer remaining: {remaining:,} / {tpm:,}")

    tpm_info = f" | TPM left: {max(0, tpm-total):,}/{tpm:,}" if tpm else ""
    line = (
        f"[{ts}] {model_id.upper()} | {step} "
        f"| in:{inp} out:{out} total:{total}{tpm_info}\n"
    )
    os.makedirs(os.path.dirname(METRICS_LOG), exist_ok=True)
    with open(METRICS_LOG, "a", encoding="utf-8") as f:
        f.write(line)


# ─── TOKEN TRIMMER ────────────────────────────────────────


def trim_prompt(prompt: str, max_chars: int) -> str:
    """Trim prompt to max_chars at a clean JSON boundary."""
    if len(prompt) <= max_chars:
        return prompt
    cutoff = prompt[:max_chars]
    last_entry = cutoff.rfind('{"platform"')
    if last_entry > 0:
        cutoff = cutoff[:last_entry]
    return cutoff + "\n... (remaining services trimmed to fit token limit)\n"


# ─── MODEL BACKENDS ───────────────────────────────────────


def call_gemini(prompt: str, step: str) -> str:
    from google import genai

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=prompt,
    )
    if response.usage_metadata:
        m = response.usage_metadata
        log_metrics(
            "gemini",
            step,
            {
                "input": m.prompt_token_count,
                "output": m.candidates_token_count,
                "total": m.total_token_count,
            },
        )
    return response.text


def call_groq(prompt: str, step: str) -> str:
    from groq import Groq

    # Groq free: 12k TPM hard cap — trim to ~8k input tokens (~32k chars)
    MAX_CHARS = GROQ_SAFE_INPUT * 4
    trimmed = trim_prompt(prompt, MAX_CHARS)
    if len(trimmed) < len(prompt):
        print(
            f"  ⚠️  Prompt trimmed for Groq free tier "
            f"({len(prompt):,} → {len(trimmed):,} chars)"
        )

    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": trimmed}],
        max_tokens=3_000,
    )
    if resp.usage:
        log_metrics(
            "groq",
            step,
            {
                "input": resp.usage.prompt_tokens,
                "output": resp.usage.completion_tokens,
                "total": resp.usage.total_tokens,
            },
        )
    return resp.choices[0].message.content


def call_openrouter(prompt: str, step: str) -> str:
    from openai import OpenAI

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
    )
    resp = client.chat.completions.create(
        model="mistralai/mistral-7b-instruct:free",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=4_000,
    )
    if resp.usage:
        log_metrics(
            "openrouter",
            step,
            {
                "input": resp.usage.prompt_tokens,
                "output": resp.usage.completion_tokens,
                "total": resp.usage.total_tokens,
            },
        )
    return resp.choices[0].message.content


def call_claude(prompt: str, step: str) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4_000,
        messages=[{"role": "user", "content": prompt}],
    )
    if message.usage:
        log_metrics(
            "claude",
            step,
            {
                "input": message.usage.input_tokens,
                "output": message.usage.output_tokens,
                "total": message.usage.input_tokens + message.usage.output_tokens,
            },
        )
    return message.content[0].text


# ─── ROUTER ───────────────────────────────────────────────


def call_ai(prompt: str, model_id: str, step: str) -> str:
    routes = {
        "gemini": call_gemini,
        "groq": call_groq,
        "openrouter": call_openrouter,
        "claude": call_claude,
    }
    fn = routes.get(model_id)
    if not fn:
        raise ValueError(f"Unknown model: {model_id}")
    return fn(prompt, step)
