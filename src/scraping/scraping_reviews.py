import pandas as pd
from google_play_scraper import reviews, Sort, search, app
from google_play_scraper.exceptions import NotFoundError
import urllib.error

def scrape_market_reviews(app_id, review_count=200, lang="en", country="ps"):
    print(f"Connecting to Google Play Store to fetch reviews for app ID: {app_id}...")
    token = None  # Initialize the continuation token to None for the first batch of reviews

    all_reviews = []

    try:
        while len(all_reviews) < review_count:
            batch_size = min(100, review_count - len(all_reviews))
            result, token = reviews(
                app_id,
                lang=lang,
                country=country,
                sort=Sort.NEWEST,
                count=batch_size,
                continuation_token=token,
            )
            all_reviews.extend(result)
            if not token or not result:     # no more pages
                break

    except NotFoundError:
        print(f"App {app_id} not found in country '{country}'.")
    except (urllib.error.URLError, OSError) as e:
        print(f"Network error while fetching reviews for {app_id}: {e}")

    return pd.DataFrame(all_reviews[:review_count])