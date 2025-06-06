import pandas as pd
# from datetime import timedelta # Already present or can be added if needed

def compute_weekly_sales_timeseries(sales_row: pd.Series) -> list:
    if sales_row is None or sales_row.empty:
        return [0.0] * 12
    weekly_sales_cols = [str(i) for i in range(12)]
    if not all(col in sales_row.index for col in weekly_sales_cols):
        return [0.0] * 12
    return sales_row[weekly_sales_cols].astype(float).fillna(0.0).tolist()

def map_restock_to_lifecycle(all_restocks_df: pd.DataFrame, selected_product_row: pd.Series) -> pd.DataFrame:
    empty_df_return = pd.DataFrame(columns=['external_code', 'lifecycle_week', 'qty'])
    if selected_product_row is None or selected_product_row.empty:
        return empty_df_return

    product_code = selected_product_row.get('external_code')
    product_retail = selected_product_row.get('retail')
    release_date_val = selected_product_row.get('release_date')

    if product_code is None or product_retail is None or pd.isna(release_date_val):
        return empty_df_return
    
    release_date = pd.to_datetime(release_date_val, errors='coerce')
    if pd.isna(release_date):
        return empty_df_return

    product_restocks_df = all_restocks_df[
        (all_restocks_df['external_code'] == product_code) &
        (all_restocks_df['retail'] == product_retail)
    ].copy()

    if product_restocks_df.empty:
        return empty_df_return

    product_restocks_df['restock_date_str'] = product_restocks_df['year'].astype(str) + \
                                              '-' + product_restocks_df['week'].astype(str).str.zfill(2) + \
                                              '-1'
    product_restocks_df['restock_date'] = pd.to_datetime(
        product_restocks_df['restock_date_str'], format='%G-%V-%u', errors='coerce'
    )
    
    product_restocks_df.dropna(subset=['restock_date'], inplace=True)
    if product_restocks_df.empty:
        return empty_df_return

    product_restocks_df['days_since_release'] = (product_restocks_df['restock_date'] - release_date).dt.days
    product_restocks_df['lifecycle_week'] = (product_restocks_df['days_since_release'] // 7) + 1
    
    relevant_restocks = product_restocks_df[
        (product_restocks_df['lifecycle_week'] >= 1) & 
        (product_restocks_df['lifecycle_week'] <= 12)
    ]
    return relevant_restocks[['external_code', 'lifecycle_week', 'qty']]

def get_unique_attributes_from_gtrends(gtrends_df: pd.DataFrame, sales_df: pd.DataFrame, attribute_type: str) -> list:
    if gtrends_df.empty or sales_df.empty:
        return []
    if attribute_type not in ["category", "color", "fabric"]:
        return []
    if attribute_type not in sales_df.columns:
        return []
    
    unique_sales_attributes = sales_df[attribute_type].dropna().unique().tolist()
    gtrends_attribute_cols = [col for col in gtrends_df.columns if col.lower() != 'date']
    
    valid_trend_attributes = sorted(list(set(unique_sales_attributes) & set(gtrends_attribute_cols)))
    return valid_trend_attributes

# --- NEW FUNCTION FOR "COULD HAVE" ---
def compute_top_trending(
    gtrends_df: pd.DataFrame, 
    sales_df: pd.DataFrame, 
    attribute_type: str, 
    top_n: int = 5, 
    days_window: int = 90
) -> pd.Series:
    """
    Computes top N trending attributes of a given type based on mean Google Trend score
    over a specified number of recent days.
    """
    empty_series = pd.Series(dtype='float64')
    if gtrends_df.empty or sales_df.empty:
        # print(f"Warning (compute_top_trending): GTrends or Sales DF is empty for attribute_type '{attribute_type}'.")
        return empty_series

    if 'date' not in gtrends_df.columns:
        # print(f"Warning (compute_top_trending): 'date' column missing in GTrends DF.")
        return empty_series
    
    # Ensure date column is datetime
    gtrends_df['date'] = pd.to_datetime(gtrends_df['date'], errors='coerce')
    gtrends_df.dropna(subset=['date'], inplace=True) # Drop rows where date conversion failed
    if gtrends_df.empty: # Check again after coerce and drop
        return empty_series


    max_date = gtrends_df['date'].max()
    if pd.isna(max_date): # If all dates were NaT
        # print(f"Warning (compute_top_trending): No valid dates in GTrends DF.")
        return empty_series
        
    cutoff_date = max_date - pd.Timedelta(days=days_window)
    recent_gtrends = gtrends_df[gtrends_df['date'] >= cutoff_date].copy()

    if recent_gtrends.empty:
        # print(f"Warning (compute_top_trending): No recent GTrends data for attribute_type '{attribute_type}'.")
        return empty_series

    # Get attributes that are valid (in sales_df for the given type) AND present in gtrends_df columns
    valid_attributes_for_type = get_unique_attributes_from_gtrends(gtrends_df, sales_df, attribute_type)

    # Further filter these to only those present as columns in recent_gtrends
    # (This should be redundant if get_unique_attributes_from_gtrends uses the original gtrends_df for column checking,
    # but good for robustness)
    cols_to_average = [attr for attr in valid_attributes_for_type if attr in recent_gtrends.columns]

    if not cols_to_average:
        # print(f"Warning (compute_top_trending): No valid attribute columns to average for '{attribute_type}'.")
        return empty_series
        
    # Calculate mean, drop NaNs from means (if a column was all NaN), sort, and take top N
    mean_scores = recent_gtrends[cols_to_average].mean().dropna().sort_values(ascending=False)
    
    return mean_scores.head(top_n)