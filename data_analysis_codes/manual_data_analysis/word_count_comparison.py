import pandas as pd
import plotly.graph_objects as go
import os
import string
import re

def get_filename():
    filename = input('Enter the filename of the CSV (with extension): ')
    foldername = input('Enter the foldername file: ')
    return filename, foldername

def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def preprocess_review(review):
    if pd.isnull(review) or review == 'N/A':
        review = ''  # Convert NaN or 'N/A' to empty string
    review = str(review)  # Ensure all inputs are treated as strings
    review = re.sub(r"\(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} 에 등록된 네이버 페이 구매평\)", "", review)
    review = review.replace("쇼핑몰 추천 리뷰", "")
    if review.startswith("NEW"):
        review = review[3:]  # Remove the first three characters assumed to be "NEW"
    review = review.lower()
    review = review.translate(str.maketrans('', '', string.punctuation))
    return review

def load_and_preprocess_data(filename):
    df = pd.read_csv(filename)
    df['review_content'] = df['review_content'].astype(str)
    df['cleaned_review_content'] = df['review_content'].apply(preprocess_review)
    return df

def remove_empty_reviews(df):
    # print(f"Total reviews before removing empty: {len(df)}")
    
    # Remove reviews with 0 word count
    filtered_df = df[df['cleaned_review_content'] != 'nan'].copy()

    filtered_df['review_content_length'] = filtered_df['cleaned_review_content'].str.split().str.len()
    # print(f"Total reviews after removing empty: {len(filtered_df)}")

    return filtered_df

def plot_word_count_distribution(df, company_name, folder_path):
    if 'review_date' in df.columns and df['review_date'].notna().any():
        df['review_date'] = pd.to_datetime(df['review_date'])
        
        bins = [1, 5, 15, 25, 40, 65, 100, 200, float('inf')]
        labels = ['1-5 words', '6-15 words', '16-25 words', '26-40 words', '41-65 words', '66-100 words', '101-200 words', '201+ words']
        df['word_count_range'] = pd.cut(df['review_content_length'], bins=bins, labels=labels, right=False)
        
        word_count_distribution = df['word_count_range'].value_counts(normalize=True) * 100
        word_count_distribution = word_count_distribution.reindex(labels)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=labels, y=word_count_distribution, fill='tozeroy', name='This Product'))
        
        fig.update_layout(
            title={
                'text': f'{company_name} Word Count Comparison',
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis_title='Word Count Ranges',
            yaxis_title='Percentage of Reviews',
            hovermode='x',
            font=dict(family="Nanum Gothic, sans-serif")
        )
        
        interactive_plot_filename = f"{company_name}_Word_Count_Comparison.html"
        interactive_plot_path = os.path.join(folder_path, interactive_plot_filename)
        fig.write_html(interactive_plot_path)
        print(f"Interactive plot saved to {interactive_plot_path}")
        
        static_plot_filename = f"{company_name}_Word_Count_Comparison.png"
        static_plot_path = os.path.join(folder_path, static_plot_filename)
        fig.write_image(static_plot_path)
        print(f"Static plot saved to {static_plot_path}")
    else:
        print("Date column is missing or contains no valid dates.")

def main():
    input_filename, foldername = get_filename()
    filename = os.path.join(f'./{foldername}_Collected_Reviews', input_filename)
    company_name = input_filename.split('.')[0]
    folder_path = f'./results/{company_name}'
    
    create_folder(folder_path)
    df = load_and_preprocess_data(filename)
    df = remove_empty_reviews(df)
    
    plot_word_count_distribution(df, company_name, folder_path)

if __name__ == "__main__":
    main()
