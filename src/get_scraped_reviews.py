from cleaning.cleaning import clean_reviews_data
from scraping.scraping_reviews import scrape_market_reviews
from write_methods.creating_db import warehouse_database_operations, drop_all_old_tables


def get_scraped_reviews(list_of_apps, st, pd):
    all_reviews = pd.DataFrame()  # Initialize an empty DataFrame to store all reviews

    for index, app in list_of_apps.iterrows():
        app_id = app['appId']
        app_name = app['title']
        st.write(f"Fetching reviews for {app_name} (App ID: {app_id})...")
        
        # Call the scrape_market_reviews function to get reviews for the current app
        reviews = scrape_market_reviews(app_id)
        
        if not reviews.empty:
            # Convert the list of reviews to a DataFrame
            reviews_df = pd.DataFrame(reviews)
            reviews_df['appId'] = app_id  # Add a column for the app ID
            reviews_df['appName'] = app_name  # Add a column for the app name

            #clean the reviews data
            cleaned_reviews_df = clean_reviews_data(reviews_df)
            
            # save the cleaned reviews data to the database
            warehouse_database_operations(cleaned_reviews_df, table_name=f"reviews_{app_id}")
        else:
            st.warning(f"No reviews found for {app_name} (App ID: {app_id}).")

    return all_reviews

