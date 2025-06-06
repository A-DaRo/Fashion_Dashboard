from dash import Input, Output, html, dcc, State # Added State if needed, not strictly for this
import dash_bootstrap_components as dbc # For dbc.Row/Col in product trend comparison
import plotly.graph_objects as go
import pandas as pd

from utils.data_loader import get_gtrends_df, get_sales_df
from utils.data_processing import get_unique_attributes_from_gtrends, compute_top_trending
from components.charts import make_trend_line_chart, make_bar_chart # Added make_bar_chart

# Load data once at module startup
gtrends_df = get_gtrends_df()
sales_df = get_sales_df()
print("--- DEBUG: GTrends and Sales DFs loaded (trend_callbacks module) ---")
if gtrends_df.empty or sales_df.empty:
    print("Warning: GTrends or Sales DataFrame is empty in trend_callbacks.")

def register_trend_callbacks(app_instance):
    print("--- DEBUG: Registering trend_callbacks ---")

    @app_instance.callback(
        [Output("specific-attribute-dropdown-brand", "options"),
         Output("specific-attribute-dropdown-brand", "value")],
        [Input("attribute-type-dropdown-brand", "value")]
    )
    def update_specific_attribute_dropdown_brand(selected_attribute_type):
        if not selected_attribute_type:
            return [], None
        if gtrends_df.empty or sales_df.empty:
            return [], None
        valid_attrs = get_unique_attributes_from_gtrends(gtrends_df, sales_df, selected_attribute_type)
        options = [{"label": attr.capitalize(), "value": attr} for attr in valid_attrs]
        value = valid_attrs[0] if valid_attrs else None
        return options, value

    @app_instance.callback(
        Output("google-trends-plot-brand", "figure"),
        [Input("specific-attribute-dropdown-brand", "value")]
    )
    def update_gtrends_plot_brand(selected_specific_attribute):
        if gtrends_df.empty:
            return make_trend_line_chart(pd.DataFrame(columns=['date']), None) 
        if selected_specific_attribute and selected_specific_attribute in gtrends_df.columns:
            fig = make_trend_line_chart(gtrends_df, selected_specific_attribute)
            return fig
        else:
            return make_trend_line_chart(gtrends_df, None)

    # --- NEW CALLBACKS FOR "COULD HAVE" ---
    @app_instance.callback(
        Output("product-dropdown-brand", "options"),
        [Input("product-dropdown-brand", "id")] # Trigger once on load
    )
    def populate_product_dropdown_brand(dropdown_id):
        if not sales_df.empty:
            unique_products = sales_df.drop_duplicates(subset=['external_code'])
            options = [
                {"label": f"{row.get('category', 'N/A')} ({row['external_code']})", "value": str(row['external_code'])}
                for index, row in unique_products.iterrows()
            ]
            return options
        return []

    @app_instance.callback(
        [Output("top-category-trends-plot", "figure"),
         Output("top-color-trends-plot", "figure")],
        [Input("tabs-main", "active_tab")] # Trigger when brand tab is active
    )
    def update_top_trending_attributes(active_tab):
        empty_fig = go.Figure().update_layout(title_text="Data loading or not applicable...")
        if active_tab == "tab-brand":
            if gtrends_df.empty or sales_df.empty:
                return empty_fig, empty_fig

            top_categories_series = compute_top_trending(gtrends_df, sales_df, "category", top_n=5)
            fig_cat = make_bar_chart(top_categories_series, "Top 5 Trending Categories", "Category")

            top_colors_series = compute_top_trending(gtrends_df, sales_df, "color", top_n=5)
            fig_col = make_bar_chart(top_colors_series, "Top 5 Trending Colors", "Color")
            
            return fig_cat, fig_col
        return empty_fig, empty_fig

    @app_instance.callback(
        Output("product-trend-comparison", "children"),
        [Input("product-dropdown-brand", "value")]
    )
    def update_product_trend_comparison(selected_product_code_str):
        if not selected_product_code_str:
            return html.P("Select a product to see its trend alignment.", className="text-muted p-3")

        try:
            selected_code = int(selected_product_code_str)
            product_row_series = sales_df[sales_df['external_code'] == selected_code]
            if product_row_series.empty:
                return html.P(f"Product {selected_code} not found.", className="text-danger p-3")
            product_row = product_row_series.iloc[0]
        except ValueError:
            return html.P("Invalid product selection.", className="text-danger p-3")

        if gtrends_df.empty:
            return html.P("Google Trends data not available for comparison.", className="text-warning p-3")

        attributes_to_compare = {
            "Category": product_row.get('category'),
            "Color": product_row.get('color'),
            "Fabric": product_row.get('fabric')
        }
        
        trend_graphs_components = []
        for label, attr_value in attributes_to_compare.items():
            graph_content = None
            if pd.notna(attr_value) and attr_value in gtrends_df.columns:
                fig = make_trend_line_chart(gtrends_df, attr_value)
                fig.update_layout(
                    title_text=f"{label}: {attr_value.capitalize()}", 
                    height=300, # Smaller height for these mini-plots
                    margin=dict(t=50, b=30, l=40, r=20) # Adjust margins
                )
                graph_content = dcc.Graph(figure=fig)
            else:
                graph_content = html.Div(
                    f"No trend data for {label}: '{attr_value}'", 
                    className="p-3 border rounded bg-light text-muted text-center h-100 d-flex align-items-center justify-content-center"
                )
            trend_graphs_components.append(dbc.Col(graph_content, md=4, className="mb-3"))
        
        return dbc.Row(trend_graphs_components, className="align-items-stretch")