from backend.endpoint_helper import simple_feature_request, simple_request_entities
from backend.helper_functions import *
import pandas as pd
import uuid
from datetime import date, timedelta
import copy
import numexpr as ne

class Feature:
    # This class will be used to hold all features that are available in the database
    def __init__(self, id_input, db_name_input, display_name_input, units_input):
        self.id = id_input
        self.db_name = db_name_input
        self.units = units_input
        self.display_name = display_name_input

    @classmethod
    def from_qz(cls, qz_feature: dict):
        return cls(
            id_input=qz_feature["id"],
            db_name_input=qz_feature["name"],
            display_name_input=qz_feature["display_name"],
            units_input=qz_feature["unit"],
        )

class session_features:
    # This class will be used to hold the features that are in the session (from the database or created by the user)
    def __init__(self) -> None:
        # Start date for the range of dates the user wants data for
        self.feature_name: str = ""
        self.id: str = ""
        self.db_name: str = ""
        self.requirements: list[str] = []
        self.equation: str = ""
        self.alias_map: dict[str, str] = {}
        self.units: str = ""
        self.cumulative: bool = False

    def read_data(
        self,
        feature_name_input,
        id_input,
        db_name_input,
        requirements_input,
        equation_input,
        alias_map_input,
        units_input,
        cumulative_input,
    ):
        self.feature_name = feature_name_input
        self.id = id_input
        self.db_name = db_name_input
        self.requirements = requirements_input
        self.equation = equation_input
        self.alias_map = alias_map_input
        self.units = units_input
        self.cumulative = cumulative_input

    def to_dict(self) -> dict:
        return {
            "feature_name": self.feature_name,
            "id": self.id,
            "db_name": self.db_name,
            "requirements": self.requirements,
            "equation": self.equation,
            "alias_map": self.alias_map,
            "units": self.units,
            "cumulative": self.cumulative,
        }

    def from_dict(self, data: dict) -> None:
        self.feature_name = data.get("feature_name", "")
        self.id = data.get("id", "")
        self.db_name = data.get("db_name", "")
        self.requirements = data.get("requirements", [])
        self.equation = data.get("equation", "")
        self.alias_map = data.get("alias_map", {})
        self.units = data.get("units", "")
        self.cumulative = data.get("cumulative", False)

