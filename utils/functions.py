from components.button_components import button
from styles.styles import button_dropdown_style
from dash import html
from backend.Class import Ops, session_features
import pandas as pd
import json
from datetime import date, datetime
import math
from utils.logic_functions import get_value_range

def list_feature_filter(client):
    return [html.Div([f"{feature_filter['feature_name']}, Range: ({get_value_range(feature_filter['range'][0],'-')} → {get_value_range(feature_filter['range'][1],'+')})", button(
                                text="REMOVE",
                                id={"type": "feature_filter_remove", "index": feature_filter["filter_uid"]},
                                style=button_dropdown_style,
                            )], className="mb-4") for feature_filter in client.feature_filters]

# Function to generate a list of custom filter components
def list_custom_filter_children(client):
    """
    Generates a list of HTML components for displaying custom features and a button to remove them.

    Args:
        client: An object managing the data and graphs.

    Returns:
        list: A list of HTML Div elements for each custom feature.
    """
    created_features = client.created_features
    return [
        html.Div(
            children=[
                # Display the custom feature name
                html.H4(
                    feature["feature_name"], 
                    className="mr-4 text-base font-bold text-slate-500", 
                    style={"white-space": "nowrap", "overflow": "hidden", "text-overflow": "ellipsis"}
                ),
                # Add a button to remove the custom feature
                button(
                    text="X",
                    id={"type": "custom_feature_remove", "index": feature["feature_id"]},
                    style=button_dropdown_style,
                )
            ],
            className="flex flex-row py-2 items-center justify-between"  # Styling for layout
        ) for feature in created_features
    ]


def ops_to_json(session: Ops):
    def default_serializer(obj):
        if isinstance(obj, pd.Timestamp):
           return obj.strftime('%Y-%m-%d')  # Convert Timestamp to string in 'YYYY-MM-DD' format
        if isinstance(obj, (pd.DatetimeIndex, pd.Series, pd.DataFrame)):
            return obj.to_json()
        if isinstance(obj, (datetime, date)):
            return obj.strftime('%Y-%m-%d')  # Convert date or datetime to string in 'YYYY-MM-DD' format
        
        raise TypeError(f"Type {type(obj)} not serializable")
    
    if session.feature_filters != []:
            for filter in session.feature_filters:
                if filter['range'][0] == -math.inf:
                    filter['range'][0] = -99999
                if filter['range'][1] == math.inf:
                    filter['range'][1] = 99999
    
    data_features_serialized: dict[str, session_features] = {}
    if session.session_data_features:
        for key, feature in session.session_data_features.items():
            data_features_serialized[key] = feature.to_dict()

    filtered_data = {
        "start_date": session.start_date,
        "end_date": session.end_date,
        "session_data_features": data_features_serialized,
        "graphs": session.graphs,
        "hour_filters": session.hour_filters,
        "day_of_week_filters": session.day_of_week_filters,
        "month_filters": session.month_filters,
        "year_filters": session.year_filters,
        "feature_filters": session.feature_filters,
    }
    return json.dumps(filtered_data, default=default_serializer, indent=4)

def json_to_ops(json_data):
    # Ensure `json_data` is parsed into a dictionary
    if isinstance(json_data, str):  # If it's a string, parse it
        data = json.loads(json_data)
    elif isinstance(json_data, dict):  # If it's already a dictionary, use it directly
        data = json_data
    else:
        raise TypeError("Input data must be a JSON string or dictionary.")

    # Create a new instance of Ops
    ops_instance = Ops()

    # Parse start_date and end_date as date objects
    date_format = "%Y-%m-%d"  # Adjust this format to match the input date strings
    ops_instance.start_date = (
        datetime.strptime(data.get("start_date"), date_format).date()
        if data.get("start_date") else None
    )
    ops_instance.end_date = (
        datetime.strptime(data.get("end_date"), date_format).date()
        if data.get("end_date") else None
    )
    session_dict = data.get("session_data_features")
    session_features_dict: dict[str, session_features] = {}
    if session_dict:
        for key, value in session_dict.items():
            session_instance = session_features()
            session_instance.from_dict(value)
            session_features_dict[key] = session_instance

    # Populate the instance
    ops_instance.session_data_features = session_features_dict
    ops_instance.graphs = data.get("graphs")
    ops_instance.hour_filters = data.get("hour_filters")
    ops_instance.day_of_week_filters = data.get("day_of_week_filters")
    ops_instance.month_filters = data.get("month_filters")
    ops_instance.year_filters = data.get("year_filters")
    ops_instance.feature_filters = data.get("feature_filters")
    # Run the update methods
    ops_instance.update_data()
    ops_instance.update_datetimes_to_exclude()
    ops_instance.update_filter_df()
    
    return ops_instance

