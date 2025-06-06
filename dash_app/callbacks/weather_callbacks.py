# dash_app/callbacks/weather_callbacks.py

from dash import Input, Output, html, dcc, callback_context, State # Added State
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta # Keep for calculating default start_date

from utils.data_loader import get_weather_df
from components.charts import make_weather_trend_chart

# Load data once at module startup
weather_df_full = get_weather_df()
print("--- DEBUG: Weather DF loaded (weather_callbacks module) ---")
if not weather_df_full.empty:
    # Ensure 'date' column is datetime type after loading
    weather_df_full['date'] = pd.to_datetime(weather_df_full['date'], errors='coerce')
    weather_df_full.dropna(subset=['date'], inplace=True) # Remove rows where date conversion failed
    if weather_df_full.empty:
        print("Warning: Weather DataFrame became empty after date parsing/cleaning.")
else:
    print("Warning: Weather DataFrame is empty in weather_callbacks.")

def register_weather_callbacks(app_instance):
    print("--- DEBUG: Registering weather_callbacks ---")

    @app_instance.callback(
        [Output("locality-dropdown-weather", "options"),
         Output("locality-dropdown-weather", "value")],
        [Input("locality-dropdown-weather", "id")] 
    )
    def populate_locality_dropdown(dropdown_id):
        if not weather_df_full.empty and 'locality' in weather_df_full.columns:
            try:
                localities = sorted(weather_df_full['locality'].dropna().unique())
                options = [{"label": str(loc), "value": loc} for loc in localities]
                value = localities[0] if localities else None
                return options, value
            except Exception as e:
                return [], None
        return [], None

    # --- NEW CALLBACK TO SET DATE PICKER RANGE ---
    @app_instance.callback(
        [Output("date-picker-weather", "min_date_allowed"),
         Output("date-picker-weather", "max_date_allowed"),
         Output("date-picker-weather", "initial_visible_month"),
         Output("date-picker-weather", "start_date"),
         Output("date-picker-weather", "end_date")],
        [Input("locality-dropdown-weather", "value")] # Trigger when locality is selected (or on first load if value is set)
                                                     # Or use Input("date-picker-weather", "id") to trigger once
    )
    def set_date_picker_ranges(selected_locality): # selected_locality can be used if ranges depend on it, otherwise just a trigger
        # print(f"--- DEBUG WeatherCB: Setting date picker ranges. Locality: {selected_locality} ---")
        if not weather_df_full.empty and 'date' in weather_df_full.columns:
            min_date_data = weather_df_full['date'].min()
            max_date_data = weather_df_full['date'].max()

            if pd.isna(min_date_data) or pd.isna(max_date_data):
                # Fallback if dates are all NaT after parsing
                # print("--- DEBUG WeatherCB: Min/Max dates are NaN, using fallback. ---")
                today = date.today()
                min_date_allowed = today - timedelta(days=365*5)
                max_date_allowed = today
                initial_month = max_date_allowed - timedelta(days=30)
                start_date_val = max_date_allowed - timedelta(days=365)
                end_date_val = max_date_allowed
            else:
                min_date_allowed = min_date_data.date()
                max_date_allowed = max_date_data.date()
                
                # Default to last year of data, or full range if less than a year
                end_date_val = max_date_allowed
                start_date_val = max_date_allowed - timedelta(days=365)
                if start_date_val < min_date_allowed:
                    start_date_val = min_date_allowed
                
                initial_month = end_date_val # Show the end of the range initially

            # print(f"--- DEBUG WeatherCB: Date Picker Ranges - Min: {min_date_allowed}, Max: {max_date_allowed}, Start: {start_date_val}, End: {end_date_val} ---")
            return min_date_allowed, max_date_allowed, initial_month, start_date_val, end_date_val
        
        # Fallback if weather_df is empty
        # print("--- DEBUG WeatherCB: weather_df_full empty or no 'date' col, using default date ranges. ---")
        today = date.today()
        return (today - timedelta(days=365*5)), today, today, (today - timedelta(days=365)), today


    @app_instance.callback(
        [Output("weather-trends-plot", "figure"),
         Output("weather-plot-title-div", "children")],
        [Input("locality-dropdown-weather", "value"),
         Input("date-picker-weather", "start_date"),
         Input("date-picker-weather", "end_date"),
         Input("weather-metrics-checklist", "value")]
    )
    def update_weather_plot(selected_locality, start_date_str, end_date_str, selected_metrics):
        ctx = callback_context
        empty_fig = go.Figure().update_layout(title_text="Select filters to view weather data")
        default_title = html.H5("Complete selections to view weather trends", className="text-center text-muted")

        if not (selected_locality and start_date_str and end_date_str and selected_metrics):
            # This condition handles both initial load (where ctx.triggered might be complex)
            # and cases where user has de-selected something vital.
            # Only show specific warning if it was a user action that made inputs incomplete.
            if ctx.triggered and any(p['value'] is None or (isinstance(p['value'], list) and not p['value']) for p in ctx.inputs_list[0]):
                 default_title = html.H5("Please complete all filter selections.", className="text-center text-warning")
            return empty_fig, default_title

        if weather_df_full.empty:
            return empty_fig, html.H5("Weather data is not available.", className="text-center text-danger")

        try:
            start_date = pd.to_datetime(start_date_str).date()
            end_date = pd.to_datetime(end_date_str).date()
        except Exception:
            return empty_fig, html.H5("Invalid date format selected.", className="text-center text-danger")

        # Ensure 'date' column is in datetime format for filtering
        # This should already be done at module level load, but double check
        if 'date' not in weather_df_full.columns or weather_df_full['date'].dtype != 'datetime64[ns]':
             weather_df_full['date'] = pd.to_datetime(weather_df_full['date'], errors='coerce')
             weather_df_full.dropna(subset=['date'], inplace=True)
             if weather_df_full.empty:
                  return empty_fig, html.H5("Weather data has invalid dates.", className="text-center text-danger")


        filtered_df = weather_df_full[
            (weather_df_full['locality'] == selected_locality) &
            (weather_df_full['date'].dt.date >= start_date) &
            (weather_df_full['date'].dt.date <= end_date)
        ].copy()

        if filtered_df.empty:
            return go.Figure().update_layout(title=f"No weather data for '{selected_locality}' in selected range."), \
                   html.H5(f"No Data: {selected_locality}", className="text-center")
        
        fig = make_weather_trend_chart(filtered_df, selected_metrics)
        plot_title_text = f"Weather Trends for {selected_locality} ({start_date_str} to {end_date_str})"
        
        return fig, html.H5(plot_title_text, className="text-center")