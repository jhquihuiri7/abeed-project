# packages needed
import dash
from dash import dcc, html, Input, Output
from components.checkbox_components import main_checkbox 
from components.daterange_components import main_daterange
from styles.styles import button_style

# external scripts
external_scripts = [{"src": "https://cdn.tailwindcss.com"}]

#init dash app
app = dash.Dash(
    __name__,
    external_scripts=external_scripts,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
app.title = "Abeed project"
#app._favicon = "favicon.ico"
app.layout = html.Div(
    className="m-10",
    children=[
            main_checkbox(),
            main_daterange(),
            html.Button('Update Graph', id='update_graph_button', n_clicks=0, 
                        className= button_style),
            
        ]
)


#serve and render app
if __name__ == "__main__":
    app.run_server(debug=True)