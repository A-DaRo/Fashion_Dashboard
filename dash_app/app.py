import dash
import dash_bootstrap_components as dbc

from config import EXTERNAL_STYLESHEETS
from layouts.main_layout import layout

# Import callback registration functions
from callbacks.restocking_callbacks import register_restocking_callbacks
from callbacks.trend_callbacks import register_trend_callbacks # New import

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=EXTERNAL_STYLESHEETS,
    assets_folder="assets",
    suppress_callback_exceptions=True
)
server = app.server

# Set the app's layout
app.layout = layout(app)

# Explicitly register callbacks by passing the app instance
register_restocking_callbacks(app)
register_trend_callbacks(app) # Register new callbacks

if __name__ == "__main__":
    app.run_server(debug=True)