class Ops:
    def __init__(self, load_features=False, db_features_json = {}) -> None:
        self.db_features_json = simple_request_entities("feature", 20000) if load_features else db_features_json
        self.db_feature_list: list[Feature] = [
            Feature.from_qz(qz_feature) for qz_feature in self.db_features_json
        ]
        self.display_features_dict = {
            f.display_name: f for f in self.db_feature_list if f.display_name
        }
        self.db_name_to_display_names_dict = {
            f.db_name: f.display_name for f in self.db_feature_list if f.display_name
        }
        self.db_name_dict = {f.db_name: f for f in self.db_feature_list}

        # Start date for the range of dates the user wants data for
        self.start_date = date.today() - timedelta(7)

        # End date for the range of dates the user wants data for
        self.end_date = date.today() + timedelta(2)

        # Fetures the user would like to see and make graphs with:
        self.session_data_features: dict[str, session_features] = {}
        # ex. ["MISO pjm RT", "MISO pjm DA", "PJM miso RT", "PJM miso DA",  "Meteologica PJM Load forcast","Meteologica MISO Load forcast"]

        # Dataframe to hold all the requested data based on self.start_date, self.end_date, and self.data_features
        self.df: pd.DataFrame = pd.DataFrame()

        self.filter_df: pd.DataFrame = pd.DataFrame()

        # A list of dictoinaries, each representing a graph. Each graph dictionary has a unique id and a list of features it will graph:
        self.graphs: list[dict] = []
        # single dictionary ex. {"graph_uid": '6da8871a-2860-474d-a8bf-4efa7383e26b', "graph_data_features": ["MISO pjm RT", "MISO pjm DA"]}

        # List of hours to include when graphing with filters (0-23)
        self.hour_filters: list[int] = list(range(24))

        # List of days of the week to include when graphing with filters (0-6)
        self.day_of_week_filters: list[int] = list(range(7))

        # List of months to include when graphing with filters (0-11)
        self.month_filters: list[int] = list(range(1, 13))

        # List of years to include when graphing with filters (2020-2025)
        self.year_filters: list[int] = list(range(2020, 2026))

        # A list of dictoinaries, each representing a filter for a feature. Each feature filter dictionary has a unique id,
        # the feature the filter is for, and the range the feature value should be within
        self.feature_filters: list[dict] = []
        # Single dictionary ex. {"filter_uid": '407f3d5d-9c1f-43d5-b35d-a559f6faf527', "feature_name": "MISO pjm RT", "range": [0.00, 50.00]}

        # self.increasing_decreasing_filter = []

        # A list of dates that should be excluded based off of the data in the dataframe and all the filters
        self.datetimes_to_exclude = []

        # A toggle to switch bettween viewing the filtered data and the un filtered data
        self.apply_filters_toggle = False

    def add_db_data_features_button(
        self, db_data_features_input: list[str], overwrite_df=False, init_columns=[]
    ):  # TODO

        for feature in db_data_features_input:
            feature_obj = session_features()
            if feature in self.display_features_dict:
                feature_obj.read_data(
                    feature,
                    self.display_features_dict[feature].id,
                    self.display_features_dict[feature].db_name,
                    [],
                    "",
                    {},
                    self.display_features_dict[feature].units,
                    False,
                )
            elif feature in self.db_name_dict:
                feature_obj.read_data(
                    feature,
                    self.db_name_dict[feature].id,
                    self.db_name_dict[feature].db_name,
                    [],
                    "",
                    {},
                    self.db_name_dict[feature].units,
                    False,
                )
            self.session_data_features[feature] = feature_obj
            for k, v in self.session_data_features.items():
                print(k," =",v)

        self.update_data(overwrite_df, init_columns)
        # after running this function we need to update the graph's to reflect the updated self.df, self.filter_df

    def remove_data_features_button(
        self, remove_data_features_input: list[str]
    ):  # TODO

        # Validation TODO: need to check that there are no feature filters dependent on the features being removed
        # Ensure that no existing features (not including the ones being requested to remove) depend on the features being removed
        for features in remove_data_features_input:
            try:
                del self.session_data_features[features]
            except:
                pass
        self.df = self.df.drop(remove_data_features_input, axis=1)
        self.filter_df = self.filter_df.drop(remove_data_features_input, axis=1)
        # after running this function we need to update the graph's to reflect the updated self.df, self.filter_df

    def update_date_range_button(
        self, start_date_input: date, end_date_input: date
    ):  # TODO
        self.start_date = start_date_input
        self.end_date = end_date_input
        self.update_data()
        # after running this function we need to update the graph's to reflect the updated self.df, self.filter_df and self.datetimes_to_exclude values

    def create_custom_feature_button(
        self,
        equation_input: str,
        alias_map_input: dict,
        cumulative_input: bool = False,
        custom_name_input: str = None,
    ):  # TODO needs to work with new custom feature format
        # Validation TODO:
        #   - DONE: confirm that there are at least two features selected to create this feature
        #   - DONE: confirm that there is not another feature in the self.data_features list or the self.created_features list with the same name
        if custom_name_input is None:
            custom_name_input = equation_input

        if cumulative_input:
            custom_name_input = f"({custom_name_input})∑"

        self.create_custom_feature(
            equation_input, alias_map_input, custom_name_input, cumulative_input
        )

        self.df[self.session_data_features[custom_name_input].feature_name] = (
            self.create_custom_feature_column(
                self.df.copy(), self.session_data_features[custom_name_input]
            )
        )

        self.filter_df[self.session_data_features[custom_name_input].feature_name] = (
            self.create_custom_feature_column(
                self.filter_df.copy(), self.session_data_features[custom_name_input]
            )
        )

        # after running this function we need to update the graph's to reflect the updated self.df and self.filter_df values

    def apply_datetime_filters_button(
        self,
        hours_to_include_input: list[int],
        days_of_week_to_include_input: list[int],
        months_to_include_input: list[int],
        years_to_include_input: list[int],
    ):
        # Validation TODO:
        #   - DONE: Confirm that there is at least on hour, day of week, month, and year selected
        self.update_datetime_filters(
            hours_to_include_input,
            days_of_week_to_include_input,
            months_to_include_input,
            years_to_include_input,
        )
        self.update_datetimes_to_exclude()
        self.update_filter_df()

        # after running this function we need to update the graph's to reflect the updated self.filter_df and self.datetimes_to_exclude values

    # TODO Done
    def add_feature_filter_button(
        self, feature_name: str, lower_bound: float, upper_bound: float
    ):
        # Selection Options:
        #   - DONE: The user should only be able to select from the self.data_features list and the self.created_features list but only ones that don't already have a feature filter

        # Validation TODO:
        #   - DONE: There is a feature selected and either an upper or lower bound selected
        #   - DONE: If there is an upper bound and a lower bound inputted confirm that the upper bound is greater than the lower bound

        new_feature_filter = {
            "filter_uid": str(uuid.uuid4()),
            "feature_name": feature_name,
            "range": [lower_bound, upper_bound],
        }
        self.feature_filters.append(new_feature_filter)
        self.update_datetimes_to_exclude()
        self.update_filter_df()

        # after running this function we need to update the graph's to reflect the updated self.filter_df and self.datetimes_to_exclude values
        #   - Also need to update the list of feature filters displayed on the feature filter tab

    # TODO Done
    def remove_feature_filter_button(self, target_uuid: str):
        self.feature_filters = [
            filters
            for filters in self.feature_filters
            if filters["filter_uid"] != target_uuid
        ]
        self.update_datetimes_to_exclude()
        self.update_filter_df()

        # after running this function we need to update the graph's to reflect the updated self.filter_df and self.datetimes_to_exclude values
        #   - Also need to update the list of feature filters displayed on the feature filter tab

    # TODO Done
    def add_graph_button(self, features_list: list[str]):
        new_graph = {
            "graph_uid": str(uuid.uuid4()),
            "graph_data_features": features_list,
        }
        self.graphs.append(new_graph)

        # after running this function we need to update the component that displays all the graphs in the self.graphs value

    # TODO Done
    def remove_graph_button(self, target_uuid: str):
        self.graphs = [
            graphs for graphs in self.graphs if graphs["graph_uid"] != target_uuid
        ]

        # after running this function we need to update the component that displays all the graphs in the self.graphs value

    def update_db_data_features(self, overwrite_df=False, init_columns=[]):
        db_session_features = [
            value.db_name
            for value in self.session_data_features.values()
            if value.equation == ""
        ]
        current_df = self.df.copy()
        self.df = simple_feature_request(
            self.start_date, self.end_date, db_session_features
        )[0]

        rename_dict = {}
        for feature in self.session_data_features:
            if feature in self.display_features_dict:
                rename_dict[self.display_features_dict[feature].db_name] = feature
        #self.db_name_to_display_names_dict
        self.df.rename(columns=rename_dict, inplace=True)
        if overwrite_df:
            init_columns = list(
                set(init_columns) - set(self.session_data_features.keys())
            )
            self.df = pd.concat([current_df[init_columns], self.df], axis=1)
        features_to_remove = set([feature for feature in self.session_data_features]) - set(self.df.columns.tolist())
        features_to_remove = [feature for feature in features_to_remove if self.session_data_features[feature].equation == ""]
        if features_to_remove:
            for feature in features_to_remove:
                del self.session_data_features[feature]
            raise ValueError(f"No data for {', '.join(features_to_remove)} in the selected date range")

    def update_created_data_features(self):
        dependent_features = [
            feature
            for feature in self.session_data_features
            if self.session_data_features[feature].equation != ""
        ]
        while len(dependent_features) > 0:
            for feature in dependent_features:
                if feature not in list(self.df.columns) and all(
                    [
                        requirement in list(self.df.columns)
                        for requirement in self.session_data_features[
                            feature
                        ].requirements
                    ]
                ):
                    dependent_features.remove(feature)
                    self.df[feature] = self.create_custom_feature_column(
                        self.df.copy(), self.session_data_features[feature]
                    )

    def update_data(self, overwrite_df=False, init_columns=[]):
        # Input Validation TODO before running this function:
        #   Validate that a start_date and end_date are selected and that there is at least one entry in the data_features_input list
        #       - right now if you don't have at least one entry in the data_features_input list we get an error message but the app breaks
        #   Validate if all features that the feature_filters depend on are in the data_feature_input list
        #   Validate if all features that Custom features depend on are in the data_feature_input list
        #       - If Either of these validations do not pass, show an error message with each feature_filter that will not be able to be created and each custom feature, along with the data feature missing
        #       - ex. Cannot create "MISO pjm DA - PJM miso DA" custom feature without "MISO pjm DA" data feature (Hint: delete "MISO pjm DA - PJM miso DA" or reselect "MISO pjm DA")
        self.update_db_data_features(overwrite_df, init_columns)
        self.update_created_data_features()
        self.update_datetimes_to_exclude()
        self.update_filter_df()

        # after running this function we need to update the graph's to reflect the updated self.df, self.filter_df and self.datetimes_to_exclude values

    def update_datetime_filters(
        self,
        hours_to_include: list[int],
        days_of_week_to_include: list[int],
        months_to_include: list[int],
        years_to_include: list[int],
    ):  # TODO: used to be update_date_filters and update_hour_filters (combined functions)
        self.hour_filters = hours_to_include
        self.day_of_week_filters = days_of_week_to_include
        self.month_filters = months_to_include
        self.year_filters = years_to_include

    def update_datetimes_to_exclude(self):
        if not self.df.empty:
            dates_to_exclude = []
            for filter in self.feature_filters:
                feature_name = filter["feature_name"]
                min_value = filter["range"][0]
                max_value = filter["range"][1]
                min_value = float("-inf") if min_value is None else min_value
                max_value = float("inf") if max_value is None else max_value
                dates_to_exclude_series = self.df.index[
                    (self.df[feature_name] <= min_value)
                    | (self.df[feature_name] >= max_value)
                ]
                dates_to_exclude.extend(dates_to_exclude_series.to_list())
            dates_to_exclude = list(set(dates_to_exclude))

            dates_to_exclude_series = self.df.index[
                ~(self.df.index.hour.isin(self.hour_filters))
                | ~(self.df.index.weekday.isin(self.day_of_week_filters))
                | ~(self.df.index.month.isin(self.month_filters))
                | ~(self.df.index.year.isin(self.year_filters))
            ]

            dates_to_exclude.extend(dates_to_exclude_series.to_list())

            dates_to_exclude = sorted(list(set(dates_to_exclude)))

            self.datetimes_to_exclude = dates_to_exclude

    def update_filter_df(self):
        self.filter_df = self.df

        # drop cumulative created features so cumulative values can be recalculated with filters
        for feature in self.session_data_features:
            if self.session_data_features[feature].cumulative:
                self.filter_df = self.filter_df.drop(
                    self.session_data_features[feature].feature_name, axis=1
                )

        for datetimes in self.datetimes_to_exclude:
            self.filter_df = self.filter_df.drop(datetimes)
        for feature in self.session_data_features:
            
            if self.session_data_features[feature].feature_name not in self.filter_df.columns.to_list():
                self.filter_df[self.session_data_features[feature].feature_name] = (
                    self.create_custom_feature_column(
                        self.filter_df.copy(), self.session_data_features[feature]
                    )
                )

    def create_custom_feature(
        self, equation, alias_map, feature_name, cumulative: bool
    ):

        requirements = []
        for alias in alias_map:
            requirements.append(alias_map[alias])

        units = self.session_data_features[requirements[0]].units

        custom_feature_object = session_features()
        custom_feature_object.read_data(
            feature_name,
            None,
            None,
            requirements,
            equation,
            alias_map,
            units,
            cumulative,
        )
        self.session_data_features[feature_name] = custom_feature_object

        # self.df[feature_name] = self.create_custom_feature_column(self.df, equation, alias_map)

    def create_custom_feature_column(self, df, session_feature_obj: session_features):
        variable_map = {}
        equation = session_feature_obj.equation
        for index, (alias, feature) in enumerate(session_feature_obj.alias_map.items()):
            new_key = chr(ord("a") + index)
            variable_map[new_key] = feature
            equation = equation.replace(alias, new_key)

        local_dict = {
            var: df[feature].values for var, feature in variable_map.items()
        }  # TODO does not work with filter_df_implementation when trying to recalculate cumulative features because it always calculates based on the self.df, not the self.filter_df
        #print("EQUATION",equation, "LOCAL DICT",local_dict)
        result = ne.evaluate(equation, local_dict)
        if session_feature_obj.cumulative:
            np.nan_to_num(result, nan=0, copy=False)
            result = result.cumsum()

        return result

    def copy(self):
        new_instance = Ops()

        new_instance.start_date = self.start_date
        new_instance.end_date = self.end_date
        new_instance.session_data_features = self.session_data_features.copy()
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

        return new_instance

    def download_df(self):
        self.df.to_csv("C:\\Users\\achowdhury\\Downloads\\candel_df.csv")
