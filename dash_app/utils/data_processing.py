import pandas as pd
# from datetime import timedelta # Not strictly needed for current scope but useful for date logic

def compute_weekly_sales_timeseries(sales_row: pd.Series) -> list:
    """
    Given one row of sales_df (indexed by external_code), extract columns '0'..'11'
    as a list of floats/ints.
    """
    if sales_row is None or sales_row.empty:
        return [0.0] * 12 # Return list of zeros if no data
        
    weekly_sales_cols = [str(i) for i in range(12)] # Columns '0', '1', ..., '11'
    
    # Check if all expected columns exist
    if not all(col in sales_row.index for col in weekly_sales_cols):
        # print(f"Warning: Missing one or more weekly sales columns in product row: {sales_row.get('external_code', 'N/A')}")
        # Fallback: return zeros or handle as per business logic
        return [0.0] * 12 
        
    return sales_row[weekly_sales_cols].astype(float).fillna(0.0).tolist()

def map_restock_to_lifecycle(all_restocks_df: pd.DataFrame, selected_product_row: pd.Series) -> pd.DataFrame:
    """
    Uses sales_df.release_date (datetime) to compute for each restock event
    the 'lifecycle_week' of the product.
    Returns a DataFrame with columns [external_code, lifecycle_week, qty].
    """
    empty_df_return = pd.DataFrame(columns=['external_code', 'lifecycle_week', 'qty'])
    if selected_product_row is None or selected_product_row.empty:
        return empty_df_return

    product_code = selected_product_row.get('external_code')
    product_retail = selected_product_row.get('retail')
    release_date_val = selected_product_row.get('release_date')

    if product_code is None or product_retail is None or pd.isna(release_date_val):
        # print("Warning: map_restock_to_lifecycle missing key product info (code, retail, or release_date).")
        return empty_df_return
    
    release_date = pd.to_datetime(release_date_val, errors='coerce')
    if pd.isna(release_date):
        # print(f"Warning: Could not parse release_date for product {product_code}")
        return empty_df_return

    product_restocks_df = all_restocks_df[
        (all_restocks_df['external_code'] == product_code) &
        (all_restocks_df['retail'] == product_retail)
    ].copy()

    if product_restocks_df.empty:
        return empty_df_return

    # Construct restock_date (Monday of the week)
    # %G-%V-%u (ISO year, ISO week number, ISO weekday 1-7 Mon-Sun)
    product_restocks_df['restock_date_str'] = product_restocks_df['year'].astype(str) + \
                                              '-' + product_restocks_df['week'].astype(str).str.zfill(2) + \
                                              '-1' # Day 1 for Monday
    product_restocks_df['restock_date'] = pd.to_datetime(
        product_restocks_df['restock_date_str'], format='%G-%V-%u', errors='coerce'
    )
    
    product_restocks_df.dropna(subset=['restock_date'], inplace=True)
    if product_restocks_df.empty: # Check again after dropna
        return empty_df_return

    product_restocks_df['days_since_release'] = (product_restocks_df['restock_date'] - release_date).dt.days
    product_restocks_df['lifecycle_week'] = (product_restocks_df['days_since_release'] // 7) + 1
    
    relevant_restocks = product_restocks_df[
        (product_restocks_df['lifecycle_week'] >= 1) & 
        (product_restocks_df['lifecycle_week'] <= 12) # For a 12-week view
    ]
    return relevant_restocks[['external_code', 'lifecycle_week', 'qty']]

def get_unique_attributes_from_gtrends(gtrends_df: pd.DataFrame, sales_df: pd.DataFrame, attribute_type: str) -> list:
    """
    Returns a list of valid attribute names from gtrends_df columns,
    intersecting with unique values from sales_df based on attribute_type.
    attribute_type in {"category", "color", "fabric"}.
    """
    if gtrends_df.empty or sales_df.empty:
        return []
    if attribute_type not in ["category", "color", "fabric"]:
        return []
    if attribute_type not in sales_df.columns:
        # print(f"Warning: Attribute type '{attribute_type}' not found in sales_df columns.")
        return []
    
    unique_sales_attributes = sales_df[attribute_type].dropna().unique().tolist()
    gtrends_attribute_cols = [col for col in gtrends_df.columns if col.lower() != 'date'] # Case insensitive for 'date'
    
    # Case-insensitive matching can be useful if CSV headers vary slightly
    # For now, assume exact match after sales_df attributes are fetched
    valid_trend_attributes = sorted(list(set(unique_sales_attributes) & set(gtrends_attribute_cols)))
    return valid_trend_attributes