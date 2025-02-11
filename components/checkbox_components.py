# Import a dictionary of feature units from the backend module
from backend.db_dictionaries import feature_units_dict

# Import necessary Dash components for building the user interface
from dash import html, dcc

# Define a function to create a checkbox component
def main_checkbox(client, id):
    """
    Creates a checklist (checkbox group) for selecting features.

    Returns:
        html.Div: A Dash HTML Div containing a Checklist component for feature selection.
    """
    
    options = client.available_readable_names if id == "main_checkbox" else client.available_db_names
    if id != "main_checkbox":
        print(len(options))
    return html.Div(
        # Create a Checklist component
        dcc.Checklist(
            # Generate the options for the checklist dynamically
            # Extracts the keys (features) from the feature_units_dict
            options=[item for item in options],
            value=[],  # Default selected values (none selected initially)
            className="flex flex-row justify-between flex-wrap",  # CSS classes for layout styling
            inputClassName="mr-5",
            labelClassName="w-[350px]",  # CSS class for styling the labels of each checkbox
            id=id,  # Unique identifier for the checklist component
        ),
        className="w-full"
    )
