
    app.layout = dmc.MantineProvider(
        children=[html.Div(
        className="p-10 w-full",
        children=[            
            main_tabs(ops, show_custom=False),  # Tabs component for layout
            apply_filters_toggle("Collapse"),
            dcc.Graph(id="main_graph"),  # Graph for displaying data
            button(text="Add Graph", id="add_graph_button", style=button_style),  # Button to add new graph
            html.Div(id="dynamic_div", children=[], className="flex flex-wrap"),  # Dynamic div for additional content
        ],
    ),
        dcc.Store(id="client", data=ops_to_json(ops)),
        ]
    ) 
    
    
    @callback(
        Output("collapse_expand_filter","label"),
        Input("collapse_expand_filter","value"),
        prevent_initial_call=True
    )
    def update_apply_filters(collapse_expand_filter):
        ctx = callback_context
        
        return "Collapse" if collapse_expand_filter else "Expand" 
    
    @callback(
        Output("date_filter_dropdown","children"),
        Input("select_all_datefilter","n_clicks"),
        State("date_filter_dropdown","children"),
        prevent_initial_call=True,
    )
    def update_date_filter(select_all_datefilter, datefilter_dropdown):
        ctx = callback_context
        
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None
        if not triggered_id:
            return datefilter_dropdown  # No changes
        try:
            # Try to convert dynamic trigger ID to dictionary if possible
            if "type" in triggered_id:
                triggered_id = eval(triggered_id)
        except:
            pass
        
        if triggered_id == "select_all_datefilter":
            
            return date_filter_dropdown()
        
        return datefilter_dropdown
    
    @callback(
        Output({"type": "hour_button", "index": ALL}, "style"),
        Input({"type": "hour_button", "index": ALL}, "n_clicks"),
        Input("apply_hour_range","n_clicks"),
        Input("select_all_hour_range","n_clicks"),
        Input("deselect_all_hour_range","n_clicks"),
        State({"type": "hour_button", "index": ALL}, "style"),
        State("hour-filter-slider", "value"),
        prevent_initial_call=True,  # Prevent initial callback call
    )
    def update_hour_button_style(
        hour_button, 
        apply_hour_range,
        select_all_hour_range,
        deselect_all_hour_range,
        hour_button_style, 
        hour_filter_slider,
        ):

        ctx = callback_context
        
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None
        if not triggered_id:
            return hour_button_style  # No changes
        try:
            # Try to convert dynamic trigger ID to dictionary if possible
            if "type" in triggered_id:
                triggered_id = eval(triggered_id)
        except:
            pass
        
        if isinstance(triggered_id, dict) and triggered_id.get("type") == "hour_button":
            index = triggered_id.get("index")
            # Toggle the background color when the hour button is clicked
            hour_button_style[index]["backgroundColor"] = "white" if hour_button_style[index]["backgroundColor"] == "#d9d9d9" else "#d9d9d9"
        
        if triggered_id == "deselect_all_hour_range":
            for index in range(0,24):
                hour_button_style[index]["backgroundColor"] = "white"# Toggle the background color when the hour button is clicked
            return hour_button_style
        
        if triggered_id == "select_all_hour_range":
            for index in range(0,24):
                hour_button_style[index]["backgroundColor"] = "#d9d9d9"# Toggle the background color when the hour button is clicked
            return hour_button_style
        
        if triggered_id == "apply_hour_range":
            for index in range(hour_filter_slider[0],hour_filter_slider[1]+1):
                hour_button_style[index]["backgroundColor"] = "#d9d9d9" if triggered_id == "apply_hour_range" else "white"# Toggle the background color when the hour button is clicked
            return hour_button_style
             
        return hour_button_style
         
    return app