from dash import Dash, dcc, html, Input, Output, callback

def main_tabs():
    return html.Div(
        dcc.Tabs(id="tabs-example-graph", value='tab-1-example-graph', children=[
                dcc.Tab(label='Feature Filter', value='tab-1-example-graph'),
                dcc.Tab(label='Hour Filter', value='tab-2-example-graph'),
                dcc.Tab(label='Day Filter', value='tab-3-example-graph'),]),
        className="my-10"
    )