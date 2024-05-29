import os
import pandas as pd

def get_main_foldername():
    foldername = input('Enter the main folder name containing company folders: ')
    return foldername

def combine_csv_files(main_foldername):
    main_folder_path = os.path.join('.', main_foldername)
    
    combined_anomalies = []
    combined_phrase_repetition = []
    combined_rating_trend = []
    combined_unique_nonunique = []
    
    if not os.path.exists(main_folder_path):
        print(f"The folder {main_folder_path} does not exist.")
        return
    
    for company_folder in os.listdir(main_folder_path):
        company_folder_path = os.path.join(main_folder_path, company_folder)
        if os.path.isdir(company_folder_path):
            print(f"Processing folder: {company_folder}")
            try:
                anomalies_file = os.path.join(company_folder_path, f"{company_folder}_Anomalies.csv")
                if os.path.exists(anomalies_file):
                    anomalies_df = pd.read_csv(anomalies_file)
                    combined_anomalies.append(anomalies_df)
                
                phrase_repetition_file = os.path.join(company_folder_path, f"{company_folder}_phrase_repetition.csv")
                if os.path.exists(phrase_repetition_file):
                    phrase_repetition_df = pd.read_csv(phrase_repetition_file)
                    combined_phrase_repetition.append(phrase_repetition_df)
                
                rating_trend_file = os.path.join(company_folder_path, f"{company_folder}_rating_trend.csv")
                if os.path.exists(rating_trend_file):
                    rating_trend_df = pd.read_csv(rating_trend_file)
                    combined_rating_trend.append(rating_trend_df)
                
                unique_nonunique_file = os.path.join(company_folder_path, f"{company_folder}_unique_nonunique.csv")
                if os.path.exists(unique_nonunique_file):
                    unique_nonunique_df = pd.read_csv(unique_nonunique_file)
                    combined_unique_nonunique.append(unique_nonunique_df)
            except Exception as e:
                print(f"Failed to process files in {company_folder}: {e}")
    
    if combined_anomalies:
        combined_anomalies_df = pd.concat(combined_anomalies, ignore_index=True)
        combined_anomalies_df.to_csv(os.path.join(main_folder_path, 'combined_Anomalies.csv'), index=False)
    
    if combined_phrase_repetition:
        combined_phrase_repetition_df = pd.concat(combined_phrase_repetition, ignore_index=True)
        combined_phrase_repetition_df.to_csv(os.path.join(main_folder_path, 'combined_phrase_repetition.csv'), index=False)
    
    if combined_rating_trend:
        combined_rating_trend_df = pd.concat(combined_rating_trend, ignore_index=True)
        combined_rating_trend_df.to_csv(os.path.join(main_folder_path, 'combined_rating_trend.csv'), index=False)
    
    if combined_unique_nonunique:
        combined_unique_nonunique_df = pd.concat(combined_unique_nonunique, ignore_index=True)
        combined_unique_nonunique_df.to_csv(os.path.join(main_folder_path, 'combined_unique_nonunique.csv'), index=False)

if __name__ == "__main__":
    main_foldername = get_main_foldername()
    combine_csv_files(main_foldername)
