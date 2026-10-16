import sys
from pathlib import Path
import pandas as pd
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))
from market_ai1 import get_market_analysis_from_file
from scraping.scraping_apps import scrape_market_apps
from get_scraped_data import show_scraped_data
from get_scraped_reviews import get_scraped_reviews
from write_methods.creating_db import drop_all_old_tables
from write_methods.save_to_excel import save_to_excel
from write_methods.get_path import get_output_dir, get_dp_path
from charts import apply_charts

st.set_page_config(page_title="Competitor Intelligence", page_icon="📊", layout="wide")

# ---------- state & cache ----------
ss = st.session_state
ss.setdefault("query", "")
ss.setdefault("done", False)
ss.setdefault("summary", None)


@st.cache_data(ttl=3600, show_spinner="Searching Google Play...")
def search(query):
    return scrape_market_apps(query)


# ---------- sidebar: search ----------
with st.sidebar:
    st.header("🔎 Search")
    with st.form("search_form"):
        q = st.text_input("App name or niche", placeholder="e.g. food delivery")
        submitted = st.form_submit_button("Search", use_container_width=True)
    if submitted and q:
        ss.query = q
        ss.done = False
        ss.summary = None
    st.caption("Select 2–4 apps, then run the analysis.")

# ---------- main ----------
st.title("📊 Competitor Intelligence")
st.caption("Compare Google Play competitors and find gaps in the market.")

if not ss.query:
    st.info("👈 Start by searching for an app or a niche in the sidebar.")
    st.stop()

tab_select, tab_results = st.tabs(["1️⃣ Select apps", "2️⃣ Results"])

with tab_select:
    try:
        scraped = search(ss.query)
        checked_apps = show_scraped_data(scraped_data=scraped, st=st)
    except Exception as e:
        st.error(f"Search failed: {e}")
        st.stop()

    n = len(checked_apps)
    valid = 2 <= n <= 4
    st.write(f"**Selected:** {n} / 4")
    if not valid:
        st.warning("Please select between 2 and 4 apps.")

    if st.button("🚀 Scrape & Analyze", type="primary", disabled=not valid):
        try:
            with st.status("Working...", expanded=True) as status:
                st.write("Cleaning old data...")
                drop_all_old_tables()
                st.write("Scraping reviews...")
                get_scraped_reviews(checked_apps, st, pd)
                st.write("Building Excel report...")
                save_to_excel()
                st.write("Generating AI insights...")
                ss.summary = get_market_analysis_from_file()
                status.update(label="Done ✅", state="complete", expanded=False)
            ss.done = True
            st.success("Analysis ready. Open the **Results** tab.")
        except Exception as e:
            st.error(f"Something went wrong: {e}")

with tab_results:
    if not ss.done:
        st.info("Run the analysis in the first tab to see results here.")
    else:
        apply_charts(st, pd)

        st.divider()
        st.subheader("🧠 AI Market Gap Analysis")
        st.markdown(ss.summary)

        st.divider()
        excel_path = Path(get_output_dir()) / "all_tables.xlsx"   # use your own path helper
        with open(excel_path, "rb") as f:
            st.download_button("📥 Download Excel report", f,
                               file_name="competitor_report.xlsx",
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")