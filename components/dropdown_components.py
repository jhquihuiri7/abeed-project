from dash import dcc, html
from utils.styles import button_dropdown_style, button_style
from components.button_components import button
from utils.functions import list_custom_filter_children
from backend.helper_functions import get_feature_units
import calendar
from backend.Class import Ops

# Import a dictionary of feature units from the backend module
from backend.db_dictionaries import feature_units_dict


def main_dropdown(client:Ops, width="w-[28%]"):
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
            options=[item for item in client.display_features_dict],
            value="",  # Default selected values (none selected initially)
            className="w-full flex flex row flex-wrap",  # CSS classes for layout styling
            id="main_dropdown",  # Unique identifier for the checklist component
            multi=True,
            searchable=True,
            search_value="Mi",
            persistence=True,
            persistence_type='session'
        ),
        className=f"{width} mr-5"
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
            html.Div(
                children=[
                    # Input field for typing a custom feature name
                    dcc.Input(
                        id="custon_name",
                        type="text",
                        value="",
                        placeholder="Type a custom name",
                        className="mx-5",
                    ),
                    # Checklist to specify additional options, such as "Cumulative"
                    dcc.Checklist(
                        options=["Cumulative"], value=[""], inline=True, id="custom_cumulative"
                    ),
                ],
                className="flex flex-row my-4",  # Styling for the layout
            ),
            html.Div(
                dcc.Input(
                        id="custon_operation",
                        type="text",
                        value="",
                        placeholder="Write the operation",
                        className="mx-5",
                    ),
                className="w-[500px] mb-4"
            ),
        ],
        className="flex flex-col w-[40%]"
    )

# Function to dynamically create dropdowns and buttons for custom features
def custom_dropdow(client, current_dropdown):
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
    dropdown_children_second_level = []
    options = client.df.columns
    id = 0
    return html.Div(
        children=[
            html.P("Feature Requirements:", className="font-bold"),
            html.Div(
                id="custom_dropdown",
                children=[
                    alias_feature(options=options, id=id),
                    button(text="Remove last", id="remove_last_alias", style=button_style+" hidden")
                ],
                className="w-full mt-3"
            )
        ],
        className="w-[60%] mt-4"
    )


# Function to generate a date filter dropdown
def date_filter_dropdown():
    """
    Creates a set of dropdown filters for selecting year, month, and day of the week.

    Returns:
        list: A list of HTML Div elements containing dropdowns for year, month, and day.
    """
    years = [2020, 2025]  # Year range
    months = [1, 12]  # Month range
    days = [0, 7]  # Day range (0=Monday, 6=Sunday)

    # Generate month options for the dropdown
    month_names = [
        {'label': calendar.month_name[month], 'value': month}
        for month in range(months[0], months[1] + 1)
    ]

    # Generate day options for the dropdown
    day_options = [
        {'label': calendar.day_name[day], 'value': day}
        for day in range(days[0], days[1])
    ]

    # Ranges for dropdown selections
    year_range = [year for year in range(years[0], years[1] + 1)]
    month_range = [month["value"] for month in month_names]
    day_range = [day["value"] for day in day_options]

    return [
        html.Div(
            children=[
                html.H2("Year", className="font-bold text-xl"),  # Label for year dropdown
                dcc.Dropdown(
                    options= year_range,  # Options for years
                    value=year_range,  # Default selected values
                    multi=True,  # Allow multiple selections
                    id="year_dropdown_date_filter",  # Unique ID for the dropdown
                    className="w-full mt-2",  # Styling for the dropdown
                ),
            ],
            className="w-[400px]"  # Width for the Div
        ),
        html.Div(
            children=[
                html.H2("Month", className="font-bold text-xl"),  # Label for month dropdown
                dcc.Dropdown(
                    options = month_names,  # Options for months
                    value = month_range,  # Default selected values
                    multi=True,  # Allow multiple selections
                    id="month_dropdown_date_filter",  # Unique ID for the dropdown
                    className="w-full mt-2",  # Styling for the dropdown
                ),
            ],
            className="w-[400px]"  # Width for the Div
        ),
        html.Div(
            children=[
                html.H2("Day of the week", className="font-bold text-xl"),  # Label for day dropdown
                dcc.Dropdown(
                    options = day_options,  # Options for days
                    value = day_range,  # Default selected values
                    multi=True,  # Allow multiple selections
                    id="day_dropdown_date_filter",  # Unique ID for the dropdown
                    className="w-full mt-2",  # Styling for the dropdown
                ),
            ],
            className="w-[400px]"  # Width for the Div
        )
    ]

