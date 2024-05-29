import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
import os
import argparse

def get_filename():
    parser = argparse.ArgumentParser(description='Process some CSV files.')
    parser.add_argument('filename', type=str, help='The filename of the CSV (with extension)')
    parser.add_argument('foldername', type=str, help='The name of the folder')
    args = parser.parse_args()
    return args.filename, args.foldername

def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def preprocess_review(review):
    review = re.sub(r"\(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} 에 등록된 네이버 페이 구매평\)", "", review)
    review = review.replace("쇼핑몰 추천 리뷰", "")
    return review

def load_data(filename):
    return pd.read_csv(filename)

def clean_data(df):
    total_reviews = df.shape[0]
    print(f"Total reviews: {total_reviews}")

    df = df.dropna(subset=['review_content'])
    print(f"Non-NaN reviews: {df.shape[0]}")

    df.loc[:, 'review_content'] = df['review_content'].apply(preprocess_review)
    df.loc[:, 'rating'] = pd.to_numeric(df['rating'], errors='coerce')
    df = df.dropna(subset=['rating'])
    
    return df, total_reviews

def analyze_data(df):
    df['is_duplicate'] = df.duplicated('review_content', keep=False)
    avg_ratings_unique = df[~df['is_duplicate']]['rating'].mean()
    avg_ratings_non_unique = df[df['is_duplicate']]['rating'].mean()
    non_unique_reviews = df['is_duplicate'].sum()
    
    return avg_ratings_unique, avg_ratings_non_unique, non_unique_reviews

def calculate_percentage(non_unique_reviews, total_reviews):
    return (non_unique_reviews / total_reviews) * 100

def plot_bar_chart(avg_ratings, bar_chart_path):
    plt.figure(figsize=(10, 6))
    plt.bar(avg_ratings.keys(), avg_ratings.values(), color=['blue', 'orange'])
    plt.xlabel('Review Category')
    plt.ylabel('Average Rating')
    plt.title('Average Ratings: Unique vs Non-Unique Reviews')
    plt.ylim([min(avg_ratings.values()) - 0.5, max(avg_ratings.values()) + 0.5])
    plt.savefig(bar_chart_path)
    plt.close()

def plot_histogram(df, histogram_path):
    plt.figure(figsize=(10, 6))
    plt.hist(df[~df['is_duplicate']]['rating'], bins=np.arange(1, 6, 0.5), alpha=0.5, label='Unique Reviews', color='blue')
    plt.hist(df[df['is_duplicate']]['rating'], bins=np.arange(1, 6, 0.5), alpha=0.5, label='Non-Unique Reviews', color='orange')
    plt.title('Histogram of Ratings for Unique vs Non-Unique Reviews')
    plt.xlabel('Rating')
    plt.ylabel('Count')
    plt.legend()
    plt.savefig(histogram_path)
    plt.close()

def save_results(results_df, output_path):
    results_df.to_csv(output_path, index=False)

def main():
    input_filename, foldername = get_filename()
    filename = os.path.join(f'./{foldername}_Collected_Reviews', input_filename)
    folder_path = f'./results/{input_filename.split(".")[0]}'
    
    create_folder(folder_path)

    df = load_data(filename)
    company_name = input_filename.split('.')[0]

    df, total_reviews = clean_data(df)
    avg_ratings_unique, avg_ratings_non_unique, non_unique_reviews = analyze_data(df)
    percentage_non_unique = calculate_percentage(non_unique_reviews, total_reviews)

    print(f"Average rating for unique reviews: {avg_ratings_unique:.2f}")
    print(f"Average rating for non-unique (duplicate) reviews: {avg_ratings_non_unique:.2f}")
    print(f"Percentage of non-unique reviews: {percentage_non_unique:.2f}%")

    avg_ratings = {
        'unique_reviews': avg_ratings_unique,
        'non_unique_reviews': avg_ratings_non_unique
    }

    bar_chart_filename = f"{company_name}_Average_Ratings_Unique_vs_Non-Unique_Reviews.png"
    bar_chart_path = os.path.join(folder_path, bar_chart_filename)
    plot_bar_chart(avg_ratings, bar_chart_path)

    histogram_filename = f"{company_name}_Histogram_of_Ratings_Unique_vs_Non-Unique_Reviews.png"
    histogram_path = os.path.join(folder_path, histogram_filename)
    plot_histogram(df, histogram_path)

    results_df = pd.DataFrame({
        'company_name': [company_name],
        'product_name': [df['product_name'].iloc[0]],
        'avg_ratings_unique': [round(avg_ratings_unique, 2)],
        'avg_ratings_non_unique': [round(avg_ratings_non_unique, 2)],
        'percentage_non_unique': [round(percentage_non_unique, 2)]
    })

    output_filename = f"{company_name}_unique_nonunique.csv"
    output_path = os.path.join(folder_path, output_filename)
    save_results(results_df, output_path)

    print(f"CSV file saved to {output_path}")
    print(f"Bar chart saved to {bar_chart_path}")
    print(f"Histogram saved to {histogram_path}")

if __name__ == "__main__":
    main()
