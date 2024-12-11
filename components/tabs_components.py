# Import necessary modules from Dash
from dash import Dash, dcc, html, Input, Output, callback
from components.dropdown_components import custom_features_head, list_custom_features
from components.button_components import button
from styles.styles import button_style

# Define a function to create the main tabs layout
def main_tabs(client):
    """
    Creates a set of tabs for filtering data based on different criteria.

    Returns:
        html.Div: A Dash HTML Div containing a Tabs component with three tabs.
    """
    return html.Div(
        # Create a Tabs component inside a Div
        dcc.Tabs(
            id="main-tab",  # Unique identifier for the Tabs component
            value="custom-feature-tab",  # Default active tab
            children=[
                # Define individual tabs with labels and values
                dcc.Tab(label="Custom Feature", value="custom-feature-tab",  children=[
                    custom_features_head(),  # Heading for custom features
                    html.Div(
                        children=[
                            html.Div(id="custom_dropdown", children=[], className="w-full"),  # Dropdown for custom features
                            list_custom_features(client)
                            ],
                        className = "flex flex-row justify-between",
                    ),
                    button(text="Add Custom Feature", id="add_custom_feature", style=button_style),  # Button to add custom feature
                ]),  # Tab for feature-based filtering
                dcc.Tab(label="Feature Filter", value="tab-1-example-graph", children=[html.H1("Tab 2")]),  # Tab for feature-based filtering
                dcc.Tab(label="Hour Filter", value="tab-2-example-graph", children=[html.H1("Tab 3")]),    # Tab for hour-based filtering
                dcc.Tab(label="Day Filter", value="tab-3-example-graph", children=[html.H1("Tab 4")]),     # Tab for day-based filtering
            ],
        ),
        className="my-10",  # CSS class to apply margin or styling
    )
