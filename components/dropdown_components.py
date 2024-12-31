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
                        labelStyle={"display": "inline", "marginRight": "15px"},
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

# Function to list custom features for a client
def list_custom_features(client):
    """
    Creates a Div containing a list of custom features for the client.

    Args:
        client: An object managing custom features.

    Returns:
        html.Div: A Div containing the list of custom features.
    """
    return html.Div(
        id="list_custom_features",  # Unique ID for the Div
        children=list_custom_filter_children(client)  # List of child elements from client features
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
                    year_range,  # Options for years
                    year_range,  # Default selected values
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
                    month_names,  # Options for months
                    month_range,  # Default selected values
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
                    day_options,  # Options for days
                    day_range,  # Default selected values
                    multi=True,  # Allow multiple selections
                    id="day_dropdown_date_filter",  # Unique ID for the dropdown
                    className="w-full mt-2",  # Styling for the dropdown
                ),
            ],
            className="w-[400px]"  # Width for the Div
        )
    ]

# Function to generate a feature filter dropdown
def feature_filter_dropdown(client):
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
                        options=[feature for feature in client.data_features],  # Feature options
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
