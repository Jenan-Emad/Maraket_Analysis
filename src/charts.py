import plotly.express as px
from write_methods.get_path import get_output_dir
SENTIMENT_COL = "review_category"
COLOR_MAP = {"positive": "#2ecc71", "neutral": "#f1c40f", "negative": "#e74c3c"}


def apply_charts(st, pd):
    OUTPUT_DIR = get_output_dir()
    out_file = OUTPUT_DIR / "all_tables.xlsx"
    sheets = pd.read_excel(out_file, sheet_name=None)  # dict: {sheet name: DataFrame}

    for name, df in sheets.items():
        if "score" not in df.columns or SENTIMENT_COL not in df.columns:
            continue

        # make labels lowercase so they match COLOR_MAP keys
        df = df.copy()
        df[SENTIMENT_COL] = df[SENTIMENT_COL].astype(str).str.lower()

        st.subheader(name)
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.subheader("stars distribution")
            fig_bar = px.histogram(
                df,
                x="score",
                color=SENTIMENT_COL,
                color_discrete_map=COLOR_MAP,
                labels={"score": "starts numbers", "count": "count"}
            )
            fig_bar.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_bar, use_container_width=True) 

        with chart_col2:
            st.subheader("acceptance percentage")
            fig_pie = px.pie(
                df,
                names=SENTIMENT_COL,
                hole=0.4,
                color=SENTIMENT_COL,
                color_discrete_map=COLOR_MAP
            )
            fig_pie.update_layout(height=350, margin=dict(l=10, r=10, t=10, b=10))
            st.plotly_chart(fig_pie, use_container_width=True)  


def apply_charts_2(st, pd):
    OUTPUT_DIR = get_output_dir()
    out_file = OUTPUT_DIR / "all_tables.xlsx"
    sheets = pd.read_excel(out_file, sheet_name=None) 

    names = list(sheets.keys())

    for i in range(0, len(names), 2):          # step through the sheets 2 at a time
        cols = st.columns(2)                    # two equal columns
        for col, name in zip(cols, names[i:i + 2]):
            df = sheets[name]
            fig = px.bar(df, x=df.columns[0], y=df.columns[1], title=name)
            col.plotly_chart(fig, use_container_width=True)