import dash_bootstrap_components as dbc
from dash import html, dcc
from components.dropdowns import make_attribute_type_dropdown, make_specific_attribute_dropdown

brand_tab_content = dbc.Container([
    dbc.Row([
        dbc.Col([ # Trend Explorer
            html.H4("Trend Explorer", className="mt-3 mb-3"),
            make_attribute_type_dropdown("attribute-type-dropdown-brand"),
            make_specific_attribute_dropdown("specific-attribute-dropdown-brand"),
            dcc.Loading( # Wrap graph in Loading component
                id="loading-google-trends-plot",
                type="circle", # or "default", "cube", "dot"
                children=dcc.Graph(id="google-trends-plot-brand", className="mt-3")
            )
        ], md=6, className="mb-3"),
        dbc.Col([ # Top Trending Attributes
            html.H4("Top Trending Attributes (Last 90 days)", className="mt-3 mb-3"),
            dcc.Loading(
                id="loading-top-category-trends", type="circle",
                children=dcc.Graph(id="top-category-trends-plot")
            ),
            dcc.Loading(
                id="loading-top-color-trends", type="circle",
                children=dcc.Graph(id="top-color-trends-plot", className="mt-3")
            )
        ], md=6, className="mb-3")
    ], className="align-items-stretch mb-3"),
    dbc.Row([ # Product Trend Alignment
        dbc.Col([
            html.H4("Product Trend Alignment", className="mt-4 mb-3"),
            dcc.Dropdown(
                id="product-dropdown-brand",
                placeholder="Select a product to see its trend alignment...",
                className="mb-3"
                # Options populated by callback
            ),
            dcc.Loading(
                id="loading-product-trend-comparison", type="circle",
                children=html.Div(id="product-trend-comparison", className="mt-3")
            )
        ])
    ], className="mt-3")
], fluid=True, className="mt-3")