# Python packages
import math
import io
import pandas as pd
from datetime import date

# Dash imports
from dash import Dash, _dash_renderer
from dash import dcc, html, Input, Output, State, callback, callback_context, ALL, exceptions

# Components
import dash_mantine_components as dmc
from components.checkbox_components import expandable_container
from components.daterange_components import main_daterange
from components.tabs_components import main_tabs
from components.button_components import button, apply_filters_toggle
from components.notification_components import show_notification, show_modal
from components.graph_components import multi_chart, bar_chart
from components.dropdown_components import main_dropdown, date_filter_dropdown, custom_dropdow


# Utilities
from utils.restore_session import restore_session
from utils.logic_functions import (
    update_custom_feature,
    validateFeatureFilterData,
    returnValidFeatures,
    extract_values_custom_feature,
    get_feature_filter_dropdown_opts,
    validateApplyDatetimeSelection,
    validate_add_custom_feature,
    validate_delete_custom_feature,
    validate_update_data,
    validateApplyFilterToggle
)
from utils.functions import (
    list_custom_filter_children,
    ops_to_json,
    json_to_ops,
    list_feature_filter
)

# Backend
from backend.Class import Ops

# Styles
from styles.styles import button_style, hourButtonStyle

# React version setting
_dash_renderer._set_react_version("18.2.0")

