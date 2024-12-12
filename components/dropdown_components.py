from dash import dcc, html, Input, Output, State, callback, callback_context, ALL
from styles.styles import button_dropdown_style
from components.button_components import button
from utils.functions import list_custom_filter_children

# Import a dictionary of feature units from the backend module
from backend.db_dictionaries import feature_units_dict


def main_dropdown():
    """
    Creates a checklist (checkbox group) for selecting features.

    Returns:
        html.Div: A Dash HTML Div containing a Checklist component for feature selection.
    """
    return html.Div(
        # Create a Checklist component
        dcc.Dropdown(
            # Generate the options for the checklist dynamically
            # Extracts the keys (features) from the feature_units_dict
            options=[item[0] for item in feature_units_dict.items()],
            value="",  # Default selected values (none selected initially)
            className="w-full flex flex row flex-wrap",  # CSS classes for layout styling
            id="main_dropdown",  # Unique identifier for the checklist component
        ),
        className="w-[28%]"
    )


# Function to create the header for the custom features section
def custom_features_head():
    """
    Creates the header section for the 'Custom Features' feature.

    Returns:
        html.Div: A container with a title, input field for custom names, and a checklist for options.
    """
    return html.Div(
        children=[
            # Title for the section
            html.H2("Custom Features", className="font-bold text-xl"),
            # Input field for typing a custom feature name
            dcc.Input(
                id="custon_name",
                type="text",
                placeholder="Type a custom name",
                className="mx-5",
            ),
            # Checklist to specify additional options, such as "Cumulative"
            dcc.Checklist(
                options=["Cumulative"], value=[""], inline=True, id="custom_cumulative"
            ),
        ],
        className="flex flex-row my-4",  # Styling for the layout
    )

# Function to dynamically create dropdowns and buttons for custom features
def custom_dropdow(options, dropdown_values, radio_values, list):
    """
    Dynamically creates dropdown menus and buttons for custom feature operations.

    Args:
        options (list): List of options for the dropdown menu.
        dropdown_values (list): Current selected values for each dropdown.
        radio_values (list): Current selected values for each radio button.
        list (list): Data for the custom features, including operations.

    Returns:
        list: A list of `html.Div` elements representing the dropdown and button components.
    """
    return [
        html.Div(
            children=[
                # Radio buttons to select an operation (Add/Subtract)
                dcc.RadioItems(
                    id={"type": "operation_custom_feature_op", "index": index},
                    options=[
                        {"label": "Add", "value": "Add"},
                        {"label": "Sub", "value": "Sub"},
                    ],
                    value=radio_value,  # Current selected operation
                    labelStyle={"display": "inline", "margin-right": "15px"},
                    # Hide the radio buttons for the first element
                    style={"display": "none"} if index == 0 else {},
                ),
                # Dropdown menu to select feature options
                dcc.Dropdown(
                    options=options,  # Dropdown options
                    value=dropdown_value,  # Current selected value
                    id={"type": "dynamic-dropdown", "index": index},
                    className="w-[400px]",
                ),
                # Button to add a new feature
                button(
                    text="ADD",
                    id={"type": "operation_custom_feature_add", "index": index},
                    style=button_dropdown_style,
                ),
                # Button to remove the feature if an operation is defined
                (
                    html.Div()
                    if not data.get("Operation")  # Check if an operation exists
                    else button(
                        text="REMOVE",
                        id={"type": "operation_custom_feature_remove", "index": index},
                        style=button_dropdown_style,
                    )
                ),
            ],
            # Layout styling for the dropdown and buttons
            className=f"flex flex-row ml-[{index*25}px] my-4",
        )
        for index, (data, dropdown_value, radio_value) in enumerate(
            zip(list, dropdown_values, radio_values)
        )  # Iterate through the input lists to generate components
    ]

def list_custom_features(client):
    return html.Div(
        id="list_custom_features",
        children=list_custom_filter_children(client)
    )
    