import pandas as pd
import os
from config import DATA_DIR

def get_sales_df():
    """
    Reads sales.csv, parses release_date, and returns the DataFrame.
    Expects columns: external_code, season, category, color, fabric, image_path, release_date, 0..11 (for sales)
    """
    sales_file_path = os.path.join(DATA_DIR, "sales.csv")
    try:
        # Assuming weekly sales columns are named '0', '1', ..., '11' as per df_heads.txt for sales.csv
        # And other descriptive columns like 'category', 'color', 'fabric', 'image_path', 'release_date'
        df = pd.read_csv(sales_file_path, parse_dates=['release_date'])
        return df
    except FileNotFoundError:
        print(f"Error: The file {sales_file_path} was not found.")
        # Return an empty DataFrame with expected columns for graceful failure in UI
        return pd.DataFrame(columns=[
            'external_code', 'retail', 'season', 'category', 'color', 
            'image_path', 'fabric', 'release_date', 
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'
        ])
    except Exception as e:
        print(f"An error occurred while loading sales.csv: {e}")
        return pd.DataFrame(columns=[
            'external_code', 'retail', 'season', 'category', 'color', 
            'image_path', 'fabric', 'release_date', 
            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11'
        ])