from styles.styles import button_style
from dash import html


def button(text, id):
    return html.Button(text, id=id, n_clicks=0, className=button_style)
