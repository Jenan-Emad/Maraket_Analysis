# Competitor Intelligence Tool

A Streamlit web app that searches the Google Play Store, scrapes customer reviews for competing apps, stores them in SQLite, builds a multi-sheet Excel report, and uses an LLM (Google Gemini) to turn 1-2 star reviews into executive-level market gap insights.

**Live demo:** _add your Streamlit Community Cloud link here_

---

## Features

- **App discovery:** search by app name, niche keyword, or category (e.g. "food delivery") and see title, developer, rating, and icon.
- **Multi-app selection:** pick 2 to 4 competing apps with checkboxes.
- **Safe review scraping:** fetches reviews in batches using continuation tokens, so large scrapes don't crash or exhaust memory.
- **Data pipeline:** cleans review text, extracts timestamps, and labels sentiment (Positive / Neutral / Negative).
- **Relational storage:** saves everything to a local SQLite database (`competitor_intelligence.db`).
- **Excel report:** generates a multi-sheet report comparing the selected competitors, downloadable from the app.
- **Interactive charts:** Plotly charts for star distribution and sentiment share.
- **AI market gap analysis:** Gemini summarizes recurring bugs, missing features users want, and strategic recommendations.

## How it works

```
Search -> Select apps -> Scrape reviews (batched) -> Clean & label sentiment
      -> SQLite -> Excel report -> Plotly charts -> Gemini gap analysis
```

1. **Search:** `google-play-scraper` returns matching apps.
2. **Scrape:** reviews are fetched 100 at a time using a continuation token (150-300 per app) and written to the database batch by batch.
3. **Sentiment:** reviews are labeled from their star rating (1-2 = Negative, 3 = Neutral, 4-5 = Positive).
4. **AI analysis:** a sample of 1-2 star reviews per app is sent to Gemini, which returns three sections: top recurring complaints, requested features, and strategic recommendations.

## Tech stack

Python 3.10+, Streamlit, Plotly, pandas, openpyxl, sqlite3, google-play-scraper, google-genai (Gemini API).

## Project structure

```
final_proj_DS/
├── src/
│   ├── app.py                 # Streamlit UI (entry point)
│   ├── market_ai.py           # Gemini gap analysis
│   ├── charts.py              # Plotly charts
│   ├── get_scraped_data.py    # app search results display
│   ├── get_scraped_reviews.py # review scraping, cleaning, saving
│   ├── scraping/              # Google Play search/scrape helpers
│   └── write_methods/         # database setup and Excel export
├── requirements.txt
├── .gitignore
└── README.md
```

_Adjust this tree to match your actual files._

## Getting started

### 1. Clone and install

```bash
git clone <your-repo-url>
cd final_proj_DS
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 2. Add your Gemini API key

Get a free key from [Google AI Studio](https://aistudio.google.com/).

Create a file named `.env` in the project root:

```
GEMINI_API_KEY=your-key-here
```

`.env` is listed in `.gitignore` and must never be committed.

### 3. Run the app

```bash
streamlit run src/app.py
```

Then open the local URL shown in the terminal (usually http://localhost:8501).

## Usage

1. Enter an app name or niche keyword in the sidebar and click **Search**.
2. Select 2 to 4 apps.
3. Click **Scrape & Analyze**.
4. Open the **Results** tab to see the charts and the AI market gap summary.
5. Download the Excel report with the download button.

## Deploying to Streamlit Community Cloud

1. Push the repo to GitHub (make sure `.env`, `*.db`, and generated output files are ignored).
2. On [share.streamlit.io](https://share.streamlit.io), create a new app and set the main file path to `src/app.py`.
3. Under **Advanced settings -> Secrets**, add:
   ```toml
   GEMINI_API_KEY = "your-key-here"
   ```
4. Deploy.

## Notes

- The database (`competitor_intelligence.db`) and the Excel report are **generated at runtime**, so they are not stored in the repository. On Streamlit Community Cloud the disk is temporary and resets when the app restarts.
- The Gemini API can return temporary 503 errors during high demand. The app retries with backoff and falls back to alternative models.
- Sentiment is derived from star ratings. Text-based sentiment models could be added as an upgrade.
- Respect Google Play's terms and keep request delays in place when scraping.
