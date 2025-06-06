import dash_bootstrap_components as dbc
from dash import html, dcc
from layouts.restocking_layout import restocking_tab_content
from layouts.brand_layout import brand_tab_content # Import new layout

def layout(app_instance):
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
            dbc.Tab( # Modified to use the new brand_tab_content
                label="Brand & Trend Strategy",
                tab_id="tab-brand",
                children=brand_tab_content
            ),
        ])
    ], fluid=True, className="pt-3") # Added some padding top to the main container