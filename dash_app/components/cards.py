import dash_bootstrap_components as dbc
from dash import html

def kpi_card(title: str, value: str, icon_class: str = None, col_md_width=4, card_classname=""):
    """
    Returns a Bootstrap-styled KPI card wrapped in a dbc.Col.
    Icon class should be FontAwesome, e.g., "fas fa-shopping-cart".
    """
    card_header_content = [html.Span(title)] # Wrap title in Span for consistent styling if icon is present
    if icon_class:
        # Assumes FontAwesome is available (e.g. via Bootstrap CDN or separate CSS link)
        card_header_content.insert(0, html.I(className=f"{icon_class} me-2")) 
    
    card_content = dbc.Card([
        dbc.CardHeader(html.Div(card_header_content, className="d-flex align-items-center justify-content-center")), # Centered header
        dbc.CardBody(html.H4(value, className="card-title text-center mb-0")) # Centered body text
    ], className=f"h-100 {card_classname}") # h-100 for equal height in a row
    
    return dbc.Col(card_content, md=col_md_width, className="mb-3") # mb-3 for spacing between rows of cards