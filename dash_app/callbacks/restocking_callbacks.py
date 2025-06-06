# dash_app/callbacks/restocking_callbacks.py

from dash import Input, Output, html, dcc, State
import dash_bootstrap_components as dbc
import os
import pandas as pd

# DO NOT import app here like: from dash_app.app import app
# We will pass the app object in.

from utils.data_loader import get_sales_df
from config import IMAGE_ASSET_SUBPATH, ASSETS_DIR

# Load data once at app startup
sales_df = get_sales_df()
print("--- DEBUG: Sales DataFrame loaded (callbacks module) ---")
if not sales_df.empty:
    print(sales_df.head())
else:
    print("Sales DataFrame is EMPTY after loading (callbacks module).")
print("--- END DEBUG: Sales DataFrame loaded (callbacks module) ---")


def register_restocking_callbacks(app): # <-- Accept app as an argument
    print("--- DEBUG: Registering restocking_callbacks ---")

    @app.callback( # Use the passed-in app instance
        Output("product-dropdown-restock", "options"),
        [Input("product-dropdown-restock", "id")]
    )
    def populate_product_dropdown_options(dropdown_id):
        print(f"--- DEBUG populate_product_dropdown_options: Triggered by component ID: {dropdown_id} ---")
        if not sales_df.empty:
            unique_products = sales_df.drop_duplicates(subset=['external_code'])
            product_options_list = [
                {"label": f"{row['category']} ({row['external_code']})", "value": str(row['external_code'])}
                for index, row in unique_products.iterrows()
            ]
            print(f"--- DEBUG populate_product_dropdown_options: Generated {len(product_options_list)} options. First few: {product_options_list[:3]} ---")
            return product_options_list
        print("--- DEBUG populate_product_dropdown_options: Sales_df empty or other issue, returning empty options list ---")
        return []

    @app.callback( # Use the passed-in app instance
        [Output("product-image-restock", "children"),
         Output("product-details-restock", "children"),
         Output("sales-restock-plot", "figure")],
        [Input("product-dropdown-restock", "value")]
    )
    def update_restock_tab(selected_external_code_str):
        print(f"\n--- DEBUG update_restock_tab: selected_external_code_str = '{selected_external_code_str}' ---")
        if not selected_external_code_str:
            print("--- DEBUG update_restock_tab: No product selected, returning defaults. ---")
            return html.Div("Select a product to see details.", className="text-muted p-3"), "", {}

        try:
            selected_external_code = int(selected_external_code_str)
            print(f"--- DEBUG update_restock_tab: Parsed selected_external_code = {selected_external_code} ---")
        except ValueError:
            print(f"--- DEBUG update_restock_tab: ValueError parsing '{selected_external_code_str}', returning error message. ---")
            return html.Div("Invalid product selection.", className="text-danger p-3"), "", {}

        if sales_df.empty:
            print("--- DEBUG update_restock_tab: Sales DataFrame is empty, returning warning. ---")
            return html.Div("Sales data is not available.", className="text-warning p-3"), "", {}

        product_row_series = sales_df[sales_df['external_code'] == selected_external_code]
        print(f"--- DEBUG update_restock_tab: Found {len(product_row_series)} rows for code {selected_external_code}. ---")

        if product_row_series.empty:
            print(f"--- DEBUG update_restock_tab: Product with code {selected_external_code} not found in sales_df. ---")
            return html.Div(f"Product with code {selected_external_code} not found.", className="text-danger p-3"), "", {}
        
        product_row = product_row_series.iloc[0]
        print(f"--- DEBUG update_restock_tab: Product row data: \n{product_row.to_string()} ---")

        # 1. Product Image
        image_element = html.Div("Image not available (initial state)", className="text-muted")
        raw_image_path_from_csv = product_row.get("image_path")
        print(f"--- DEBUG update_restock_tab: Raw image_path from CSV = '{raw_image_path_from_csv}' ---")

        if pd.notna(raw_image_path_from_csv) and raw_image_path_from_csv.strip() != "":
            dash_asset_relative_path = os.path.join(IMAGE_ASSET_SUBPATH, raw_image_path_from_csv)
            print(f"--- DEBUG update_restock_tab: Constructed Dash asset relative path = '{dash_asset_relative_path}' ---")
            
            # Use the app instance passed to register_restocking_callbacks
            img_url = app.get_asset_url(dash_asset_relative_path)
            print(f"--- DEBUG update_restock_tab: Generated img_url for <img> tag = '{img_url}' ---")
            
            physical_image_path = os.path.join(ASSETS_DIR, dash_asset_relative_path)
            print(f"--- DEBUG update_restock_tab: Expected physical image path on server = '{physical_image_path}' ---")

            if os.path.exists(physical_image_path):
                print(f"--- DEBUG update_restock_tab: SUCCESS - Physical file FOUND at: {physical_image_path} ---")
                image_element = html.Img(src=img_url, className="product-image-restock")
            else:
                print(f"--- DEBUG update_restock_tab: ERROR - Physical file NOT FOUND at: {physical_image_path} ---")
                image_element = html.Div(f"Image file not found on server. Expected: ...{physical_image_path[-70:]}", className="text-danger")
        else:
            print(f"--- DEBUG update_restock_tab: image_path in CSV is NaN or empty. ---")
            image_element = html.Div("Image path not specified in data.", className="text-muted")
        
        # 2. Product Details
        details_list = [
            html.Strong("Category: "), html.Span(f"{product_row.get('category', 'N/A')}"), html.Br(),
            html.Strong("Color: "), html.Span(f"{product_row.get('color', 'N/A')}"), html.Br(),
            html.Strong("Fabric: "), html.Span(f"{product_row.get('fabric', 'N/A')}"), html.Br(),
            html.Strong("Season: "), html.Span(f"{product_row.get('season', 'N/A')}"), html.Br(),
            html.Strong("Release Date: "), html.Span(
                product_row['release_date'].strftime('%Y-%m-%d') if pd.notna(product_row['release_date']) else 'N/A'
            ), html.Br(),
            html.Strong("Retail ID: "), html.Span(f"{product_row.get('retail', 'N/A')}")
        ]
        details_card = dbc.Card(dbc.CardBody(details_list))

        # 3. Sales Plot Figure (Empty for this "MUST HAVE" MVP)
        sales_figure = {
            'layout': {
                'title': 'Sales & Restock Chart (Data coming in next phase)',
                'xaxis': {'visible': False},
                'yaxis': {'visible': False},
                'annotations': [{
                    'text': 'Chart data will be displayed here.',
                    'xref': 'paper',
                    'yref': 'paper',
                    'showarrow': False,
                    'font': {'size': 14}
                }]
            }
        }
        print(f"--- DEBUG update_restock_tab: Returning image_element, details_card, sales_figure. ---")
        return image_element, details_card, sales_figure