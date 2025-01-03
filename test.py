
from datetime import datetime

# Example list of sorted datetime objects
datetime_axis = [
    datetime(2025, 1, 1, 8, 0),
    datetime(2025, 1, 1, 9, 0),
    datetime(2025, 1, 1, 10, 0),
    datetime(2025, 1, 1, 12, 30),  # Break in sequence (>1 hour)
    datetime(2025, 1, 1, 13, 30),
    datetime(2025, 1, 1, 14, 0),
]


from datetime import timedelta

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


result = get_first_consecutive_datetime(datetime_axis)

