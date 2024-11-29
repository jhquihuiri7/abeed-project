from backend.endpoint_helper import simple_request
from backend.db_dictionaries import (
    feature_db_id_to_read_name,
    feature_db_name_to_read_name_dict,
    feature_read_name_to_db_name_dict,
    feature_units_dict,
    features_read_name_to_db_id_dict,
)
from backend.helper_functions import *
import pandas as pd
import uuid
from datetime import date, datetime
import unittest
import pdb


class Ops:
    def __init__(self) -> None:

        # Dataframe to hold all the requested data based on self.start_date, self.end_date, and self.data_features
        self.df = pd.DataFrame()

        # A list of dictoinaries, each representing a graph. Each graph dictionary has a unique id and a list of features it will graph:
        self.graphs = []
        # single dictionary ex. {"graph_uid": '6da8871a-2860-474d-a8bf-4efa7383e26b', "graph_data_features": ["MISO pjm RT", "MISO pjm DA"]}

        # List of hours to include when graphing with filters (0-23)
        self.hour_filters = list(range(24))

        # List of days of the week to include when graphing with filters (0-6)
        self.day_of_week_filters = list(range(7))

        # List of months to include when graphing with filters (0-11)
        self.month_filters = list(range(12))

        # List of years to include when graphing with filters (2000-2025)
        self.year_filters = list(range(2000, 2026))

        # A list of dictoinaries, each representing a filter for a feature. Each feature filter dictionary has a unique id,
        # the feature the filter is for, and the range the feature value should be within
        self.feature_filters = []
        # Single dictionary ex. {"filter_uid": '407f3d5d-9c1f-43d5-b35d-a559f6faf527', "feature_name": "MISO pjm RT", "range": [0.00, 50.00]}

        # A list of dates that should be excluded based off of the data in the dataframe and all the filters
        self.datetimes_to_exclude = []

        # A toggle to switch bettween viewing the filtered data and the un filtered data
        self.apply_filters_toggle = False

    def update_df(self, new_features_list: list[str], start_date, end_date):
        if new_features_list and start_date and end_date:
            db_names = []
            for feature in new_features_list:
                db_names.append(feature_read_name_to_db_name_dict[feature])
            self.df = simple_request(start_date, end_date, db_names)[0]
            self.df.rename(columns=feature_db_name_to_read_name_dict, inplace=True)

    def add_graph(self, features_list: list[str]):

        # this is incase the user tries to make a graph with features that haven't been requested,
        # in reality this would not be possible because the user selects the features for new graphs
        # from the features that have been selected
        # for feature in features_list:
        # if not feature in self.data_features:
        #    print(f"{feature} has not been requested")
        #    return None

        new_graph = {
            "graph_uid": str(uuid.uuid4()),
            "graph_data_features": features_list,
        }
        self.graphs.append(new_graph)

    def remove_graph(self, target_uuid: str):
        self.graphs = [
            graphs for graphs in self.graphs if graphs["graph_uid"] != target_uuid
        ]

    def update_hour_filters(self, hours_to_include: list[int]):
        self.hour_filters = hours_to_include
        if not self.df.empty:
            self.update_datetimes_to_exclude()

    def update_days_of_week_filters(self, days_of_week_to_include: list[int]):
        self.day_of_week_filters = days_of_week_to_include
        if not self.df.empty:
            self.update_datetimes_to_exclude()

    def update_month_filters(self, months_to_include: list[int]):
        self.hour_filters = months_to_include
        if not self.df.empty:
            self.update_datetimes_to_exclude()

    def update_year_filters(self, years_to_include: list[int]):
        self.year_filters = years_to_include
        if not self.df.empty:
            self.update_datetimes_to_exclude()

    def add_feature_filter(
        self, feature_name: str, lower_bound: float, upper_bound: float
    ):
        # TODO only allow user to select features from the data_features list to filter by
        if feature_name not in self.df.columns.to_list():
            print(f"Feature has not been requested yet")

        elif not any(d["feature_name"] == feature_name for d in self.feature_filters):
            new_feature_filter = {
                "filter_uid": str(uuid.uuid4()),
                "feature_name": feature_name,
                "range": [lower_bound, upper_bound],
            }
            self.feature_filters.append(new_feature_filter)

            if not self.df.empty:
                self.update_datetimes_to_exclude()
        else:
            print(f"A filter already exists for the {feature_name} feature")

    def remove_feature_filter(self, target_uuid: str):
        self.feature_filters = [
            filters
            for filters in self.feature_filters
            if filters["filter_uid"] != target_uuid
        ]

    def update_datetimes_to_exclude(self):
        if not self.df.empty:
            self.datetimes_to_exclude = get_excluded_datetimes(
                self.df,
                self.hour_filters,
                self.day_of_week_filters,
                self.month_filters,
                self.year_filters,
                self.feature_filters,
            )

    # def create_feature(self, feature_operation_list: list, cumulative: bool = False, custom_name:str = None ):
    #     custom_feature_series = pd.Series
    #     for idx, features in enumerate(feature_operation_list):
    #         if idx == 0:
    #             custom_feature_series = self.df[features["Feature"]]

    #         elif features["Operation"] == '+':
    #             custom_feature_series = custom_feature_series + self.df[features["Feature"]]

    #         elif features["Operation"] == '-':
    #             custom_feature_series = custom_feature_series - self.df[features["Feature"]]

    #     if cumulative:
    #         custom_feature_series = custom_feature_series.cumsum()

    #     if not custom_name:
    #         for idx, features in enumerate(feature_operation_list):
    #             if idx == 0:
    #                 custom_name = features["Feature"]

    #             else:
    #                 custom_name = custom_name + " " + features["Operation"] + " " + features["Feature"]

    #     self.df[custom_name] = custom_feature_series
    #     self.data_features.append(custom_name)
