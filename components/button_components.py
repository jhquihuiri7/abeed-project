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

def hourButton(hours):
    return html.Div(
        children=[
        html.Button(
        hour,        # Text displayed on the button
        id={"type": "hour_button", "index": hour},       # Unique ID for the button
        n_clicks=0,  # Initial click count set to 0
        style={"backgroundColor": "white"},
        className=hourButtonStyle  # CSS class for styling the button
    ) for hour in hours
    ],
    className="flex flex-row w-full justify-between"
    )

def apply_filters_toggle(action):
    return html.Div(
        children=[
            dcc.Checklist(
              options=["Apply filter"],
              value=[],
              className="mb-2",
              id="apply_filters"
            ),
            html.Div(
                daq.ToggleSwitch(
                id='collapse_expand_filter',
                value=True,
                label=action,
                labelPosition='right',
                color= "#1975fa",
                disabled=True
                ),
                className="ml-5 w-[150px]"
            )
        ],
        className="flex flex-col"
    )