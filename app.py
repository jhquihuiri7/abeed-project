# Python packages
import math
import io
import pandas as pd
from datetime import date

# Dash imports
from dash import Dash, _dash_renderer
from dash import (
    dcc,
    html,
    Input,
    Output,
    State,
    callback,
    callback_context,
    ALL,
    MATCH,
    exceptions,
)

# Components
import dash_mantine_components as dmc
from components.checkbox_components import expandable_container
from components.daterange_components import main_daterange
from components.tabs_components import main_tabs
from components.button_components import button, apply_filters_toggle
from components.notification_components import show_notification, show_modal
from components.graph_components import multi_chart, bar_chart
from components.dropdown_components import (
    main_dropdown,
    date_filter_dropdown,
    custom_features_children,
    remove_features_children,
    delete_features_dropdown,
)


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
    validateApplyFilterToggle,
    validate_add_features,
    validate_delete_features,
)
from utils.functions import (
    list_custom_filter_children,
    ops_to_json,
    json_to_ops,
    list_feature_filter,
)

# Backend
from backend.Class import Ops

# Styles
from utils.styles import button_style, hourButtonStyle

# React version setting
_dash_renderer._set_react_version("18.2.0")

ops = Ops()

def create_dash_app(server):

    # External scripts (e.g., TailwindCSS)
    external_stylesheets = [dmc.styles.NOTIFICATIONS]

    external_scripts = ["https://cdn.tailwindcss.com"]

    # Initialize the Dash app
    app = Dash(
        __name__,
        server=server,
        url_base_pathname="/home/",
        external_scripts=external_scripts,
        external_stylesheets=external_stylesheets,
        meta_tags=[
            {"name": "viewport", "content": "width=device-width, initial-scale=1"}
        ],
    )
    app.title = "Market Operation Dashboard"
    # app._favicon = "favicon.ico"
    app.layout = dmc.MantineProvider(
        children=[
            html.Div(
                className="p-10 w-full",
                children=[
                    html.Div(
                        className="w-full flex flex-row justify-around",
                        children=[
                            expandable_container(
                                toggle_button_id="toggle_exapandable_button_primary",
                                expandable_text_id="expandable_text_primary",
                                client=ops,
                            ),
                            button(
                                text="Download Data",
                                id="download_data_button",
                                style=button_style,
                            ),
                            button(
                                text="Save Session",
                                id="download_client_button",
                                style=button_style,
                            ),
                        ],
                    ),
                    html.Div(
                        children=[
                            main_dropdown(ops, "w-[56%]"),
                            button(
                                text="Add Features",
                                id="add_feature_button",
                                style=button_style,
                            ),
                        ],
                        className="flex flex-row justify-start w-1/2 mb-5",
                    ),
                    html.Div(
                        children=[
                            delete_features_dropdown(ops),
                            button(
                                text="Remove Features",
                                id="delete_features_button",
                                style=button_style,
                            ),
                        ],
                        className="flex flex-row justify-start w-1/2 mb-5",
                    ),
                    html.Div(
                        children=[
                            main_daterange(ops),
                            button(
                                text="Update Dates",
                                id="update_date_range_button",
                                style=button_style,
                            ),
                        ],
                        className="flex flex-row justify-start w-1/2",
                    ),
                    main_tabs(ops),  # Tabs component for layout
                    apply_filters_toggle("Collapse", is_upload=False),
                    dcc.Graph(id="main_graph"),  # Graph for displaying data
                    button(
                        text="Add Graph", id="add_graph_button", style=button_style
                    ),  # Button to add new graph
                    html.Div(
                        id="dynamic_div", children=[], className="flex flex-wrap"
                    ),  # Dynamic div for additional content
                    dmc.NotificationProvider(position="top-center"),
                    html.Div(id="notifications-container"),
                    show_modal(),
                    dcc.Download(id="download-data"),
                    dcc.Download(id="download-client"),
                    dcc.Store(id="temp_feature", data=[]),
                    dcc.Store(id="restore_session", data=""),
                    dcc.Store(id="custom_feature_options", data=[]),
                    dcc.Store(id="alias_map", data={}),
                ],
            ),
            dcc.Store(id="client", data=ops_to_json(ops)),
            dcc.Store(id="init_flag", data=False),
        ]
    )
    @app.callback(
        Output("init_flag", "data"),
        Output("main_dropdown", "options", allow_duplicate=True),
        Input("client", "data"),
        State("init_flag", "data"),
        prevent_initial_call='initil_duplicate'
    )
    def initial_call(client, init_flag):
        global ops, books
        if init_flag:  
            raise exceptions.PreventUpdate
        ops = Ops(load_features=True)
        return True, [item for item in ops.display_features_dict]

    @app.callback(
        Output("delete_features_dropdown", "options"), Input("client", "data")
    )
    def delete_feature_dropdown(data):
        client = json_to_ops(data, db_features_json=ops.db_features_json)
        return client.df.columns

    @app.callback(
        Output("main-date-picker-range", "start_date"),
        Output("main-date-picker-range", "end_date"),
        Output("main_dropdown", "value"),
        Input("restore_session", "data"),
        State("client", "data"),
    )
    def restore_session_call(session, data):
        client = json_to_ops(data, db_features_json=ops.db_features_json)
        return client.start_date, client.end_date, []  

    @app.callback(
        Output("main_dropdown", "options"),
        Output("expandable_text_primary", "style"),
        Output("toggle_exapandable_button_primary", "children"),
        Input("toggle_exapandable_button_primary", "n_clicks"),
        State("expandable_text_primary", "style"),
        prevent_initial_call=True,
    )
    def toggle_text_primary(n_clicks, expandable_text_primary):
        ctx = callback_context
        if not ctx.triggered:
            raise exceptions.PreventUpdate
        options = [item for item in ops.display_features_dict]
        if n_clicks % 2 == 1:
            if expandable_text_primary["display"] == "block":
                options = list(set(options) | set([item for item in ops.db_name_dict]))
            return options, {"display": "block"}, "Collapse Feature Menu"
        return options, {"display": "none"}, "Expand Feature Menu"

    @app.callback(
        Output("main_dropdown", "options", allow_duplicate=True),
        Input("all_features_checkbox", "value"),
        prevent_initial_call=True,
    )
    def toggle_all_features(value):
        global ops
        ctx = callback_context
        if not ctx.triggered:
            raise exceptions.PreventUpdate
        options = [item for item in ops.display_features_dict]
        if value != []:
            options = list(set(options) | set(ops.db_name_dict))
        return options

    @app.callback(
        Output("download-client", "data"),
        Output("input-modal", "opened"),
        Input("download_client_button", "n_clicks"),
        Input("save-button", "n_clicks"),
        State("client", "data"),
        State("user-session", "value"),
        prevent_initial_call=True,
    )
    def download_client(download_client_button, save_button, data, value):
        ctx = callback_context
        if not ctx.triggered:
            raise exceptions.PreventUpdate
        triggered_id = callback_context.triggered[0]["prop_id"].split(".")[0]
        if triggered_id == "download_client_button":
            return None, True

        client = json_to_ops(data, db_features_json=ops.db_features_json)
        client_json = ops_to_json(client)
        if value == None:
            value = date.today().strftime("%Y-%m-%d")
        return dict(content=client_json, filename=f"{value}.json"), False

    @app.callback(
        Output("download-data", "data"),
        Input("download_data_button", "n_clicks"),
        State("main_graph", "figure"),
        State("client", "data"),
        prevent_initial_call=True,
    )
    def download_logic(n_clicks, currentFigure, data):
        client = json_to_ops(data, db_features_json=ops.db_features_json)
        export_df = pd.DataFrame()
        if currentFigure:  # Ensure the figure is not None
            sub_features = [
                i["name"] for i in currentFigure["data"] if i["visible"] == True
            ]
            export_df = client.df[sub_features]

        buffer = io.StringIO()
        export_df.reset_index(inplace=True)
        export_df.rename(columns={"datetime": "Datetime (HB)"}, inplace=True)
        export_df.to_csv(buffer, index=False, encoding="utf-8")
        buffer.seek(0)

        return dict(content=buffer.getvalue(), filename="data.csv")

    @app.callback(
        Output("collapse_expand_filter", "label"),
        Input("collapse_expand_filter", "value"),
    )
    def update_apply_filters(collapse_expand_filter):
        ctx = callback_context
        if not ctx.triggered:
            raise exceptions.PreventUpdate
        return "Collapse" if collapse_expand_filter else "Expand"

    @app.callback(
        Output("date_filter_dropdown", "children"),
        Input("select_all_datefilter", "n_clicks"),
        State("date_filter_dropdown", "children"),
        prevent_initial_call=True,  # Prevent initial callback call
    )
    def update_date_filter(select_all_datefilter, datefilter_dropdown):
        ctx = callback_context
        if not ctx.triggered:
            raise exceptions.PreventUpdate
        triggered_id = (
            ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None
        )
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
        Output("hour_filter_buttons", "children"),
        Output("year_dropdown_date_filter", "value"),
        Output("month_dropdown_date_filter", "value"),
        Output("day_dropdown_date_filter", "value"),
        Input("restore_session", "data"),
        State("client", "data"),
    )
    def reset_session_hourfilter(session, data):
        ctx = callback_context
        if not ctx.triggered:
            raise exceptions.PreventUpdate
        client = json_to_ops(data, db_features_json=ops.db_features_json)
        hour_filter_buttons = []
        for hour in range(0, 24):
            hour_filter_buttons.append(
                html.Button(
                    hour,  # Text displayed on the button
                    id={
                        "type": "hour_button",
                        "index": hour,
                    },  # Unique ID for the button
                    n_clicks=0,  # Initial click count set to 0
                    style={
                        "backgroundColor": (
                            "#d9d9d9" if hour in client.hour_filters else "white"
                        )
                    },  # Default background color
                    className=hourButtonStyle,  # CSS class for styling the button
                )
            )
        return (
            hour_filter_buttons,
            client.year_filters,
            client.month_filters,
            client.day_of_week_filters,
        )

    @app.callback(
        Output("custon_operation", "value"),
        Input("add_custom_feature", "n_clicks"),
    )
    def reset_custom_tab(add_custom_feature):
        return ""

    @app.callback(
        Output({"type": "hour_button", "index": ALL}, "style"),
        Input({"type": "hour_button", "index": ALL}, "n_clicks"),
        Input("apply_hour_range", "n_clicks"),
        Input("select_all_hour_range", "n_clicks"),
        Input("deselect_all_hour_range", "n_clicks"),
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
        if not ctx.triggered:
            raise exceptions.PreventUpdate
        triggered_id = (
            ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None
        )
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
            hour_button_style[index]["backgroundColor"] = (
                "white"
                if hour_button_style[index]["backgroundColor"] == "#d9d9d9"
                else "#d9d9d9"
            )

        if triggered_id == "deselect_all_hour_range":
            for index in range(0, 24):
                hour_button_style[index][
                    "backgroundColor"
                ] = "white"  # Toggle the background color when the hour button is clicked
            return hour_button_style

        if triggered_id == "select_all_hour_range":
            for index in range(0, 24):
                hour_button_style[index][
                    "backgroundColor"
                ] = "#d9d9d9"  # Toggle the background color when the hour button is clicked
            return hour_button_style

        if triggered_id == "apply_hour_range":
            for index in range(hour_filter_slider[0], hour_filter_slider[1] + 1):
                hour_button_style[index]["backgroundColor"] = (
                    "#d9d9d9" if triggered_id == "apply_hour_range" else "white"
                )
            return hour_button_style

        return hour_button_style

    @app.callback(
        Output({"type": "feature_dropdown", "index": ALL}, "options"),
        Input("custom_feature_options", "data"),
        State("custom_dropdown", "children"),
    )
    def update_custom_dropdown_options(options, custom_dropdown):
        output = []
        for i in range(len(custom_dropdown) - 1):
            output.append(options)
        return output

    @app.callback(
        Output({"type": "feature_alias", "index": MATCH}, "value"),
        Input({"type": "feature_dropdown", "index": MATCH}, "value"),
        State({"type": "feature_alias", "index": MATCH}, "value"),
        prevent_initial_call=True,
    )
    def update_custom_dropdown_alias(triggered_value, current_alias):
        ctx = callback_context
        if not ctx.triggered:
            raise exceptions.PreventUpdate
        if current_alias != "":
            raise exceptions.PreventUpdate
        return triggered_value

    @app.callback(
        Output("custom_dropdown", "children"),
        Input({"type": "add_custom_alias", "index": ALL}, "n_clicks"),
        Input("remove_last_alias", "n_clicks"),
        Input("add_custom_feature", "n_clicks"),
        Input("client", "data"),
        State("custom_dropdown", "children"),
        prevent_initial_call=True,
    )
    def custom_dropdown_children(
        add_custom_alias,
        remove_last_alias,
        add_custom_feature,
        data,
        currentDropdownChildren,
    ):
        ctx = callback_context
        triggered_id = (
            ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None
        )

        try:
            if "type" in triggered_id:
                triggered_id = eval(triggered_id)
        except:
            pass

        if (
            isinstance(triggered_id, dict)
            and triggered_id.get("type") == "add_custom_alias"
        ):
            currentDropdownChildren = custom_features_children(
                [], currentDropdownChildren
            )

        elif triggered_id == "remove_last_alias":
            currentDropdownChildren = remove_features_children(currentDropdownChildren)

        elif triggered_id == "add_custom_feature":
            currentDropdownChildren = custom_features_children([], [])
        return currentDropdownChildren

    @app.callback(
        Output("client", "data"),
        Output("main_graph", "figure"),
        Output("dynamic_div", "children"),
        Output("custon_name", "value"),
        Output("feature_filter_dropdown", "options"),
        Output("feature_filter_dropdown", "value"),
        Output("feature_filter_min_range", "value"),
        Output("feature_filter_max_range", "value"),
        Output("feature_filter_list", "children"),
        Output("notifications-container", "children"),
        Output("apply_filters", "value"),
        Output("collapse_expand_filter", "disabled"),
        Output("custom_feature_options", "data"),
        # Inputs and states for callback
        Input("add_feature_button", "n_clicks"),
        Input("delete_features_button", "n_clicks"),  # update_date_range_button
        Input("update_date_range_button", "n_clicks"),
        Input("add_graph_button", "n_clicks"),
        Input({"type": "remove_button", "index": ALL}, "n_clicks"),
        Input({"type": "dynamic-dropdown", "index": ALL}, "value"),
        Input("add_custom_feature", "n_clicks"),
        Input("feature_filter_add", "n_clicks"),
        Input({"type": "feature_filter_remove", "index": ALL}, "n_clicks"),
        Input("apply_selection_hourfilter", "n_clicks"),
        Input("apply_filters", "value"),
        Input("collapse_expand_filter", "value"),
        Input("apply_selection_datefilter", "n_clicks"),
        # Input("remove_last_alias", "n_clicks"),
        # Input({"type": "hour_button", "index": ALL}, "n_clicks"),
        State("main_dropdown", "value"),
        State("delete_features_dropdown", "value"),
        State("main-date-picker-range", "start_date"),
        State("main-date-picker-range", "end_date"),
        State("main_graph", "figure"),
        State("dynamic_div", "children"),
        State("custom_dropdown", "children"),
        State("custon_name", "value"),
        State("custom_cumulative", "value"),
        State("feature_filter_dropdown", "options"),
        State("feature_filter_dropdown", "value"),
        State("feature_filter_min_range", "value"),
        State("feature_filter_max_range", "value"),
        State("feature_filter_list", "children"),
        State({"type": "hour_button", "index": ALL}, "style"),
        State("apply_filters", "value"),
        State("collapse_expand_filter", "value"),
        State("collapse_expand_filter", "disabled"),
        State("year_dropdown_date_filter", "value"),
        State("month_dropdown_date_filter", "value"),
        State("day_dropdown_date_filter", "value"),
        State("client", "data"),
        State("custon_operation", "value"),
        State({"type": "feature_alias", "index": ALL}, "value"),
        State({"type": "feature_dropdown", "index": ALL}, "value"),
    )
    def update_render(
        add_feature_button,
        delete_feature_button,
        update_date_range_button,
        add_button,
        remove_button,
        dynamic_dropdown,
        add_custom_feature,
        feature_filter_add,
        feature_filter_remove,
        apply_selection_hourfilter,
        apply_filters,
        collapse_expand_filter,
        apply_selection_datefilter,
        # remove_last_alias,
        features,
        delete_features_dropdown,
        start_date,
        end_date,
        currentFigure,
        currentChildren,
        currentDropdownChildren,
        custom_name,
        custom_cumulative,
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
        custon_operation,
        custom_alias,
        custom_feature,
    ):
        client = json_to_ops(data, db_features_json=ops.db_features_json)
        notification = []
        ctx = callback_context
        triggered_id = (
            ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None
        )
        try:
            # Try to convert dynamic trigger ID to dictionary if possible
            if "type" in triggered_id:
                triggered_id = eval(triggered_id)
        except:
            pass

        client.start_date = start_date
        client.end_date = end_date

        if triggered_id == "add_feature_button":
            is_valid, message = validate_add_features(features)
            if is_valid:
                try:
                    client.add_db_data_features_button(features)
                    currentFigure = bar_chart(
                        client,
                        None,
                        apply_filters_state != [],
                        collapse_expand_filter_state,
                    )
                    currentChildren = multi_chart(
                        client, apply_filters_state != [], collapse_expand_filter_state
                    )
                    feature_filter_dropdown_opts = get_feature_filter_dropdown_opts(client)
                except ValueError as e:
                    message = str(e)
                    notification = show_notification(message)
                
            else:
                notification = show_notification(message)

        if triggered_id == "delete_features_button":
            is_valid, message = validate_delete_features(
                client, delete_features_dropdown
            )
            if is_valid:
                client.remove_data_features_button(delete_features_dropdown)
                currentFigure = bar_chart(
                    client,
                    None,
                    apply_filters_state != [],
                    collapse_expand_filter_state,
                )
                currentChildren = multi_chart(
                    client, apply_filters_state != [], collapse_expand_filter_state
                )
                feature_filter_dropdown_opts = get_feature_filter_dropdown_opts(client)
            else:
                notification = show_notification(message)

        if triggered_id == "update_date_range_button":
            client.update_date_range_button(client.start_date, client.end_date)
            currentFigure = bar_chart(
                client, None, apply_filters_state != [], collapse_expand_filter_state
            )
            currentChildren = multi_chart(
                client, apply_filters_state != [], collapse_expand_filter_state
            )
            feature_filter_dropdown_opts = get_feature_filter_dropdown_opts(client)

        elif triggered_id == "add_graph_button":
            sub_features = [
                i["name"] for i in currentFigure["data"] if i["visible"] == True
            ]
            client.add_graph_button(sub_features)
            currentChildren = multi_chart(
                client, apply_filters_state != [], collapse_expand_filter_state
            )

        elif (
            isinstance(triggered_id, dict)
            and triggered_id.get("type") == "remove_button"
        ):
            client.remove_graph_button(triggered_id.get("index"))
            currentChildren = multi_chart(
                client, apply_filters_state != [], collapse_expand_filter_state
            )

        elif triggered_id == "add_custom_feature":
            alias_map = {}
            custom_cumulative = len(custom_cumulative) == 2
            for alias, feature in zip(custom_alias, custom_feature):
                alias_map[alias] = feature
            is_valid, message = validate_add_custom_feature(
                client, custon_operation, alias_map, custom_name, custom_cumulative
            )
            if is_valid:
                custom_name = None if custom_name == "" else custom_name
                client.create_custom_feature_button(
                    custon_operation, alias_map, custom_cumulative, custom_name
                )
                currentFigure = bar_chart(
                    client,
                    None,
                    apply_filters_state != [],
                    collapse_expand_filter_state,
                )
                feature_filter_dropdown_opts = get_feature_filter_dropdown_opts(client)
                custom_name = ""
            else:
                notification = show_notification(message)

        if triggered_id == "feature_filter_add":
            is_valid, message, feature_filter_min_range, feature_filter_max_range = (
                validateFeatureFilterData(
                    client,
                    feature_filter_dropdown,
                    feature_filter_min_range,
                    feature_filter_max_range,
                )
            )
            if is_valid:
                client.add_feature_filter_button(
                    feature_filter_dropdown,
                    feature_filter_min_range,
                    feature_filter_max_range,
                )
                feature_filter_list = list_feature_filter(client)
                feature_filter_dropdown_opts = get_feature_filter_dropdown_opts(client)
                apply_filters_state = ["Apply filter"]
                collapse_expand_filter_disabled = False
                currentFigure = bar_chart(
                    client,
                    None,
                    apply_filters_state != [],
                    collapse_expand_filter_state,
                )
                currentChildren = multi_chart(
                    client, apply_filters_state != [], collapse_expand_filter_state
                )
                feature_filter_min_range = ""
                feature_filter_max_range = ""
            else:
                notification = show_notification(message)

        if (
            isinstance(triggered_id, dict)
            and triggered_id.get("type") == "feature_filter_remove"
        ):
            index = triggered_id.get("index")
            client.remove_feature_filter_button(index)
            feature_filter_list = list_feature_filter(client)
            feature_filter_dropdown_opts = get_feature_filter_dropdown_opts(client)
            apply_filters_state = ["Apply filter"]
            collapse_expand_filter_disabled = False
            currentFigure = bar_chart(
                client, None, apply_filters_state != [], collapse_expand_filter_state
            )
            currentChildren = multi_chart(
                client, apply_filters_state != [], collapse_expand_filter_state
            )

        if (triggered_id == "apply_selection_datefilter") or (
            triggered_id == "apply_selection_hourfilter"
        ):
            hours_to_include = [
                index
                for index, hour in enumerate(hour_button)
                if hour["backgroundColor"] != "white"
            ]
            client.apply_datetime_filters_button(
                hours_to_include,
                day_dropdown_date_filter_state,
                month_dropdown_date_filter_state,
                year_dropdown_date_filter_state,
            )
            is_valid, message = validateApplyDatetimeSelection(client)
            if is_valid:
                apply_filters_state = ["Apply filter"]
                collapse_expand_filter_disabled = False
                currentFigure = bar_chart(
                    client,
                    None,
                    apply_filters_state != [],
                    collapse_expand_filter_state,
                )
                currentChildren = multi_chart(
                    client, apply_filters_state != [], collapse_expand_filter_state
                )
            else:
                notification = show_notification(message)

        if triggered_id == "apply_filters":
            is_valid, message = validateApplyFilterToggle(
                client, apply_filters_state, collapse_expand_filter_state
            )
            if is_valid:
                if apply_filters_state == []:
                    collapse_expand_filter_disabled = True
                    currentFigure = bar_chart(client, None, False, False)
                else:
                    collapse_expand_filter_disabled = False
                    currentFigure = bar_chart(
                        client,
                        None,
                        apply_filters_state != [],
                        collapse_expand_filter_state,
                    )
            else:
                notification = show_notification(message)
            currentChildren = multi_chart(
                client, apply_filters_state != [], collapse_expand_filter_state
            )

        if triggered_id == "collapse_expand_filter":
            currentFigure = bar_chart(
                client, None, apply_filters_state != [], collapse_expand_filter_state
            )
            currentChildren = multi_chart(
                client, apply_filters_state != [], collapse_expand_filter_state
            )

        if not currentFigure:
            return restore_session(
                client,
                apply_filters_state,
                collapse_expand_filter_state,
                collapse_expand_filter_disabled,
                feature_filter_min_range,
                feature_filter_max_range,
                currentDropdownChildren,
            )

        return (
            ops_to_json(client),
            currentFigure,
            currentChildren,
            custom_name,
            feature_filter_dropdown_opts,
            feature_filter_dropdown,
            feature_filter_min_range,
            feature_filter_max_range,
            feature_filter_list,
            notification,
            apply_filters_state,
            collapse_expand_filter_disabled,
            client.df.columns,
        )

    return app
