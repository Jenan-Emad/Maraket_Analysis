"""Dashboard charts for the competitor intelligence app.

Reads all_tables.xlsx, combines every reviews sheet, and renders:
  Overview    -> KPI cards, sentiment share, average rating, star distribution, reply rate
  Trends      -> rating over time, release (app version) impact
  Pain points -> most mentioned words in 1-2 star reviews, most helpful negative reviews
"""
import re
from collections import Counter

import pandas as pd
import plotly.express as px

from write_methods.get_path import get_output_dir

SENTIMENT_COL = "review_category"
SENTIMENT_ORDER = ["negative", "neutral", "positive"]
COLOR_MAP = {"positive": "#10b981", "neutral": "#fbbf24", "negative": "#ef4444"}
APP_PALETTE = ["#6366f1", "#06b6d4", "#f97316", "#ec4899", "#84cc16", "#a855f7"]

STOPWORDS = set("""
the and for that this with you your not but are was were have has had its it's i'm i've dont don't cant can't
can will would could should from they them their there then than when what which who whom while about after
before just very really much more most some any all out one two get got getting also even only too still
again always never every each been being into over under here where why how because since until
app apps application please use using used time times thing things like need want make made good bad
update updates updated version well now new old lot even though around back keep going doesn't didn't
isn't wasn't won't wont does did doing done etc
""".split())


# --------------------------------------------------------------------------- data
def load_reviews():
    """Combine every sheet that looks like a reviews table into one DataFrame."""
    path = get_output_dir() / "all_tables.xlsx"
    sheets = pd.read_excel(path, sheet_name=None)

    frames = []
    for name, df in sheets.items():
        if "score" in df.columns and SENTIMENT_COL in df.columns:
            d = df.copy()
            if "appName" not in d.columns:
                d["appName"] = d["appId"] if "appId" in d.columns else name
            frames.append(d)
    if not frames:
        return None

    df = pd.concat(frames, ignore_index=True)
    if "reviewId" in df.columns:
        df = df.drop_duplicates(subset="reviewId")

    df["appName"] = df["appName"].astype(str)
    df["score"] = pd.to_numeric(df["score"], errors="coerce")
    df = df.dropna(subset=["score"])

    # normalise sentiment labels; fall back to star rating if labels are unexpected
    df[SENTIMENT_COL] = df[SENTIMENT_COL].astype(str).str.lower().str.strip()
    if not set(df[SENTIMENT_COL]).issubset(COLOR_MAP):
        df[SENTIMENT_COL] = df["score"].apply(
            lambda s: "negative" if s <= 2 else ("neutral" if s == 3 else "positive"))

    if "at" in df.columns:
        df["at"] = pd.to_datetime(df["at"], errors="coerce")
    return df


# --------------------------------------------------------------------------- styling
def _style(fig, height=360, title=None):
    fig.update_layout(
        height=height,
        title=dict(text=title, font=dict(size=15), x=0, xanchor="left") if title else None,
        margin=dict(l=10, r=10, t=60 if title else 20, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title=None),
        bargap=0.25,
        hoverlabel=dict(font_size=12),
    )
    fig.update_xaxes(showgrid=False, title=None)
    fig.update_yaxes(gridcolor="rgba(128,128,128,0.2)", title=None)
    return fig


def _app_colors(df):
    apps = sorted(df["appName"].unique())
    return {a: APP_PALETTE[i % len(APP_PALETTE)] for i, a in enumerate(apps)}


# --------------------------------------------------------------------------- figures
def sentiment_share_fig(df):
    counts = df.groupby(["appName", SENTIMENT_COL]).size().reset_index(name="n")
    counts["percent"] = counts["n"] / counts.groupby("appName")["n"].transform("sum") * 100
    fig = px.bar(
        counts, x="percent", y="appName", color=SENTIMENT_COL, orientation="h",
        color_discrete_map=COLOR_MAP, category_orders={SENTIMENT_COL: SENTIMENT_ORDER},
        text="percent", custom_data=["n"],
    )
    fig.update_traces(
        texttemplate="%{x:.0f}%", textposition="inside",
        hovertemplate="%{y}<br>%{fullData.name}: %{x:.1f}% (%{customdata[0]} reviews)<extra></extra>")
    fig.update_layout(barmode="stack")
    fig.update_xaxes(range=[0, 100], ticksuffix="%")
    return _style(fig, title="Sentiment share by app")


