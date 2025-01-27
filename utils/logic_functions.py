# Import the feature_units_dict dictionary from the backend, 
# which maps features to their respective measurement units.
from backend.db_dictionaries import feature_units_dict
from backend.helper_functions import get_feature_units
from datetime import datetime, timedelta
import pandas as pd

# Function to determine if a set of columns requires both primary and secondary axes
def contains_both_axis(client, cols):
    """
    Determines if the features in the given columns have different units,
    which would require both primary and secondary Y-axes.

    Args:
        cols (list): List of column names representing features.

    Returns:
        tuple: 
            - (bool): True if there are multiple units (dual axes required), False otherwise.
            - (list): Sorted list of unique units present in the columns.
    """
    units = []
    for column in cols:
        try:
            unit = get_feature_units(column)
        except:
            for feature in client.created_features:
                if feature["feature_name"] == column:
                    unit = feature["unit"]
        units.append(unit)      
    # Extract unique units from the feature_units_dict for the given columns
    units = set(units)
    # Check if there is more than one unique unit
    return len(units) > 1, sorted(units)  # Return a boolean and a sorted list of units

# Function to manage checkbox selection, ensuring only one item remains selected
def select_one_checkbox(last_selection):
    """
    Ensures that only one checkbox remains selected by keeping the most recent selection.

    Args:
        last_selection (list): List of currently selected items.

    Returns:
        list: Updated list with only the most recently selected item.
    """
    if len(last_selection) > 1:
        # If more than one item is selected, keep only the last one
        return [last_selection[-1]]
    return last_selection  # Return the selection as is if it contains one or no items

# Function to update a custom feature dictionary with operations and feature values
def update_custom_feature(features, custom_features, values):
    """
    Updates custom feature dictionaries with operations and feature names.

    Args:
        features (list): List of feature names.
        custom_features (list): List of dictionaries representing custom feature configurations.
        values (list): List of operations (e.g., "Add", "Subtract") for each feature.

    Returns:
        list: Updated list of custom feature dictionaries with updated operations and names.
    """
    updated_features = []  # Initialize a list to hold the updated features
    # Iterate through the features, custom features, and values together
    for index, (f, feature, value) in enumerate(zip(features, custom_features, values)):
        if index > 0:
            # For features after the first one, set the operation based on the value
            feature["Operation"] = "+" if value == "Add" else "-"
        
        feature["Feature"] = f  # Assign the feature name to the "Feature" key
        updated_features.append(feature)  # Add the updated feature to the list

    return updated_features  # Return the list of updated features


# Function to validate feature filter data
def validateFeatureFilterData(client, feature, min_range, max_range):
    """
    Validates the input data for feature filters.

    Args:
        feature (str): The selected feature name.
        min_range (str): Minimum range value.
        max_range (str): Maximum range value.

    Returns:
        tuple: 
            - (bool): True if valid, False otherwise.
            - (str): Reason for invalidation, if applicable.
    """
    reason = ""
    
    if feature == "":
        reason = f"Cannot create a feature filter because the is no feature selected (Hint: select a feature)"
        return False, reason
    if min_range == "" and max_range == "":
        reason = f"Cannot create a feature filter because the is no values in the input range (Hint: provide at least one input range)"
        return False, reason
    try:
        min_range = float(min_range) 
    except:
        min_range = None
    
    try:
        max_range = float(max_range)
    except:
        max_range = None
    
    if isinstance(min_range, float) and isinstance(max_range, float):
        if min_range > max_range:
            reason = f"Cannot create a feature filter because the the min_input_range is greater than the max_input_range (Hint: min_input_range must be lesser than max_input_range)"
            return False, reason
    
    return True, reason, min_range, max_range

# Function to validate the main dropdown selection
def validateMainDropdownSelection(client):
    """
    Validates whether the main dropdown selection is valid.

    Args:
        client (object): Client object containing feature data.

    Returns:
        bool: True if valid, False otherwise.
    """
    if client.data_features == []:
        return False
    return True

# Function to validate if a custom feature filter can be deleted
def validateDeleteCustomFeatureFilter(feature_to_remove, client):
    """
    Validates whether a custom feature filter can be deleted.

    Args:
        feature_to_remove (str): Feature name to be removed.
        client (object): Client object containing feature filters.

    Returns:
        bool: True if the feature can be deleted, False otherwise.
    """
    if feature_to_remove in [featureFilter["feature_name"] for featureFilter in client.feature_filters]:
        return False
    else:
        return True

