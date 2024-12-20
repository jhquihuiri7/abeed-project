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
from components.dropdown_components import custom_features_head, custom_dropdow, main_dropdown, date_filter_dropdown
import plotly.graph_objects as go
from backend.Class import Ops
from styles.styles import button_style, button_dropdown_style
from backend.db_dictionaries import feature_units_dict
import math


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
    className="p-10 w-full",
    children=[
        html.Div(
            children=[
                    main_dropdown(),
                    main_checkbox(),# Checkbox component for feature selection
                ],
            className="flex flex-row w-full justify-between"
            ),
        main_daterange(),  # Date range component
        button(text="Update Graph", id="update_graph_button", style=button_style),  # Button to update graph
        main_tabs(client),  # Tabs component for layout
        dcc.Graph(id="main_graph"),  # Graph for displaying data
        button(text="Add Graph", id="add_graph_button", style=button_style),  # Button to add new graph
        html.Div(id="dynamic_div", children=[], className="flex flex-wrap"),  # Dynamic div for additional content
    ],
)


@callback(
    Output("date_filter_dropdown","children"),
    Input("select_all_datefilter","n_clicks"),
    State("date_filter_dropdown","children"),
    prevent_initial_call=True,  # Prevent initial callback call
)
def update_date_filter(select_all_datefilter, datefilter_dropdown):
    
    ctx = callback_context
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None
    if not triggered_id:
        return datefilter_dropdown  # No changes
    try:
        # Try to convert dynamic trigger ID to dictionary if possible
        if "type" in triggered_id:
            triggered_id = eval(triggered_id)
    except:
        pass
    
    if triggered_id == "select_all_datefilter":
        
        return date_filter_dropdown()
    
    return datefilter_dropdown

@callback(
    Output({"type": "hour_button", "index": ALL}, "style"),
    Input({"type": "hour_button", "index": ALL}, "n_clicks"),
    Input("apply_hour_range","n_clicks"),
    Input("remove_hour_range","n_clicks"),
    State({"type": "hour_button", "index": ALL}, "style"),
    State("hour-filter-slider", "value"),
    prevent_initial_call=True,  # Prevent initial callback call
)
def update_hour_button_style(
    hour_button, 
    apply_hour_range,
    remove_hour_range,
    hour_button_style, 
    hour_filter_slider,
    ):
    # Context to determine which input triggered the callback
    ctx = callback_context
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None
    if not triggered_id:
        return hour_button_style  # No changes
    try:
        # Try to convert dynamic trigger ID to dictionary if possible
        if "type" in triggered_id:
            triggered_id = eval(triggered_id)
    except:
        pass
    
    if isinstance(triggered_id, dict) and triggered_id.get("type") == "hour_button":
        index = triggered_id.get("index")
        # Toggle the background color when the hour button is clicked
        hour_button_style[index]["backgroundColor"] = "white" if hour_button_style[index]["backgroundColor"] == "#d9d9d9" else "#d9d9d9"
    
    if triggered_id == "apply_hour_range" or triggered_id == "remove_hour_range":
        for index in range(hour_filter_slider[0],hour_filter_slider[1]+1):
            hour_button_style[index]["backgroundColor"] = "#d9d9d9" if triggered_id == "apply_hour_range" else "white"# Toggle the background color when the hour button is clicked
        return hour_button_style
         
    return hour_button_style

