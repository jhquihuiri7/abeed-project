# packages needed
import dash
from dash import dcc, html, Input, Output, State, callback, callback_context, ALL
from components.checkbox_components import main_checkbox
from components.daterange_components import main_daterange
from components.button_components import button
from utils.functions import update_graph, add_graph, remove_graph
from components.graph_components import bar_chart, multi_chart
import plotly.graph_objects as go
from backend.Class import Ops



# init client
client = Ops()
fig = go.Figure()

# external scripts
external_scripts = [{"src": "https://cdn.tailwindcss.com"}]

# init dash app
app = dash.Dash(
    __name__,
    external_scripts=external_scripts,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Abeed project"
# app._favicon = "favicon.ico"
app.layout = html.Div(
    className="m-10",
    children=[
        main_checkbox(),
        main_daterange(),
        button(text="Update Graph", id="update_graph_button"),
        dcc.Graph(id="main_graph"),
        button(text="Add Graph", id="add_graph_button"),
        html.Div(id="dynamic_div", children=[]),
    ],
)


@callback(
    Output("main_graph", "figure"),
    Output("dynamic_div", "children"),
    Input("update_graph_button", "n_clicks"),
    Input("add_graph_button", "n_clicks"),
    Input({"type": "remove_button", "index": ALL}, "n_clicks"),
    State("main_checkbox", "value"),
    State("main-date-picker-range", "start_date"),
    State("main-date-picker-range", "end_date"),
    State("main_graph", "figure"),
    State("dynamic_div", "children"),
)
def update_render(
    update_button,
    add_button,
    remove_button,
    features,
    start_date,
    end_date,
    currentFigure,
    currentChildren,
):
    global fig
    ctx = callback_context
    triggered_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None

    try:
        triggered_id = eval(triggered_id)  # Convert to dictionary if dynamic
    except:
        pass
    
    # Update graph when update button is clicked
    if triggered_id == "update_graph_button":
        fig = update_graph(client,features, start_date=start_date, end_date=end_date)
        return fig, currentChildren

    # Add graph when add button is clicked
    elif triggered_id == "add_graph_button":
        currentChildren = add_graph(client, currentFigure)
        return currentFigure, currentChildren
    
    elif isinstance(triggered_id, dict) and triggered_id.get("type") == "remove_button":
        currentChildren = remove_graph(client, triggered_id.get("index"))
        return currentFigure, currentChildren
        
    # If no figure, return initial empty state
    if not currentFigure:
        return fig, currentChildren

    return currentFigure, currentChildren


# serve and render app
if __name__ == "__main__":
    app.run_server(debug=True)
