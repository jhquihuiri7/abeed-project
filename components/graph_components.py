# Import necessary modules and components
import plotly.graph_objects as go  # For creating Plotly charts
from plotly.subplots import make_subplots  # For creating charts with subplots and multiple axes
from components.button_components import button  # Custom button component
from backend.db_dictionaries import feature_units_dict  # Dictionary containing units for features
from utils.logic_functions import contains_both_axis, get_last_consecutive_datetime, group_consecutive  # Function to check for double axis requirements
from dash import dcc, html  # Dash components for UI
from styles.styles import button_style  # Custom button styling
import pandas as pd
import numpy as np


# Function to create a bar chart with optional dual axes
def bar_chart(client, cols=None, apply_filter=False, collapse=False):
    """
    Generates a bar chart with support for a secondary Y-axis if needed.

    Args:
        client: An object containing the dataframe and other metadata.
        cols (list, optional): Specific columns to include in the chart. 
                               If None, all columns in the client's dataframe are used.

    Returns:
        go.Figure: A Plotly figure with the bar chart.
    """
    # Create a figure with support for a secondary Y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    custom_df = client.df
    filter_df = client.filter_df
    if apply_filter and collapse:
        if client.created_features != []:
            custom_features = [ feature["feature_name"] for feature in client.created_features if feature["cumulative?"] == True]
            df_1 = client.df.loc[:, ~client.df.columns.isin(custom_features)]
            df_2 = client.filter_df[custom_features]
            custom_df = pd.concat([df_1, df_2], axis=1)
            custom_df[custom_features] = custom_df[custom_features].ffill()

    
    if client.datetimes_to_exclude and apply_filter and collapse==False:
        margin = pd.Timedelta(hours=1)
        new_datetimes = [result + margin for result in get_last_consecutive_datetime(client.filter_df.index)]
        new_data = {client.filter_df.columns[0]: [np.nan]*len(new_datetimes)}
        df_new = pd.DataFrame(new_data, index=new_datetimes)
        filter_df = pd.concat([client.filter_df, df_new])
        filter_df = filter_df.sort_index()
        
        
    # Determine the columns to use for the chart
    data = (custom_df if collapse else filter_df) if apply_filter else client.df 
    
    columns = data.columns if cols is None else data[cols].columns
    # Check if dual axes are needed and get axis names
    double_axis, axis_names = contains_both_axis(columns)
    
    # Initialize lists to store maximum Y values for each axis
    max_y_primary = []
    max_y_secondary = []
    
    # Iterate over the columns to add data traces to the chart
    for column in columns:
        # Calculate the maximum value in the column
        max_val = max(data[column])
        
        # Append the value to the appropriate axis based on the feature's unit
        (
            max_y_secondary.append(max_val)
            if double_axis and feature_units_dict[column] == "mw"  # Secondary Y-axis for "mw" units
            else max_y_primary.append(max_val)  # Primary Y-axis for other units
        )
        
        # Add a trace to the chart
        fig.add_trace(
            go.Scatter(
                x=data.index,  # X-axis data (index of the dataframe)
                y=data[column],  # Y-axis data (column values)
                mode="lines",  # Line chart
                line_shape="hv",
                name=column,  # Legend label
                visible=True,  # Initial visibility
                showlegend=True,  # Show legend entry
                
            ),
            secondary_y=(
                True if double_axis and feature_units_dict[column] == "mw" else False
            ),  # Assign trace to secondary Y-axis if applicable
        )
        
    
    if client.datetimes_to_exclude and apply_filter and collapse:
        margin_top = pd.Timedelta(minutes=55)
        margin_bottom = pd.Timedelta(minutes=5)
        for highlight_date in group_consecutive(client.datetimes_to_exclude):
            fig.add_shape(
                type="rect",
                x0=highlight_date[0] - margin_bottom,
                x1=highlight_date[1] + margin_top,
                xref="x",
                y0=0,
                y1=1,
                yref="paper",
                line=dict(width=0),
                fillcolor="red",
                opacity=0.3
            )
    if client.datetimes_to_exclude and apply_filter and collapse==False:
        
        result = get_last_consecutive_datetime(data.index)
        margin = pd.Timedelta(hours=1)
        
        for highlight_date in result:
            fig.add_vline(x=highlight_date, line_dash="solid", line_color="red", opacity=0.3, line_width=3)
        
        formatted_dates = [timestamp.strftime("%b %d") for timestamp in result]
        fig.update_xaxes(type="category", tickvals= result, ticktext=formatted_dates)
    
    # Update the layout of the chart
    fig.update_layout(
        xaxis_title="datetime",  # X-axis title
        legend_title="Features",  # Legend title
        hovermode="x unified",  # Unified hover mode
        yaxis=dict(
            title=dict(text=axis_names[0]),  # Title for primary Y-axis
            side="left",  # Position on the left
            range=[0, int(max(max_y_primary) * 1.05)],  # Dynamic range with a 5% margin
        ),
        xaxis=dict(
            showspikes=True,  # Show spikes on hover
            spikemode="across",  # Spikes extend across the chart
            spikedash="dash",  # Dashed line for spikes
            spikesnap="cursor",  # Spikes snap to cursor
        ),
    )
    
    # If dual axes are required, configure the secondary Y-axis
    if double_axis:
        fig.update_layout(
            yaxis2=dict(
                title=dict(text=axis_names[1]),  # Title for secondary Y-axis
                side="right",  # Position on the right
                range=[0, int(max(max_y_secondary) * 1.05)],  # Dynamic range with a 5% margin
                overlaying="y",  # Overlay on the primary Y-axis
            )
        )
    
    return fig  # Return the complete figure

# Function to generate multiple charts and associate them with remove buttons
def multi_chart(client, apply_filter=False, collapse=False):
    """
    Creates multiple charts and associates a remove button with each chart.

    Args:
        client: An object containing the dataframe and a list of graphs.

    Returns:
        list: A list of Dash HTML Div components, each containing a chart and a remove button.
    """
    list = []  # Initialize an empty list to store chart components
    
    # Iterate through the graphs in reverse order
    for index, graph in enumerate(client.graphs[::-1]):
        # Append a Div containing a chart and a remove button to the list
        list.append(
            html.Div(
                children=[
                    # Graph component displaying the bar chart
                    dcc.Graph(
                        id=graph["graph_uid"],  # Unique ID for the graph
                        figure=bar_chart(client, graph["graph_data_features"],apply_filter, collapse),  # Generate the chart
                    ),
                    # Button to remove the graph
                    button(
                        text="Remove Graph",  # Button label
                        id={"type": "remove_button", "index": graph["graph_uid"]},  # Unique button ID
                        style=button_style,  # Apply custom button styling
                    ),
                ],
                # Apply styling for layout and spacing
                className=f"w-[49%] rounded-lg border mt-10 p-4 {'ml-[1%]' if index % 2 != 0 else 'mr-[1%]'}",
            )
        )
    
    # Return the list of chart components if it is not empty, otherwise return an empty list
    return list if list else []
