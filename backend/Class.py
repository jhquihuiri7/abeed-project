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
from datetime import date, datetime, timedelta
import unittest
import pdb
import copy


class Ops:
    def __init__(self) -> None:

        # Start date for the range of dates the user wants data for
        self.start_date = date.today() - timedelta(7)

        # End date for the range of dates the user wants data for
        self.end_date = date.today() + timedelta(1)

        # Fetures the user would like to see and make graphs with:
        self.data_features = []
        # ex. ["MISO pjm RT", "MISO pjm DA", "PJM miso RT", "PJM miso DA",  "Meteologica PJM Load forcast","Meteologica MISO Load forcast"]

        # Dataframe to hold all the requested data based on self.start_date, self.end_date, and self.data_features
        self.df = pd.DataFrame()

        self.filter_df = pd.DataFrame()

        # A list of dictoinaries, each representing a graph. Each graph dictionary has a unique id and a list of features it will graph:
        self.graphs = []
        # single dictionary ex. {"graph_uid": '6da8871a-2860-474d-a8bf-4efa7383e26b', "graph_data_features": ["MISO pjm RT", "MISO pjm DA"]}

        # List of hours to include when graphing with filters (0-23)
        self.hour_filters = list(range(24))

        # List of days of the week to include when graphing with filters (0-6)
        self.day_of_week_filters = list(range(7))

        # List of months to include when graphing with filters (0-11)
        self.month_filters = list(range(1, 13))

        # List of years to include when graphing with filters (2020-2025)
        self.year_filters = list(range(2020, 2026))

        # A list of dictoinaries, each representing a filter for a feature. Each feature filter dictionary has a unique id,
        # the feature the filter is for, and the range the feature value should be within
        self.feature_filters = []
        # Single dictionary ex. {"filter_uid": '407f3d5d-9c1f-43d5-b35d-a559f6faf527', "feature_name": "MISO pjm RT", "range": [0.00, 50.00]}

        # self.increasing_decreasing_filter = []

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

        # A list of dictoinaries, each representing a graph. Each graph dictionary has a unique id and a list of two features:
        self.scatter_graphs = []
        # single dictionary ex. {"graph_uid": '6da8871a-2860-474d-a8bf-4efa7383e26b', "graph_data_features": ["MISO pjm RT", "MISO pjm DA"]}
    def update_data_button(self, start_date_input: str, end_date_input: str, data_features_input: list[str]):
        # Input Validation TODO before running this function:
        #   Validate that a start_date and end_date are selected and that there is at least one entry in the data_features_input list
        #       - right now if you don't have at least one entry in the data_features_input list we get an error message but the app breaks
        #   Validate if all features that the feature_filters depend on are in the data_feature_input list
        #   Validate if all features that Custom features depend on are in the data_feature_input list
        #       - If Either of these validations do not pass, show an error message with each feature_filter that will not be able to be created and each custom feature, along with the data feature missing
        #       - ex. Cannot create "MISO pjm DA - PJM miso DA" custom feature without "MISO pjm DA" data feature (Hint: delete "MISO pjm DA - PJM miso DA" or reselect "MISO pjm DA")

        # Here are two for loops you can use to do these validations, please confirm that these make sense and work:
        # for filters in self.feature_filters:
        #     if filters["feature_name"] not in data_features_input:
        #         print(error_message)
        # for created_feature in self.created_features:
        #     for features in created_feature["equation"]:
        #         if features["Feature"] not in data_features_input:
        #             print(error_message)

        self.update_date_range(start_date_input, end_date_input)
        self.update_data_features(data_features_input)
        self.update_data()
        self.add_created_features_to_df()
        self.update_datetimes_to_exclude()
        print(self.datetimes_to_exclude)
        self.update_filter_df()

        #after running this function we need to update the graph's to reflect the updated self.df, self.filter_df and self.datetimes_to_exclude values

    def create_custom_feature_button(self, feature_operation_list_input: list, cumulative_input: bool = False, custom_name_input:str = None):
        # Validation TODO:
        #   - confirm that there are at least two features selected to create this feature
        #   - confirm that there is not another feature in the self.data_features list or the self.created_features list with the same name

        self.create_feature(feature_operation_list_input, cumulative_input, custom_name_input)
        self.add_created_features_to_df()
        self.update_filter_df()

        #after running this function we need to update the graph's to reflect the updated self.df and self.filter_df values
        #   - Also need to update  the list of created features displayed on the custom features tab 

    def remove_custom_feature_button(self, target_uid: str):
        # Validation TODO:
        #   - Confirm that there is not a feature filter that is dependent on the custom feature being requested to delete
        #   - If There is tell the user and give a hint to delete the filter first
        removed_feature_name = ""
        for features in self.created_features:
            if features['feature_id'] == target_uid:
                removed_feature_name = features["feature_name"]
        self.created_features = [
            features for features in self.created_features if features['feature_id'] != target_uid
        ]
        self.df = self.df.drop(removed_feature_name, axis=1)
        self.filter_df = self.filter_df.drop(removed_feature_name, axis=1)

        #after running this function we need to update the graph's to reflect the updated self.df, self.filter_df and self.datetimes_to_exclude values
        #   - Also need to update  the list of created features displayed on the custom features tab 

    def apply_datetime_filters_button(self, hours_to_include_input: list[int], days_of_week_to_include_input: list[int], months_to_include_input: list[int], years_to_include_input: list[int]):
        # Validation TODO:
        #   - Confirm that there is at least on hour, day of week, month, and year selected
        self.update_datetime_filters(hours_to_include_input, days_of_week_to_include_input, months_to_include_input, years_to_include_input)
        self.update_datetimes_to_exclude()
        self.update_filter_df()

        #after running this function we need to update the graph's to reflect the updated self.filter_df and self.datetimes_to_exclude values

    def add_feature_filter_button(self, feature_name: str, lower_bound: float, upper_bound: float):
        # Selection Options:
        #   - The user should only be able to select from the self.data_features list and the self.created_features list but only ones that don't already have a feature filter
        
        # Validation TODO:
        #   - There is a feature selected and either an upper or lower bound selected
        #   - If there is an upper bound and a lower bound inputted confirm that the upper bound is greater than the lower bound

        new_feature_filter = {
            "filter_uid": str(uuid.uuid4()),
            "feature_name": feature_name,
            "range": [lower_bound, upper_bound],
        }
        self.feature_filters.append(new_feature_filter)
        self.update_datetimes_to_exclude()
        self.update_filter_df()

        #after running this function we need to update the graph's to reflect the updated self.filter_df and self.datetimes_to_exclude values
        #   - Also need to update the list of feature filters displayed on the feature filter tab 


    def remove_feature_filter_button(self, target_uuid: str):
        self.feature_filters = [
            filters
            for filters in self.feature_filters
            if filters["filter_uid"] != target_uuid
        ]
        self.update_datetimes_to_exclude()
        self.update_filter_df()

        #after running this function we need to update the graph's to reflect the updated self.filter_df and self.datetimes_to_exclude values
        #   - Also need to update the list of feature filters displayed on the feature filter tab 


    def add_graph_button(self, features_list: list[str]):
        new_graph = {
            "graph_uid": str(uuid.uuid4()),
            "graph_data_features": features_list,
        }
        self.graphs.append(new_graph)

        # after running this function we need to update the component that displays all the graphs in the self.graphs value

    def remove_graph_button(self, target_uuid: str):
        self.graphs = [
            graphs for graphs in self.graphs if graphs["graph_uid"] != target_uuid
        ]        

        # after running this function we need to update the component that displays all the graphs in the self.graphs value

    def update_data(self): # TODO: used to be update_df
        if self.data_features and self.start_date and self.end_date:
            db_names = []
            for feature in self.data_features:
                db_names.append(feature_read_name_to_db_name_dict[feature])
            self.df = simple_request(self.start_date, self.end_date, db_names)[0]
            self.df.rename(columns=feature_db_name_to_read_name_dict, inplace=True)

    def update_date_range(self, new_start, new_end):
        self.start_date = new_start
        self.end_date = new_end

    def update_data_features(self, new_data_features: list[str]):
        self.data_features = new_data_features

    def update_datetime_filters(self, hours_to_include: list[int], days_of_week_to_include: list[int], months_to_include: list[int], years_to_include: list[int]): # TODO: used to be update_date_filters and update_hour_filters (combined functions)
        self.hour_filters = hours_to_include
        self.day_of_week_filters = days_of_week_to_include
        self.month_filters = months_to_include
        self.year_filters = years_to_include



    # def add_increasing_decreasing_filter(self, feature_name:str, increaseing:bool):

    #     new_increasing_decreasing_filter = {
    #         "fillter_uid": str(uuid.uuid4()),
    #         "feature_name": feature_name,
    #         "increasing": increaseing
    #     }
    #     self.increasing_decreasing_filter.append(new_increasing_decreasing_filter)

    #     if not self.df.empty:
    #         self.update_datetimes_to_exclude()

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

    def update_filter_df(self):
        self.filter_df = self.df

        # drop cumulative created features so cumulative values can be recalculated with filters
        for custom_feature in self.created_features:
            if custom_feature["cumulative?"] == True:
                self.filter_df = self.filter_df.drop(custom_feature["feature_name"], axis=1)

        for datetimes in self.datetimes_to_exclude:
            self.filter_df = self.filter_df.drop(datetimes)

        for feature in self.created_features:
            if feature["feature_name"] not in self.filter_df.columns.to_list():   
                self.filter_df = add_custom_feature_column(self.filter_df, feature)

    def create_feature(self, feature_operation_list: list, cumulative: bool = False, custom_name:str = None):
        # feature_operation_list example
        # [
        #     {"Feature": "MISO pjm RT"},                       (first feature has no operation as it is the column we are starting with)
        #     {"Feature": "MISO pjm DA", "Operation": "-"},     (all subsequent features have a plus or minus operation value. there can be as many subsequent features as the user wants)
        #      {"Feature": "PJM miso DA", "Operatiion": "+"}
        # ]
        # Feature options to create a custom feature should only be features in self.data_features 

        if not custom_name:
            for idx, features in enumerate(feature_operation_list):
                if idx == 0:
                    custom_name = "(" + features["Feature"]
                
                else:
                    custom_name = custom_name + " " + features["Operation"] + " " + str(features["Feature"])

            custom_name = custom_name + ")"

            if cumulative:
                custom_name = custom_name + "Σ" 

        custom_feature_unit = get_feature_units(feature_operation_list[0]["Feature"])
        self.created_features.append(
            {
            "feature_name": custom_name,
            "feature_id": str(uuid.uuid4()),
            "cumulative?": cumulative,
            "equation" : feature_operation_list,
            "unit" : custom_feature_unit
            }
        )

    def add_created_features_to_df(self):
        for feature in self.created_features:
            if feature["feature_name"] not in self.df.columns.to_list():   
                self.df = add_custom_feature_column(self.df, feature)
        

    def add_scatter_graph(self, feature1, feature2):
        # Only allow user to select features from the self.data_features or self.created_features lists (if it is a created_feature it cannot be cummulative)
        # Only allow user to select two features per sccatter graph
        # The user should also be able to select the year, month, day of week, or hour as one of the features 

        new_graph = {
            "graph_uid": str(uuid.uuid4()),
            "graph_data_features": [feature1, feature2],
        }
        self.scatter_graphs.append(new_graph)

    def remove_sccatter_graph(self, target_uuid):
        self.scatter_graphs = [
            graphs for graphs in self.scatter_graphs if graphs['graph_uid'] != target_uuid
        ]

    def copy(self):
        new_instance = Ops()
        
        new_instance.start_date = self.start_date
        new_instance.end_date = self.end_date
        new_instance.data_features = self.data_features.copy()
        new_instance.df = self.df.copy()
        new_instance.filter_df = self.filter_df.copy()
        new_instance.graphs = copy.deepcopy(self.graphs)
        new_instance.hour_filters = self.hour_filters.copy()
        new_instance.day_of_week_filters = self.day_of_week_filters.copy()
        new_instance.month_filters = self.month_filters.copy()
        new_instance.year_filters = self.year_filters.copy()
        new_instance.feature_filters = copy.deepcopy(self.feature_filters)
        new_instance.datetimes_to_exclude = self.datetimes_to_exclude.copy()
        new_instance.apply_filters_toggle = self.apply_filters_toggle
        new_instance.created_features = copy.deepcopy(self.created_features)
        new_instance.scatter_graphs = copy.deepcopy(self.scatter_graphs)
        
        return new_instance

    def download_df(self):
        self.df.to_csv("C:\\Users\\achowdhury\\Downloads\\candel_df.csv")