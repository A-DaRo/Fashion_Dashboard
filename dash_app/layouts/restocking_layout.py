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
        ], md=4, className="mb-3"), # Added mb-3 for spacing on small screens
        dbc.Col([
            html.H4("Sales & Restock Timeline", className="mt-3 mb-3"),
            dcc.Graph(id="sales-restock-plot"), # Plot will be empty for this MVP
        ], md=8, className="mb-3"),
    ])
], fluid=True)