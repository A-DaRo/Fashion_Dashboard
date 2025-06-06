import dash_bootstrap_components as dbc
from dash import html, dcc

restocking_tab_content = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H4("Product Selection", className="mt-3 mb-3"),
            dcc.Dropdown(
                id="product-dropdown-restock",
                placeholder="Select a product...",
                className="mb-3"
            ),
            html.Div(id="product-image-restock", className="product-image-container mt-3"),
            html.Div(id="product-details-restock", className="mt-3 product-details-card"),
        ], md=4, className="mb-3"),
        dbc.Col([
            html.H4("Sales & Restock Timeline", className="mt-3 mb-3"),
            dcc.Graph(id="sales-restock-plot"),
            html.H5("Key Performance Indicators", className="mt-4 mb-2"), # Title for KPIs
            html.Div(id="kpi-output-restock", className="mt-2") # Placeholder for KPIs
        ], md=8, className="mb-3"),
    ])
], fluid=True, className="mt-3") # Added margin top to the container