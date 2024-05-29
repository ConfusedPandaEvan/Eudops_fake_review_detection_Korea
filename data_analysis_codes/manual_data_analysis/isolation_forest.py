import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
import os

def get_filename():
    filename = input('Enter the filename of the CSV (with extension): ')
    foldername = input('Enter the foldername file: ')
    return filename, foldername

def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def load_data(filename):
    return pd.read_csv(filename)

def preprocess_data(df):
    df['review_date'] = pd.to_datetime(df['review_date'])
    return df

def compute_daily_reviews(df):
    daily_reviews = df.groupby('review_date').size().reset_index(name='review_count')
    return daily_reviews

def compute_rolling_mean(daily_reviews, window=3):
    daily_reviews['rolling_mean'] = daily_reviews['review_count'].rolling(window=window).mean().fillna(0)
    return daily_reviews

def detect_anomalies(daily_reviews):
    X = daily_reviews[['review_count', 'rolling_mean']]
    model = IsolationForest(contamination=0.05)
    model.fit(X)
    daily_reviews['anomaly'] = model.predict(X)
    daily_reviews['anomaly'] = daily_reviews['anomaly'].map({1: 0, -1: 1})
    return daily_reviews

def calculate_statistics(df, daily_reviews):
    high_review_dates = daily_reviews[daily_reviews['anomaly'] == 1]['review_date']
    anomalies = df[df['review_date'].isin(high_review_dates)]
    non_anomalies = df[~df['review_date'].isin(high_review_dates)]
    avg_rating_anomalies = anomalies['rating'].mean()
    avg_rating_non_anomalies = non_anomalies['rating'].mean()
    percentage_anomalies = (len(high_review_dates) / len(daily_reviews)) * 100
    return avg_rating_anomalies, avg_rating_non_anomalies, percentage_anomalies, high_review_dates

def plot_results(daily_reviews, high_review_dates, company_name, folder_path):
    plt.figure(figsize=(14, 7))
    plt.plot(daily_reviews['review_date'], daily_reviews['review_count'], label='Review Count')
    plt.plot(daily_reviews['review_date'], daily_reviews['rolling_mean'], color='orange', label='Rolling Mean')
    plt.scatter(high_review_dates, daily_reviews.loc[daily_reviews['review_date'].isin(high_review_dates), 'review_count'], 
                color='red', label='Anomaly', marker='x')
    plt.xlabel('Date')
    plt.ylabel('Number of Reviews')
    plt.title(f'{company_name} Review Counts and Anomalies')
    plt.legend()

    anomaly_plot_filename = f"{company_name}_Review_Counts_Anomalies.png"
    anomaly_plot_path = os.path.join(folder_path, anomaly_plot_filename)
    plt.savefig(anomaly_plot_path)
    plt.close()
    print(f"Anomaly detection plot saved to {anomaly_plot_path}")

def save_results(company_name, product_name, avg_rating_anomalies, avg_rating_non_anomalies, percentage_anomalies, folder_path):
    results_df = pd.DataFrame({
        'company_name': [company_name],
        'product_name': [product_name],
        'avg_rating_anomalies': [round(avg_rating_anomalies, 2)],
        'avg_rating_non_anomalies': [round(avg_rating_non_anomalies, 2)],
        'percentage_anomalies': [round(percentage_anomalies, 2)]
    })
    anomaly_data_filename = f"{company_name}_Anomalies.csv"
    anomaly_data_path = os.path.join(folder_path, anomaly_data_filename)
    results_df.to_csv(anomaly_data_path, index=False)
    print(f"Anomaly data saved to {anomaly_data_path}")

def main():
    input_filename, foldername = get_filename()
    filename = os.path.join(f'./{foldername}_Collected_Reviews', input_filename)
    company_name = input_filename.split('.')[0]
    folder_path = f'./results/{company_name}'
    create_folder(folder_path)
    
    df = load_data(filename)
    df = preprocess_data(df)
    daily_reviews = compute_daily_reviews(df)
    daily_reviews = compute_rolling_mean(daily_reviews)
    daily_reviews = detect_anomalies(daily_reviews)
    
    avg_rating_anomalies, avg_rating_non_anomalies, percentage_anomalies, high_review_dates = calculate_statistics(df, daily_reviews)
    
    plot_results(daily_reviews, high_review_dates, company_name, folder_path)
    product_name = df['product_name'].iloc[0],
    save_results(company_name, product_name, avg_rating_anomalies, avg_rating_non_anomalies, percentage_anomalies, folder_path)

if __name__ == "__main__":
    main()
