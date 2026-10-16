
def show_scraped_data(scraped_data, st):
    column_configuration = {
        "title": st.column_config.TextColumn("Name", width="medium"),
        "developer": st.column_config.TextColumn("Developer", width="medium"),
        "icon": st.column_config.ImageColumn("Icon", width="small"),
        "appId": st.column_config.TextColumn("Package Name", width="medium"),
        "score":  st.column_config.NumberColumn("Star Rating", format="%.1f ⭐"),
    }

    # show the scraped data in a dataframe with the specified column configuration
    event = st.dataframe(
        scraped_data,
        column_config=column_configuration,
        column_order=[c for c in column_configuration if c in scraped_data.columns],
        hide_index=True,
        use_container_width=True,
        on_select="rerun",             
        selection_mode="multi-row",     
        key="results_table",
    )

    selected_rows = event.selection.rows            # list of row positions, e.g. [0, 3]
    return scraped_data.iloc[selected_rows]  
