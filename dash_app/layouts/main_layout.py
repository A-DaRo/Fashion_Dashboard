import dash_bootstrap_components as dbc
from dash import html, dcc
from layouts.restocking_layout import restocking_tab_content # Renamed for clarity

def layout(app_instance): # Pass app object to use app.get_asset_url
    return dbc.Container([
        dbc.Row([
            dbc.Col(
                html.Img(src=app_instance.get_asset_url("intellistock_logo.png"), className="logo-img"),
                width="auto"
            ),
            dbc.Col(
                html.H1("Intellistock: Fashion Sales & Trend Forecaster", className="app-title"),
                width=True
            )
        ], className="app-header", align="center"),
        dbc.Tabs(id="tabs-main", active_tab="tab-restocking", children=[
            dbc.Tab(
                label="Restocking Intelligence",
                tab_id="tab-restocking",
                children=restocking_tab_content
            ),
            dbc.Tab(
                label="Brand & Trend Strategy",
                tab_id="tab-brand",
                children=html.Div(
                    "Brand & Trend Strategy Content Coming Soon in the Next Phase!",
                    className="p-4"
                )
            ),
        ])
    ], fluid=True)