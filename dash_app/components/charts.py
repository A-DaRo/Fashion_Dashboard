import plotly.graph_objects as go
import pandas as pd # For type hinting

def make_sales_restock_figure(
    external_code: str, 
    retail_code: int, # or str
    sales_ts_list: list, 
    product_restocks_lc_df: pd.DataFrame, 
    product_price_info_row: pd.Series = None # Can be None or empty
) -> go.Figure:
    weeks = list(range(1, 13))
    fig = go.Figure()

    # Sales Line
    fig.add_trace(go.Scatter(
        x=weeks, 
        y=sales_ts_list, 
        mode='lines+markers', 
        name='Sales',
        line=dict(color='royalblue', width=2),
        marker=dict(size=6)
    ))

    # Restock Bars
    if product_restocks_lc_df is not None and not product_restocks_lc_df.empty:
        fig.add_trace(go.Bar(
            x=product_restocks_lc_df['lifecycle_week'],
            y=product_restocks_lc_df['qty'],
            name='Restock Qty',
            marker_color='rgba(255, 99, 71, 0.7)', # Tomato color with opacity
            opacity=0.7
        ))

    # Discount Shading
    if product_price_info_row is not None and not product_price_info_row.empty:
        discount_cols = [str(i) for i in range(12)] # Columns '0' through '11'
        # Ensure all discount_cols exist in the product_price_info_row
        discounts_present = [col for col in discount_cols if col in product_price_info_row.index]
        if discounts_present:
            discounts = product_price_info_row[discounts_present]
            for i, col_name in enumerate(discounts_present): # Iterate based on actual columns '0' to '11'
                discount_rate = product_price_info_row.get(col_name, 0.0) # Get discount for col_name '0', '1', etc.
                week_num_for_discount_col = int(col_name) + 1 # '0' is week 1, '1' is week 2 ...

                if pd.notna(discount_rate) and discount_rate > 0:
                    fig.add_vrect(
                        x0=week_num_for_discount_col - 0.5, x1=week_num_for_discount_col + 0.5,
                        fillcolor="LightSalmon", opacity=0.3,
                        layer="below", line_width=0,
                        annotation_text=f"{int(discount_rate*100)}% off",
                        annotation_position="top left"
                    )
    
    fig.update_layout(
        title_text=f"Sales & Restock: Product {external_code} (Retail: {retail_code})",
        xaxis_title="Lifecycle Week",
        yaxis_title="Units Sold / Restocked",
        template="simple_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=40, r=40, t=80, b=40) # Adjust margins
    )
    return fig

def make_trend_line_chart(gtrends_df: pd.DataFrame, attribute_column_name: str) -> go.Figure:
    fig = go.Figure()
    if attribute_column_name and attribute_column_name in gtrends_df.columns:
        fig.add_trace(go.Scatter(
            x=gtrends_df['date'],
            y=gtrends_df[attribute_column_name],
            mode='lines',
            name=attribute_column_name.capitalize(),
            line=dict(color='darkgreen', width=2)
        ))
        fig.update_layout(
            title_text=f"Google Trend: {attribute_column_name.capitalize()}",
            xaxis_title="Date",
            yaxis_title="Trend Score (0-100)", # Assuming this scale
            template="simple_white",
            margin=dict(l=40, r=20, t=60, b=40)
        )
    else: 
        fig.update_layout(
            title_text="Trend Data Not Available",
            xaxis={'visible': False}, 
            yaxis={'visible': False},
            annotations=[{
                'text': f"No trend data for '{attribute_column_name}'." if attribute_column_name else "Select an attribute.",
                'xref': 'paper', 'yref': 'paper',
                'showarrow': False, 'font': {'size': 14}
            }]
        )
    return fig