import pandas as pd
from utils.constants import UNIQUE_CATEGORIES, UNIQUE_COLORS, UNIQUE_FABRICS, DEFAULT_PRODUCT_IMAGE
from config import DATA_DIR # Not directly used here now for images, path comes from get_asset_image_url
import os
from datetime import datetime

def compute_weekly_sales_timeseries(sales_row_series):
    if sales_row_series is None or sales_row_series.empty:
        return [0] * 12
    # Uses w0-w11 as produced by prepare_data.py
    weekly_sales_cols = [f"w{i}" for i in range(12)]
    return [sales_row_series.get(col, 0) for col in weekly_sales_cols]

def map_restock_to_lifecycle(restocks_cleaned_df, sales_cleaned_df):
    """
    Uses sales_cleaned_df.release_date to compute lifecycle_week for restock events.
    restocks_cleaned_df is already aggregated by external_code, year, week.
    sales_cleaned_df is aggregated by external_code.
    """
    if restocks_cleaned_df.empty or sales_cleaned_df.empty:
        return pd.DataFrame(columns=["external_code", "lifecycle_week", "qty"])

    # sales_cleaned_df is indexed by external_code, need 'release_date' column
    sales_info_df = sales_cleaned_df.reset_index()[["external_code", "release_date"]]
    
    restocks_cleaned_df['external_code'] = restocks_cleaned_df['external_code'].astype(str)
    sales_info_df['external_code'] = sales_info_df['external_code'].astype(str)

    merged_df = pd.merge(restocks_cleaned_df, sales_info_df, on="external_code", how="left")

    if merged_df.empty or "release_date" not in merged_df.columns:
        return pd.DataFrame(columns=["external_code", "lifecycle_week", "qty"])

    merged_df.dropna(subset=["release_date"], inplace=True) # Critical
    merged_df["release_date"] = pd.to_datetime(merged_df["release_date"])


    def get_date_from_year_week(row):
        try:
            return datetime.fromisocalendar(int(row['year']), int(row['week']), 1) # Monday
        except (ValueError, TypeError): # Added TypeError for robustness
            return pd.NaT

    merged_df["restock_date"] = merged_df.apply(get_date_from_year_week, axis=1)
    merged_df.dropna(subset=["restock_date"], inplace=True)

    if merged_df.empty:
         return pd.DataFrame(columns=["external_code", "lifecycle_week", "qty"])

    merged_df["lifecycle_week"] = ((merged_df["restock_date"] - merged_df["release_date"]).dt.days // 7) + 1
    
    result_df = merged_df[["external_code", "lifecycle_week", "qty"]].copy()
    result_df.dropna(subset=["lifecycle_week"], inplace=True)
    result_df = result_df[(result_df["lifecycle_week"] >= 1) & (result_df["lifecycle_week"] <= 12)]
    
    return result_df

def get_unique_attributes(attribute_type: str):
    if attribute_type == "category":
        return UNIQUE_CATEGORIES
    elif attribute_type == "color":
        return UNIQUE_COLORS
    elif attribute_type == "fabric":
        return UNIQUE_FABRICS
    else:
        return []

def get_asset_image_url(image_subpath: str):
    """
    image_subpath from sales_df is like "PE17/00001.png".
    Actual image must be in dash_app/assets/visuelle2/images/PE17/00001.png
    """
    if not image_subpath or pd.isna(image_subpath):
        # Path relative to assets folder
        return f"visuelle2/images/{DEFAULT_PRODUCT_IMAGE}" 
    
    # Path relative to assets folder
    asset_path = os.path.join("visuelle2", "images", image_subpath)
    return asset_path.replace("\\", "/") # Ensure forward slashes for URL