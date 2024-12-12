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
        
        self.filter_df = pd.DataFrame()
        
        # Start date for the range of dates the user wants data for
        self.start_date = date(2024, 10, 20)

        # End date for the range of dates the user wants data for
        self.end_date = date(2024, 10, 25)

        # Fetures the user would like to see and make graphs with:
        self.data_features = []
        # ex. ["MISO pjm RT", "MISO pjm DA", "PJM miso RT", "PJM miso DA",  "Meteologica PJM Load forcast","Meteologica MISO Load forcast"]

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

        self.created_features = []
        # example
        # [
        #     {
        #     "feature name": "MISO pjm spread"
        #     "feature id": str(uuid.uuid4())
        #     "Equation" : [
        #         {"Feature": "MISO pjm RT"},
        #         {"Feature": "MISO pjm DA", "Operation": "-"},
        #     ]
        #     },
        #     {
        #     "feature name": "PJM miso spread"
        #     "feature id": str(uuid.uuid4())
        #     "Equation" : [
        #         {"Feature": "PJM miso RT"},
        #         {"Feature": "PJM miso DA", "Operation": "-"},
        #     ]
        #     }
        # ]

    def update_df(self, new_features_list: list[str], start_date, end_date):
        if new_features_list and start_date and end_date:
            db_names = []
            for feature in new_features_list:
                db_names.append(feature_read_name_to_db_name_dict[feature])
            self.df = simple_request(start_date, end_date, db_names)[0]
            self.df.rename(columns=feature_db_name_to_read_name_dict, inplace=True)

    def update_date_range(self, new_start, new_end):
        self.start_date = new_start
        self.end_date = new_end

        if self.data_features:
            self.update_df()

    def update_data_features(self, new_data_features: list[str]):
        self.data_features = new_data_features

        if self.start_date and self.end_date:
            self.update_df()

    def add_graph(self, features_list: list[str]):
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

    def update_date_filters(
        self,
        days_of_week_to_include: list[int],
        months_to_include: list[int],
        years_to_include: list[int],
    ):
        self.day_of_week_filters = days_of_week_to_include
        self.month_filters = months_to_include
        self.year_filters = years_to_include
        if not self.df.empty:
            self.update_datetimes_to_exclude()

    def add_feature_filter(
        self, feature_name: str, lower_bound: float, upper_bound: float
    ):
        # TODO only allow user to select features from the data_features list to filter by
        if feature_name not in self.data_features:
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

    # def update_filter_df(self):
    #     self.filter_df = self.df

    #     # drop cumulative created features so cumulative values can be recalculated with filters
    #     for custom_feature in self.created_features:
    #         if custom_feature["cumulative?"] == True:
    #             self.filter_df = self.filter_df.drop(custom_feature["feature_name"], axis=1)

    #     for datetimes in self.datetimes_to_exclude:
    #         self.filter_df = self.filter_df.drop(datetimes)

    #     for feature in self.created_features:
    #         if feature["feature_name"] not in self.filter_df.columns.to_list():
    #             self.filter_df = add_custom_feature_column(self.df, feature)

    def create_feature(
        self,
        feature_operation_list: list,
        cumulative: bool = False,
        custom_name: str = None,
    ):
        # feature_operation_list example
        # [
        #     {"Feature": "MISO pjm RT"},                       (first feature has no operation as it is the column we are starting with)
        #     {"Feature": "MISO pjm DA", "Operation": "-"},     (all subsequent features have a plus or minus operation value. there can be as many subsequent features as the user wants)
        #      {"Feature": "PJM miso DA", "Operatiion": "+"}
        # ]

        if not custom_name:
            for idx, features in enumerate(feature_operation_list):
                if idx == 0:
                    custom_name = features["Feature"]

                else:
                    custom_name = (
                        custom_name
                        + " "
                        + features["Operation"]
                        + " "
                        + features["Feature"]
                    )

        self.created_features.append(
            {
                "feature_name": custom_name,
                "feature_id": str(uuid.uuid4()),
                "cumulative?": cumulative,
                "equation": feature_operation_list,
                "unit": get_feature_units(feature_operation_list[0]["Feature"])
            }
        )
        self.add_created_features_to_df()
    
    def remove_custom_feature(self, target_uid: str):
        # Don't let the user remove a created feature if there is a feature filter that is dependent on it (tell user to delete the filter first)
        removed_feature_name = ""
        for features in self.created_features:
            if features['feature_id'] == target_uid:
                removed_feature_name = features["feature_name"]
        self.created_features = [
            features for features in self.created_features if features['feature_id'] != target_uid
        ]
        self.df = self.df.drop(removed_feature_name, axis=1)
        
        #self.filter_df = self.filter_df.drop(removed_feature_name, axis=1)

    def add_created_features_to_df(self):
        for feature in self.created_features:
            if feature["feature_name"] not in self.df.columns.to_list():
                self.df = add_custom_feature_column(self.df, feature)

    def download_df(self):
        self.df.to_csv("C:\\Users\\achowdhury\\Downloads\\test_df.csv")