def avg_rating_fig(df, colors):
    avg = df.groupby("appName")["score"].agg(avg="mean", n="count").reset_index()
    fig = px.bar(
        avg, x="appName", y="avg", color="appName", color_discrete_map=colors,
        text="avg", custom_data=["n"],
    )
    fig.update_traces(
        texttemplate="%{y:.2f} ★", textposition="outside",
        hovertemplate="%{x}<br>Average: %{y:.2f}<br>Reviews: %{customdata[0]}<extra></extra>")
    fig.add_hline(y=df["score"].mean(), line_dash="dot", line_color="gray",
                  annotation_text="all apps", annotation_position="top left")
    fig.update_yaxes(range=[0, 5.5])
    fig.update_layout(showlegend=False)
    return _style(fig, title="Average rating (scraped reviews)")


def star_distribution_fig(df, colors):
    dist = df.groupby(["appName", "score"]).size().reset_index(name="n")
    dist["percent"] = dist["n"] / dist.groupby("appName")["n"].transform("sum") * 100
    dist["score"] = dist["score"].astype(int).astype(str) + " ★"
    fig = px.bar(
        dist, x="score", y="percent", color="appName", barmode="group",
        color_discrete_map=colors, custom_data=["n"],
        category_orders={"score": [f"{i} ★" for i in range(1, 6)]},
    )
    fig.update_traces(
        hovertemplate="%{fullData.name}<br>%{x}: %{y:.1f}% (%{customdata[0]} reviews)<extra></extra>")
    fig.update_yaxes(ticksuffix="%")
    return _style(fig, title="Star distribution (% of each app's reviews)")


def reply_rate_fig(df, colors):
    if "replyContent" not in df.columns:
        return None
    neg = df[df["score"] <= 2]
    if neg.empty:
        return None
    rate = (neg.assign(replied=neg["replyContent"].notna())
               .groupby("appName")["replied"].agg(rate="mean", n="count").reset_index())
    rate["rate"] *= 100
    fig = px.bar(
        rate, x="appName", y="rate", color="appName", color_discrete_map=colors,
        text="rate", custom_data=["n"],
    )
    fig.update_traces(
        texttemplate="%{y:.0f}%", textposition="outside",
        hovertemplate="%{x}<br>Replied to %{y:.1f}% of %{customdata[0]} negative reviews<extra></extra>")
    fig.update_yaxes(range=[0, 110], ticksuffix="%")
    fig.update_layout(showlegend=False)
    return _style(fig, title="Developer reply rate to 1-2★ reviews")


def rating_trend_fig(df, colors):
    if "at" not in df.columns or df["at"].notna().sum() == 0:
        return None
    d = df.dropna(subset=["at"]).copy()
    d["month"] = d["at"].dt.to_period("M").dt.to_timestamp()
    monthly = d.groupby(["appName", "month"])["score"].agg(avg="mean", n="count").reset_index()
    if monthly["month"].nunique() < 2:
        return None
    fig = px.line(
        monthly, x="month", y="avg", color="appName", markers=True,
        color_discrete_map=colors, custom_data=["n"],
    )
    fig.update_traces(
        hovertemplate="%{fullData.name}<br>%{x|%b %Y}: %{y:.2f} ★ (%{customdata[0]} reviews)<extra></extra>")
    fig.update_yaxes(range=[1, 5])
    return _style(fig, title="Average rating over time (monthly)")


def version_impact_fig(df, app, min_reviews=5, top=10):
    if "appVersion" not in df.columns:
        return None
    d = df[(df["appName"] == app) & df["appVersion"].notna()].copy()
    if d.empty:
        return None
    d["negative"] = d["score"] <= 2
    g = d.groupby("appVersion").agg(n=("score", "count"), neg=("negative", "sum")).reset_index()
    g = g[g["n"] >= min_reviews]
    if g.empty:
        return None
    g["neg_pct"] = g["neg"] / g["n"] * 100
    g = g.sort_values("neg", ascending=False).head(top)
    g["appVersion"] = g["appVersion"].astype(str)
    fig = px.bar(
        g, x="appVersion", y="neg_pct", color="neg_pct", text="neg_pct",
        color_continuous_scale=["#fde68a", "#ef4444"], custom_data=["n", "neg"],
    )
    fig.update_traces(
        texttemplate="%{y:.0f}%", textposition="outside",
        hovertemplate="Version %{x}<br>%{y:.1f}% negative (%{customdata[1]} of %{customdata[0]} reviews)<extra></extra>")
    fig.update_xaxes(type="category")
    fig.update_yaxes(range=[0, 110], ticksuffix="%")
    fig.update_layout(coloraxis_showscale=False)
    return _style(fig, title=f"{app}: versions with the most complaints (min {min_reviews} reviews)")


