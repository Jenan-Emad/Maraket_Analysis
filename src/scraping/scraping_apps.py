import pandas as pd
from google_play_scraper import reviews, Sort, search, app
import urllib.error


def scrape_market_apps(name, review_count=20):

    print(f"Connecting to Google Play Store to fetch app information for: {name}...")

    try:
        results = search(name, lang="en", country="ps", n_hits=6)
    except urllib.error.URLError as e:
        print(f"Error occurred while fetching app information for {name}: {e}")
        return pd.DataFrame()

    df = pd.DataFrame(results)
    return df
