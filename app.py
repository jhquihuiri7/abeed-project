# packages needed
import dash
from dash import dcc, html, Input, Output

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
    html.H1("Abeed App")
)


#serve and render app
if __name__ == "__main__":
    app.run_server(debug=True)