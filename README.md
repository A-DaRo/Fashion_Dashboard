# Fashion_Dashboard
Dash dashboard for Data Driven Business creation project

---

## MoSCoW Prioritization Plan: Intellistock Dash App:

**Explicit Exclusions for this Plan (Not to be loaded or used):**

*   `category_labels.pt`
*   `color_labels.pt`
*   `fabric_labels.pt`
*   `stfore_sales_norm_scalar.npy`
*   `stfore_test.csv`
*   `stfore_train.csv`
*   `shop_weather_pairs.pt` (and any functionality relying on it, like direct retail-to-locality mapping if it was sourced from here)

---

### **MUST HAVE (Core MVP - Focus on Restocking Intelligence)**

Goal: A user can select a product (by `external_code`) and see its basic sales data, image, and details.

1.  **Basic App Setup & Configuration:**
    *   **`dash_app/config.py`**: (No change from previous plan)
    *   **`dash_app/app.py`**: (No change from previous plan)
    *   **`dash_app/assets/custom.css`**: (No change from previous plan)
    *   **`dash_app/assets/intellistock_logo.png`**: (No change from previous plan)
    *   **`dash_app/requirements.txt`**: (No change from previous plan)

2.  **Core Data Loading (Sales Data):**
    *   **`dash_app/utils/__init__.py`**: Empty.
    *   **`dash_app/utils/data_loader.py`**:
        *   Content:
            *   `get_sales_df()`: Loads `sales.csv`, `parse_dates=['release_date']`.
            *   **No functions to load `.pt` or `.npy` files listed in exclusions.**
        *   Function: Centralized sales data loading.

3.  **Basic Layouts (Main Shell & Restocking Tab Structure):**
    *   **`dash_app/layouts/__init__.py`**: Empty.
    *   **`dash_app/layouts/restocking_layout.py`**: (No change from previous plan – placeholders are fine)
    *   **`dash_app/layouts/main_layout.py`**:
        *   Content: `layout(app)` function defining main structure. Initially, tabs will be "Restocking Intelligence" and "Brand & Trend Strategy". (Weather tab added in "COULD HAVE").
        *   Function: Defines the overall app page structure and navigation.

4.  **Core Callbacks (Restocking Tab - Product Selection & Display):**
    *   **`dash_app/callbacks/__init__.py`**: Empty.
    *   **`dash_app/callbacks/restocking_callbacks.py`**:
        *   Content: (As per previous revised plan, focusing on `sales_df` for product info, image, details. Sales plot returns empty initially).
            *   Product dropdown options from unique `external_code` in `sales_df`.
        *   Function: Handles product selection, displaying its image and details.

---

### **SHOULD HAVE (Enhance Restocking, Basic Brand/Trend)**

Goal: Complete the Restocking Intelligence tab with charts and KPIs. Introduce the basic Brand & Trend Strategy tab.

1.  **Enhanced Data Loading & Processing:**
    *   **`dash_app/utils/data_loader.py`** (Modify):
        *   Content:
            *   `get_restock_df()`: Loads `restocks.csv`.
            *   `get_price_df()`: Loads `price_discount_series.csv`.
            *   `get_gtrends_df()`: Loads `vis2_gtrends_data.csv`, `parse_dates=['date']`.
            *   **NEW**: `get_weather_df()`: Loads `vis2_weather_data.csv`, `parse_dates=['date']`.
        *   Function: Load additional necessary data.
    *   **`dash_app/utils/data_processing.py`**:
        *   Content:
            *   `compute_weekly_sales_timeseries(sales_row: pd.Series) -> list`: Extracts sales from `sales.csv` columns `'0'`-`'11'`.
            *   `map_restock_to_lifecycle(restocks_df: pd.DataFrame, selected_product_row: pd.Series) -> pd.DataFrame`: Filters `restocks_df` by `external_code` & `retail` from `selected_product_row` and uses `release_date`.
            *   `get_unique_attributes_from_gtrends(gtrends_df: pd.DataFrame, sales_df: pd.DataFrame, attribute_type: str) -> list`: Derives unique categories/colors/fabrics from `sales_df`, then filters `gtrends_df` columns. (Does NOT use `.pt` files).
        *   Function: Core data transformation logic.
    *   **`dash_app/utils/constants.py`**: (No change - still optional, can derive dynamically).

2.  **Reusable UI Components:**
    *   **`dash_app/components/__init__.py`**: Empty.
    *   **`dash_app/components/charts.py`**:
        *   Content: `make_sales_restock_figure()`, `make_trend_line_chart()`. (Logic as per previous revised plan, using correct column names from `df_heads.txt`).
        *   Function: Generates standardized charts.
    *   **`dash_app/components/cards.py`**: (No change)
    *   **`dash_app/components/dropdowns.py`**: (No change)

