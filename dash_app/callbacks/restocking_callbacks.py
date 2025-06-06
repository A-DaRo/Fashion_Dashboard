from dash import Input, Output, html, dcc
import dash_bootstrap_components as dbc
import os
import pandas as pd

from utils.data_loader import get_sales_df, get_restock_df, get_price_df
from utils.data_processing import compute_weekly_sales_timeseries, map_restock_to_lifecycle
from components.charts import make_sales_restock_figure
from components.cards import kpi_card
from config import IMAGE_ASSET_SUBPATH, ASSETS_DIR

# Load data once at app startup
sales_df = get_sales_df()
restocks_df_full = get_restock_df()
price_df_full = get_price_df()

print("--- DEBUG: Sales, Restocks, Price DFs loaded (restocking_callbacks module) ---")
if sales_df.empty or restocks_df_full.empty or price_df_full.empty:
    print("Warning: One or more essential DataFrames are empty after loading!")

def register_restocking_callbacks(app_instance): # Changed app to app_instance to avoid conflict if app is global
    print("--- DEBUG: Registering restocking_callbacks ---")

    @app_instance.callback(
        Output("product-dropdown-restock", "options"),
        [Input("product-dropdown-restock", "id")]
    )
    def populate_product_dropdown_options(dropdown_id):
        # print(f"--- DEBUG populate_product_dropdown_options: Triggered by component ID: {dropdown_id} ---")
        if not sales_df.empty:
            unique_products = sales_df.drop_duplicates(subset=['external_code'])
            product_options_list = [
                {"label": f"{row.get('category', 'N/A')} ({row['external_code']})", "value": str(row['external_code'])}
                for index, row in unique_products.iterrows()
            ]
            # print(f"--- DEBUG populate_product_dropdown_options: Generated {len(product_options_list)} options. ---")
            return product_options_list
        # print("--- DEBUG populate_product_dropdown_options: Sales_df empty, returning empty options list ---")
        return []

    @app_instance.callback(
        [Output("product-image-restock", "children"),
         Output("product-details-restock", "children"),
         Output("sales-restock-plot", "figure"),
         Output("kpi-output-restock", "children")],
        [Input("product-dropdown-restock", "value")]
    )
    def update_restock_tab(selected_external_code_str):
        # print(f"\n--- DEBUG update_restock_tab: selected_external_code_str = '{selected_external_code_str}' ---")
        no_selection_outputs = (
            html.Div("Select a product to see details.", className="text-muted p-3"), 
            "", 
            make_sales_restock_figure("", 0, [0]*12, pd.DataFrame(), None), # Empty chart
            ""
        )
        if not selected_external_code_str:
            return no_selection_outputs

        try:
            selected_external_code = int(selected_external_code_str)
        except ValueError:
            return (html.Div("Invalid product selection.", className="text-danger p-3"), "", 
                    make_sales_restock_figure("", 0, [0]*12, pd.DataFrame(), None), "")

        if sales_df.empty:
            return (html.Div("Sales data is not available.", className="text-warning p-3"), "", 
                    make_sales_restock_figure("", 0, [0]*12, pd.DataFrame(), None), "")

        product_row_series = sales_df[sales_df['external_code'] == selected_external_code]
        if product_row_series.empty:
            return (html.Div(f"Product with code {selected_external_code} not found.", className="text-danger p-3"), "", 
                    make_sales_restock_figure("", 0, [0]*12, pd.DataFrame(), None), "")
        
        product_row = product_row_series.iloc[0]

        # Image
        image_element = html.Div("Image not available", className="text-muted")
        raw_image_path_from_csv = product_row.get("image_path")
        if pd.notna(raw_image_path_from_csv) and raw_image_path_from_csv.strip() != "":
            dash_asset_relative_path = os.path.join(IMAGE_ASSET_SUBPATH, raw_image_path_from_csv)
            img_url = app_instance.get_asset_url(dash_asset_relative_path) # Use app_instance
            physical_image_path = os.path.join(ASSETS_DIR, dash_asset_relative_path)
            if os.path.exists(physical_image_path):
                image_element = html.Img(src=img_url, className="product-image-restock")
            else:
                image_element = html.Div(f"Img file not found.", className="text-danger small")
        
        # Details
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

        # Sales Time Series & Mapped Restocks
        sales_ts = compute_weekly_sales_timeseries(product_row)
        product_restocks_lc = map_restock_to_lifecycle(restocks_df_full, product_row)
        
        # Price/Discount Info
        product_price_rows = price_df_full[
            (price_df_full['external_code'] == product_row['external_code']) &
            (price_df_full['retail'] == product_row['retail'])
        ]
        current_product_price_info = product_price_rows.iloc[0] if not product_price_rows.empty else None

        sales_figure = make_sales_restock_figure(
            str(product_row['external_code']), 
            product_row.get('retail', 0), 
            sales_ts, 
            product_restocks_lc, 
            current_product_price_info
        )

        # KPIs
        total_sales_val = sum(sales_ts)
        avg_weekly_sales_val = total_sales_val / 12 if sales_ts and sum(sales_ts) > 0 else 0.0 # Avoid div by zero if sales_ts is all zeros
        total_restocked_val = product_restocks_lc['qty'].sum() if not product_restocks_lc.empty else 0

        kpi_cards_layout = dbc.Row([
            kpi_card("Total Sales (12wk)", f"{total_sales_val:.0f} units", "fas fa-shopping-cart", col_md_width=4),
            kpi_card("Avg. Weekly Sales", f"{avg_weekly_sales_val:.1f} units", "fas fa-calendar-alt", col_md_width=4),
            kpi_card("Total Restocked", f"{total_restocked_val:.0f} units", "fas fa-box-open", col_md_width=4)
        ], className="justify-content-center") # Center the row of cards
        
        return image_element, details_card, sales_figure, kpi_cards_layout