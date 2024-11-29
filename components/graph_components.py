import plotly.graph_objects as go
from components.button_components import button
from dash import dcc, html


def bar_chart(client, cols=None):
    fig = go.Figure()

    columns = client.df.columns if cols == None else client.df[cols].columns
    for column in columns:
        fig.add_trace(
            go.Scatter(
                x=client.df.index,
                y=client.df[column],
                mode="lines",
                name=column,
                visible=True,
            )
        )
    fig.update_layout(
        xaxis_title="datetime",
        yaxis_title="Dolars",
        legend_title="Features",
        hovermode="x unified",
        xaxis=dict(
            showspikes=True, spikemode="across", spikedash="dash", spikesnap="cursor"
        ),
    )
    return fig


def multi_chart(client):
    list = []
    for graph in client.graphs:
        list.append(
            html.Div(
                children=[
                    dcc.Graph(
                        id=graph["graph_uid"],
                        figure=bar_chart(client, graph["graph_data_features"]),
                    ),
                    button(
                        text="Remove Graph",
                        id={"type": "remove_button", "index": graph["graph_uid"]},
                    ),
                ],
                className="w-1/2 rounded-lg border mt-10 p-4",
            )
        )
    if list != []:
        return list
    else:
        return []
