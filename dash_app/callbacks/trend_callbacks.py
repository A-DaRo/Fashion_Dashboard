from dash import Input, Output, html, dcc
import plotly.graph_objects as go
import pandas as pd

# from dash_app.app import app # Will be passed in
from utils.data_loader import get_gtrends_df, get_sales_df
from utils.data_processing import get_unique_attributes_from_gtrends
from components.charts import make_trend_line_chart

# Load data once at module startup
gtrends_df = get_gtrends_df()
sales_df = get_sales_df() # Needed to find valid attributes for trends
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
        # print(f"--- DEBUG TrendCB: update_specific_attribute_dropdown_brand: type = {selected_attribute_type} ---")
        if not selected_attribute_type:
            return [], None
        
        # Ensure gtrends_df and sales_df are not empty before proceeding
        if gtrends_df.empty or sales_df.empty:
            # print("--- DEBUG TrendCB: gtrends_df or sales_df is empty, cannot populate specific attributes. ---")
            return [], None

        valid_attrs = get_unique_attributes_from_gtrends(gtrends_df, sales_df, selected_attribute_type)
        options = [{"label": attr.capitalize(), "value": attr} for attr in valid_attrs]
        value = valid_attrs[0] if valid_attrs else None
        # print(f"--- DEBUG TrendCB: update_specific_attribute_dropdown_brand: options count = {len(options)}, first value = {value} ---")
        return options, value

    @app_instance.callback(
        Output("google-trends-plot-brand", "figure"),
        [Input("specific-attribute-dropdown-brand", "value")]
    )
    def update_gtrends_plot_brand(selected_specific_attribute):
        # print(f"--- DEBUG TrendCB: update_gtrends_plot_brand: attribute = {selected_specific_attribute} ---")
        
        # Ensure gtrends_df is not empty
        if gtrends_df.empty:
            # print("--- DEBUG TrendCB: gtrends_df is empty, cannot plot trend. ---")
            return make_trend_line_chart(pd.DataFrame(columns=['date']), None) # Return empty chart

        if selected_specific_attribute and selected_specific_attribute in gtrends_df.columns:
            fig = make_trend_line_chart(gtrends_df, selected_specific_attribute)
            # print(f"--- DEBUG TrendCB: update_gtrends_plot_brand: Generated trend chart for {selected_specific_attribute} ---")
            return fig
        else:
            # print(f"--- DEBUG TrendCB: update_gtrends_plot_brand: No valid attribute selected, returning placeholder. ---")
            return make_trend_line_chart(gtrends_df, None) # Chart component handles empty message