# Function to generate a feature filter dropdown
def feature_filter_dropdown(client:Ops):
    """
    Creates a feature filter dropdown with input fields for range and a button to add filters.

    Args:
        client: An object managing data features.

    Returns:
        html.Div: A Div containing the feature filter dropdown and associated controls.
    """
    return html.Div(
        className="w-full flex flex-row justify-between",  # Main container styling
        children=[
            html.Div(
                children=[
                    # Dropdown for selecting features
                    dcc.Dropdown(
                        options=[feature for feature in client.session_data_features] if (client.session_data_features != []) else [],  # Feature options
                        value=[],  # Default selected value
                        id="feature_filter_dropdown",  # Unique ID for the dropdown
                        multi=False,  # Allow single selection
                        className="w-[400px] mr-5"  # Styling for the dropdown
                    ),
                    # Range inputs for filtering
                    html.Div([
                        dcc.Input(
                            id="feature_filter_min_range",  # Unique ID for min range input
                            type="text",  # Input type
                            placeholder="- Infinity",  # Placeholder text
                            className="mx-5 w-[65px]",  # Styling for the input
                        ),
                        dcc.Input(
                            id="feature_filter_max_range",  # Unique ID for max range input
                            type="text",  # Input type
                            placeholder="+ Infinity",  # Placeholder text
                            className="mx-5 w-[65px]",  # Styling for the input
                        )
                    ]),
                    # Button to add the filter
                    html.Div(
                        button(
                            text="ADD",  # Button text
                            id="feature_filter_add",  # Unique ID for the button
                            style=button_dropdown_style,  # Styling for the button
                        )
                    )
                ],
                className="w-[65%] flex flex-row justify my-10"  # Container styling
            ),
            html.Div(
                children=[],  # Placeholder for filter list
                id="feature_filter_list",  # Unique ID for the list
                className="w-[35%] my-10 flex flex-col items-end"  # Styling for the list container
            )
        ]
    )

def cumulative_conversion_dropdown(client):
    return html.Div(
        dcc.Dropdown(
            id="cumulative_dropdown",
            value="",
            options=client.df.columns,
            className="w-full flex flex row flex-wrap",
        ),
        className="w-[28%] mr-5",
    )

def delete_features_dropdown(client):
    return html.Div(
        dcc.Dropdown(
            id="delete_features_dropdown",
            value="",
            options=client.df.columns,
            className="w-full flex flex row flex-wrap",
            multi=True
        ),
        className="w-[56%] mr-5",
    )

def custom_features_children(options, currentDropdownChildren):
    children = currentDropdownChildren
    id = len(children) if children != [] else 0
    alias = alias_feature(options=options, id=id)

    children = children[:-1]

    children.append(alias)

    if currentDropdownChildren != [] and len(currentDropdownChildren) >= 2:
        children.append(button(text="Remove last", id="remove_last_alias", style=button_style))
    else:
        children.append(button(text="Remove last", id="remove_last_alias", style=button_style+" hidden"))
    return children

def remove_features_children(currentDropdownChildren):
    if len(currentDropdownChildren) >= 3:
        currentDropdownChildren = currentDropdownChildren[:-2]

    if currentDropdownChildren != [] and len(currentDropdownChildren) >= 2:
        currentDropdownChildren.append(button(text="Remove last", id="remove_last_alias", style=button_style))
    else:
        currentDropdownChildren.append(button(text="Remove last", id="remove_last_alias", style=button_style+" hidden"))
    return currentDropdownChildren

def alias_feature(options, id):
    id_add_button = {"type": "add_custom_alias", "index": id}
    id_feature_dropdown = {"type": "feature_dropdown", "index": id}
    id_feature_alias = {"type": "feature_alias", "index": id}
    return html.Div(
                children=[
                    html.P("Alias"),
                    dcc.Input(
                        id=id_feature_alias,
                        type="text",
                        value="",
                        placeholder="Write an alias",
                        className="w-[150px]",
                    ),
                    html.P("Feature"),
                    dcc.Dropdown(
                        options= options,
                        value=[],
                        multi=False,
                        className="w-[300px]",
                        id=id_feature_dropdown
                    ),
                    button(text="+", id=id_add_button, style=button_style),
                ],
                className="flex flex-row justify-between my-4 items-end"
            )
