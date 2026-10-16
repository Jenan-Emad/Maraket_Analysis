import pandas as pd

def clean_reviews_data(reviews_df):

    reviews_df = reviews_df.drop_duplicates(subset=['reviewId', 'appId'])  
    reviews_df['content'] = reviews_df['content'].fillna('No comment provided').str.strip().str.title()
    reviews_df['at'] = pd.to_datetime(reviews_df['at'])
    reviews_df['Review_Year'] = reviews_df['at'].dt.year
    reviews_df['score'] = pd.to_numeric(reviews_df['score'], errors='coerce')
    
    reviews_df['review_category'] = reviews_df['score'].apply(categorize_review)
        
    return reviews_df



def categorize_review(score):
    if score >= 4:
        return 'Positive'
    elif score == 3:
        return 'Neutral'
    else:
        return 'Negative'