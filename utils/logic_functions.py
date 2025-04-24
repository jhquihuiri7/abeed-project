from backend.helper_functions import get_feature_units
from datetime import timedelta
from backend.Class import Ops

def get_unit(client, column):
    unit = "USD"
    try:
        unit = client.session_data_features[column].units
    except:
        if "(mw)" in column:
            unit = "MW"
    return unit
# Function to determine if a set of columns requires both primary and secondary axes
def contains_both_axis(client: Ops, cols):
    
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
        unit = get_unit(client, column) #get_unit(client, column)
        units.append(unit)      
    # Extract unique units from the feature_units_dict for the given columns
    units = set(units)
    # Check if there is more than one unique unit
    return len(units) > 1, sorted(units, reverse=True)  # Return a boolean and a sorted list of units

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
        return False, reason, min_range, max_range
    if (min_range == "" and max_range == "") or (min_range == None and max_range == None):
        reason = f"Cannot create a feature filter because the is no values in the input range (Hint: provide at least one input range)"
        return False, reason, min_range, max_range
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
            return False, reason, min_range, max_range
    
    return True, reason, min_range, max_range

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

def get_custom_features_dependence(client:Ops, selected_features) -> dict:
    dependence_features = {}
    for key, value in client.session_data_features.items():
        if value.alias_map:
            common_filter = []
            for k,v in value.alias_map.items():
                if v in selected_features:
                    common_filter.append(v) 
            if common_filter:
                dependence_features[key] = common_filter
    return dependence_features
    
def get_custom_features_names(client, missing_features, show_all = False, show_cumulative = False):
    names = []
    for cf in client.created_features:
        if show_cumulative  or not cf["cumulative?"]:
            for eq in cf["equation"]:
                if show_all:
                    names.append(cf["feature_name"])
                else:
                    if eq["Feature"] in missing_features:
                        names.append(cf["feature_name"])
                        break
    return names
    
def get_feature_fitler_name_by_id(client, index):
    name = ''
    for feature in client.feature_filters:
        if feature["filter_uid"] == index:
            name = feature["feature_name"]
            break
    return name

def validate_add_custom_feature(client, custom_feature, cumulative, custom_name):
    message = ""
    if len(client.data_features) < 2:
        message = "Cannot create custom feature (Hint: select at least two data features)"
        return False, message
    if len(custom_feature) < 2:
        message = "Cannot create custom feature 2 (Hint: select at least two data features)"
        return False, message
    for cf in custom_feature:
        if cf["Feature"] == "" or cf["Feature"]==None:
            message = "Cannot create custom feature (Hint: Dont leave an operation without selection)"
            return False, message      
    if not custom_name or custom_name == '':
        for idx, features in enumerate(custom_feature):
            if idx == 0:
                custom_name = "(" + features["Feature"]
            
            else:
                custom_name = custom_name + " " + features["Operation"] + " " + str(features["Feature"])
        custom_name = custom_name + ")"
        if cumulative:
            custom_name = custom_name + "Σ" 
    if custom_name in client.data_features:
        message = "Cannot create custom feature (Hint: Feature name already exists in data_features)"
        return False, message
    if custom_name in [feature["feature_name"] for feature in client.created_features]:
            
            message = "Cannot create custom feature (Hint: Feature name already exists in created_features)"
            return False, message
                
    return True, message

def validate_delete_custom_feature(client, feature_to_remove):
    message = ""
    if feature_to_remove in get_feature_filter_name(client):
        message = f"Cannot delete {feature_to_remove} because it has a 'Feature Filter' (Hint: delete {feature_to_remove} filter first)"
        return False, message
    return True, message

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
    is_valid = True
    message = ""
    
    if apply_filter != []:
        if client.datetimes_to_exclude == []:
            is_valid = False
            message = "No filters to apply"
    
    return is_valid, message

def validate_add_features(selected_features):
    message = ""
    if selected_features == []:
        message = "Cannot create update data (Hint: select at least one data feature)"
        return False, message
    return True, message
def validate_delete_features(client:Ops, selected_features):
    message = ""
    if selected_features == []:
        message = "Cannot create delete feature (Hint: select at least one data feature)"
        return False, message
    common_filter = list(set(selected_features) & set(get_feature_filter_name(client)))
    common_custom = get_custom_features_dependence(client, selected_features)
    if common_custom:
        custom_features = common_custom.keys()
        dependent_features = common_custom.values()
        message = f"Cannot have {format_set(custom_features)} custom feature without {format_set(dependent_features)} data feature (Hint: delete {format_set(custom_features)} or reselect {format_set(dependent_features)} data feature)"
        return False, message
    if common_filter:
        message = f"Cannot have {format_set(common_filter)} feature filter without {format_set(common_filter)} data feature (Hint: delete {format_set(common_filter)} filter or reselect {format_set(common_filter)} data feature)"
        return False, message
    return True, message
    
def format_set(s):
    return ', '.join(f"'{item}'" for item in s)

def get_feature_filter_dropdown_opts(client: Ops, is_upload=False):
    if is_upload:
        return list(set(client.df.columns)-set(get_feature_filter_name(client)))
    else:    
        return list(set(client.session_data_features.keys() or []) - set(get_feature_filter_name(client) or []))
