# Import custom styles from the styles module
from styles.styles import button_style, hourButtonStyle
import dash_daq as daq

# Import the HTML module from Dash
from dash import html, dcc

# Define a function to create a button using Dash
def button(text, id, style):
    """
    Creates an HTML button with custom properties.

    Args:
        text (str): The text to display on the button.
        id (str): A unique identifier for the button.
        style (str): A CSS class name to apply styles to the button.

    Returns:
        dash.html.Button: A button component with the specified properties.
    """
    # Create and return an HTML button with the given parameters
    return html.Button(
        text,        # Text displayed on the button
        id=id,       # Unique ID for the button
        n_clicks=0,  # Initial click count set to 0
        className=style  # CSS class for styling the button
    )

# Define a function to create a row of hour buttons
def hourButton(hours):
    """
    Creates a row of buttons for each hour provided in the list.

    Args:
        hours (list): List of hour strings to create buttons for.

    Returns:
        dash.html.Div: A div containing a row of buttons, each representing an hour.
    """
    return html.Div(
        children=[
            # Create a button for each hour in the provided list
            html.Button(
                hour,  # Text displayed on the button
                id={"type": "hour_button", "index": hour},  # Unique ID for the button
                n_clicks=0,  # Initial click count set to 0
                style={"backgroundColor": "#d9d9d9"},  # Default background color
                className=hourButtonStyle  # CSS class for styling the button
            ) for hour in hours
        ],
        className="flex flex-row w-full justify-between",
        id="hour_filter_buttons"# CSS class for layout styling
    )

# Define a function to create a toggle switch for applying filters
def apply_filters_toggle(action):
    """
    Creates a toggle switch component for applying filters with an optional checklist.

    Args:
        action (str): Label to display next to the toggle switch.

    Returns:
        dash.html.Div: A div containing a checklist and a toggle switch for filter application.
    """
    return html.Div(
        children=[
            # Checklist to indicate whether the filters should be applied
            dcc.Checklist(
                options=["Apply filter"],  # Option displayed in the checklist
                value=[],  # Default value (unchecked)
                className="mb-2",  # CSS class for margin styling
                id="apply_filters"  # ID for the checklist
            ),
            # Toggle switch with a label
            html.Div(
                daq.ToggleSwitch(
                    id='collapse_expand_filter',  # Unique ID for the toggle switch
                    value=True,  # Default value (enabled)
                    label=action,  # Label displayed next to the switch
                    labelPosition='right',  # Position of the label
                    color="#1975fa",  # Color of the toggle switch
                    disabled=True  # Disable interaction by default
                ),
                className="ml-5 w-[150px]"  # CSS class for layout and width
            )
        ],
        className="flex flex-col"  # CSS class for column layout
    )
