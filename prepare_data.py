import pandas as pd
import numpy as np
import os
import shutil
from pathlib import Path

# Define paths relative to this script's location (intellistock_mvp/)
RAW_DATA_PARENT_DIR = Path("dash_app/data/visuelle2")
ASSETS_PARENT_DIR = Path("dash_app/assets/visuelle2") # For images

def prepare_all_data():
    print("Starting data preparation...")
    RAW_DATA_PARENT_DIR.mkdir(parents=True, exist_ok=True)
    ASSETS_PARENT_DIR.mkdir(parents=True, exist_ok=True) # Ensure assets/visuelle2 exists

    # --- 1. Process sales.csv ---
    raw_sales_path = RAW_DATA_PARENT_DIR / "sales.csv"
    cleaned_sales_path = RAW_DATA_PARENT_DIR / "sales_cleaned.csv"
    if raw_sales_path.exists():
        print(f"Processing {raw_sales_path}...")
        sales_df = pd.read_csv(raw_sales_path)
        
        if "Unnamed: 0" in sales_df.columns:
            sales_df = sales_df.drop(columns=["Unnamed: 0"])
            
        sales_df["external_code"] = sales_df["external_code"].astype(str)
        sales_df["release_date"] = pd.to_datetime(sales_df["release_date"], errors='coerce')
        
        week_cols_map = {str(i): f"w{i}" for i in range(12)}
        week_cols_int_map = {i: f"w{i}" for i in range(12)}
        
        renamed_successfully = False
        if any(str(i) in sales_df.columns for i in range(12)):
            sales_df = sales_df.rename(columns=week_cols_map)
            renamed_successfully = True
        elif any(i in sales_df.columns for i in range(12)):
            sales_df = sales_df.rename(columns=week_cols_int_map)
            renamed_successfully = True
        
        if not renamed_successfully:
            print("Warning: Could not find numeric weekly sales columns (0-11 or '0'-'11') in sales.csv")

        agg_funcs = {}
        attribute_cols = ['season', 'category', 'color', 'image_path', 'fabric', 'release_date', 'restock'] # Added 'restock' from sales.csv
        for col in attribute_cols:
            if col in sales_df.columns:
                agg_funcs[col] = 'first'
        
        for i in range(12):
            if f"w{i}" in sales_df.columns:
                agg_funcs[f"w{i}"] = 'sum'
        
        valid_agg_funcs = {k: v for k, v in agg_funcs.items() if k in sales_df.columns}
        if 'external_code' in sales_df.columns and valid_agg_funcs:
            sales_cleaned_df = sales_df.groupby("external_code", as_index=False).agg(valid_agg_funcs)
            sales_cleaned_df.to_csv(cleaned_sales_path, index=False)
            print(f"Saved cleaned sales data to {cleaned_sales_path}")
        else:
            print(f"Could not perform sales aggregation. Required columns for aggregation: {list(valid_agg_funcs.keys())}. Saving raw-like (but typed).")
            sales_df.to_csv(cleaned_sales_path, index=False)

    else:
        print(f"CRITICAL: {raw_sales_path} not found. Cannot proceed with sales data preparation.")

    # --- 2. Process price_discount_series.csv ---
    raw_price_path = RAW_DATA_PARENT_DIR / "price_discount_series.csv"
    cleaned_price_path = RAW_DATA_PARENT_DIR / "price_discount_series_cleaned.csv"
    if raw_price_path.exists():
        print(f"Processing {raw_price_path}...")
        price_df = pd.read_csv(raw_price_path)
        price_df["external_code"] = price_df["external_code"].astype(str)
        
        discount_week_cols_map = {str(i): f"discount_w{i}" for i in range(12)}
        discount_week_cols_int_map = {i: f"discount_w{i}" for i in range(12)}

        renamed_price_successfully = False
        if any(str(i) in price_df.columns for i in range(12)):
            price_df = price_df.rename(columns=discount_week_cols_map)
            renamed_price_successfully = True
        elif any(i in price_df.columns for i in range(12)):
            price_df = price_df.rename(columns=discount_week_cols_int_map)
            renamed_price_successfully = True

        if not renamed_price_successfully:
            print("Warning: Could not find numeric weekly discount columns (0-11 or '0'-'11') in price_discount_series.csv")
            
        price_agg_funcs = {}
        if 'price' in price_df.columns:
             price_agg_funcs['price'] = 'mean'
        for i in range(12):
            if f"discount_w{i}" in price_df.columns:
                price_agg_funcs[f"discount_w{i}"] = 'mean'
        
        valid_price_agg_funcs = {k: v for k, v in price_agg_funcs.items() if k in price_df.columns}
        if 'external_code' in price_df.columns and valid_price_agg_funcs:
            price_cleaned_df = price_df.groupby("external_code", as_index=False).agg(valid_price_agg_funcs)
            price_cleaned_df.to_csv(cleaned_price_path, index=False)
            print(f"Saved cleaned price/discount data to {cleaned_price_path}")
        else:
            print(f"Could not perform price aggregation. Required columns for aggregation: {list(valid_price_agg_funcs.keys())}. Saving raw-like (but typed).")
            price_df.to_csv(cleaned_price_path, index=False)
    else:
        print(f"Warning: {raw_price_path} not found.")

    # --- 3. Process restocks.csv ---
    raw_restocks_path = RAW_DATA_PARENT_DIR / "restocks.csv"
    cleaned_restocks_path = RAW_DATA_PARENT_DIR / "restocks_cleaned.csv"
    if raw_restocks_path.exists():
        print(f"Processing {raw_restocks_path}...")
        restocks_df = pd.read_csv(raw_restocks_path)
        restocks_df["external_code"] = restocks_df["external_code"].astype(str)
        
        if all(col in restocks_df.columns for col in ["external_code", "year", "week", "qty"]):
            restocks_cleaned_df = restocks_df.groupby(
                ["external_code", "year", "week"], as_index=False
            )["qty"].sum()
            restocks_cleaned_df.to_csv(cleaned_restocks_path, index=False)
            print(f"Saved cleaned restocks data to {cleaned_restocks_path}")
        else:
            print(f"Could not perform restocks aggregation. Required cols: external_code, year, week, qty. Saving raw.")
            restocks_df.to_csv(cleaned_restocks_path, index=False)
    else:
        print(f"Warning: {raw_restocks_path} not found.")

    # --- 4. Process vis2_gtrends_data.csv ---
    raw_gtrends_path = RAW_DATA_PARENT_DIR / "vis2_gtrends_data.csv"
    cleaned_gtrends_path = RAW_DATA_PARENT_DIR / "vis2_gtrends_data_cleaned.csv" # Save with _cleaned suffix for consistency
    if raw_gtrends_path.exists():
        print(f"Processing {raw_gtrends_path}...")
        gtrends_df = pd.read_csv(raw_gtrends_path)
        if "date" in gtrends_df.columns:
            gtrends_df["date"] = pd.to_datetime(gtrends_df["date"], errors='coerce')
        # No other major cleaning needed for gtrends based on OCR, just saving consistently
        gtrends_df.to_csv(cleaned_gtrends_path, index=False)
        print(f"Saved (essentially copied and date-parsed) Google Trends data to {cleaned_gtrends_path}")
    else:
        print(f"Warning: {raw_gtrends_path} not found.")

    # --- 5. Copy images to assets folder ---
    source_images_dir = RAW_DATA_PARENT_DIR / "images"
    dest_images_dir = ASSETS_PARENT_DIR / "images" # dash_app/assets/visuelle2/images
    
    if source_images_dir.exists() and source_images_dir.is_dir():
        print(f"Copying images from {source_images_dir} to {dest_images_dir}...")
        if dest_images_dir.exists():
            print(f"Destination images directory {dest_images_dir} already exists. Removing it first for a clean copy.")
            shutil.rmtree(dest_images_dir)
        try:
            shutil.copytree(source_images_dir, dest_images_dir)
            print("Images copied successfully.")
        except Exception as e:
            print(f"Error copying images: {e}")
    else:
        print(f"Warning: Source images directory {source_images_dir} not found. Cannot copy images.")

    print("Data preparation finished.")

if __name__ == "__main__":
    prepare_all_data()