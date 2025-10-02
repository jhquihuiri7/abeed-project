# Import necessary modules from Dash
from dash import dcc, html
from components.dropdown_components import (
    custom_features_head,
    date_filter_dropdown,
    feature_filter_dropdown,
    custom_dropdow
)
from components.button_components import button, hourButton
from styles.styles import button_style, button_dropdown_style


# Define a function to create the main tabs layout
def main_tabs(client, show_custom=True):
    """
    Creates a set of tabs for filtering data based on different criteria.

    Returns:
        html.Div: A Dash HTML Div containing a Tabs component with three tabs.
    """

    # Lista de tabs, excluyendo "Custom Feature" si show_custom es False
    tabs = []

    if show_custom:
        tabs.append(
            dcc.Tab(
                label="Custom Feature",
                value="custom-feature-tab",
                children=[
                    html.Div(
                        children=[
                            custom_features_head(),
                            custom_dropdow(client=client, current_dropdown=[]),
                            
                        ],
                        className="flex flex-row justify-between",
                    ),
                    button(
                        text="Add Custom Feature",
                        id="add_custom_feature",
                        style=button_style,
                    ),  # Button to add custom feature
                ],
            )
        )

    # Agregar los otros tabs
    tabs.extend(
        [
            dcc.Tab(
                label="Feature Filter",
                value="feature-filter-tab",
                children=[feature_filter_dropdown(client)],
            ),
            dcc.Tab(
                label="Hour Filter",
                value="hour-filter-tab",
                children=[
                    html.Div(
                        children=[
                            html.Div(
                                children=[
                                    hourButton(range(0, 24)),
                                    html.Div(
                                        dcc.RangeSlider(
                                            0,
                                            23,
                                            1,
                                            value=[0, 23],
                                            id="hour-filter-slider",
                                            className="w-full",
                                        ),
                                        className="w-full mt-5",
                                    ),
                                ],
                                className="flex flex-col w-[80%] justify-center",
                            ),
                            html.Div(
                                children=[
                                    button(
                                        "Select range",
                                        id="apply_hour_range",
                                        style=button_style,
                                    ),
                                    button(
                                        "Select All",
                                        id="select_all_hour_range",
                                        style=button_style,
                                    ),
                                    button(
                                        "Deselect All",
                                        id="deselect_all_hour_range",
                                        style=button_style,
                                    ),
                                ],
                                className="flex flex-col w-[160px] justify-between",
                            ),
                        ],
                        className="w-full flex flex-row justify-between pt-5",
                    ),
                    html.Div(
                        button(
                            text="Apply selection",
                            id="apply_selection_hourfilter",
                            style=button_style,
                        ),
                        className="w-full flex flex-row justify-center pt-5",
                    ),
                ],
            ),
            dcc.Tab(
                label="Date Filter",
                value="date-filter-tab",
                children=[
                    html.Div(
                        children=date_filter_dropdown(),
                        id="date_filter_dropdown",
                        className="flex flex-row justify-around mt-10",
                    ),
                    html.Div(
                        children=[
                            button(
                                text="Select all",
                                id="select_all_datefilter",
                                style=button_style,
                            ),
                            button(
                                text="Apply selection",
                                id="apply_selection_datefilter",
                                style=f"{button_style} ml-4",
                            ),
                        ],
                        className="flex flex-row justify-center",
                    ),
                ],
            ),
        ]
    )

    return html.Div(
        children=[
            dcc.Tabs(
                id="main-tab",
                value=(
                    tabs[0].value if tabs else None
                ),  # Asegurar que el valor inicial sea válido
                children=tabs,
            ),
        ],
        className="my-10",
    )
