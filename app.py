# packages needed
import dash
from dash import dcc, html, Input, Output, State, callback, callback_context, ALL
from components.checkbox_components import main_checkbox
from components.daterange_components import main_daterange
from components.tabs_components import main_tabs
from components.button_components import button
from utils.functions import update_graph, add_graph, remove_graph, list_custom_filter_children, remove_custom_feature_from_graphs
from utils.logic_functions import update_custom_feature
from components.graph_components import multi_chart
from components.dropdown_components import custom_features_head, custom_dropdow
import plotly.graph_objects as go
from backend.Class import Ops
from styles.styles import button_style
from backend.db_dictionaries import feature_units_dict


# Initialize the client and global variables
client = Ops()
fig = go.Figure()
custom_feature = []
features_selected = []

# External scripts (e.g., TailwindCSS)
external_scripts = [{"src": "https://cdn.tailwindcss.com"}]

# Initialize the Dash app
app = dash.Dash(
    __name__,
    external_scripts=external_scripts,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Abeed project"
# app._favicon = "favicon.ico"
app.layout = html.Div(
    className="m-10",
    children=[
        main_checkbox(),  # Checkbox component for feature selection
        main_daterange(),  # Date range component
        button(text="Update Graph", id="update_graph_button", style=button_style),  # Button to update graph
        main_tabs(client),  # Tabs component for layout
        dcc.Graph(id="main_graph"),  # Graph for displaying data
        button(text="Add Graph", id="add_graph_button", style=button_style),  # Button to add new graph
        html.Div(id="dynamic_div", children=[], className="flex flex-wrap"),  # Dynamic div for additional content
    ],
)


@callback(
    Output("main_graph", "figure"),
    Output("dynamic_div", "children"),
    Output("custom_dropdown", "children"),
    Output("custon_name", "value"),
    Output("list_custom_features", "children"),
    # Inputs and states for callback
    Input("update_graph_button", "n_clicks"),
    Input("add_graph_button", "n_clicks"),
    Input({"type": "remove_button", "index": ALL}, "n_clicks"),
    Input({"type": "operation_custom_feature_add", "index": ALL}, "n_clicks"),
    Input({"type": "operation_custom_feature_remove", "index": ALL}, "n_clicks"),
    Input({"type": "operation_custom_feature_op", "index": ALL}, "value"),
    Input({"type": "dynamic-dropdown", "index": ALL}, "value"),
    Input({"type": "custom_feature_remove", "index": ALL}, "n_clicks"),
    Input("add_custom_feature", "n_clicks"),
    State("main_checkbox", "value"),
    State("main-date-picker-range", "start_date"),
    State("main-date-picker-range", "end_date"),
    State("main_graph", "figure"),
    State("dynamic_div", "children"),
    State("custom_dropdown", "children"),
    State("custon_name", "value"),
    State("custom_cumulative", "value"),
    State("list_custom_features", "children"),
    prevent_initial_call=True,  # Prevent initial callback call
)
def update_render(
    update_button,
    add_button,
    remove_button,
    operation_custom_feature_add,
    operation_custom_feature_remove,
    operation_custom_feature_op,
    dynamic_dropdown,
    custom_feature_remove,
    add_custom_feature,
    features,
    start_date,
    end_date,
    currentFigure,
    currentChildren,
    currentDropdownChildren,
    custom_name,
    custom_cumulative,
    list_custom_features
):
    global fig
    global custom_feature
    global features_selected

    # Context to determine which input triggered the callback
    ctx = callback_context
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None
    
    if custom_feature != []:
        # Update custom features if any
        custom_feature = update_custom_feature(
            dynamic_dropdown, custom_feature, operation_custom_feature_op
        )

    try:
        # Try to convert dynamic trigger ID to dictionary if possible
        if "type" in triggered_id:
            triggered_id = eval(triggered_id)
    except:
        pass

    # Update graph when update button is clicked
    if triggered_id == "update_graph_button":
        if client.df.empty:
            fig = update_graph(client, features, start_date=start_date, end_date=end_date, update_action=3)
        else:
            fig = update_graph(client, features, start_date=start_date, end_date=end_date, update_action=2)
        currentChildren = multi_chart(client)
        features_selected = features
        dynamic_dropdown = [features_selected[0]]
        custom_feature = [{"Feature": features_selected[0]}]
        custom_dropdow_children = custom_dropdow(features_selected, [""], ["Add"], custom_feature)
        return fig, currentChildren, custom_dropdow_children, custom_name, list_custom_features

    # Add graph when add button is clicked
    elif triggered_id == "add_graph_button":
        currentChildren = add_graph(client, currentFigure)
        return currentFigure, currentChildren, currentDropdownChildren, custom_name, list_custom_features

    # Add custom feature when button is clicked
    elif triggered_id == "add_custom_feature":
        client.create_feature(custom_feature, False if custom_cumulative[-1] == "" else True, custom_name)
        features.extend([feature["feature_name"] for feature in client.created_features])
        feature_units_dict[features[-1]] = "dollars"

        fig = update_graph(client, features, start_date=start_date, end_date=end_date, update_action=1)
        custom_dropdow_children = custom_dropdow(features_selected, [""], ["Add"], custom_feature)
        return fig, currentChildren, custom_dropdow_children,"",list_custom_filter_children(client)

    # Remove graph when remove button is clicked
    elif isinstance(triggered_id, dict) and triggered_id.get("type") == "remove_button":
        currentChildren = remove_graph(client, triggered_id.get("index"))
        return currentFigure, currentChildren, currentDropdownChildren, custom_name, list_custom_features

    # Add new custom feature operation
    elif isinstance(triggered_id, dict) and triggered_id.get("type") == "operation_custom_feature_add":
        custom_feature.append({"Operation": "+", "Feature": features[0]})
        dynamic_dropdown.append("")
        operation_custom_feature_op.append("Add")
        custom_dropdow_children = custom_dropdow(features_selected, dynamic_dropdown, operation_custom_feature_op, custom_feature)
        return currentFigure, currentChildren, custom_dropdow_children, custom_name, list_custom_features

    # Remove custom feature operation
    elif isinstance(triggered_id, dict) and triggered_id.get("type") == "operation_custom_feature_remove":
        index = triggered_id.get("index")
        del custom_feature[index]
        del dynamic_dropdown[index]
        del operation_custom_feature_op[index]
        custom_dropdow_children = custom_dropdow(features_selected, dynamic_dropdown, operation_custom_feature_op, custom_feature)
        return currentFigure, currentChildren, custom_dropdow_children, custom_name, list_custom_features
    
    # Remove custom feature
    elif isinstance(triggered_id, dict) and triggered_id.get("type") == "custom_feature_remove":
        index = triggered_id.get("index")
        feature_to_remove = next((feature["feature_name"] for feature in client.created_features if feature["feature_id"] == index), None)
        client.remove_custom_feature(index)
        features.extend([feature["feature_name"] for feature in client.created_features])
        feature_units_dict[features[-1]] = "dollars"
        currentChildren = remove_custom_feature_from_graphs(client, feature_to_remove)
        fig = update_graph(client, features, start_date=start_date, end_date=end_date, update_action=1)
        
        return fig, currentChildren, currentDropdownChildren, custom_name,list_custom_filter_children(client)

    # If no figure, return initial empty state
    if not currentFigure:
        return fig, currentChildren, currentDropdownChildren,custom_name,list_custom_features

    return currentFigure, currentChildren, currentDropdownChildren,custom_name,list_custom_features


# Serve and render the app
if __name__ == "__main__":
    app.run_server(debug=True)
