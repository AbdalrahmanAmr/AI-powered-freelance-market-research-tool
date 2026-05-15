# AI-powered Freelance Market Research Tool

# Freelance Market Research Pipeline

Scrapes Khamsat + Mostaql for competitor services, sends data to Claude API,
and generates a market analysis + ready-to-paste service listings.

---

## Setup (one time)

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### 2. Set your Anthropic API key

```bash
# On Linux/Mac
export ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx

# On Windows CMD
set ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxx

# On Windows PowerShell
$env:ANTHROPIC_API_KEY="sk-ant-xxxxxxxxxxxxxxxx"
```

Get your API key from: https://console.anthropic.com/

### 3. Edit your skills in analyzer.py

Open `analyzer.py` and update the `MY_SKILLS` variable with your current skills.

---

## Run

```bash
python main.py
```

Or run steps separately:

```bash
# Only scrape (no API key needed)
python scraper.py

# Only analyze (uses existing output/raw_services.json)
python analyzer.py
```

---

## Output

| File                       | Description                          |
| -------------------------- | ------------------------------------ |
| `output/raw_services.json` | Raw scraped competitor data          |
| `output/analysis.md`       | Market analysis report by Claude     |
| `output/my_service.md`     | Your ready-to-paste service listings |

---

## Project Structure

```
freelance-researcher/
├── main.py              # Full pipeline runner
├── scraper.py           # Playwright scraper (Khamsat + Mostaql)
├── analyzer.py          # Claude API analysis + generation
├── requirements.txt     # Python dependencies
├── output/
│   ├── raw_services.json
│   ├── analysis.md
│   └── my_service.md
└── logs/
```

---

## Troubleshooting

**Scraped 0 services?**
The site structure may have changed. Open `scraper.py` and update the CSS selectors
in `scrape_khamsat()` or `scrape_mostaql()`. Use browser DevTools to find the right selectors.

**API key error?**
Make sure the env variable is exported in the same terminal session you run the script from.

**Playwright not found?**
Run `playwright install chromium` after pip install.
