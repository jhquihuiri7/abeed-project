# Import a dictionary of feature units from the backend module
from backend.db_dictionaries import feature_units_dict

# Import necessary Dash components for building the user interface
from dash import html, dcc
from backend.Class import Ops

# Define a function to create a checkbox component
def main_checkbox(client, id):
    """
    Creates a checklist (checkbox group) for selecting features.

    Returns:
        html.Div: A Dash HTML Div containing a Checklist component for feature selection.
    """
    
    options = client.available_readable_names if id == "main_checkbox" else client.available_db_names[:45]

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

def pagination(page_store_id, features_id, prev_id, next_id, pagination_id, is_main=False):
    display = "hidden" if is_main else "flex"
    return html.Div(
    className="w-full h-fit shadows-lg",
    children=[
        dcc.Store(id=page_store_id, data=0),  # Almacenamos la página actual
        
        html.Div(id=features_id, className="flex flex-row flex-wrap justify-between"),


    ]
)
    
def expandable_container(toggle_button_id, expandable_text_id, client: Ops):
    return html.Div(
                children= [
                    html.Div(
                        children=[
                            html.Button("Expand Feature Menu", id=toggle_button_id, n_clicks=0, className="btn btn-primary font-bold"),
                            dcc.Checklist(
                                options=["DB features"],
                                value=[],  # Default selected values (none selected initially)
                                className="flex flex-row justify-between flex-wrap mx-10",  # CSS classes for layout styling
                                inputClassName="mr-5",
                                id="all_features_checkbox",  # Unique identifier for the checklist component
                            ),
                        ],
                        className="flex flex-row"    
                    ),
                    html.Div(
                        html.Div(
                            html.Div(
                                [html.Div(i, className="w-[300px] overflow-hidden mt-1") 
                                 for i in client.db_name_dict], 
                                className="flex flex-row flex-wrap justify-between"),
                            className="w-full h-fit shadows-lg"
                        ),
                    id=expandable_text_id, style={"display": "none"}, className="p-3 text-gray-700 shadow-lg rounded-lg")
                ],
                className="flex flex-col justify-center items-center w-[60%] h-fit"    
            )