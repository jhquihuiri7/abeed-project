import dash
from dash import dcc, html
from dash.dependencies import Input, Output

app = dash.Dash(__name__)

# Generamos una lista de palabras


app.layout = html.Div(
    style={"width": "500px", "height": "500px", "border": "1px solid black", "padding": "10px"},
    children=[
        dcc.Store(id="current-page", data=0),  # Almacenamos la página actual
        
        html.Div(id="words-container", style={"display": "grid", "gridTemplateColumns": "repeat(5, 1fr)", "gap": "10px"}),

        html.Div(
            style={"display": "flex", "justifyContent": "center", "marginTop": "20px"},
            children=[
                html.Button("Prev", id="prev-btn", n_clicks=0, style={"marginRight": "10px"}),
                html.Button("Next", id="next-btn", n_clicks=0),
            ],
        ),
    ],
)

@app.callback(
    Output("words-container", "children"),
    Output("prev-btn", "disabled"),
    Output("next-btn", "disabled"),
    Input("prev-btn", "n_clicks"),
    Input("next-btn", "n_clicks"),
    Input("current-page", "data"),
)
def update_words(prev_clicks, next_clicks, current_page):
    words = [f"Word {i+1}" for i in range(100)]
    items_per_page = 25
    total_pages = len(words) // items_per_page
    new_page = min(max(current_page + (next_clicks - prev_clicks), 0), total_pages)
    
    start_index = new_page * items_per_page
    end_index = start_index + items_per_page
    current_words = words[start_index:end_index]

    return (
        [html.Div(word, style={"padding": "10px", "background": "#f0f0f0", "borderRadius": "5px", "textAlign": "center"}) for word in current_words],
        new_page == 0,
        new_page == total_pages,
    )

if __name__ == "__main__":
    app.run_server(debug=True)