def keywords_fig(df, app, top=12):
    neg = df[df["score"] <= 2]
    if app != "All apps":
        neg = neg[neg["appName"] == app]
    if neg.empty or "content" not in neg.columns:
        return None
    counter = Counter()
    for text in neg["content"].dropna().astype(str):
        words = re.findall(r"[a-z']{3,}", text.lower())
        counter.update(w.replace("'", "") for w in set(words)
                       if w not in STOPWORDS and w.replace("'", "") not in STOPWORDS)
    common = counter.most_common(top)
    if not common:
        return None
    kw = pd.DataFrame(common, columns=["word", "reviews"]).iloc[::-1]
    fig = px.bar(kw, x="reviews", y="word", orientation="h", text="reviews",
                 color_discrete_sequence=["#ef4444"])
    fig.update_traces(textposition="outside",
                      hovertemplate="%{y}: mentioned in %{x} negative reviews<extra></extra>")
    fig.update_xaxes(showgrid=True, gridcolor="rgba(128,128,128,0.2)")
    fig.update_yaxes(showgrid=False)
    return _style(fig, height=420, title=f"Most mentioned words in 1-2★ reviews ({app})")


# --------------------------------------------------------------------------- page
def apply_charts(st, _pd=None):
    """Render the full dashboard. Signature kept compatible with apply_charts(st, pd)."""
    try:
        df = load_reviews()
    except FileNotFoundError:
        st.warning("No report found yet. Run the analysis first.")
        return
    if df is None or df.empty:
        st.warning("No review data found in the report.")
        return

    colors = _app_colors(df)
    apps = sorted(df["appName"].unique())

    tab_overview, tab_trends, tab_pain = st.tabs(["📌 Overview", "📈 Trends", "🔥 Pain points"])

    # ---- Overview
    with tab_overview:
        avg_by_app = df.groupby("appName")["score"].mean()
        k1, k2, k3, k4 = st.columns(4)
        with k1.container(border=True):
            st.metric("Reviews analysed", f"{len(df):,}")
        with k2.container(border=True):
            st.metric("Average rating", f"{df['score'].mean():.2f} ★")
        with k3.container(border=True):
            st.metric("Negative reviews", f"{(df[SENTIMENT_COL] == 'negative').mean() * 100:.0f}%")
        with k4.container(border=True):
            st.metric("Top rated app", avg_by_app.idxmax(), f"{avg_by_app.max():.2f} ★", delta_color="off")

        c1, c2 = st.columns(2)
        with c1.container(border=True):
            st.plotly_chart(sentiment_share_fig(df), use_container_width=True, key="ch_sentiment")
        with c2.container(border=True):
            st.plotly_chart(avg_rating_fig(df, colors), use_container_width=True, key="ch_avg")

        c3, c4 = st.columns(2)
        with c3.container(border=True):
            st.plotly_chart(star_distribution_fig(df, colors), use_container_width=True, key="ch_stars")
        with c4.container(border=True):
            fig = reply_rate_fig(df, colors)
            if fig:
                st.plotly_chart(fig, use_container_width=True, key="ch_reply")
            else:
                st.info("No developer reply data available.")

    # ---- Trends
    with tab_trends:
        with st.container(border=True):
            fig = rating_trend_fig(df, colors)
            if fig:
                st.plotly_chart(fig, use_container_width=True, key="ch_trend")
            else:
                st.info("Not enough dated reviews to show a trend (need at least 2 months).")

        with st.container(border=True):
            app = st.selectbox("Select an app", apps, key="version_app")
            fig = version_impact_fig(df, app)
            if fig:
                st.plotly_chart(fig, use_container_width=True, key="ch_version")
                st.caption("Spikes can point to a buggy release. Only versions with enough reviews are shown.")
            else:
                st.info("Not enough app-version data for this app.")

    # ---- Pain points
    with tab_pain:
        with st.container(border=True):
            choice = st.selectbox("Focus on", ["All apps"] + apps, key="kw_app")
            fig = keywords_fig(df, choice)
            if fig:
                st.plotly_chart(fig, use_container_width=True, key="ch_keywords")
                st.caption("Counts show how many 1-2★ reviews mention each word.")
            else:
                st.info("No negative reviews to analyse.")

        with st.container(border=True):
            st.markdown("**Most helpful negative reviews** (ranked by thumbs-up votes)")
            neg = df[df["score"] <= 2].copy()
            if "thumbsUpCount" in neg.columns and not neg.empty:
                cols = [c for c in ["appName", "score", "thumbsUpCount", "content", "at"] if c in neg.columns]
                top = neg.sort_values("thumbsUpCount", ascending=False).head(10)[cols]
                st.dataframe(
                    top, hide_index=True, use_container_width=True,
                    column_config={
                        "appName": "App",
                        "score": st.column_config.NumberColumn("Stars", format="%d ★"),
                        "thumbsUpCount": st.column_config.NumberColumn("👍 Votes"),
                        "content": st.column_config.TextColumn("Review", width="large"),
                        "at": st.column_config.DatetimeColumn("Date", format="YYYY-MM-DD"),
                    },
                )
            else:
                st.info("No vote data available.")


# backward compatibility if app.py still imports the old name
apply_charts_2 = apply_charts