from dash import dcc, html, Input, Output, State, callback, callback_context, ALL
from styles.styles import button_dropdown_style
from components.button_components import button
from utils.functions import list_custom_filter_children
from backend.helper_functions import get_feature_units
import calendar

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
    first_feature_unit = ""
    dropdown_children = []
    for index, (data, dropdown_value, radio_value) in enumerate(
            zip(list, dropdown_values, radio_values)
        ):
        if index == 0:
            try:
                first_feature_unit = get_feature_units(dropdown_value)
            except:
                pass
            
        dropdown_children.append(
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
                        options= options if index == 0 else [option for option in options if get_feature_units(option) == first_feature_unit], # Dropdown options
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
        )    
    
    return dropdown_children

def list_custom_features(client):
    return html.Div(
        id="list_custom_features",
        children=list_custom_filter_children(client)
    )

def date_filter_dropdown():
    years = [2020,2025]
    months = [1,12]
    days = [0,7]
    month_names = [
    {'label': calendar.month_name[month], 'value': month}
    for month in range(months[0], months[1] + 1)
    ]
    day_options = [
    {'label': calendar.day_name[day], 'value': day}
    for day in range(days[0], days[1])
    ]
    
    return html.Div(
        children=[
            dcc.Dropdown(
                [year for year in range(years[0], years[1]+1)],
                [],
                multi=True,
                className="w-[400px]",
            ),
            dcc.Dropdown(
                month_names,
                [],
                multi=True,
                className="w-[400px]",
            ),
            dcc.Dropdown(
                day_options,
                [],
                multi=True,
                className="w-[400px]",
            ),
        ],
        className="flex flex-row justify-around mt-10"
    )
    
    