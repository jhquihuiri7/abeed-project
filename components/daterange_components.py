from dash import html, dcc
from datetime import date, datetime, timedelta


def main_daterange():

    return html.Div(
        # TODO manage min, max, init, end dates
        className="mt-10",
        children=[
            dcc.DatePickerRange(
                id="main-date-picker-range",
                min_date_allowed=date(2015, 8, 5),
                max_date_allowed=date(2027, 9, 19),
                start_date= datetime.now().date() - timedelta(days=5),
                end_date=datetime.now().date(),
            )
        ],
    )
