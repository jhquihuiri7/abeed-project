import plotly.graph_objects as go
from plotly.subplots import make_subplots
from components.button_components import button
from backend.db_dictionaries import feature_units_dict
from utils.logic_functions import contains_both_axis
from dash import dcc, html


def bar_chart(client, cols=None):
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    columns = client.df.columns if cols == None else client.df[cols].columns
    double_axis, axis_names = contains_both_axis(columns)
    max_y_primary=[]
    max_y_secondary = []
    for column in columns:
        max_val = max(client.df[column])
        max_y_secondary.append(max_val) if double_axis and feature_units_dict[column] == "mw" else max_y_primary.append(max_val)
        fig.add_trace(
            go.Scatter(
                x=client.df.index,
                y=client.df[column],
                mode="lines",
                name=column,
                visible=True,
            ),
            secondary_y=True if double_axis and feature_units_dict[column] == "mw" else False 
        )
    fig.update_layout(
        xaxis_title="datetime",
        legend_title="Features",
        hovermode="x unified",
        yaxis=dict(
            title=dict(text=axis_names[0]),
            side="left",
            range=[0, int(max(max_y_primary)* 1.05)],
        ),
        xaxis=dict(
            showspikes=True, spikemode="across", spikedash="dash", spikesnap="cursor"
        ),
    )
    
    if double_axis:
        fig.update_layout(
            yaxis2=dict(
            title=dict(text=axis_names[1]),
            side="right",
            range=[0, int(max(max_y_secondary)* 1.05)],
            overlaying="y"
            )
        )
    return fig


def multi_chart(client):
    list = []
    for index, graph in enumerate(client.graphs[::-1]):
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
                className=f"w-[49%] rounded-lg border mt-10 p-4 {'ml-[1%]' if index % 2 != 0 else 'mr-[1%]'}"

            )
        )
    if list != []:
        return list
    else:
        return []