def ops_to_json_upload(session: Ops):
    df = session.df.reset_index()
    filter_df = session.filter_df.reset_index()

    try:
       df['Datetime (HB)'] = df['Datetime (HB)'].astype(str)
       filter_df['Datetime (HB)'] = filter_df['Datetime (HB)'].astype(str)
    except:
        pass
    try:
       df['datetime'] = df['datetime'].astype(str)
       filter_df['datetime'] = filter_df['datetime'].astype(str)
    except:
        pass
    try:
       df['index'] = df['index'].astype(str)
       filter_df['index'] = filter_df['index'].astype(str)
    except:
        pass
    
    data_features_serialized: dict[str, session_features] = {}
    if session.session_data_features:
        for key, feature in session.session_data_features.items():
            data_features_serialized[key] = feature.to_dict()

    filtered_data = {
        "df": df.to_dict(orient='records'),
        "filter_df": filter_df.to_dict(orient='records'),
        "start_date":session.start_date.strftime('%Y-%m-%d'),
        "end_date":session.end_date.strftime('%Y-%m-%d'),
        "session_data_features": data_features_serialized,
        "graphs": session.graphs,
        "hour_filters": session.hour_filters,
        "day_of_week_filters": session.day_of_week_filters,
        "month_filters": session.month_filters,
        "year_filters": session.year_filters,
        "feature_filters": session.feature_filters,
    }
    return json.dumps(filtered_data, indent=4)

def json_to_ops_upload(json_data):
    # Ensure `json_data` is parsed into a dictionary
    if isinstance(json_data, str):  # If it's a string, parse it
        data = json.loads(json_data)
        df = pd.DataFrame(data["df"])
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0])
        df.set_index(df.columns[0], inplace=True)
        
        start_date = pd.to_datetime(data["start_date"]).date()
        end_date = pd.to_datetime(data["end_date"]).date()
        filter_df = pd.DataFrame(data["filter_df"])
        if not filter_df.empty:
            filter_df.iloc[:, 0] = pd.to_datetime(filter_df.iloc[:, 0])
            filter_df.set_index(filter_df.columns[0], inplace=True)
        
    elif isinstance(json_data, dict):  # If it's already a dictionary, use it directly
        data = json_data
    else:
        raise TypeError("Input data must be a JSON string or dictionary.")

    # Create a new instance of Ops
    ops_instance = Ops()
    
    session_dict = data.get("session_data_features")
    session_features_dict: dict[str, session_features] = {}
    if session_dict:
        for key, value in session_dict.items():
            session_instance = session_features()
            session_instance.from_dict(value)
            session_features_dict[key] = session_instance

    # Populate the instance
    ops_instance.df = df
    ops_instance.filter_df = filter_df
    ops_instance.session_data_features = session_features_dict
    ops_instance.start_date = start_date
    ops_instance.end_date = end_date
    ops_instance.graphs = data.get("graphs")
    ops_instance.hour_filters = data.get("hour_filters")
    ops_instance.day_of_week_filters = data.get("day_of_week_filters")
    ops_instance.month_filters = data.get("month_filters")
    ops_instance.year_filters = data.get("year_filters")
    ops_instance.feature_filters = data.get("feature_filters")
    # Run the update methods
    ops_instance.update_datetimes_to_exclude()
    ops_instance.update_filter_df()

    return ops_instance

