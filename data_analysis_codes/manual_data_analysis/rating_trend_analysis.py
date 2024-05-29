import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import os
import math

def get_filename():
    filename = input('Enter the filename of the CSV (with extension): ')
    foldername = input('Enter the foldername file: ')
    return filename, foldername

def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def load_and_preprocess_data(filename):
    df = pd.read_csv(filename)
    df['review_date'] = pd.to_datetime(df['review_date']).dt.date
    return df

def get_review_counts(df):
    review_counts = df.groupby(df['review_date']).size()
    review_counts_df = pd.DataFrame({'review_date': review_counts.index, 'review_count': review_counts.values})
    review_counts_df['review_date'] = pd.to_datetime(review_counts_df['review_date'])
    return review_counts_df

def add_missing_dates(review_counts_df):
    min_date = review_counts_df['review_date'].min()
    max_date = review_counts_df['review_date'].max()
    all_dates = pd.date_range(start=min_date, end=max_date)
    missing_dates = all_dates[~all_dates.isin(review_counts_df['review_date'])]
    missing_df = pd.DataFrame({'review_date': missing_dates, 'review_count': 0})
    review_counts_df = pd.concat([review_counts_df, missing_df]).sort_values(by='review_date')
    return review_counts_df

def fit_poisson_model(review_counts_df):
    X = sm.add_constant(np.arange(len(review_counts_df)))
    y = review_counts_df['review_count']
    poisson_model = sm.GLM(y, X, family=sm.families.Poisson()).fit()
    return poisson_model

def plot_avg_ratings(avg_ratings_higher_than_max, avg_ratings_lower_than_max, company_name, folder_path):
    plt.figure(figsize=(10, 6))
    plt.bar(['High Volume Dates', 'Not High Volume Dates'], [avg_ratings_higher_than_max, avg_ratings_lower_than_max], color=['red', 'green'])
    plt.xlabel('Date Category')
    plt.ylabel('Average Rating')
    plt.title(f'{company_name} Average Ratings from Different Date Categories')
    plt.ylim(0.5, 5.0)
    avg_ratings_filename = f"{company_name}_Average_Ratings_from_Different_Date_Categories.png"
    avg_ratings_path = os.path.join(folder_path, avg_ratings_filename)
    plt.savefig(avg_ratings_path)
    plt.close()
    print(f"Average Ratings visualization saved to {avg_ratings_path}")

def plot_review_counts(dates_higher_than_max, dates_lower_than_max, max_reviews_per_day, company_name, folder_path):
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(dates_higher_than_max['review_date'], dates_higher_than_max['review_count'], color='blue', label='High Volume Dates', width=5)
    ax.bar(dates_lower_than_max['review_date'], dates_lower_than_max['review_count'], color='red', label='Not High Volume Dates', width=5)
    ax.xaxis.set_major_locator(plt.MaxNLocator(15))
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: pd.to_datetime(x, unit='D').strftime('%Y-%m')))
    plt.xticks(rotation=45)
    plt.axhline(y=max_reviews_per_day, color='green', linestyle='--', label='Max #Review on Random Date')
    plt.xlabel('Date')
    plt.ylabel('Review Count')
    plt.title(f'{company_name} Review Counts Comparison')
    plt.legend()
    plt.tight_layout()
    review_counts_filename = f"{company_name}_Review_Counts_Comparison.png"
    review_counts_path = os.path.join(folder_path, review_counts_filename)
    plt.savefig(review_counts_path)
    plt.close()
    print(f"Review Counts Comparison visualization saved to {review_counts_path}")

def save_results(results_df, company_name, folder_path):
    output_filename = f"{company_name}_rating_trend.csv"
    output_path = os.path.join(folder_path, output_filename)
    results_df.to_csv(output_path, index=False)
    print(f"CSV file saved to {output_path}")

def main():
    input_filename, foldername = get_filename()
    filename = os.path.join(f'./{foldername}_Collected_Reviews', input_filename)
    company_name = input_filename.split('.')[0]
    folder_path = f'./results/{company_name}'
    
    create_folder(folder_path)
    
    df = load_and_preprocess_data(filename)
    
    earliest_date = df['review_date'].min()
    latest_date = df['review_date'].max()
    days_diff = (latest_date - earliest_date).days
    print(f"days_diff: {days_diff}")
    
    review_counts_df = get_review_counts(df)
    review_counts_df = add_missing_dates(review_counts_df)
    
    #Calculate the maximum review count per day based on poisson regression model. The ceiling makes the analysis more lenient, but is needed for dataset with overall low review counts
    poisson_model = fit_poisson_model(review_counts_df)
    max_reviews_per_day = math.ceil(poisson_model.mu.max())
    print(f"max_reviews_per_day: {max_reviews_per_day}")
    
    dates_higher_than_max = review_counts_df[review_counts_df['review_count'] > max_reviews_per_day].copy()
    dates_higher_than_max['review_date'] = dates_higher_than_max['review_date'].dt.date
    
    dates_lower_than_max = review_counts_df[review_counts_df['review_count'] <= max_reviews_per_day].copy()
    dates_lower_than_max['review_date'] = dates_lower_than_max['review_date'].dt.date
    
    num_dates_higher_than_max = len(dates_higher_than_max)
    print(f"num_dates_higher_than_max{num_dates_higher_than_max}")
    
    total_reviews_higher_than_max = dates_higher_than_max['review_count'].sum()
    print(f"total_reviews_higher_than_max: {total_reviews_higher_than_max}")
    
    high_volume_review_percentage = total_reviews_higher_than_max / len(df) * 100
    print(f"high_volume_review_percentage: {high_volume_review_percentage}")
    
    reviews_higher_than_max = df[df['review_date'].isin(dates_higher_than_max['review_date'])]
    reviews_lower_than_max = df[~df['review_date'].isin(dates_higher_than_max['review_date'])]
    
    avg_ratings_higher_than_max = reviews_higher_than_max['rating'].mean()
    avg_ratings_lower_than_max = reviews_lower_than_max['rating'].mean()
    print(f"avg_ratings_higher_than_max: {avg_ratings_higher_than_max}")
    print(f"avg_ratings_lower_than_max: {avg_ratings_lower_than_max}")
    
    plot_avg_ratings(avg_ratings_higher_than_max, avg_ratings_lower_than_max, company_name, folder_path)
    plot_review_counts(dates_higher_than_max, dates_lower_than_max, max_reviews_per_day, company_name, folder_path)
    
    results_df = pd.DataFrame({
        'company_name': [company_name],
        'product_name': [df['product_name'].iloc[0]],
        'days_diff': [days_diff],
        'max_reviews_per_day': [max_reviews_per_day],
        'num_dates_higher_than_max': [num_dates_higher_than_max],
        'total_reviews_higher_than_max': [total_reviews_higher_than_max],
        'high_volume_review_percentage': [round(high_volume_review_percentage, 2)],
        'avg_ratings_higher_than_max': [round(avg_ratings_higher_than_max, 2)],
        'avg_ratings_lower_than_max': [round(avg_ratings_lower_than_max, 2)]
    })
    
    save_results(results_df, company_name, folder_path)

if __name__ == "__main__":
    main()