@callback(
    Output("main_dropdown", "value"),
    Output("main_checkbox", "value"),
    Output("main_graph", "figure"),
    Output("dynamic_div", "children"),
    Output("custom_dropdown", "children"),
    Output("custon_name", "value"),
    Output("list_custom_features", "children"),
    Output("feature_filter_dropdown", "options"),
    Output("feature_filter_dropdown", "value"),
    Output("feature_filter_min_range", "value"),
    Output("feature_filter_max_range", "value"),
    Output("feature_filter_list", "children"),
    # Inputs and states for callback
    Input("main_dropdown", "value"),
    Input("update_graph_button", "n_clicks"),
    Input("add_graph_button", "n_clicks"),
    Input({"type": "remove_button", "index": ALL}, "n_clicks"),
    Input({"type": "operation_custom_feature_add", "index": ALL}, "n_clicks"),
    Input({"type": "operation_custom_feature_remove", "index": ALL}, "n_clicks"),
    Input({"type": "operation_custom_feature_op", "index": ALL}, "value"),
    Input({"type": "dynamic-dropdown", "index": ALL}, "value"),
    Input({"type": "custom_feature_remove", "index": ALL}, "n_clicks"),
    Input("add_custom_feature", "n_clicks"),
    Input("feature_filter_add","n_clicks"),
    Input({"type": "feature_filter_remove", "index":ALL}, "n_clicks"),
    #Input({"type": "hour_button", "index": ALL}, "n_clicks"),
    State("main_checkbox", "value"),
    State("main-date-picker-range", "start_date"),
    State("main-date-picker-range", "end_date"),
    State("main_graph", "figure"),
    State("dynamic_div", "children"),
    State("custom_dropdown", "children"),
    State("custon_name", "value"),
    State("custom_cumulative", "value"),
    State("list_custom_features", "children"),
    State("feature_filter_dropdown", "options"),
    State("feature_filter_dropdown", "value"),
    State("feature_filter_min_range", "value"),
    State("feature_filter_max_range", "value"),
    State("feature_filter_list", "children"),
    prevent_initial_call=True,  # Prevent initial callback call
)
def update_render(
    main_dropdown,
    update_button,
    add_button,
    remove_button,
    operation_custom_feature_add,
    operation_custom_feature_remove,
    operation_custom_feature_op,
    dynamic_dropdown,
    custom_feature_remove,
    add_custom_feature,
    feature_filter_add, 
    feature_filter_remove,
    features,
    start_date,
    end_date,
    currentFigure,
    currentChildren,
    currentDropdownChildren,
    custom_name,
    custom_cumulative,
    list_custom_features,
    feature_filter_dropdown_opts,
    feature_filter_dropdown,
    feature_filter_min_range,
    feature_filter_max_range,
    feature_filter_list,
):
    global fig
    global custom_feature
    global features_selected

    # Context to determine which input triggered the callback
    ctx = callback_context
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None

    try:
        # Try to convert dynamic trigger ID to dictionary if possible
        if "type" in triggered_id:
            triggered_id = eval(triggered_id)
    except:
        pass
    
    
    if isinstance(triggered_id, dict) and (triggered_id.get("type") == "dynamic-dropdown" or triggered_id.get("type") == "operation_custom_feature_op"):
        custom_feature = update_custom_feature(
            dynamic_dropdown, custom_feature, operation_custom_feature_op
        )
    
    client.start_date = start_date
    client.end_date = end_date
    client.data_features = features
            
    # Update graph when update button is clicked
    if triggered_id == "update_graph_button":
        features_selected = features
        if client.df.empty:
            fig = update_graph(client, features, start_date=start_date, end_date=end_date, update_action=3)
        else:
            fig = update_graph(client, features, start_date=start_date, end_date=end_date, update_action=2)
        currentChildren = multi_chart(client)
        features_selected = features
        dynamic_dropdown = [features_selected[0]]
        custom_feature = [{"Feature": features_selected[0]}]
        custom_dropdow_children = custom_dropdow(features_selected, [""], ["Add"], custom_feature)
        return "",features,fig, currentChildren, custom_dropdow_children, custom_name, list_custom_filter_children(client), client.data_features, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list

    # Add graph when add button is clicked
    elif triggered_id == "add_graph_button":
        currentChildren = add_graph(client, currentFigure)
        return "",features,currentFigure, currentChildren, currentDropdownChildren, custom_name, list_custom_features, feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list

    # Add custom feature when button is clicked
    elif triggered_id == "add_custom_feature":
        client.create_feature(custom_feature, False if custom_cumulative[-1] == "" else True, custom_name)
        features.extend([feature["feature_name"] for feature in client.created_features])
        feature_units_dict[features[-1]] = client.created_features[-1]["unit"]
        fig = update_graph(client, features, start_date=start_date, end_date=end_date, update_action=1)
        custom_dropdow_children = custom_dropdow(features_selected, [""], ["Add"], custom_feature)
        
        return "",features,fig, currentChildren, custom_dropdow_children,"",list_custom_filter_children(client), feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list
    
    # Remove graph when remove button is clicked
    elif isinstance(triggered_id, dict) and triggered_id.get("type") == "remove_button":
        currentChildren = remove_graph(client, triggered_id.get("index"))
        return "",features,currentFigure, currentChildren, currentDropdownChildren, custom_name, list_custom_features, feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list
    # Add new custom feature operation
    elif isinstance(triggered_id, dict) and triggered_id.get("type") == "operation_custom_feature_add":
        custom_feature.append({"Operation": "+", "Feature": features[0]})
        dynamic_dropdown.append("")
        operation_custom_feature_op.append("Add")
        custom_dropdow_children = custom_dropdow(features_selected, dynamic_dropdown, operation_custom_feature_op, custom_feature)
        return "",features,currentFigure, currentChildren, custom_dropdow_children, custom_name, list_custom_features, feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list
    # Remove custom feature operation
    elif isinstance(triggered_id, dict) and triggered_id.get("type") == "operation_custom_feature_remove":
        index = triggered_id.get("index")
        del custom_feature[index]
        del dynamic_dropdown[index]
        del operation_custom_feature_op[index]
        
        custom_dropdow_children = custom_dropdow(features_selected, dynamic_dropdown, operation_custom_feature_op, custom_feature)
        return "",features,currentFigure, currentChildren, custom_dropdow_children, custom_name, list_custom_features, feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list
    
    # Remove custom feature
    elif isinstance(triggered_id, dict) and triggered_id.get("type") == "custom_feature_remove":
        index = triggered_id.get("index")
        feature_to_remove = next((feature["feature_name"] for feature in client.created_features if feature["feature_id"] == index), None)
        client.remove_custom_feature(index)
        features= [feature for feature in features if feature != feature_to_remove]
        currentChildren = remove_custom_feature_from_graphs(client, feature_to_remove)
        fig = update_graph(client, features, start_date=start_date, end_date=end_date, update_action=1)
        
        return "",features,fig, currentChildren, currentDropdownChildren, custom_name,list_custom_filter_children(client), feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list
    
    if triggered_id == "feature_filter_add":
        try:
            feature_filter_min_range = float(feature_filter_min_range)
            feature_filter_max_range = float(feature_filter_max_range) 
        except:
            feature_filter_min_range = -math.inf
            feature_filter_max_range = math.inf
        client.add_feature_filter(feature_filter_dropdown,feature_filter_min_range, feature_filter_max_range)
        feature_filter_list = [html.Div([f"{feature_filter["feature_name"]}, Range: ({feature_filter["range"][0]} → {feature_filter["range"][1]})", button(
                            text="REMOVE",
                            id={"type": "feature_filter_remove", "index": feature_filter["filter_uid"]},
                            style=button_dropdown_style,
                        )], className="mb-4") for feature_filter in client.feature_filters]
        feature_filter_dropdown_opts = [feature for feature in feature_filter_dropdown_opts if feature not in feature_filter_dropdown]
        return "",features, currentFigure, currentChildren, currentDropdownChildren,custom_name,list_custom_features, feature_filter_dropdown_opts, feature_filter_dropdown, "", "", feature_filter_list
    
    
    if isinstance(triggered_id, dict) and triggered_id.get("type") == "feature_filter_remove":
        index = triggered_id.get("index")
        client.remove_feature_filter(index)
        feature_filter_list = [html.Div([feature_filter["feature_name"], button(
                            text="REMOVE",
                            id={"type": "feature_filter_remove", "index": feature_filter["filter_uid"]},
                            style=button_dropdown_style,
                        )]) for feature_filter in client.feature_filters]
        feature_filter_dropdown_opts = [feature for feature in client.data_features if feature not in [feature["feature_name"] for feature in client.feature_filters]]
        return "",features, currentFigure, currentChildren, currentDropdownChildren,custom_name,list_custom_features, feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list   
    
    if main_dropdown != "":
        features.append(main_dropdown)

    
    # If no figure, return initial empty state
    if not currentFigure:
        return "",features,fig, currentChildren, currentDropdownChildren,custom_name,list_custom_features, client.data_features, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list

    return "",features, currentFigure, currentChildren, currentDropdownChildren,custom_name,list_custom_features, client.data_features, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list


# Serve and render the app
if __name__ == "__main__":
    app.run_server(debug=True)
