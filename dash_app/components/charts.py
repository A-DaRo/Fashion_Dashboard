import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def make_sales_restock_figure(
    external_code: str, 
    retail_code: int,
    sales_ts_list: list, 
    product_restocks_lc_df: pd.DataFrame, 
    product_price_info_row: pd.Series = None
) -> go.Figure:
    weeks = list(range(1, 13))
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=weeks, 
        y=sales_ts_list, 
        mode='lines+markers', 
        name='Sales',
        line=dict(color='royalblue', width=2),
        marker=dict(size=6)
    ))

    if product_restocks_lc_df is not None and not product_restocks_lc_df.empty:
        fig.add_trace(go.Bar(
            x=product_restocks_lc_df['lifecycle_week'],
            y=product_restocks_lc_df['qty'],
            name='Restock Qty',
            marker_color='rgba(255, 99, 71, 0.7)',
            opacity=0.7
        ))

    if product_price_info_row is not None and not product_price_info_row.empty:
        discount_cols = [str(i) for i in range(12)]
        discounts_present = [col for col in discount_cols if col in product_price_info_row.index]
        if discounts_present:
            for col_name in discounts_present:
                discount_rate = product_price_info_row.get(col_name, 0.0)
                week_num_for_discount_col = int(col_name) + 1
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
        margin=dict(l=40, r=40, t=80, b=40)
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
            yaxis_title="Trend Score (0-100)",
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

# --- NEW FUNCTION FOR "COULD HAVE" ---
def make_bar_chart(
    data_series: pd.Series, 
    chart_title: str, 
    category_axis_label: str = "Attribute", 
    value_axis_label: str = "Avg. Trend Score"
) -> go.Figure:
    """
    Creates a horizontal bar chart from a Pandas Series.
    Index of series = categories, values of series = bar lengths.
    """
    fig = go.Figure() # Initialize an empty figure

    if data_series is None or data_series.empty:
        fig.update_layout(
            title_text=chart_title,
            xaxis={'visible': False}, 
            yaxis={'visible': False},
            annotations=[{
                'text': 'No data available for this chart.',
                'xref': 'paper', 'yref': 'paper',
                'showarrow': False, 'font': {'size': 14}
            }]
        )
        return fig

    # For Plotly Express, convert Series to DataFrame
    df_to_plot = data_series.reset_index()
    df_to_plot.columns = [category_axis_label, value_axis_label] # Ensure correct column names
    
    # Sort by value for better visualization if not already sorted by px
    df_to_plot = df_to_plot.sort_values(by=value_axis_label, ascending=True)

    fig = px.bar(
        df_to_plot,
        x=value_axis_label,       # Values for bar length
        y=category_axis_label,    # Categories on y-axis
        orientation='h',          # Horizontal bar chart
        title=chart_title,
        labels={value_axis_label: value_axis_label, category_axis_label: category_axis_label.capitalize()},
        text=value_axis_label, # Show values on bars (might need formatting)
    )
    fig.update_traces(texttemplate='%{text:.2s}', textposition='outside') # Format text on bars, e.g. 2 sig figs
    fig.update_layout(
        # yaxis={'categoryorder':'total ascending'}, # Already sorted df_to_plot
        template="simple_white",
        height=300 + len(data_series) * 20, # Dynamic height based on number of bars
        margin=dict(l=120, r=20, t=60, b=40) # Adjust left margin for longer labels
    )
    return fig

# --- NEW FUNCTION FOR "COULD HAVE" ---
def make_weather_trend_chart(filtered_weather_df: pd.DataFrame, selected_metrics: list) -> go.Figure:
    fig = go.Figure()

    if filtered_weather_df.empty or not selected_metrics:
        fig.update_layout(
            title_text="No Data for Selected Weather Metrics/Filters",
            xaxis={'visible': False}, yaxis={'visible': False},
            annotations=[{
                'text': 'Please adjust filters or select metrics.',
                'xref': 'paper', 'yref': 'paper',
                'showarrow': False, 'font': {'size': 14}
            }]
        )
        return fig

    # Define which metrics might need a secondary y-axis based on typical scales
    # Ensure these column names exactly match those in vis2_weather_data.csv
    secondary_y_metrics = ['rain mm', 'humidity %', 'avg wind km/h', 'max wind km/h', 'gust km/h'] 
    
    primary_metrics_plotted = 0
    secondary_metrics_plotted = 0

    for metric in selected_metrics:
        if metric not in filtered_weather_df.columns or filtered_weather_df[metric].isnull().all():
            continue # Skip if metric column doesn't exist or is all NaN

        if metric in secondary_y_metrics:
            current_y_axis_assignment = 'y2'
            secondary_metrics_plotted +=1
        else:
            current_y_axis_assignment = 'y1'
            primary_metrics_plotted += 1
            
        fig.add_trace(go.Scatter(
            x=filtered_weather_df['date'],
            y=filtered_weather_df[metric],
            mode='lines', # Using lines for trends, markers can be added if preferred
            name=metric.replace('°C', 'C').replace('%','Pct').capitalize(), # Clean up names for legend
            yaxis=current_y_axis_assignment
        ))
    
    # Configure layout and axes
    layout_args = {
        "template": "simple_white",
        "xaxis_title": "Date",
        "legend": dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        "margin": dict(l=50, r=50, t=50, b=50) # Adjusted margins
    }

    if primary_metrics_plotted > 0:
        layout_args["yaxis_title"] = "Primary Metric Value"
    else: # If only secondary metrics are plotted, make y2 the primary visual
        layout_args["yaxis_title"] = "Secondary Metric Value" # Placeholder, y1 might be hidden

    if secondary_metrics_plotted > 0:
        layout_args["yaxis2"] = dict(
            title="Secondary Metric Value",
            overlaying='y',
            side='right',
            showgrid=False # Optionally hide grid for secondary axis
        )
        if primary_metrics_plotted == 0: # If only secondary, make y1 invisible
            layout_args["yaxis"] = dict(visible=False)


    fig.update_layout(**layout_args)
    return fig