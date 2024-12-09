# Import necessary modules and components
import plotly.graph_objects as go  # For creating Plotly charts
from plotly.subplots import make_subplots  # For creating charts with subplots and multiple axes
from components.button_components import button  # Custom button component
from backend.db_dictionaries import feature_units_dict  # Dictionary containing units for features
from utils.logic_functions import contains_both_axis  # Function to check for double axis requirements
from dash import dcc, html  # Dash components for UI
from styles.styles import button_style  # Custom button styling

# Function to create a bar chart with optional dual axes
def bar_chart(client, cols=None):
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
    
    # Determine the columns to use for the chart
    columns = client.df.columns if cols is None else client.df[cols].columns
    
    # Check if dual axes are needed and get axis names
    double_axis, axis_names = contains_both_axis(columns)
    
    # Initialize lists to store maximum Y values for each axis
    max_y_primary = []
    max_y_secondary = []
    
    # Iterate over the columns to add data traces to the chart
    for column in columns:
        # Calculate the maximum value in the column
        max_val = max(client.df[column])
        
        # Append the value to the appropriate axis based on the feature's unit
        (
            max_y_secondary.append(max_val)
            if double_axis and feature_units_dict[column] == "mw"  # Secondary Y-axis for "mw" units
            else max_y_primary.append(max_val)  # Primary Y-axis for other units
        )
        
        # Add a trace to the chart
        fig.add_trace(
            go.Scatter(
                x=client.df.index,  # X-axis data (index of the dataframe)
                y=client.df[column],  # Y-axis data (column values)
                mode="lines",  # Line chart
                name=column,  # Legend label
                visible=True,  # Initial visibility
                showlegend=True,  # Show legend entry
            ),
            secondary_y=(
                True if double_axis and feature_units_dict[column] == "mw" else False
            ),  # Assign trace to secondary Y-axis if applicable
        )
    
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
def multi_chart(client):
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
                        figure=bar_chart(client, graph["graph_data_features"]),  # Generate the chart
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
