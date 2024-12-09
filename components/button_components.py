# Import custom styles from the styles module
from styles.styles import button_style

# Import the HTML module from Dash
from dash import html

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
