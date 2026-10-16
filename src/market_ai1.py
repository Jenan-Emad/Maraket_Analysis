from dotenv import load_dotenv
from google import genai
from google.genai import errors
import os
import time
import pandas as pd
from write_methods.file_to_upload import save_pain_to_excel
from write_methods.get_path import get_output_dir
from get_api_key import get_api_key
from openai import OpenAI

load_dotenv(override=True)

MODELS = ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-2.5-flash-lite"]  # main + backups
MAX_CHARS = 200_000  # keep the prompt a sane size

ANALYZE_PROMPT = """You are a product strategy analyst. Below are 1-2 star Google Play
reviews for competing apps. Analyze them and write a concise, executive-level
summary for a product team that is about to build a competing app.

Use exactly these three sections:

## 1. Top Recurring Bugs & Complaints
List the 4-6 most common problems across the apps. Mention which apps are affected.

## 2. Features Users Are Asking For
List features users want that the apps are missing.

## 3. Strategic Recommendations
Give 4-5 actionable recommendations for our new app, based on the gaps above.

Rules: be concise, use bullet points, base everything only on the reviews,
no filler.

REVIEWS (CSV):
"""


def get_market_analysis_from_file():

    # get the file path for the reviews excel file
    save_pain_to_excel()  # Ensure the Excel file is created before proceeding
    
    api_key = get_api_key()
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set in environment variables.")

    client = genai.Client(api_key=api_key)

    out_file = get_output_dir() / "pain_reviews.xlsx"  # Ensure this function is defined and returns the path to the Excel file
    if not out_file.exists():
        raise FileNotFoundError(f"Reviews file not found: {out_file}")

    reviews_csv = pd.read_excel(out_file).to_csv(index=False)[:MAX_CHARS]
    prompt = ANALYZE_PROMPT + reviews_csv

    for model in MODELS:
        for attempt in range(4):
            try:
                response = client.models.generate_content(model=model, contents=prompt)
                return response.text
            except errors.ServerError as e:      # 500/503: temporary, retry
                wait = 2 ** attempt * 2
                print(f"{model} busy ({e.code}), retry in {wait}s...")
                time.sleep(wait)
            except errors.ClientError as e:      # 404/400/429: try next model
                print(f"{model} failed: {e.code} {e.message}")
                break

    return "The AI service is busy right now. Please try again in a few minutes."

def get_market_analysis_from_file_gpt():
    api_key = os.getenv("CHATGPT_API_KEY")
    if not api_key:
        raise ValueError("CHATGPT_API_KEY is not set in environment variables.")

    # get the file path for the reviews excel file
    save_pain_to_excel()

    out_file = get_output_dir() / "pain_reviews.xlsx"  # Ensure this function is defined and returns the path to the Excel file
    if not out_file.exists():
        raise FileNotFoundError(f"Reviews file not found: {out_file}")

    reviews_csv = pd.read_excel(out_file).to_csv(index=False)[:MAX_CHARS]
    prompt = ANALYZE_PROMPT + reviews_csv

    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content


def get_market_analysis_from_file_grok():
    api_key = os.getenv(get_api_key())
    if not api_key:
        raise ValueError("GROK_API_KEY is not set in environment variables.")

    # get the file path for the reviews excel file
    save_pain_to_excel()

    out_file = get_output_dir() / "pain_reviews.xlsx"
    if not out_file.exists():
        raise FileNotFoundError(f"Reviews file not found: {out_file}")

    reviews_csv = pd.read_excel(out_file).to_csv(index=False)[:MAX_CHARS]
    prompt = ANALYZE_PROMPT + reviews_csv

    client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1/responses")
    response = client.chat.completions.create(
        model="grok-4",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def get_market_analysis_from_file_deep_seek():
    api_key = os.getenv("DEEP_SEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEP_SEEK_API_KEY is not set in environment variables.")

    # get the file path for the reviews excel file
    save_pain_to_excel()

    out_file = get_output_dir() / "pain_reviews.xlsx"
    if not out_file.exists():
            raise FileNotFoundError(f"Reviews file not found: {out_file}")
    
    reviews_csv = pd.read_excel(out_file).to_csv(index=False)[:MAX_CHARS]
    prompt = ANALYZE_PROMPT + reviews_csv

    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content