import pandas as pd
from datetime import datetime
from backend.db_dictionaries import feature_units_dict


def convert_df_to_dict(df):
    """
    Converts a Pandas DataFrame into a list of dictionaries for storage in Dash's dcc.Store component.

    Parameters:
        df (pd.DataFrame): The DataFrame to be converted.

    Returns:
        list: A list of dictionaries with each dictionary representing a row in the DataFrame.
    """
    # Reset the index (Datetime) to include it as a column, then convert to dict
    df_reset = df.reset_index()
    new_dict = df_reset.to_dict(orient="records")
    return new_dict


def convert_dict_to_df(dict):
    """
    Converts a list of dictionaries back into a Pandas DataFrame and adjusts the 'datetime' column have a datetime dtype and set the datetime column as the index.

    Parameters:
        dict (list): A list of dictionaries, where each dictionary represents a row of data.

    Returns:
        pd.DataFrame: A DataFrame with the 'datetime' column as the index.
    """
    # Convert dict to df
    df = pd.DataFrame(dict)

    # Convert the datetime column to datetime dtype (of timestamp type if not done)
    df["datetime"] = pd.to_datetime(df["datetime"])

    # Set the index and drop the column
    df.set_index("datetime", inplace=True)

    return df


def get_excluded_datetimes(
    df, hour_filters, day_of_week_filters, month_filters, year_filters, feature_filters
):
    dates_to_exclude = []

    for filter in feature_filters:
        feature_name = filter["feature_name"]
        min_value = filter["range"][0]
        max_value = filter["range"][1]
        min_value = float("-inf") if min_value is None else min_value
        max_value = float("inf") if max_value is None else max_value
        dates_to_exclude_series = df.index[
            (df[feature_name] <= min_value) | (df[feature_name] >= max_value)
        ]
        dates_to_exclude.extend(dates_to_exclude_series.to_list())
    dates_to_exclude = list(set(dates_to_exclude))

    dates_to_exclude_series = df.index[
        ~(df.index.hour.isin(hour_filters))
        | ~(df.index.weekday.isin(day_of_week_filters))
        | ~(df.index.month.isin(month_filters))
        | ~(df.index.year.isin(year_filters))
    ]
    dates_to_exclude.extend(dates_to_exclude_series.to_list())

    # for idx, datetimes in enumerate(dates_to_exclude):
    #     dates_to_exclude[idx] = datetimes.to_datetime64()

    # print(dates_to_exclude)

    dates_to_exclude = sorted(list(set(dates_to_exclude)))
    return dates_to_exclude


def get_feature_units(feature_name):
    return feature_units_dict[feature_name]


def add_custom_feature_column(df: pd.DataFrame, custom_feature):
    available_features = df.columns.to_list()
    for features in custom_feature["equation"]:
        feature_name = features["Feature"]
        if feature_name not in available_features:
            return df

    custom_feature_series = pd.Series
    for idx, features in enumerate(custom_feature["equation"]):
        if idx == 0:
            custom_feature_series = df[features["Feature"]]

        elif features["Operation"] == "+":
            custom_feature_series = custom_feature_series + df[features["Feature"]]

        elif features["Operation"] == "-":
            custom_feature_series = custom_feature_series - df[features["Feature"]]

    if custom_feature["cumulative?"]:
        custom_feature_series = custom_feature_series.cumsum()

    df[custom_feature["feature_name"]] = custom_feature_series

    return df
