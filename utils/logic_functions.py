# Import the feature_units_dict dictionary from the backend, 
# which maps features to their respective measurement units.
from backend.db_dictionaries import feature_units_dict
from datetime import datetime, timedelta

# Function to determine if a set of columns requires both primary and secondary axes
def contains_both_axis(cols):
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
    # Extract unique units from the feature_units_dict for the given columns
    units = list(set([feature_units_dict[col] for col in cols]))
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

def updateHourButton(buttons, index_to_color):
        for button in buttons:
            print(button)
            
def validateFeatureFilterData(feature, min_range, max_range):
    reason = ""
    if feature == "" :
        reason = "You must select a Feature"
        return False, reason
    if min_range == "" and max_range == "":
        reason = "You must give at least one input range"
        return False, reason
    return True, reason

def validateMainDropdownSelection(client):
    if client.data_features == []:
        return False 
    return True

def validateDeleteCustomFeatureFilter(feature_to_remove, client):
    if feature_to_remove in [featureFilter["feature_name"] for featureFilter in client.feature_filters]:
        return False
    else:
        return True

def validateCustomFeaturesExistInFeatures(client, features):
    missing_features = []
    if client.created_features != []:
        for custom_feature in client.created_features:
            for feature in custom_feature["equation"]:
                if feature["Feature"] not in features:
                    missing_features.append(feature["Feature"])
    
    return True if len(missing_features)==0 else False, missing_features

def validateApplyFilterToggle(client, apply_filter, toggle):
    
    apply_action = True
    toggle_action = True
    is_valid = True
    message = ""
    
    if apply_filter != []:
        if client.datetimes_to_exclude==[]:
            is_valid = False
            message = "No filters to apply"
    
    return is_valid, apply_action, toggle_action, message

def validateApplySelection(client, type):
    is_valid = True
    message = ""
    if type == "hour_filter":
        if client.hour_filters == []:
            is_valid = False
            message = "No hours selected"
    
    if type=="date_filter":
        if client.day_of_week_filters == [] or client.month_filters == [] or client.year_filters == []:
            is_valid = False
            message = "Please select at least one year, month and day of the week"
            
    return is_valid, message
    
def get_last_consecutive_datetime(datetime_axis):
    # Resultado final
    result = []

    # Iterar sobre la lista para identificar grupos consecutivos
    current_group_last = datetime_axis[0]  # Inicialmente el primer elemento
    
    for i in range(1, len(datetime_axis)):
        if datetime_axis[i] - datetime_axis[i - 1] > timedelta(hours=1):  # Cambia el intervalo según necesidad
            # Si no son consecutivos, guardar el último del grupo actual
            result.append(current_group_last)
        current_group_last = datetime_axis[i]
    
    # Agregar el último elemento del último grupo
    result.append(current_group_last)
    return result