# Import necessary modules from Dash
from dash import Dash, dcc, html, Input, Output, callback

# Define a function to create the main tabs layout
def main_tabs():
    """
    Creates a set of tabs for filtering data based on different criteria.

    Returns:
        html.Div: A Dash HTML Div containing a Tabs component with three tabs.
    """
    return html.Div(
        # Create a Tabs component inside a Div
        dcc.Tabs(
            id="tabs-example-graph",  # Unique identifier for the Tabs component
            value="tab-1-example-graph",  # Default active tab
            children=[
                # Define individual tabs with labels and values
                dcc.Tab(label="Feature Filter", value="tab-1-example-graph"),  # Tab for feature-based filtering
                dcc.Tab(label="Hour Filter", value="tab-2-example-graph"),    # Tab for hour-based filtering
                dcc.Tab(label="Day Filter", value="tab-3-example-graph"),     # Tab for day-based filtering
            ],
        ),
        className="my-10",  # CSS class to apply margin or styling
    )
