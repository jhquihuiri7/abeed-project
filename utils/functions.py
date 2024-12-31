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
        features (list): List of features to include in the graph.
        start_date (str): Start date for filtering data.
        end_date (str): End date for filtering data.
        update_action (int, optional): Specifies the update action:
            1 - Update the graph without modifying data.
            2 - Update data and recreate custom features.
            3 - Update data based on the selected features and date range.

    Returns:
        Figure: The updated bar chart figure.
    """
    if update_action == 1:
        # Return the bar chart as is without modifying the data
        return bar_chart(client,  None, False, False)

    if update_action == 2:
        # Update the client's data frame with the new features and date range
        client.update_df()
        
        # Store and reset created features
        custom_features = client.created_features
        client.created_features = []
        
        # Recreate each custom feature in the client's data
        for custom_feature in custom_features:
            client.create_feature(
                feature_operation_list=custom_feature["equation"],
                cumulative=custom_feature["cumulative?"],  # Check if cumulative is required
                custom_name=custom_feature["feature_name"],  # Assign custom feature name
            )

    if update_action == 3:
        # Update the client's data frame with the selected features and date range
        client.update_df()
    
    if update_action == 4:
        return bar_chart(client,  None, apply_filters, collapse)       

    # Return the updated bar chart
    return bar_chart(client, None,False, False)


# Function to add a graph when a button is clicked
def add_graph(client, currentFigure, apply_filter=False, collapse=False, update=False):
    """
    Adds a new graph based on the currently visible features in the provided figure.

    Args:
        client: An object managing the data and graphs.
        currentFigure (dict): The current figure, containing data about visible features.

    Returns:
        list: Updated list of graphs to be displayed.
    """
    if currentFigure:  # Ensure that currentFigure is not None
        # Extract names of features that are currently visible
        if not update:
            sub_features = [
                i["name"] for i in currentFigure["data"] if i["visible"] == True
            ]
            # Add the selected features as a new graph to the client
            client.add_graph(sub_features)

        # Return the updated list of graphs
        return multi_chart(client, apply_filter, collapse)

def remove_custom_feature_from_graphs(client, custom_feature):
    for i in range(0,len(client.graphs)):
        try:
            client.graphs[i]["graph_data_features"].remove(custom_feature)
        except:
            pass
    return multi_chart(client)

# Function to remove a graph when a button is clicked
def remove_graph(client, index, apply_filter, collapse):
    """
    Removes a graph based on its unique identifier (UUID).

    Args:
        client: An object managing the data and graphs.
        index (str): The unique identifier of the graph to be removed.

    Returns:
        list: Updated list of graphs to be displayed.
    """
    # Remove the specified graph from the client
    client.remove_graph(target_uuid=index)

    # Return the updated list of graphs
    return multi_chart(client, apply_filter, collapse)

def list_custom_filter_children(client):
    created_features = client.created_features
    return [
            html.Div(
               children=[
                   html.H4(feature["feature_name"], className="mr-4 text-base font-bold text-slate-500",style={"white-space": "nowrap", "overflow": "hidden", "text-overflow": "ellipsis"}),
                   button(
                        text="X",
                        id={"type": "custom_feature_remove", "index": feature["feature_id"]},
                        style=button_dropdown_style,
                    )
               ],
               className="flex flex-row py-2 items-center justify-between"
            ) for feature in created_features
        ]