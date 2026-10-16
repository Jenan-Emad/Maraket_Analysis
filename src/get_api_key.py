import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()  # locally: reads .env. Online: does nothing, harmlessly

def get_api_key():
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    try:
        return st.secrets["GEMINI_API_KEY"]
    except Exception:
        return None