from dash import dcc

def make_attribute_type_dropdown(dropdown_id: str, default_value: str = "category"):
    return dcc.Dropdown(
        id=dropdown_id,
        options=[
            {"label": "Product Category Trends", "value": "category"},
            {"label": "Color Trends", "value": "color"},
            {"label": "Fabric Trends", "value": "fabric"},
        ],
        value=default_value,
        clearable=False,
        className="mb-3" # Bootstrap margin bottom
    )

def make_specific_attribute_dropdown(dropdown_id: str):
    return dcc.Dropdown(
        id=dropdown_id,
        placeholder="Select specific attribute...",
        className="mb-3"
        # Options and value will be set by a callback
    )