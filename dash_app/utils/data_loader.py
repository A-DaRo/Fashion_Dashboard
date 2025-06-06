import pandas as pd
import os
from config import DATA_DIR

def get_sales_df():
    sales_file_path = os.path.join(DATA_DIR, "sales.csv")
    try:
        df = pd.read_csv(sales_file_path, parse_dates=['release_date'])
        return df
    except FileNotFoundError:
        print(f"Error: The file {sales_file_path} was not found.")
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

def get_restock_df():
    restock_file_path = os.path.join(DATA_DIR, "restocks.csv")
    try:
        df = pd.read_csv(restock_file_path)
        return df
    except FileNotFoundError:
        print(f"Error: The file {restock_file_path} was not found.")
        return pd.DataFrame(columns=['external_code', 'retail', 'week', 'year', 'qty'])
    except Exception as e:
        print(f"An error occurred while loading restocks.csv: {e}")
        return pd.DataFrame(columns=['external_code', 'retail', 'week', 'year', 'qty'])

def get_price_df():
    price_file_path = os.path.join(DATA_DIR, "price_discount_series.csv")
    try:
        df = pd.read_csv(price_file_path)
        return df
    except FileNotFoundError:
        print(f"Error: The file {price_file_path} was not found.")
        # Assuming columns based on df_heads.txt, including 'external_code', 'retail', '0'-'11', 'price'
        cols = ['external_code', 'retail'] + [str(i) for i in range(12)] + ['price']
        return pd.DataFrame(columns=cols)
    except Exception as e:
        print(f"An error occurred while loading price_discount_series.csv: {e}")
        cols = ['external_code', 'retail'] + [str(i) for i in range(12)] + ['price']
        return pd.DataFrame(columns=cols)

def get_gtrends_df():
    gtrends_file_path = os.path.join(DATA_DIR, "vis2_gtrends_data.csv")
    try:
        df = pd.read_csv(gtrends_file_path, parse_dates=['date'])
        return df
    except FileNotFoundError:
        print(f"Error: The file {gtrends_file_path} was not found.")
        return pd.DataFrame(columns=['date']) # Minimal for graceful failure
    except Exception as e:
        print(f"An error occurred while loading vis2_gtrends_data.csv: {e}")
        return pd.DataFrame(columns=['date'])

def get_weather_df(): # Added for SHOULD HAVE, used in COULD HAVE
    weather_file_path = os.path.join(DATA_DIR, "vis2_weather_data.csv")
    try:
        df = pd.read_csv(weather_file_path, parse_dates=['date'])
        return df
    except FileNotFoundError:
        print(f"Error: The file {weather_file_path} was not found.")
        return pd.DataFrame(columns=['date', 'locality']) # Minimal
    except Exception as e:
        print(f"An error occurred while loading vis2_weather_data.csv: {e}")
        return pd.DataFrame(columns=['date', 'locality'])