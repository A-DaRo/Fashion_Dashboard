import os

# Base directory for this Dash app
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Path to the raw data folder (visuelle2)
DATA_DIR = os.path.join(BASE_DIR, "data", "visuelle2")

# Path to the assets folder (for CSS, logo, and images subfolders)
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# External stylesheets (we use a Dash Bootstrap theme)
EXTERNAL_STYLESHEETS = ["https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css"]

# Image subpath under assets: visuelle2/images/ will be inside assets/
IMAGE_ASSET_SUBPATH = os.path.join("visuelle2", "images")

# Helper to build asset URL (Dash's app.get_asset_url is preferred when app object is available)
def get_static_asset_url(filename):
    return f"/assets/{filename}"