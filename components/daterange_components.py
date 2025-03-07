# Import necessary modules from Dash for creating HTML components and date picker
from dash import html, dcc

# Import date and time utilities for managing and formatting dates
from datetime import date, datetime, timedelta

# Define a function to create a date range picker component
def main_daterange(client):
    """
    Creates a date range picker component for selecting a range of dates.

    Returns:
        html.Div: A Dash HTML Div containing a DatePickerRange component.
    """
    return html.Div(
        className="mt-10",  # CSS class to apply a top margin for spacing
        children=[
            # Create a DatePickerRange component
            dcc.DatePickerRange(
                id="main-date-picker-range",  # Unique identifier for the date range picker
                min_date_allowed=date(2015, 8, 5),  # Earliest date that can be selected
                max_date_allowed=date(2027, 9, 19),  # Latest date that can be selected
                start_date=client.start_date,  # Default start date (5 days ago)
                end_date=client.end_date,  # Default end date (today)
            )
        ],
    )
