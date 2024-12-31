from components.graph_components import bar_chart, multi_chart
from components.button_components import button
from styles.styles import button_dropdown_style
from dash import dcc, html, Input, Output, State, callback, callback_context, ALL


# Function to update the graph when a button is clicked
def update_graph(client, update_action=1, apply_filters=False, collapse=False):
    """
    Updates the graph based on the specified update action.

    Args:
        client: An object managing the data and graphs.
        update_action (int, optional): Specifies the update action:
            1 - Update the graph without modifying data.
            2 - Update data and recreate custom features.
            3 - Update data based on the selected features and date range.
            4 - Update the graph with filters and collapse options.

    Returns:
        Figure: The updated bar chart figure.
    """
    if update_action == 1:
        # Return the bar chart without modifying the data
        return bar_chart(client, None, False, False)

    if update_action == 2:
        # Update the client's data frame
        client.update_df()
        
        # Store and reset created features
        custom_features = client.created_features
        client.created_features = []
        
        # Recreate each custom feature in the data frame
        for custom_feature in custom_features:
            client.create_feature(
                feature_operation_list=custom_feature["equation"],  # Feature equation
                cumulative=custom_feature["cumulative?"],          # Cumulative option
                custom_name=custom_feature["feature_name"],         # Custom feature name
            )

    if update_action == 3:
        # Update the client's data frame with the selected features and date range
        client.update_df()
    
    if update_action == 4:
        # Return the bar chart with filters and collapse options
        return bar_chart(client, None, apply_filters, collapse)

    # Return the default bar chart
    return bar_chart(client, None, False, False)


# Function to add a graph when a button is clicked
def add_graph(client, currentFigure, apply_filter=False, collapse=False, update=False):
    """
    Adds a new graph based on the currently visible features in the provided figure.

    Args:
        client: An object managing the data and graphs.
        currentFigure (dict): The current figure, containing data about visible features.
        apply_filter (bool, optional): Whether to apply filters to the graph.
        collapse (bool, optional): Whether to collapse the graph layout.
        update (bool, optional): Whether to update the graph instead of adding a new one.

    Returns:
        list: Updated list of graphs to be displayed.
    """
    if currentFigure:  # Ensure the figure is not None
        if not update:
            # Extract names of visible features in the current figure
            sub_features = [
                i["name"] for i in currentFigure["data"] if i["visible"]
            ]
            # Add the selected features as a new graph
            client.add_graph(sub_features)

        # Return the updated list of graphs
        return multi_chart(client, apply_filter, collapse)


# Function to remove a specific custom feature from all graphs
def remove_custom_feature_from_graphs(client, custom_feature):
    """
    Removes a custom feature from all graphs managed by the client.

    Args:
        client: An object managing the data and graphs.
        custom_feature (str): The name of the custom feature to remove.

    Returns:
        list: Updated list of graphs without the custom feature.
    """
    for i in range(len(client.graphs)):
        try:
            # Attempt to remove the custom feature from each graph
            client.graphs[i]["graph_data_features"].remove(custom_feature)
        except ValueError:
            # Ignore if the custom feature is not found in the graph
            pass
    return multi_chart(client)


# Function to remove a graph when a button is clicked
def remove_graph(client, index, apply_filter, collapse):
    """
    Removes a graph based on its unique identifier (UUID).

    Args:
        client: An object managing the data and graphs.
        index (str): The unique identifier of the graph to remove.
        apply_filter (bool): Whether to apply filters to the updated graph list.
        collapse (bool): Whether to collapse the graph layout.

    Returns:
        list: Updated list of graphs to be displayed.
    """
    # Remove the specified graph by its UUID
    client.remove_graph(target_uuid=index)

    # Return the updated list of graphs
    return multi_chart(client, apply_filter, collapse)


# Function to generate a list of custom filter components
def list_custom_filter_children(client):
    """
    Generates a list of HTML components for displaying custom features and a button to remove them.

    Args:
        client: An object managing the data and graphs.

    Returns:
        list: A list of HTML Div elements for each custom feature.
    """
    created_features = client.created_features
    return [
        html.Div(
            children=[
                # Display the custom feature name
                html.H4(
                    feature["feature_name"], 
                    className="mr-4 text-base font-bold text-slate-500", 
                    style={"white-space": "nowrap", "overflow": "hidden", "text-overflow": "ellipsis"}
                ),
                # Add a button to remove the custom feature
                button(
                    text="X",
                    id={"type": "custom_feature_remove", "index": feature["feature_id"]},
                    style=button_dropdown_style,
                )
            ],
            className="flex flex-row py-2 items-center justify-between"  # Styling for layout
        ) for feature in created_features
    ]
