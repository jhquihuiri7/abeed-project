
# Import necessary modules from Dash
from dash import Dash, dcc, html, Input, Output, callback
from components.dropdown_components import custom_features_head, list_custom_features, date_filter_dropdown
from components.button_components import button, hourButton
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
                dcc.Tab(label="Hour Filter", value="hour-filter-tab", children=[
                    html.Div(
                        children=[
                            hourButton(range(0,24)),
                            button("Apply range",id="apply_hour_range", style=button_style)
                        ],
                        className="flex flex-row w-full justify-between"
                    ),
                    html.Div(
                        dcc.RangeSlider(0, 23, 1, value=[5, 15], id='hour-filter-slider', className="w-[85%]"),
                        className="w-full mt-5"
                    )    
                ]),    # Tab for hour-based filtering
                dcc.Tab(label="Date Filter", value="date-filter-tab", children=[
                        date_filter_dropdown()
                    ]),     # Tab for day-based filtering
            ],
        ),
        className="my-10",  # CSS class to apply margin or styling
    )
