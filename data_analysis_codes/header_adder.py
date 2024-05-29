# Adds missing headers cuz I was too lazy before

import os
import pandas as pd

def get_foldername():
    foldername = input('Enter the folder name containing the CSV files: ')
    return foldername

def add_headers_to_csv_files(foldername):
    folder_path = os.path.join('.', foldername)
    headers = ['review_uid', 'product_name', 'product_price', 'product_type', 'username_1', 'username_2', 'rating', 'review_content', 'review_date']
    
    if not os.path.exists(folder_path):
        print(f"The folder {folder_path} does not exist.")
        return
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            print(f"Processing file: {filename}")
            try:
                df = pd.read_csv(file_path, header=None)
                df.columns = headers
                df.to_csv(file_path, index=False)
                print(f"Headers added to file: {filename}")
            except Exception as e:
                print(f"Failed to process {filename}: {e}")

if __name__ == "__main__":
    foldername = get_foldername()
    add_headers_to_csv_files(foldername)
