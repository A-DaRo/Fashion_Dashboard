# dash_app/app.py

import dash
import dash_bootstrap_components as dbc

from config import EXTERNAL_STYLESHEETS
from layouts.main_layout import layout # layout function

# Import the function that registers callbacks
from callbacks.restocking_callbacks import register_restocking_callbacks

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
register_restocking_callbacks(app) # <-- CALL THE FUNCTION HERE

if __name__ == "__main__":
    app.run_server(debug=True)