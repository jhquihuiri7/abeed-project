from backend.db_dictionaries import features_read_name_to_db_id_dict
from dash import html, dcc

def main_checkbox():    
    return html.Div(
        dcc.Checklist(
            #get features from db_dictionaries and display for checkbox selection
            [item[0] for item in features_read_name_to_db_id_dict.items()],
            [],
            className="w-full flex flex row flex-wrap",
            labelClassName="pr-10"
        )
    )    