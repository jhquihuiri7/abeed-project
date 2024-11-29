from backend.db_dictionaries import feature_units_dict
from dash import html, dcc


def main_checkbox():
    return html.Div(
        dcc.Checklist(
            # get features from db_dictionaries and display for checkbox selection
            options=[item[0] for item in feature_units_dict.items()],
            value=[],
            className="w-full flex flex row flex-wrap",
            labelClassName="pr-10",
            id="main_checkbox",
        )
    )
