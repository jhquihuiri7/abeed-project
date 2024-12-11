# Import the feature_units_dict dictionary from the backend, 
# which maps features to their respective measurement units.
from backend.db_dictionaries import feature_units_dict

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



