import dash_bootstrap_components as dbc
from dash import html, dcc
from components.dropdowns import make_attribute_type_dropdown, make_specific_attribute_dropdown

brand_tab_content = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.H4("Trend Explorer", className="mt-3 mb-3"),
            make_attribute_type_dropdown(dropdown_id="attribute-type-dropdown-brand"), # Ensure unique ID
            make_specific_attribute_dropdown(dropdown_id="specific-attribute-dropdown-brand"), # Ensure unique ID
            dcc.Graph(id="google-trends-plot-brand", className="mt-3") # Ensure unique ID
        ], md=6, className="mb-3"),
        dbc.Col([
            html.H4("Top Trending Attributes (Last 90 days)", className="mt-3 mb-3"),
            html.Div(
                "Top trending attribute charts will be implemented in the 'COULD HAVE' phase.", 
                id="top-trending-charts-placeholder", 
                className="p-3 border rounded bg-light text-muted text-center h-100 d-flex align-items-center justify-content-center"
            ) # Placeholder
        ], md=6, className="mb-3")
    ], className="align-items-stretch") # To make columns in row stretch to same height if content differs
], fluid=True, className="mt-3")