3.  **Complete Restocking Callbacks & Layout:**
    *   **`dash_app/layouts/restocking_layout.py`** (Modify): Add `html.Div(id="kpi-output-restock")`.
    *   **`dash_app/callbacks/restocking_callbacks.py`** (Modify `update_restock_tab`): (Logic as per previous revised plan for full chart and KPIs).

4.  **Basic Brand & Trend Layout & Callbacks:**
    *   **`dash_app/layouts/brand_layout.py`**: (No change)
    *   **`dash_app/callbacks/trend_callbacks.py`**:
        *   Content: (As per previous revised plan, for `update_specific_attribute_dropdown` and `update_gtrends_plot`).

---

### **COULD HAVE (Full Feature Set, New Insights, Polish)**

Goal: Implement advanced brand/trend features, add a new Weather Insights tab, and add polish.

1.  **Advanced Brand & Trend Features:**
    *   **`dash_app/utils/data_processing.py`** (Modify): Add `compute_top_trending()`.
    *   **`dash_app/components/charts.py`** (Modify): Add `make_bar_chart()`.
    *   **`dash_app/layouts/brand_layout.py`** (Modify): Add `product-dropdown-brand` and `product-trend-comparison` div.
    *   **`dash_app/callbacks/trend_callbacks.py`** (Modify): Add `update_top_trending_attributes` and `update_product_trend_comparison` callbacks.

2.  **NEW: Weather Insights Tab Implementation:**
    *   **`dash_app/layouts/weather_layout.py` (New File)**:
        *   Content: `weather_tab` variable. Defines UI:
            *   `dcc.Dropdown(id="locality-dropdown-weather")` (options populated from unique `vis2_weather_data['locality']`).
            *   `dcc.DatePickerRange(id="date-picker-weather")`.
            *   `dcc.Checklist(id="weather-metrics-checklist")` (options like 'Avg Temp', 'Rainfall').
            *   `dcc.Graph(id="weather-trends-plot")`.
        *   Function: Defines the static UI for the weather tab.
    *   **`dash_app/layouts/main_layout.py` (Modify)**:
        *   Content: Import `weather_tab` from `weather_layout.py` and add it as a new `dbc.Tab` in the main `dbc.Tabs`.
        *   Function: Integrate the new tab into the app.
    *   **`dash_app/callbacks/weather_callbacks.py` (New File)**:
        *   Content:
            *   Load `weather_df = get_weather_df()` at module level.
            *   Populate `locality-dropdown-weather` options dynamically.
            *   `@app.callback` `update_weather_plot`:
                *   Inputs: `locality-dropdown-weather`, `date-picker-weather`, `weather-metrics-checklist`.
                *   Output: `weather-trends-plot` figure.
                *   Logic: Filter `weather_df` by selected locality and date range. Call a new chart function from `components/charts.py` to plot selected weather metrics over time.
        *   Function: Handles interactivity for the weather tab.
    *   **`dash_app/components/charts.py` (Modify)**:
        *   Content: Add `make_weather_trend_chart(filtered_weather_df, selected_metrics)`:
            *   Takes filtered weather data.
            *   Plots selected metrics (e.g., 'avg temp °C', 'rain mm') against 'date'. Can use subplots or multiple traces if multiple metrics are selected.
        *   Function: Generates weather trend charts.
    *   **`dash_app/utils/data_processing.py` (Potentially Modify/Add)**:
        *   Content: If complex filtering or aggregation of weather data is needed beyond basic Pandas slicing, add helper functions here.
        *   Function: Weather data manipulation utilities.

3.  **Offline Scripts & Data Exploration:**
    *   **`intellistock_mvp/prepare_data.py`**: (No change)
    *   **`intellistock_mvp/scripts/train_sales_forecaster.py`**: (This script would use the excluded `.npy` / `.csv` files for training its model. Its existence is fine as an offline tool, but its outputs are not directly used by the dashboard UI in this plan).
    *   **`intellistock_mvp/design_helper.ipynb`**: (No change)

4.  **Refinements:** (No change - CSS, error handling, loading states).

---

### **WON'T HAVE (For this Iteration/Initial Release)**

*   **Direct use of `.pt`, `.npy`, `stfore_*.csv` files within the Dash app's `data_loader.py` or callbacks.**
*   **Live Sales Forecasting Integration using models trained from the excluded files.**
*   **Direct use of `customer_data.csv` in the initial Weather Insights tab** (e.g., overlaying sales on weather charts). This would be a subsequent enhancement, potentially requiring linking `retail` to `locality` and aggregating sales.
*   (Other items from original "WON'T HAVE" remain, such as user auth, DB backend, etc.).

---