# Dash imports
from dash import Dash, _dash_renderer
from dash import dcc, html, Input, Output, State, callback_context, ALL, exceptions

# Components
import dash_mantine_components as dmc
from components.checkbox_components import expandable_container

from components.tabs_components import main_tabs
from components.button_components import button, apply_filters_toggle
from components.notification_components import show_notification
from components.graph_components import multi_chart, bar_chart
from components.dropdown_components import main_dropdown, date_filter_dropdown, cumulative_conversion_dropdown, delete_features_dropdown


# Utilities
from utils.restore_session import restore_session_upload
from utils.logic_functions import (
    validate_update_data,
    validateFeatureFilterData,
    get_feature_filter_dropdown_opts,
    validateApplyDatetimeSelection,
    validateApplyFilterToggle,
    get_custom_features_names
)
from utils.functions import (
    ops_to_json_upload,
    json_to_ops_upload,
    list_feature_filter
)

# Backend
from backend.Class import Ops

# Styles
from styles.styles import button_style

# React version setting
_dash_renderer._set_react_version("18.2.0")

def create_dash_upload_app(server):
    
    # External scripts (e.g., TailwindCSS)
    external_stylesheets = [
        dmc.styles.NOTIFICATIONS
    ]
    
    external_scripts = [
        "https://cdn.tailwindcss.com"
    ]
    
    ops = Ops()
    # Initialize the Dash app
    app = Dash(
        __name__,
        server=server,
        assets_folder="upload",
        url_base_pathname='/custom_dash/',
        #suppress_callback_exceptions=True,
        external_scripts=external_scripts,
        external_stylesheets=external_stylesheets,
        meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
    )
    app.title = "Market Operation Dashboard"
    
    
    # app._favicon = "favicon.ico"
    app.layout = dmc.MantineProvider(
        children=[html.Div(
        className="p-10 w-full",
        children=[     
            expandable_container(
                toggle_button_id="toggle_exapandable_button_primary", 
                expandable_text_id="expandable_text_primary",
                client=ops
            ),        
            html.Div(
                children=[
                    html.Div(
                        children=[
                            main_dropdown(ops, "w-[56%]"),  
                            button(text="Add Features", id="update_graph_button", style=button_style)      
                        ],
                        className="flex flex-row justify-start w-1/2"
                    ),
                    html.Div(
                        children=[
                            delete_features_dropdown(ops),
                            button(text="Remove Features", id="delete_features_button", style=button_style)      
                        ],
                        className="flex flex-row justify-start w-1/2"
                    ),
                    ],
                className="flex flex-row justify-between mt-5"    
            ),  
            html.Div(
                children=[
                    cumulative_conversion_dropdown(ops),
                    button(text="Make cumulative", id="make_cumulative_button", style=button_style)
                ],
                className="flex flex-row justify-start my-10"
            ),
            main_tabs(ops, show_custom=False),  # Tabs component for layout
            apply_filters_toggle("Collapse"),
            dcc.Graph(id="main_graph"),  # Graph for displaying data
            button(text="Add Graph", id="add_graph_button", style=button_style),  # Button to add new graph
            html.Div(id="dynamic_div", children=[], className="flex flex-wrap"),  # Dynamic div for additional content
            dmc.NotificationProvider(position="top-center"),
            html.Div(id="notifications-container"),
        ],
    ),
        dcc.Store(id="client", data=ops_to_json_upload(ops)),
        dcc.Store(id="init_columns", data=[]),
        ]
    ) 
    
    @app.callback(
    Output("main_dropdown", "options"),
    Output("expandable_text_primary", "style"),
    Output("toggle_exapandable_button_primary", "children"),
    Input("toggle_exapandable_button_primary", "n_clicks"),
    State("expandable_text_primary", "style"),
    prevent_initial_call=True
    )
    def toggle_text_primary(n_clicks, expandable_text_primary):
        ctx = callback_context
        if not ctx.triggered:
            raise exceptions.PreventUpdate
        options = ops.available_readable_names
        if n_clicks % 2 == 1:
            if expandable_text_primary["display"] == "block":
                options = list(set(ops.available_readable_names) | set(ops.available_db_names))
            return options, {"display": "block"}, "Collapse Feature Menu"
        return options, {"display": "none"}, "Expand Feature Menu"
    
    @app.callback(
        Output("main_dropdown", "options", allow_duplicate=True),
        Input("all_features_checkbox", "value"),
        prevent_initial_call=True
    )
    def toggle_all_features(value):
        ctx = callback_context
        if not ctx.triggered:
            raise exceptions.PreventUpdate
        options = ops.available_readable_names
        if value != []:
            options = list(set(options) | set(ops.available_db_names))
        return options
    
    
    @app.callback(
        Output("collapse_expand_filter","label"),
        Input("collapse_expand_filter","value"),
        prevent_initial_call=True
    )
    def update_apply_filters(collapse_expand_filter):
                
        return "Collapse" if collapse_expand_filter else "Expand" 
    
    @app.callback(
        Output("date_filter_dropdown","children"),
        Input("select_all_datefilter","n_clicks"),
        State("date_filter_dropdown","children"),
        prevent_initial_call=True,
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
    
    @app.callback(
        Output({"type": "hour_button", "index": ALL}, "style"),
        Input({"type": "hour_button", "index": ALL}, "n_clicks"),
        Input("apply_hour_range","n_clicks"),
        Input("select_all_hour_range","n_clicks"),
        Input("deselect_all_hour_range","n_clicks"),
        State({"type": "hour_button", "index": ALL}, "style"),
        State("hour-filter-slider", "value"),
        prevent_initial_call=True,  # Prevent initial callback call
    )
    def update_hour_button_style(
        hour_button, 
        apply_hour_range,
        select_all_hour_range,
        deselect_all_hour_range,
        hour_button_style, 
        hour_filter_slider,
        ):

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
        
        if triggered_id == "deselect_all_hour_range":
            for index in range(0,24):
                hour_button_style[index]["backgroundColor"] = "white"# Toggle the background color when the hour button is clicked
            return hour_button_style
        
        if triggered_id == "select_all_hour_range":
            for index in range(0,24):
                hour_button_style[index]["backgroundColor"] = "#d9d9d9"# Toggle the background color when the hour button is clicked
            return hour_button_style
        
        if triggered_id == "apply_hour_range":
            for index in range(hour_filter_slider[0],hour_filter_slider[1]+1):
                hour_button_style[index]["backgroundColor"] = "#d9d9d9" if triggered_id == "apply_hour_range" else "white"# Toggle the background color when the hour button is clicked
            return hour_button_style
             
        return hour_button_style
    
    @app.callback(
        Output("cumulative_dropdown","options"),
        Input("client", "data")
    )
    def cumulative_dropdown(data):
        client = json_to_ops_upload(data)
        return client.df.columns
    
    @app.callback(
        Output("delete_features_dropdown","options"),
        Input("client", "data")
    )
    def delete_feature_dropdown(data):
        client = json_to_ops_upload(data)
        return client.df.columns
    
    @app.callback(
        Output("client", "data"),
        Output("main_graph", "figure"),
        Output("dynamic_div", "children"),
        Output("feature_filter_dropdown", "options"),
        Output("feature_filter_dropdown", "value"),
        Output("feature_filter_min_range", "value"),
        Output("feature_filter_max_range", "value"),
        Output("feature_filter_list", "children"),
        Output("notifications-container", "children"),
        Output("apply_filters", "value"),
        Output("collapse_expand_filter", "disabled"),
        Output("init_columns","data"),
        Output("main_dropdown", "value"),
        # Inputs and states for callback
        Input("update_graph_button", "n_clicks"),
        Input("delete_features_button", "n_clicks"),
        Input("make_cumulative_button", "n_clicks"),
        Input("add_graph_button", "n_clicks"),
        Input({"type": "remove_button", "index": ALL}, "n_clicks"),
        Input("feature_filter_add","n_clicks"),
        Input({"type": "feature_filter_remove", "index":ALL}, "n_clicks"),
        Input("apply_selection_hourfilter","n_clicks"),
        Input("apply_filters", "value"),
        Input("collapse_expand_filter","value"),
        Input("apply_selection_datefilter", "n_clicks"),
        #Input({"type": "hour_button", "index": ALL}, "n_clicks"),
        State("main_dropdown", "value"),
        State("cumulative_dropdown","value"),
        State("main_graph", "figure"),
        State("dynamic_div", "children"),
        State("feature_filter_dropdown", "options"),
        State("feature_filter_dropdown", "value"),
        State("feature_filter_min_range", "value"),
        State("feature_filter_max_range", "value"),
        State("feature_filter_list", "children"),
        State({"type": "hour_button", "index": ALL}, "style"),
        State("apply_filters", "value"),
        State("collapse_expand_filter","value"),
        State("collapse_expand_filter","disabled"),
        State("year_dropdown_date_filter", "value"),
        State("month_dropdown_date_filter", "value"),
        State("day_dropdown_date_filter", "value"),
        State("client", "data"),
        State("init_columns","data"),
        State("delete_features_dropdown","value"),
    )
    def update_render(
        update_button,
        delete_features_button,
        make_cumulative,
        add_button,
        remove_button,
        feature_filter_add, 
        feature_filter_remove,
        apply_selection_hourfilter,
        apply_filters,
        collapse_expand_filter,
        apply_selection_datefilter,
        features,
        cumulative_dropdown,
        currentFigure,
        currentChildren,
        feature_filter_dropdown_opts,
        feature_filter_dropdown,
        feature_filter_min_range,
        feature_filter_max_range,
        feature_filter_list,
        hour_button,
        apply_filters_state,
        collapse_expand_filter_state,
        collapse_expand_filter_disabled,
        year_dropdown_date_filter_state,
        month_dropdown_date_filter_state,
        day_dropdown_date_filter_state,
        data,
        init_columns,
        delete_features_dropdown
    ):

        client = json_to_ops_upload(data)
        #client.data_features =  features
        notification = []
        ctx = callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None
        try:
            # Try to convert dynamic trigger ID to dictionary if possible
            if "type" in triggered_id:
                triggered_id = eval(triggered_id)
        except:
            pass
        
        if triggered_id == "delete_features_button":
            init_columns = list(set(init_columns) - set(delete_features_dropdown))
            client.data_features = list(set(client.data_features) - set(delete_features_dropdown))
            custom_features = list(set(delete_features_dropdown) & set(get_custom_features_names(client,[],True, True)))
            if custom_features != []:
                for custom_feature in custom_features:
                    feature_to_remove = next((feature["feature_id"] for feature in client.created_features if feature["feature_name"] == custom_feature), None)
                    client.remove_custom_feature_button(feature_to_remove)
            client.update_data_button(client.start_date, client.end_date, client.data_features, overrite_current_df=False, init_columns=init_columns)
            currentFigure = bar_chart(client, None, apply_filters_state!=[], collapse_expand_filter_state)
            currentChildren = multi_chart(client, apply_filters_state!=[], collapse_expand_filter_state)
            feature_filter_dropdown_opts = get_feature_filter_dropdown_opts(client, is_upload=True)
            
            return ops_to_json_upload(client),currentFigure, currentChildren, feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list, notification, apply_filters_state, collapse_expand_filter_disabled, init_columns, []
        
        if triggered_id == "update_graph_button":
            if features != []:
                client.data_features = list(set(client.data_features) | set(features))
                client.update_data_button(client.start_date, client.end_date, client.data_features, overrite_current_df=False, init_columns=init_columns)
                currentFigure = bar_chart(client, None, apply_filters_state!=[], collapse_expand_filter_state)
                currentChildren = multi_chart(client, apply_filters_state!=[], collapse_expand_filter_state)
                feature_filter_dropdown_opts = get_feature_filter_dropdown_opts(client, is_upload=True)
            else:
                notification = show_notification("Select at least one feature")
            return ops_to_json_upload(client),currentFigure, currentChildren, feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list, notification, apply_filters_state, collapse_expand_filter_disabled, init_columns, []
        
        if triggered_id == "make_cumulative_button":
            dropdown_operation = [
                {"Feature": cumulative_dropdown}
            ]
            client.create_custom_feature_button(dropdown_operation, True,"")
            currentFigure = bar_chart(client, None, apply_filters_state!=[], collapse_expand_filter_state)
            currentChildren = multi_chart(client, apply_filters_state!=[], collapse_expand_filter_state)
            feature_filter_dropdown_opts = get_feature_filter_dropdown_opts(client, is_upload=True)
            
            return ops_to_json_upload(client),currentFigure, currentChildren, feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list, notification, apply_filters_state, collapse_expand_filter_disabled, init_columns, []
        
        # Add graph when add button is clicked
        if triggered_id == "add_graph_button":
            sub_features = [
                      i["name"] for i in currentFigure["data"] if i["visible"]==True
                  ]
            client.add_graph_button(sub_features)
            currentChildren = multi_chart(client, apply_filters_state!=[], collapse_expand_filter_state)
            return ops_to_json_upload(client),currentFigure, currentChildren, feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list, notification, apply_filters_state, collapse_expand_filter_disabled, init_columns, []
            
        # Remove graph when remove button is clicked
        elif isinstance(triggered_id, dict) and triggered_id.get("type") == "remove_button":
            client.remove_graph_button(triggered_id.get("index"))
            currentChildren = multi_chart(client, apply_filters_state!=[], collapse_expand_filter_state)            
            return ops_to_json_upload(client),currentFigure, currentChildren, feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list, notification, apply_filters_state, collapse_expand_filter_disabled, init_columns, []
               
        if triggered_id == "feature_filter_add":
            is_valid, message, feature_filter_min_range, feature_filter_max_range = validateFeatureFilterData(client, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range)
            if is_valid:    
                client.add_feature_filter_button(feature_filter_dropdown,feature_filter_min_range, feature_filter_max_range)
                feature_filter_list = list_feature_filter(client)
                feature_filter_dropdown_opts = get_feature_filter_dropdown_opts(client, is_upload=True)  
                apply_filters_state = ['Apply filter']
                collapse_expand_filter_disabled = False 
                currentFigure = bar_chart(client, None, apply_filters_state!=[], collapse_expand_filter_state)
                currentChildren = multi_chart(client, apply_filters_state!=[], collapse_expand_filter_state)     
            else:
                notification = show_notification(message)
            return ops_to_json_upload(client), currentFigure, currentChildren, feature_filter_dropdown_opts, feature_filter_dropdown, "", "", feature_filter_list, notification, apply_filters_state, collapse_expand_filter_disabled, init_columns, []       
        
        if isinstance(triggered_id, dict) and triggered_id.get("type") == "feature_filter_remove":
            index = triggered_id.get("index")
            client.remove_feature_filter_button(index)
            feature_filter_list = list_feature_filter(client)
            feature_filter_dropdown_opts = get_feature_filter_dropdown_opts(client, is_upload=True)
            apply_filters_state = ['Apply filter']
            collapse_expand_filter_disabled = False 
            currentFigure = bar_chart(client, None, apply_filters_state!=[], collapse_expand_filter_state)
            currentChildren = multi_chart(client, apply_filters_state!=[], collapse_expand_filter_state)  
            return ops_to_json_upload(client), currentFigure, currentChildren, feature_filter_dropdown_opts, feature_filter_dropdown, "", "", feature_filter_list, notification, apply_filters_state, collapse_expand_filter_disabled, init_columns, []
         
        if (triggered_id == "apply_selection_datefilter") or (triggered_id == "apply_selection_hourfilter"):
            hours_to_include = [index for index, hour in enumerate(hour_button) if hour["backgroundColor"] != "white"]
            client.apply_datetime_filters_button(hours_to_include, day_dropdown_date_filter_state, month_dropdown_date_filter_state, year_dropdown_date_filter_state)
            is_valid, message = validateApplyDatetimeSelection(client)
            if is_valid:
                apply_filters_state = ['Apply filter']
                collapse_expand_filter_disabled = False 
                currentFigure = bar_chart(client, None, apply_filters_state!=[], collapse_expand_filter_state)
                currentChildren = multi_chart(client, apply_filters_state!=[], collapse_expand_filter_state)
            else:
                notification = show_notification(message)
                
            return ops_to_json_upload(client), currentFigure, currentChildren, feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list, notification, apply_filters_state, collapse_expand_filter_disabled, init_columns, []
        
        if triggered_id == "apply_filters":
            is_valid, message = validateApplyFilterToggle(client, apply_filters_state, collapse_expand_filter_state)
            if is_valid:  
                if apply_filters_state == []:
                    collapse_expand_filter_disabled = True
                    currentFigure = bar_chart(client, None, False, False)
                else:
                    collapse_expand_filter_disabled = False
                    currentFigure = bar_chart(client, None, apply_filters_state!=[], collapse_expand_filter_state)
            else:
                notification = show_notification(message)
            currentChildren = multi_chart(client, apply_filters_state!=[], collapse_expand_filter_state) 
            return ops_to_json_upload(client), currentFigure, currentChildren, feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list, notification, apply_filters_state, collapse_expand_filter_disabled, init_columns, []
          
        if triggered_id == "collapse_expand_filter":
            currentFigure = bar_chart(client, None, apply_filters_state!=[], collapse_expand_filter_state)
            currentChildren = multi_chart(client, apply_filters_state!=[], collapse_expand_filter_state) 
            return ops_to_json_upload(client), currentFigure, currentChildren, feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list, [], apply_filters_state, collapse_expand_filter_disabled, init_columns, []
        
        if not currentFigure:
            
            return restore_session_upload(client, apply_filters_state, collapse_expand_filter_state, collapse_expand_filter_disabled,feature_filter_min_range, feature_filter_max_range)

        else: 
            raise exceptions.PreventUpdate
    
    
        
    return app