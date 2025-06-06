import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from dash_app.utils.constants import UNIQUE_CATEGORIES, UNIQUE_COLORS, UNIQUE_FABRICS
from datetime import timedelta

def make_sales_restock_figure(external_code, sales_ts, restock_lc_df, price_df_all_cleaned):
    # ... (rest of the function largely same as before) ...
    # 3. Add discount‐period shading
    if price_df_all_cleaned is not None and not price_df_all_cleaned.empty:
        # price_df_all_cleaned is already aggregated by external_code
        product_price_info = price_df_all_cleaned[price_df_all_cleaned["external_code"] == external_code]
        if not product_price_info.empty:
            # Use discount_w0 to discount_w11 columns
            discount_cols = [f"discount_w{i}" for i in range(12)]
            # Check if all discount columns exist before trying to access
            if all(col in product_price_info.columns for col in discount_cols):
                discounts = product_price_info.iloc[0][discount_cols].values
                for i, discount_percentage in enumerate(discounts, start=1): # i is lifecycle week 1-12
                    if pd.notna(discount_percentage) and discount_percentage > 0: # Check for NaN
                        fig.add_vrect(
                            x0=i - 0.5, x1=i + 0.5,
                            fillcolor="LightSalmon",
                            opacity=0.3,
                            layer="below",
                            line_width=0,
                            annotation_text=f"{int(discount_percentage*100)}% off",
                            annotation_position="top left"
                        )
            else:
                print(f"Warning: Not all discount_w* columns found for product {external_code} in price_df.")
    # ... (rest of the layout tweaks) ...
    fig.update_layout(
        title_text=f"Sales & Restock Analysis for Product: {external_code}",
        xaxis_title="Week in Season (Lifecycle Week 1–12)",
        yaxis_title="Units",
        template="simple_white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        margin=dict(l=20, r=20, t=50, b=20),
        hovermode="x unified"
    )
    weeks = list(range(1, 13))
    fig.update_xaxes(tickvals=weeks, ticktext=[f"W{w}" for w in weeks])
    return fig

# make_trend_line_chart and make_bar_chart remain the same, but they will now operate on
# gtrends_cleaned_df. The UNIQUE_CATEGORIES etc. in constants.py should align with its columns.
def make_trend_line_chart(gtrends_df, attribute_column_name, chart_title_prefix="Google Trend: "):
    if gtrends_df.empty or attribute_column_name not in gtrends_df.columns:
        return go.Figure(layout={"title": f"{chart_title_prefix}{attribute_column_name} (No data available)"})

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=gtrends_df["date"],
            y=gtrends_df[attribute_column_name],
            mode="lines",
            name=attribute_column_name,
            line=dict(width=2, color="#008080")
        )
    )
    fig.update_layout(
        title_text=f"{chart_title_prefix}{attribute_column_name}",
        xaxis_title="Date",
        yaxis_title="Trend Score (0–100)",
        template="simple_white",
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

def make_bar_chart(gtrends_df, attribute_type, top_n=5, days_lookback=90):
    if gtrends_df.empty:
        return go.Figure(layout={"title": f"Top {top_n} {attribute_type.capitalize()} Trends (No data)"})

    if attribute_type == "category":
        attribute_columns = [col for col in UNIQUE_CATEGORIES if col in gtrends_df.columns]
        chart_title = f"Top {top_n} Category Trends (Last {days_lookback} Days)"
    elif attribute_type == "color":
        attribute_columns = [col for col in UNIQUE_COLORS if col in gtrends_df.columns]
        chart_title = f"Top {top_n} Color Trends (Last {days_lookback} Days)"
    elif attribute_type == "fabric":
        attribute_columns = [col for col in UNIQUE_FABRICS if col in gtrends_df.columns]
        chart_title = f"Top {top_n} Fabric Trends (Last {days_lookback} Days)"
    else:
        return go.Figure(layout={"title": "Invalid attribute type for bar chart"})
    
    if not attribute_columns:
        return go.Figure(layout={"title": f"{chart_title} (No relevant attribute columns found in data for {attribute_type})"})

    gtrends_df['date'] = pd.to_datetime(gtrends_df['date'])
    cutoff_date = gtrends_df['date'].max() - timedelta(days=days_lookback)
    recent_trends = gtrends_df[gtrends_df['date'] >= cutoff_date]

    if recent_trends.empty:
        return go.Figure(layout={"title": f"{chart_title} (No recent data)"})
        
    mean_scores = recent_trends[attribute_columns].mean().sort_values(ascending=False)
    top_n_series = mean_scores.head(top_n)

    if top_n_series.empty:
         return go.Figure(layout={"title": f"{chart_title} (No trends to display for {attribute_type})"})

    fig = px.bar(
        x=top_n_series.index, 
        y=top_n_series.values,
        labels={'x': attribute_type.capitalize(), 'y': 'Average Trend Score'},
        title=chart_title,
        color=top_n_series.values,
        color_continuous_scale=px.colors.sequential.Teal,
    )
    fig.update_layout(template="simple_white", coloraxis_showscale=False, margin=dict(l=20, r=20, t=50, b=20))
    return fig 