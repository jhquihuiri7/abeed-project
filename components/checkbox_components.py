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

def expland_collapse_checkbox(client):
    return html.Div([
                html.Details([  # Equivalente a <details>
                    html.Summary("▼", className="collapse-title text-lg text-center"),  # Equivalente a <summary>
                    html.Div(main_checkbox(client,"secondary_checkbox"), className="collapse-content")  # Contenido dentro del colapso
                ], className="collapse bg-base-200")  # Clase DaisyUI para estilo
            ])

def secondary_pagination():
    return html.Div(
    className="w-full h-fit shadows-lg",
    children=[
        dcc.Store(id="current-page", data=0),  # Almacenamos la página actual
        
        html.Div(id="words-container", className="flex flex-row flex-wrap justify-between"),

        html.Div(
            style={"display": "flex", "justifyContent": "center", "marginTop": "20px"},
            children=[
                html.Button("Prev", id="prev-btn", n_clicks=0, style={"marginRight": "10px"}),
                html.Button("Next", id="next-btn", n_clicks=0),
            ],
        ),
        html.Div(id="pagination-numbers", className="flex flex-row flex-wrap mt-5")
    ]
)
    
def expandable_container(toggle_button_id, expandable_text_id, is_main=False):
    return html.Div(
                children= [
                    html.Button("Expand Main Features" if is_main else "Expand DB Features", id=toggle_button_id, n_clicks=0, className="btn btn-primary font-bold"),
                    html.Div(secondary_pagination(),
                    id=expandable_text_id, style={"display": "none"}, className="p-3 text-gray-700 shadow-lg rounded-lg")
                ],
                className="flex flex-col justify-center items-center w-full h-fit"    
            )