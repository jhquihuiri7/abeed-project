from dash import html, dcc
from datetime import date


def main_daterange():

    return html.Div(
        # TODO manage min, max, init, end dates
        className="mt-10",
        children=[
            dcc.DatePickerRange(
                id="main-date-picker-range",
                min_date_allowed=date(2015, 8, 5),
                max_date_allowed=date(2027, 9, 19),
                initial_visible_month=date(2024, 8, 5),
                start_date=date(2024, 10, 20),
                end_date=date(2027, 8, 25),
            )
        ],
    )
