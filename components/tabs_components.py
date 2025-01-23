
# Import necessary modules from Dash
from dash import dcc, html
from components.dropdown_components import custom_features_head, list_custom_features, date_filter_dropdown, feature_filter_dropdown
from components.button_components import button, hourButton
from styles.styles import button_style, button_dropdown_style

# Define a function to create the main tabs layout
def main_tabs(client):
    """
    Creates a set of tabs for filtering data based on different criteria.

    Returns:
        html.Div: A Dash HTML Div containing a Tabs component with three tabs.
    """
    return html.Div(
        # Create a Tabs component inside a Div
        children=[
            dcc.Tabs(
            id="main-tab",  # Unique identifier for the Tabs component
            value="custom-feature-tab",  # Default active tab
            children=[
                # Define individual tabs with labels and values
                dcc.Tab(label="Custom Feature", value="custom-feature-tab",  children=[
                    custom_features_head(),  # Heading for custom features
                    html.Div(
                        children=[
                            html.Div(id="custom_dropdown", children=[], className="w-[1200px] flex flex-row justify-between"),  # Dropdown for custom features
                            list_custom_features(client)
                            ],
                        className = "flex flex-row justify-between",
                    ),
                    button(text="Add Custom Feature", id="add_custom_feature", style=button_style),  # Button to add custom feature
                ]),  # Tab for feature-based filtering
                dcc.Tab(label="Feature Filter", value="feature-filter-tab", children=[
                    feature_filter_dropdown(client)
                ]),  # Tab for feature-based filteringclient
                dcc.Tab(label="Hour Filter", value="hour-filter-tab", children=[
                    html.Div(
                        children=[
                            html.Div(
                                children=[
                                    hourButton(range(0,24)),
                                    html.Div(
                                        dcc.RangeSlider(0, 23, 1, value=[0, 23], id='hour-filter-slider', className="w-full"),
                                        className="w-full mt-5"
                                    ),
                                ],
                                className="flex flex-col w-[80%] justify-center"
                            ),
                            html.Div(
                                children=[
                                    button("Select range",id="apply_hour_range", style=button_style),
                                    button("Deselect range",id="remove_hour_range", style=button_style)
                                ],
                                className="flex flex-col w-[160px] justify-between"
                            ),      
                        ],
                      className="w-full flex flex-row justify-between"  
                    ),
                    button(text="Apply selection", id="apply_selection_hourfilter", style=button_style),    
                ]),    # Tab for hour-based filtering
                dcc.Tab(label="Date Filter", value="date-filter-tab", children=[
                        html.Div(
                            children=date_filter_dropdown(),
                            id= "date_filter_dropdown",
                            className="flex flex-row justify-around mt-10"
                        ),
                        html.Div(
                            children=[
                                button(text="Select all", id="select_all_datefilter", style=button_style),  # Button to add custom feature,
                                button(text="Apply selection", id="apply_selection_datefilter", style=f"{button_style} ml-4"),  # Button to add custom feature
                            ],
                            className="flex flex-row justify-end"
                        )
                    ]),     # Tab for day-based filtering
            ],
        ),
        
        ],
        className="my-10",  # CSS class to apply margin or styling
    )