def create_dash_app(server):
    
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
        url_base_pathname='/dash/',
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
                page_store_id="current_page_primary",
                features_id="features_container_principal",
                prev_id="prev_btn_principal",
                next_id="next_btn_principal",
                pagination_id="pagination_principal",
                is_main=True
                ),
            expandable_container(
                toggle_button_id="toggle_exapandable_button_seccondary", 
                expandable_text_id="expandable_text_secondary",
                page_store_id="current_page_secondary",
                features_id="features_container_secondary",
                prev_id="prev_btn_secondary",
                next_id="next_btn_secondary",
                pagination_id="pagination_secondary"
                ),
            # Checkbox component for feature selection
            html.Div(
                children=[
                    main_dropdown(ops),
                    main_daterange(),  # Date range component
                    html.Div(
                        children=[
                            button(text="Update Graph", id="update_graph_button", style=button_style),  # Button to update graph
                            button(text="Download Data", id="download_data_button", style=button_style),
                            button(text="Save Session", id="download_client_button", style=button_style)
                        ],
                        className="flex flex-row justify-between items-end w-[500px]"
                    )
                    ],
                className="flex flex-row justify-between"    
            ),
            main_tabs(ops),  # Tabs component for layout
            apply_filters_toggle("Collapse"),
            dcc.Graph(id="main_graph"),  # Graph for displaying data
            button(text="Add Graph", id="add_graph_button", style=button_style),  # Button to add new graph
            html.Div(id="dynamic_div", children=[], className="flex flex-wrap"),  # Dynamic div for additional content
            dmc.NotificationProvider(position="top-center"),
            html.Div(id="notifications-container"),
            show_modal(),
            dcc.Download(id="download-data"),
            dcc.Download(id="download-client"),
            dcc.Store(id="temp_feature", data=[]),
            dcc.Store(id="restore_session",data="")
        ],
    ),
        dcc.Store(id="client", data=ops_to_json(ops)),
        ]
    )
    @app.callback(
        Output("main-date-picker-range","start_date"),
        Output("main-date-picker-range","end_date"),
        Output("main_dropdown", "value"),
        Input("restore_session", "data"),
        State("client","data")
    )      
    def restore_session_call(session, data):
        print("restore")
        client = json_to_ops(data)
        return client.start_date, client.end_date, client.data_features
    
    @app.callback(
    Output("main_dropdown", "options"),
    Output("expandable_text_primary", "style"),
    Output("toggle_exapandable_button_primary", "children"),
    Input("toggle_exapandable_button_primary", "n_clicks"),
    State("expandable_text_secondary", "style"),
    prevent_initial_call=True
    )
    def toggle_text_primary(n_clicks, expandable_text_secondary):
        ctx = callback_context
        if not ctx.triggered:
            raise exceptions.PreventUpdate
        options = ops.available_readable_names
        if n_clicks % 2 == 1:
            if expandable_text_secondary["display"] == "block":
                options = list(set(ops.available_readable_names) | set(ops.available_db_names))
            return options, {"display": "block"}, "Collapse Main Features"
        return options, {"display": "none"}, "Expand Main Features"
    
    @app.callback(
        Output("main_dropdown", "options", allow_duplicate=True),
        Output("expandable_text_secondary", "style"),
        Output("toggle_exapandable_button_seccondary", "children"),
        Input("toggle_exapandable_button_seccondary", "n_clicks"),
        prevent_initial_call=True
    )
    def toggle_text_secondary(n_clicks):
        ctx = callback_context
        if not ctx.triggered:
            raise exceptions.PreventUpdate
        options = ops.available_readable_names
        if n_clicks % 2 == 1:
            options = list(set(ops.available_readable_names) | set(ops.available_db_names))
            return options, {"display": "block"}, "Collapse DB Features"
        return options, {"display": "none"}, "Expand DB Features"
    
    @app.callback(
        Output("features_container_principal", "children"),
        Output("prev_btn_principal", "disabled"),
        Output("next_btn_principal", "disabled"),
        Output("pagination_principal", "children"),
        Input("prev_btn_principal", "n_clicks"),
        Input("next_btn_principal", "n_clicks"),
        Input({"type": "page_btn_principal", "index": ALL}, "n_clicks"),
        Input("current_page_primary", "data"),
    )
    def update_words(prev_clicks, next_clicks, page_clicks, current_page):
        ctx = callback_context
        
        words = ops.available_readable_names
        items_per_page = 100
        
        total_pages = (len(words) + items_per_page - 1) // items_per_page  # Redondeo hacia arriba
        new_page = min(max(current_page + (next_clicks - prev_clicks), 0), total_pages - 1)
        
        ctx = callback_context
        triggered_id = ctx.triggered_id
        if isinstance(triggered_id, dict) and "index" in triggered_id:
            new_page = triggered_id["index"]
        else:
            new_page = min(max(current_page + (next_clicks - prev_clicks), 0), total_pages - 1)
    
        start_index = new_page * items_per_page
        end_index = start_index + items_per_page
        current_words = words[start_index:end_index]
    
        word_elements = [
            html.Div(word, className="w-[300px] overflow-hidden mt-1") 
            for word in current_words
        ]
    
        pagination_numbers = [
            html.Button(
                str(i + 1),
                id={"type": "page_btn_principal", "index": i},
                n_clicks=0,
                className=f"px-2 m-1 py-1 rounded-lg border border-gray-300 cursor-pointer {'bg-blue-500 text-white' if i == new_page else 'bg-gray-300 text-black'}"
            ) 
            for i in range(total_pages)
        ]
    
        return word_elements, new_page == 0, new_page == total_pages - 1, pagination_numbers
    
    @app.callback(
        Output("features_container_secondary", "children"),
        Output("prev_btn_secondary", "disabled"),
        Output("next_btn_secondary", "disabled"),
        Output("pagination_secondary", "children"),
        Input("prev_btn_secondary", "n_clicks"),
        Input("next_btn_secondary", "n_clicks"),
        Input({"type": "page_btn_secondary", "index": ALL}, "n_clicks"),
        Input("current_page_secondary", "data"),
    )
    def update_words(prev_clicks, next_clicks, page_clicks, current_page):
        words = ops.available_db_names
        items_per_page = 100
        
        total_pages = (len(words) + items_per_page - 1) // items_per_page  # Redondeo hacia arriba
        new_page = min(max(current_page + (next_clicks - prev_clicks), 0), total_pages - 1)
        
        ctx = callback_context
        triggered_id = ctx.triggered_id
        if isinstance(triggered_id, dict) and "index" in triggered_id:
            new_page = triggered_id["index"]
        else:
            new_page = min(max(current_page + (next_clicks - prev_clicks), 0), total_pages - 1)
    
        start_index = new_page * items_per_page
        end_index = start_index + items_per_page
        current_words = words[start_index:end_index]
    
        word_elements = [
            html.Div(word, className="w-[300px] overflow-hidden mt-1") 
            for word in current_words
        ]
    
        pagination_numbers = [
            html.Button(
                str(i + 1),
                id={"type": "page_btn_secondary", "index": i},
                n_clicks=0,
                className=f"px-2 m-1 py-1 rounded-lg border border-gray-300 cursor-pointer {'bg-blue-500 text-white' if i == new_page else 'bg-gray-300 text-black'}"
            ) 
            for i in range(total_pages)
        ]
    
        return word_elements, new_page == 0, new_page == total_pages - 1, pagination_numbers

        
    
    @callback(
        Output("download-client", "data"),
        Output("input-modal", "opened"),
        Input("download_client_button", "n_clicks"),
        Input("save-button", "n_clicks"),
        State("client", "data"),
        State("user-session", "value"),
        prevent_initial_call=True,
    )
    def download_client(download_client_button, save_button, data, value):
        print("down client")
        ctx = callback_context
        if not ctx.triggered:
            raise exceptions.PreventUpdate
        triggered_id = callback_context.triggered[0]["prop_id"].split(".")[0]
        if triggered_id == "download_client_button":
            return None, True
        
        client = json_to_ops(data)    
        client_json = ops_to_json(client)
        if value == None:
            value =  date.today().strftime("%Y-%m-%d")
        return dict(content=client_json, filename=f"{value}.json"), False
    
    @callback(
        Output("download-data", "data"),
        Input("download_data_button", "n_clicks"),
        State("main_graph", "figure"),
        State("client", "data"),
        prevent_initial_call=True,
    )
    def download_logic(n_clicks, currentFigure, data):
        print("download")
        client = json_to_ops(data) 
        export_df = pd.DataFrame()
        if currentFigure:  # Ensure the figure is not None
            sub_features = [
                    i["name"] for i in currentFigure["data"] if i["visible"]==True
                ]    
            export_df = client.df[sub_features]
            
        buffer = io.StringIO()
        export_df.reset_index(inplace=True)
        export_df.rename(columns={'datetime': 'Datetime (HB)'}, inplace=True)
        export_df.to_csv(buffer, index=False, encoding="utf-8")
        buffer.seek(0)
    
        return dict(content=buffer.getvalue(), filename="data.csv")
    
    @callback(
        Output("collapse_expand_filter","label"),
        Input("collapse_expand_filter","value")
    )
    def update_apply_filters(collapse_expand_filter):
        print("apply filter")
        ctx = callback_context
        if not ctx.triggered:
            raise exceptions.PreventUpdate
        return "Collapse" if collapse_expand_filter else "Expand" 
    
    
    @callback(
        Output("date_filter_dropdown","children"),
        Input("select_all_datefilter","n_clicks"),
        State("date_filter_dropdown","children"),
        prevent_initial_call=True,  # Prevent initial callback call
    )
    def update_date_filter(select_all_datefilter, datefilter_dropdown):
        print("Dat filtr")
        ctx = callback_context
        if not ctx.triggered:
            raise exceptions.PreventUpdate
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
        Output("hour_filter_buttons","children"),
        Output("year_dropdown_date_filter", "value"),
        Output("month_dropdown_date_filter", "value"),
        Output("day_dropdown_date_filter", "value"),
        Input("restore_session", "data"),
        State("client", "data"),
    )
    def reset_session_hourfilter(session, data):
        print("reset")
        ctx = callback_context
        if not ctx.triggered:
            raise exceptions.PreventUpdate
        client = json_to_ops(data)
        hour_filter_buttons = []
        for hour in range(0,24):
            hour_filter_buttons.append(
                html.Button(
                    hour,  # Text displayed on the button
                    id={"type": "hour_button", "index": hour},  # Unique ID for the button
                    n_clicks=0,  # Initial click count set to 0
                    style={"backgroundColor": "#d9d9d9" if hour in client.hour_filters else "white"},  # Default background color
                    className=hourButtonStyle  # CSS class for styling the button
                )
            )    
        return hour_filter_buttons, client.year_filters, client.month_filters, client.day_of_week_filters
    
    @callback(
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
        # Context to determine which input triggered the callback
        print("HORA")
        ctx = callback_context
        if not ctx.triggered:
            raise exceptions.PreventUpdate
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
    
    @callback(
        Output("custom_dropdown", "children", allow_duplicate=True),
        Input({"type": "operation_custom_feature_add", "index": ALL}, "n_clicks"),
        Input({"type": "operation_custom_feature_remove", "index": ALL}, "n_clicks"),
        Input({"type": "operation_custom_feature_op", "index": ALL}, "value"),
        State("client", "data"),
        State("custom_dropdown", "children"),
        State({"type": "dynamic-dropdown", "index": ALL}, "value"),
        State("temp_feature", "data"),
        prevent_initial_call=True
    )
    def custom_feature_tab(operation_custom_feature_add, operation_custom_feature_remove, operation_custom_feature_op, data, currentDropdownChildren,dynamic_dropdown, custom_feature):
        print("custom_feaurre")
        
        ctx = callback_context
        if not ctx.triggered:
            raise exceptions.PreventUpdate
        if len(ctx.triggered) > 1:
            raise exceptions.PreventUpdate
        client = json_to_ops(data)
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None
        try:
            if "type" in triggered_id:
                triggered_id = eval(triggered_id)
        except:
            pass
        
        if isinstance(triggered_id, dict) and (triggered_id.get("type") == "dynamic-dropdown" or triggered_id.get("type") == "operation_custom_feature_op"):
            custom_feature = update_custom_feature(
                dynamic_dropdown, custom_feature, operation_custom_feature_op
            )
            custom_feature = extract_values_custom_feature(currentDropdownChildren)
            currentDropdownChildren = custom_dropdow(client, custom_feature)
        
        # Add new custom feature operation
        elif isinstance(triggered_id, dict) and triggered_id.get("type") == "operation_custom_feature_add":
            custom_feature = extract_values_custom_feature(currentDropdownChildren)
            custom_feature.append({"Operation":"-", "Feature":""})
            currentDropdownChildren = custom_dropdow(client, custom_feature)
        
        else:
            raise exceptions.PreventUpdate
        print('CUSTOn FINAL')
        return currentDropdownChildren
    
    @callback(
        Output("client", "data"),
        Output("temp_feature", "data"),
        Output("main_graph", "figure"),
        Output("dynamic_div", "children"),
        Output("custon_name", "value"),
        Output("custom_dropdown", "children"),
        Output("list_custom_features", "children"),
        Output("feature_filter_dropdown", "options"),
        Output("feature_filter_dropdown", "value"),
        Output("feature_filter_min_range", "value"),
        Output("feature_filter_max_range", "value"),
        Output("feature_filter_list", "children"),
        Output("notifications-container", "children"),
        Output("apply_filters", "value"),
        Output("collapse_expand_filter", "disabled"),
        # Inputs and states for callback
        Input("update_graph_button", "n_clicks"),
        Input("add_graph_button", "n_clicks"),
        Input({"type": "remove_button", "index": ALL}, "n_clicks"),
        Input({"type": "dynamic-dropdown", "index": ALL}, "value"),
        Input({"type": "custom_feature_remove", "index": ALL}, "n_clicks"),
        Input("add_custom_feature", "n_clicks"),
        Input("feature_filter_add","n_clicks"),
        Input({"type": "feature_filter_remove", "index":ALL}, "n_clicks"),
        Input("apply_selection_hourfilter","n_clicks"),
        Input("apply_filters", "value"),
        Input("collapse_expand_filter","value"),
        Input("apply_selection_datefilter", "n_clicks"),
        #Input({"type": "hour_button", "index": ALL}, "n_clicks"),
        State("main_dropdown", "value"),
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
        State({"type": "hour_button", "index": ALL}, "style"),
        State("apply_filters", "value"),
        State("collapse_expand_filter","value"),
        State("collapse_expand_filter","disabled"),
        State("year_dropdown_date_filter", "value"),
        State("month_dropdown_date_filter", "value"),
        State("day_dropdown_date_filter", "value"),
        State("client", "data"),
        State("temp_feature", "data"),
    )
    def update_render(
        update_button,
        add_button,
        remove_button,
        dynamic_dropdown,
        custom_feature_remove,
        add_custom_feature,
        feature_filter_add, 
        feature_filter_remove,
        apply_selection_hourfilter,
        apply_filters,
        collapse_expand_filter,
        apply_selection_datefilter,
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
        hour_button,
        apply_filters_state,
        collapse_expand_filter_state,
        collapse_expand_filter_disabled,
        year_dropdown_date_filter_state,
        month_dropdown_date_filter_state,
        day_dropdown_date_filter_state,
        data,
        custom_feature
    ):
        client = json_to_ops(data)
        notification = []
        print("ANTES")
        # Context to determine which input triggered the callback
        ctx = callback_context
        if not ctx.triggered:
            print("DESPUES")
            #raise exceptions.PreventUpdate
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None
    
        try:
            # Try to convert dynamic trigger ID to dictionary if possible
            if "type" in triggered_id:
                triggered_id = eval(triggered_id)
        except:
            pass
        
        
        client.start_date = start_date
        client.end_date = end_date
                
        # Update graph when update button is clicked
        if triggered_id == "update_graph_button":
            print("AQUI")
            is_valid, message = validate_update_data(client, features)
            if is_valid:
                client.update_data_button(start_date, end_date, features)
                currentFigure = bar_chart(client, None, apply_filters_state!=[], collapse_expand_filter_state)
                currentChildren = multi_chart(client, apply_filters_state!=[], collapse_expand_filter_state)
                custom_feature = extract_values_custom_feature(currentDropdownChildren)
                currentDropdownChildren = custom_dropdow(client, custom_feature)
                feature_filter_dropdown_opts = get_feature_filter_dropdown_opts(client)
            else:
                notification = show_notification(message)
            return ops_to_json(client), custom_feature,currentFigure, currentChildren, custom_name, currentDropdownChildren, list_custom_filter_children(client), feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list, notification, apply_filters_state, collapse_expand_filter_disabled
    
        # Add graph when add button is clicked
        elif triggered_id == "add_graph_button":
            sub_features = [
                      i["name"] for i in currentFigure["data"] if i["visible"]==True
                  ]
            client.add_graph_button(sub_features)
            currentChildren = multi_chart(client, apply_filters_state!=[], collapse_expand_filter_state)
            return ops_to_json(client),custom_feature,currentFigure, currentChildren, custom_name, currentDropdownChildren, list_custom_features, feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list, [], apply_filters_state, collapse_expand_filter_disabled
    
        # Remove graph when remove button is clicked
        elif isinstance(triggered_id, dict) and triggered_id.get("type") == "remove_button":
            client.remove_graph_button(triggered_id.get("index"))
            currentChildren = multi_chart(client, apply_filters_state!=[], collapse_expand_filter_state)            
            return ops_to_json(client),custom_feature,currentFigure, currentChildren, custom_name, currentDropdownChildren, list_custom_features, feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list, [], apply_filters_state, collapse_expand_filter_disabled

        # Add custom feature when button is clicked
        elif triggered_id == "add_custom_feature":
            custom_feature = extract_values_custom_feature(currentDropdownChildren)
            is_valid, message = validate_add_custom_feature(client, custom_feature, custom_cumulative[-1] != "", custom_name)
            if is_valid:
                client.create_custom_feature_button(custom_feature, custom_cumulative[-1] != "", custom_name)
                currentFigure = bar_chart(client, None, apply_filters_state!=[], collapse_expand_filter_state)
                custom_feature = []
                currentDropdownChildren = custom_dropdow(client, custom_feature)
                feature_filter_dropdown_opts = get_feature_filter_dropdown_opts(client)
            else:
                notification = show_notification(message)
            return ops_to_json(client),custom_feature,currentFigure, currentChildren, "", currentDropdownChildren, list_custom_filter_children(client), feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list, notification, apply_filters_state, collapse_expand_filter_disabled
         
        # Remove custom feature
        elif isinstance(triggered_id, dict) and triggered_id.get("type") == "custom_feature_remove":
            index = triggered_id.get("index")
            feature_to_remove = next((feature["feature_name"] for feature in client.created_features if feature["feature_id"] == index), None)
            is_valid, message = validate_delete_custom_feature(client,feature_to_remove)
            if is_valid:
                client.remove_custom_feature_button(index)
                for i in range(len(client.graphs)):
                    try:
                        # Attempt to remove the custom feature from each graph
                        client.graphs[i]["graph_data_features"].remove(feature_to_remove)
                    except ValueError:
                        # Ignore if the custom feature is not found in the graph
                        pass
                currentDropdownChildren = custom_dropdow(client, [])
                currentFigure = bar_chart(client, None, apply_filters_state!=[], collapse_expand_filter_state)
                currentChildren = multi_chart(client, apply_filters_state!=[], collapse_expand_filter_state)
                feature_filter_dropdown_opts = get_feature_filter_dropdown_opts(client)
            else:
                notification = show_notification(message)
            return ops_to_json(client),custom_feature,currentFigure, currentChildren, custom_name,currentDropdownChildren, list_custom_filter_children(client), feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list, notification, apply_filters_state, collapse_expand_filter_disabled
               
        # Add new custom feature operation
                
        # Remove custom feature operation
        elif isinstance(triggered_id, dict) and triggered_id.get("type") == "operation_custom_feature_remove":
            index = triggered_id.get("index")
            custom_feature = extract_values_custom_feature(currentDropdownChildren)
            del custom_feature[index]
            currentDropdownChildren = custom_dropdow(client, custom_feature)
            return ops_to_json(client),custom_feature,currentFigure, currentChildren, custom_name, currentDropdownChildren, list_custom_features, feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list, [], apply_filters_state, collapse_expand_filter_disabled
                

        if triggered_id == "feature_filter_add":
            is_valid, message, feature_filter_min_range, feature_filter_max_range = validateFeatureFilterData(client, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range)
            if is_valid:    
                client.add_feature_filter_button(feature_filter_dropdown,feature_filter_min_range, feature_filter_max_range)
                feature_filter_list = list_feature_filter(client)
                feature_filter_dropdown_opts = get_feature_filter_dropdown_opts(client)  
                apply_filters_state = ['Apply filter']
                collapse_expand_filter_disabled = False 
                currentFigure = bar_chart(client, None, apply_filters_state!=[], collapse_expand_filter_state)
                currentChildren = multi_chart(client, apply_filters_state!=[], collapse_expand_filter_state)     
            else:
                notification = show_notification(message)
            return ops_to_json(client),custom_feature,currentFigure, currentChildren, custom_name, currentDropdownChildren, list_custom_features, feature_filter_dropdown_opts, feature_filter_dropdown, "", "", feature_filter_list, notification, apply_filters_state, collapse_expand_filter_disabled       
        
        if isinstance(triggered_id, dict) and triggered_id.get("type") == "feature_filter_remove":
            index = triggered_id.get("index")
            client.remove_feature_filter_button(index)
            feature_filter_list = list_feature_filter(client)
            feature_filter_dropdown_opts = get_feature_filter_dropdown_opts(client)
            apply_filters_state = ['Apply filter']
            collapse_expand_filter_disabled = False 
            currentFigure = bar_chart(client, None, apply_filters_state!=[], collapse_expand_filter_state)
            currentChildren = multi_chart(client, apply_filters_state!=[], collapse_expand_filter_state)  
            return ops_to_json(client),custom_feature, currentFigure, currentChildren, custom_name,currentDropdownChildren, list_custom_features, feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list, [], apply_filters_state, collapse_expand_filter_disabled
        
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
            return ops_to_json(client),custom_feature, currentFigure, currentChildren, custom_name, currentDropdownChildren, list_custom_features, feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list, notification, apply_filters_state, collapse_expand_filter_disabled
        
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
            return ops_to_json(client),custom_feature, currentFigure, currentChildren, custom_name, currentDropdownChildren, list_custom_features, feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list, notification, apply_filters_state, collapse_expand_filter_disabled
            
        if triggered_id == "collapse_expand_filter":
            currentFigure = bar_chart(client, None, apply_filters_state!=[], collapse_expand_filter_state)
            currentChildren = multi_chart(client, apply_filters_state!=[], collapse_expand_filter_state) 
            return ops_to_json(client),custom_feature, currentFigure, currentChildren, custom_name, currentDropdownChildren,list_custom_features, feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list, [], apply_filters_state, collapse_expand_filter_disabled
        
        if not currentFigure:
            #return client_data,custom_feature,empty,data_features, currentFigure, currentChildren, custom_dropdow_children,custom_name,list_custom_features, feature_filter_dropdown_opts, feature_filter_default_opts, feature_filter_min_range, feature_filter_max_range, feature_filter_list, empty_array, apply_filters_state, collapse_expand_filter_disabled
            return restore_session(client, apply_filters_state, collapse_expand_filter_state, collapse_expand_filter_disabled,feature_filter_min_range, feature_filter_max_range, extract_values_custom_feature(currentDropdownChildren))

        else: 
            raise exceptions.PreventUpdate
        
        if main_dropdown != "":
            features.append(main_dropdown)
            
        # If no figure, return initial empty state
        if not currentFigure:
            #return client_data,custom_feature,empty,data_features, currentFigure, currentChildren, custom_dropdow_children,custom_name,list_custom_features, feature_filter_dropdown_opts, feature_filter_default_opts, feature_filter_min_range, feature_filter_max_range, feature_filter_list, empty_array, apply_filters_state, collapse_expand_filter_disabled
            return restore_session(client, apply_filters_state, collapse_expand_filter_state, collapse_expand_filter_disabled,feature_filter_min_range, feature_filter_max_range, extract_values_custom_feature(currentDropdownChildren))
        
        
        return ops_to_json(client),custom_feature, currentFigure, currentChildren, custom_name,list_custom_features, feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list, [], apply_filters_state, collapse_expand_filter_disabled
    
    return app