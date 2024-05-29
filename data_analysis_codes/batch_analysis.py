import os
import subprocess

def get_foldername():
    foldername = input('Enter the folder name containing the CSV files: ')
    return foldername

def run_analysis_for_all_files(foldername):
    folder_path = os.path.join('.', foldername)
    folder_path = f'{folder_path}_Collected_Reviews'
    
    if not os.path.exists(folder_path):
        print(f"The folder {folder_path} does not exist.")
        return
    
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            print(f"Processing file: {filename}")
            subprocess.run(['python', 'unique_review_analysis.py', filename, foldername])
            subprocess.run(['python', 'isolation_forest.py', filename, foldername])
            subprocess.run(['python', 'phrase_repetition_analysis.py', filename, foldername])
            subprocess.run(['python', 'rating_trend_analysis.py', filename, foldername])
            subprocess.run(['python', 'word_count_comparison.py', filename, foldername])

if __name__ == "__main__":
    foldername = get_foldername()
    run_analysis_for_all_files(foldername)



            