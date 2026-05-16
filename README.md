# Freelance Market Research Pipeline

Scrapes Khamsat + Mostaql → AI analysis → copy-paste service listings.

---

## Setup (one time)

```bash
pip install -r requirements.txt
playwright install chromium
```

---

## API Keys

### 1. Gemini (Free)

- Go to: https://aistudio.google.com/app/apikey
- Create key → copy it
- `set GEMINI_API_KEY=your_key` (Windows CMD)

### 2. Groq (Free — fastest)

- Go to: https://console.groq.com/keys
- Sign up free → Create API Key → copy it
- `set GROQ_API_KEY=your_key`
- Model used: `llama-3.3-70b-versatile`
- Free limit: ~6,000 tokens/minute

### 3. OpenRouter (Free models available)

- Go to: https://openrouter.ai/settings/keys
- Sign up → Create Key → copy it
- `set OPENROUTER_API_KEY=your_key`
- Model used: `mistralai/mistral-7b-instruct:free`
- Free tier: no hard TPM cap, rate limited per IP

### 4. Claude (Paid)

- Go to: https://console.anthropic.com/
- Add $5 credit → Settings → API Keys → Create
- `set ANTHROPIC_API_KEY=sk-ant-...`

> **Student tip:** Groq and Gemini are both fully free with no card required.
> Start with Groq for speed, Gemini for larger context windows.

---

## Run

```bash
python main.py
```

Pipeline flow:

1. Pick your AI model
2. Pick which service categories to scrape (and which queries per category)
3. Scraper runs on Khamsat + Mostaql
4. AI analyzes competitors → generates your listings

---

## Output Files

| File                     | Description                       |
| ------------------------ | --------------------------------- |
| `data/raw_services.json` | Raw scraped competitor data       |
| `data/analysis.md`       | Market analysis report            |
| `data/my_service.md`     | Your copy-paste service listings  |
| `data/run_metrics.log`   | Token usage per run (compact log) |

---

## Project Structure

```
freelance-researcher/
├── main.py          # Entry point — orchestrates everything
├── menu.py          # Interactive CLI menus
├── scraper.py       # Playwright scraper (Khamsat + Mostaql)
├── analyzer.py      # Prompt builder + AI calls
├── ai_backends.py   # All model backends + token metrics
├── config.py        # Search queries + model registry
├── requirements.txt
└── data/
```

---

## Troubleshooting

**0 services scraped?**
Site structure may have changed. Open `scraper.py`, update CSS selectors using browser DevTools (F12 → Inspector → find the card element class).

**Wrong model package missing?**
Install only what you need: `pip install groq` or `pip install google-genai` etc.
