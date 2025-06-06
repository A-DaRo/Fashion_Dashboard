# dash_app/layouts/weather_layout.py

import dash_bootstrap_components as dbc
from dash import html, dcc
# from datetime import date, timedelta # No longer needed for hardcoding dates here

weather_tab_content = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H4("Weather Filters", className="mt-3 mb-3"),
            html.Label("Select Locality:", htmlFor="locality-dropdown-weather", className="form-label"),
            dcc.Dropdown(
                id="locality-dropdown-weather", 
                placeholder="Select Locality...",
                className="mb-3"
                # Options populated by callback
            ),
            html.Label("Select Date Range:", htmlFor="date-picker-weather", className="form-label"),
            dcc.DatePickerRange(
                id="date-picker-weather",
                # min_date_allowed, max_date_allowed, start_date, end_date, initial_visible_month
                # will be set by a callback after data load.
                # We can set a display format here if desired.
                display_format='YYYY-MM-DD',
                className="mb-3 d-block" # d-block for full width
            ),
            html.Label("Select Weather Metrics:", htmlFor="weather-metrics-checklist", className="form-label"),
            dcc.Checklist(
                id="weather-metrics-checklist",
                options=[ # These options are based on expected columns
                    {'label': 'Avg Temp (°C)', 'value': 'avg temp °C'},
                    {'label': 'Min Temp (°C)', 'value': 'min temp °C'},
                    {'label': 'Max Temp (°C)', 'value': 'max temp °C'},
                    {'label': 'Rainfall (mm)', 'value': 'rain mm'},
                    {'label': 'Avg Wind (km/h)', 'value': 'avg wind km/h'},
                    {'label': 'Humidity (%)', 'value': 'humidity %'},
                ],
                value=['avg temp °C', 'rain mm'],
                labelStyle={'display': 'block', 'marginBottom': '8px', 'cursor': 'pointer'},
                inputStyle={'marginRight': '5px', 'cursor': 'pointer'}
            )
        ], md=3, className="mb-3 p-3 border rounded bg-light"),
        dbc.Col([
            html.Div(id="weather-plot-title-div", className="mt-3 mb-2 text-center"),
            dcc.Loading(
                id="loading-weather-trends-plot", type="circle",
                children=dcc.Graph(id="weather-trends-plot", style={'height': '60vh'})
            )
        ], md=9, className="mb-3")
    ])
], fluid=True, className="mt-3")