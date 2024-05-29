import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import re
import nltk
from nltk.util import ngrams
from nltk import word_tokenize
from collections import Counter
import string
from scipy import stats
import os
import ssl
import argparse

# Ensure necessary NLTK resources are downloaded
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt')

def get_filename():
    parser = argparse.ArgumentParser(description='Process some CSV files.')
    parser.add_argument('filename', type=str, help='The filename of the CSV (with extension)')
    parser.add_argument('foldername', type=str, help='The name of the folder')
    args = parser.parse_args()
    return args.filename, args.foldername

def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def load_data(filename):
    return pd.read_csv(filename)

def preprocess_review(review):
    if pd.isnull(review):
        review = ''  # Convert NaN to empty string
    review = str(review)  # Ensure all inputs are treated as strings
    review = re.sub(r"\(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} 에 등록된 네이버 페이 구매평\)", "", review)
    review = review.replace("쇼핑몰 추천 리뷰", "")
    if review.startswith("NEW"):
        review = review[3:]  # Remove the first three characters assumed to be "NEW"
    review = review.lower()
    review = review.translate(str.maketrans('', '', string.punctuation))
    return review

def find_common_phrases(reviews, min_length=3, min_freq=3):
    phrases = Counter()
    for review in reviews:
        tokens = word_tokenize(review)
        for n in range(min_length, 6):  # Analyze up to 5-grams
            for gram in ngrams(tokens, n):
                phrases[gram] += 1
    return {phrase: freq for phrase, freq in phrases.items() if freq >= min_freq}

def contains_common_phrase(review, common_phrases):
    tokens = word_tokenize(review)
    for n in range(3, 6):
        for gram in ngrams(tokens, n):
            if gram in common_phrases:
                return True
    return False

def main():
    input_filename, foldername = get_filename()
    filename = os.path.join(f'./{foldername}_Collected_Reviews', input_filename)
    company_name = input_filename.split('.')[0]
    folder_path = f'./results/{company_name}'
    
    create_folder(folder_path)
    
    df = load_data(filename)
    df['review_content'] = df['review_content'].astype(str)
    df['cleaned_review_content'] = df['review_content'].apply(preprocess_review)
    
    common_phrases = find_common_phrases(df['cleaned_review_content'])
    df['contains_common_phrase'] = df['cleaned_review_content'].apply(lambda x: contains_common_phrase(x, common_phrases))
    
    ratings_with_phrases = round(df[df['contains_common_phrase']]['rating'].mean(), 2)
    ratings_without_phrases = round(df[~df['contains_common_phrase']]['rating'].mean(), 2)
    
    print("Average rating for reviews containing common phrases: ", ratings_with_phrases)
    print("Average rating for reviews not containing common phrases: ", ratings_without_phrases)
    
    percentage_of_review_w_common_phrases = df[df['contains_common_phrase']].shape[0] / df.shape[0]
    percentage_of_review_w_common_phrases = "%0.2f" % (percentage_of_review_w_common_phrases * 100)
    print(percentage_of_review_w_common_phrases)
    
    t_stat, p_value = stats.ttest_ind(df[df['contains_common_phrase']]['rating'], df[~df['contains_common_phrase']]['rating'], equal_var=False)
    print(f"T-statistic: {t_stat}, P-value: {p_value}")
    
    results_df = pd.DataFrame({
        'company_name': [company_name],
        'product_name': [df['product_name'].iloc[0]],
        'ratings_with_phrases': [ratings_with_phrases],
        'ratings_without_phrases': [ratings_without_phrases],
        'percentage_of_review_w_common_phrases': [percentage_of_review_w_common_phrases]
    })
    
    output_filename = f"{company_name}_phrase_repetition.csv"
    output_path = os.path.join(folder_path, output_filename)
    results_df.to_csv(output_path, index=False)
    print(f"CSV file saved to {output_path}")
    
    avg_ratings = {
        'With Repetitive Phrases': ratings_with_phrases,
        'Without Repetitive Phrases': ratings_without_phrases
    }
    
    # Check for NaN or Inf values in the average ratings
    min_rating = min([v for v in avg_ratings.values() if pd.notnull(v) and np.isfinite(v)], default=0)
    max_rating = max([v for v in avg_ratings.values() if pd.notnull(v) and np.isfinite(v)], default=5)

    plt.figure(figsize=(10, 6))
    plt.bar(avg_ratings.keys(), avg_ratings.values(), color=['red', 'green'])
    plt.xlabel('Review Category')
    plt.ylabel('Average Rating')
    plt.title(f'{company_name} Average Ratings: With vs Without Repetitive Phrases')
    plt.ylim([min_rating - 0.5, max_rating + 0.5])
    avg_ratings_filename = f"{company_name}_Average_Ratings_With_vs_Without_Repetitive_Phrases.png"
    avg_ratings_path = os.path.join(folder_path, avg_ratings_filename)
    plt.savefig(avg_ratings_path)
    plt.close()
    print(f"Average Ratings visualization saved to {avg_ratings_path}")
    
    ratings_with = df[df['contains_common_phrase']]['rating']
    ratings_without = df[~df['contains_common_phrase']]['rating']
    
    plt.figure(figsize=(10, 6))
    plt.hist(ratings_with, bins=np.arange(0.5, 5.6, 0.5), alpha=0.5, label='With Repetitive Phrases', color='red')
    plt.hist(ratings_without, bins=np.arange(0.5, 5.6, 0.5), alpha=0.5, label='Without Repetitive Phrases', color='green')
    plt.title(f'{company_name} Distribution of Ratings With vs Without Repetitive Phrases')
    plt.xlabel('Rating')
    plt.ylabel('Frequency')
    plt.legend()
    distribution_filename = f"{company_name}_Distribution_of_Ratings_With_vs_Without_Repetitive_Phrases.png"
    distribution_path = os.path.join(folder_path, distribution_filename)
    plt.savefig(distribution_path)
    plt.close()
    print(f"Distribution of Ratings visualization saved to {distribution_path}")

if __name__ == "__main__":
    main()
