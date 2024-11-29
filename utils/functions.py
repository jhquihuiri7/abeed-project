from components.graph_components import bar_chart, multi_chart

def update_graph(client,features, start_date, end_date):
    client.update_df(features, start_date=start_date, end_date=end_date)
    return bar_chart(client)

def add_graph(client, currentFigure):
    if currentFigure:  # Ensure that currentFigure is not None
            sub_features = [
                i["name"] for i in currentFigure["data"] if i["visible"] == True
            ]
            client.add_graph(sub_features)
            
            return multi_chart(client)

def remove_graph(client, index):
    client.remove_graph(target_uuid=index)
    return multi_chart(client)