# Function to check if custom features exist in a list of features
def validateCustomFeaturesExistInFeatures(client, features):
    """
    Checks if all custom features created by the client exist in the given list of features.

    Args:
        client (object): Client object containing created features.
        features (list): List of available feature names.

    Returns:
        tuple: 
            - (bool): True if all custom features exist, False otherwise.
            - (list): List of missing features, if any.
    """
    missing_features = []
    if client.created_features != []:
        for custom_feature in client.created_features:
            for feature in custom_feature["equation"]:
                if feature["Feature"] not in features:
                    missing_features.append(feature["Feature"])
    
    return True if len(missing_features) == 0 else False, missing_features

# Function to validate the toggle for applying filters
def validateApplyFilterToggle(client, apply_filter, toggle):
    """
    Validates whether filters can be applied based on the toggle state and filter data.

    Args:
        client (object): Client object containing filter data.
        apply_filter (list): List of filters to be applied.
        toggle (bool): Toggle state for applying filters.

    Returns:
        tuple:
            - (bool): True if valid, False otherwise.
            - (bool): Action for applying filters.
            - (bool): Action for toggling filters.
            - (str): Message explaining the validation result.
    """
    apply_action = True
    toggle_action = True
    is_valid = True
    message = ""
    
    if apply_filter != []:
        if client.datetimes_to_exclude == []:
            is_valid = False
            message = "No filters to apply"
    
    return is_valid, apply_action, toggle_action, message

def validateApplyDatetimeSelection(client):
    """
    Validates whether filter selections can be applied.

    Args:
        client (object): Client object containing filter data.
        type (str): Type of filter (e.g., "hour_filter" or "date_filter").

    Returns:
        tuple:
            - (bool): True if valid, False otherwise.
            - (str): Message explaining the validation result.
    """
    is_valid = True
    message = ""
    
    if client.hour_filters == [] or client.day_of_week_filters == [] or client.month_filters == [] or client.year_filters == []:
        is_valid = False
        message = "Cannot apply datetime filter (Hint: select at least one year, one month, one day of the week and one hour of the day)"    
    return is_valid, message

# Function to get the last consecutive datetime in a list
def get_last_consecutive_datetime(datetime_axis):
    """
    Identifies and returns the last datetime in consecutive groups from a sorted list.

    Args:
        datetime_axis (list): List of datetime objects, sorted in ascending order.

    Returns:
        list: List of last datetime objects from each consecutive group.
    """
    result = []  # Final result list

    # Initialize with the first element
    current_group_last = datetime_axis[0]
    
    # Iterate to identify consecutive groups
    for i in range(1, len(datetime_axis)):
        if datetime_axis[i] - datetime_axis[i - 1] > timedelta(hours=1):  # Adjust interval if needed
            result.append(current_group_last)  # Save the last element of the current group
        current_group_last = datetime_axis[i]
    
    result.append(current_group_last)  # Add the last element of the last group
    return result

def get_first_consecutive_datetime(datetime_axis):
    """
    Identifies and returns the first datetime in consecutive groups from a sorted list.

    Args:
        datetime_axis (list): List of datetime objects, sorted in ascending order.

    Returns:
        list: List of first datetime objects from each consecutive group.
    """
    result = []  # Final result list

    # Initialize with the first element as the start of a group
    current_group_first = datetime_axis[0]
    result.append(current_group_first)  # Save the first element of the first group
    
    # Iterate to identify consecutive groups
    for i in range(1, len(datetime_axis)):
        if datetime_axis[i] - datetime_axis[i - 1] > timedelta(hours=1):  # Adjust interval if needed
            current_group_first = datetime_axis[i]  # Update to the start of the next group
            result.append(current_group_first)  # Save the first element of the new group
    
    return result

def group_consecutive(datetime_axis):
    groups = []
    start = datetime_axis[0]
    for i in range(1, len(datetime_axis)):
        if datetime_axis[i] != datetime_axis[i - 1] + timedelta(hours=1):
            groups.append([start, datetime_axis[i - 1]])
            start = datetime_axis[i]
    groups.append([start, datetime_axis[-1]])
    return groups

def returnValidFeatures(client):
    if len(client.created_features) > 0 :
        return client.df.columns[:-len(client.created_features)]    
    return client.df.columns

def get_value_range(value, sign):
    if value == None:
        if sign == "+":
            return "Inf"
        else:
            return "-Inf"
    else:
        return value
    
def extract_values_custom_feature(data):
    custom_feature = []
    for i in data:
        temp= i["props"]["children"]
        try:
            custom_feature.append({"Feature": temp[0]['props']['value']})
        except:
            for j in temp:    
                custom_feature.append({"Operation": "-" if j['props']['children'][0]['props']['value'] == "Sub" else "+", "Feature": j['props']['children'][1]['props']['value']})
    return custom_feature

def get_feature_filter_name(client):
    return [feature["feature_name"] for feature in client.feature_filters]

def get_feature_fitler_name_by_id(client, index):
    name = ''
    for feature in client.feature_filters:
        if feature["filter_uid"] == index:
            name = feature["feature_name"]
            break
    return name