from utils.functions import ops_to_json, ops_to_json_upload,list_custom_filter_children
from utils.logic_functions import get_value_range, get_feature_filter_dropdown_opts
from components.dropdown_components import custom_features_children
from components.graph_components import bar_chart, multi_chart
import plotly.graph_objects as go
from dash import html
from components.button_components import button
from backend.Class import Ops, session_features
# Styles
from styles.styles import button_dropdown_style


def restore_session(client: Ops, apply_filters_state, collapse_expand_filter_state, collapse_expand_filter_disabled, feature_filter_min_range, feature_filter_max_range, currentDropdownChildren):
    
    currentFigure = go.Figure()
    currentChildren = []
    custom_name = ""
    feature_filter_dropdown_opts = get_feature_filter_dropdown_opts(client)
    feature_filter_dropdown_default = ""
    feature_filter_list = []
    if client.feature_filters != [] or client.year_filters != [] or client.month_filters != [] or client.day_of_week_filters or client.hour_filters:
        apply_filters_state = ["Apply filter"]
        collapse_expand_filter_disabled = False
    
    if client.session_data_features:
        currentFigure = bar_chart(client, None, apply_filters_state!=[], collapse_expand_filter_state)
        
    if client.graphs != []:
        currentChildren = multi_chart(client, apply_filters_state!=[], collapse_expand_filter_state)
        
    if client.feature_filters != []:
        feature_filter_list = [html.Div([f"{feature_filter['feature_name']}, Range: ({get_value_range(feature_filter['range'][0],'-')} → {get_value_range(feature_filter['range'][1],'+')})", button(
                                text="REMOVE",
                                id={"type": "feature_filter_remove", "index": feature_filter["filter_uid"]},
                                style=button_dropdown_style,
                            )], className="mb-4") for feature_filter in client.feature_filters]
        
    return ops_to_json(client), currentFigure,currentChildren, custom_name, feature_filter_dropdown_opts, feature_filter_dropdown_default, feature_filter_min_range, feature_filter_max_range, feature_filter_list,[], apply_filters_state, collapse_expand_filter_disabled, client.df.columns
    

def restore_session_upload(client: Ops, apply_filters_state, collapse_expand_filter_state, collapse_expand_filter_disabled, feature_filter_min_range, feature_filter_max_range):
    currentFigure = go.Figure()
    currentChildren = []
    feature_filter_dropdown_opts = client.df.columns
    feature_filter_dropdown_default = ""
    feature_filter_list = []
    notification = []
    init_columns = client.df.columns
    main_dropdown = []
    currentFigure = bar_chart(client, None, apply_filters_state!=[], collapse_expand_filter_state)
        
    return ops_to_json_upload(client), currentFigure,currentChildren, feature_filter_dropdown_opts, feature_filter_dropdown_default, feature_filter_min_range, feature_filter_max_range, feature_filter_list, notification, apply_filters_state, collapse_expand_filter_disabled, init_columns, main_dropdown







