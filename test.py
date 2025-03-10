@callback(
        Output("client", "data"),
        Output("temp_feature", "data"),
        Output("main_graph", "figure"),
        Output("dynamic_div", "children"),
        Output("custon_name", "value"),
        Output("custom_dropdown", "children"),
        Output("list_custom_features", "children"),
        Output("feature_filter_dropdown", "options"),
        Output("feature_filter_dropdown", "value"),
        Output("feature_filter_min_range", "value"),
        Output("feature_filter_max_range", "value"),
        Output("feature_filter_list", "children"),
        Output("notifications-container", "children"),
        Output("apply_filters", "value"),
        Output("collapse_expand_filter", "disabled"),
        # Inputs and states for callback
        Input("update_graph_button", "n_clicks"),
        Input("add_graph_button", "n_clicks"),
        Input({"type": "remove_button", "index": ALL}, "n_clicks"),
        Input({"type": "dynamic-dropdown", "index": ALL}, "value"),
        Input({"type": "custom_feature_remove", "index": ALL}, "n_clicks"),
        Input("add_custom_feature", "n_clicks"),
        Input("feature_filter_add","n_clicks"),
        Input({"type": "feature_filter_remove", "index":ALL}, "n_clicks"),
        Input("apply_selection_hourfilter","n_clicks"),
        Input("apply_filters", "value"),
        Input("collapse_expand_filter","value"),
        Input("apply_selection_datefilter", "n_clicks"),
        #Input({"type": "hour_button", "index": ALL}, "n_clicks"),
        State("main_dropdown", "value"),
        State("main-date-picker-range", "start_date"),
        State("main-date-picker-range", "end_date"),
        State("main_graph", "figure"),
        State("dynamic_div", "children"),
        State("custom_dropdown", "children"),
        State("custon_name", "value"),
        State("custom_cumulative", "value"),
        State("list_custom_features", "children"),
        State("feature_filter_dropdown", "options"),
        State("feature_filter_dropdown", "value"),
        State("feature_filter_min_range", "value"),
        State("feature_filter_max_range", "value"),
        State("feature_filter_list", "children"),
        State({"type": "hour_button", "index": ALL}, "style"),
        State("apply_filters", "value"),
        State("collapse_expand_filter","value"),
        State("collapse_expand_filter","disabled"),
        State("year_dropdown_date_filter", "value"),
        State("month_dropdown_date_filter", "value"),
        State("day_dropdown_date_filter", "value"),
        State("client", "data"),
        State("temp_feature", "data"),
    )
    def update_render(
        update_button,
        add_button,
        remove_button,
        dynamic_dropdown,
        custom_feature_remove,
        add_custom_feature,
        feature_filter_add, 
        feature_filter_remove,
        apply_selection_hourfilter,
        apply_filters,
        collapse_expand_filter,
        apply_selection_datefilter,
        features,
        start_date,
        end_date,
        currentFigure,
        currentChildren,
        currentDropdownChildren,
        custom_name,
        custom_cumulative,
        list_custom_features,
        feature_filter_dropdown_opts,
        feature_filter_dropdown,
        feature_filter_min_range,
        feature_filter_max_range,
        feature_filter_list,
        hour_button,
        apply_filters_state,
        collapse_expand_filter_state,
        collapse_expand_filter_disabled,
        year_dropdown_date_filter_state,
        month_dropdown_date_filter_state,
        day_dropdown_date_filter_state,
        data,
        custom_feature
    ):
        client = json_to_ops(data)
        print(data)
        notification = []
        ctx = callback_context
        triggered_id = ctx.triggered[0]["prop_id"].split(".")[0] if ctx.triggered else None
    
        try:
            # Try to convert dynamic trigger ID to dictionary if possible
            if "type" in triggered_id:
                triggered_id = eval(triggered_id)
        except:
            pass
        
        
        client.start_date = start_date
        client.end_date = end_date
                
        # Add graph when add button is clicked
        if triggered_id == "add_graph_button":
            sub_features = [
                      i["name"] for i in currentFigure["data"] if i["visible"]==True
                  ]
            client.add_graph_button(sub_features)
            currentChildren = multi_chart(client, apply_filters_state!=[], collapse_expand_filter_state)
            return ops_to_json(client),custom_feature,currentFigure, currentChildren, custom_name, currentDropdownChildren, list_custom_features, feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list, [], apply_filters_state, collapse_expand_filter_disabled
    
        # Remove graph when remove button is clicked
        elif isinstance(triggered_id, dict) and triggered_id.get("type") == "remove_button":
            client.remove_graph_button(triggered_id.get("index"))
            currentChildren = multi_chart(client, apply_filters_state!=[], collapse_expand_filter_state)            
            return ops_to_json(client),custom_feature,currentFigure, currentChildren, custom_name, currentDropdownChildren, list_custom_features, feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list, [], apply_filters_state, collapse_expand_filter_disabled
                
        if triggered_id == "feature_filter_add":
            is_valid, message, feature_filter_min_range, feature_filter_max_range = validateFeatureFilterData(client, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range)
            if is_valid:    
                client.add_feature_filter_button(feature_filter_dropdown,feature_filter_min_range, feature_filter_max_range)
                feature_filter_list = list_feature_filter(client)
                feature_filter_dropdown_opts = get_feature_filter_dropdown_opts(client)  
                apply_filters_state = ['Apply filter']
                collapse_expand_filter_disabled = False 
                currentFigure = bar_chart(client, None, apply_filters_state!=[], collapse_expand_filter_state)
                currentChildren = multi_chart(client, apply_filters_state!=[], collapse_expand_filter_state)     
            else:
                notification = show_notification(message)
            return ops_to_json(client),custom_feature,currentFigure, currentChildren, custom_name, currentDropdownChildren, list_custom_features, feature_filter_dropdown_opts, feature_filter_dropdown, "", "", feature_filter_list, notification, apply_filters_state, collapse_expand_filter_disabled       
        
        if isinstance(triggered_id, dict) and triggered_id.get("type") == "feature_filter_remove":
            index = triggered_id.get("index")
            client.remove_feature_filter_button(index)
            feature_filter_list = list_feature_filter(client)
            feature_filter_dropdown_opts = get_feature_filter_dropdown_opts(client)
            apply_filters_state = ['Apply filter']
            collapse_expand_filter_disabled = False 
            currentFigure = bar_chart(client, None, apply_filters_state!=[], collapse_expand_filter_state)
            currentChildren = multi_chart(client, apply_filters_state!=[], collapse_expand_filter_state)  
            return ops_to_json(client),custom_feature, currentFigure, currentChildren, custom_name,currentDropdownChildren, list_custom_features, feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list, [], apply_filters_state, collapse_expand_filter_disabled
        
        if (triggered_id == "apply_selection_datefilter") or (triggered_id == "apply_selection_hourfilter"):
            hours_to_include = [index for index, hour in enumerate(hour_button) if hour["backgroundColor"] != "white"]
            client.apply_datetime_filters_button(hours_to_include, day_dropdown_date_filter_state, month_dropdown_date_filter_state, year_dropdown_date_filter_state)
            is_valid, message = validateApplyDatetimeSelection(client)
            if is_valid:
                apply_filters_state = ['Apply filter']
                collapse_expand_filter_disabled = False 
                currentFigure = bar_chart(client, None, apply_filters_state!=[], collapse_expand_filter_state)
                currentChildren = multi_chart(client, apply_filters_state!=[], collapse_expand_filter_state)
            else:
                notification = show_notification(message)
            return ops_to_json(client),custom_feature, currentFigure, currentChildren, custom_name, currentDropdownChildren, list_custom_features, feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list, notification, apply_filters_state, collapse_expand_filter_disabled
        
        if triggered_id == "apply_filters":
            is_valid, message = validateApplyFilterToggle(client, apply_filters_state, collapse_expand_filter_state)
            if is_valid:  
                if apply_filters_state == []:
                    collapse_expand_filter_disabled = True
                    currentFigure = bar_chart(client, None, False, False)
                else:
                    collapse_expand_filter_disabled = False
                    currentFigure = bar_chart(client, None, apply_filters_state!=[], collapse_expand_filter_state)
            else:
                notification = show_notification(message)
            currentChildren = multi_chart(client, apply_filters_state!=[], collapse_expand_filter_state) 
            return ops_to_json(client),custom_feature, currentFigure, currentChildren, custom_name, currentDropdownChildren, list_custom_features, feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list, notification, apply_filters_state, collapse_expand_filter_disabled
            
        if triggered_id == "collapse_expand_filter":
            currentFigure = bar_chart(client, None, apply_filters_state!=[], collapse_expand_filter_state)
            currentChildren = multi_chart(client, apply_filters_state!=[], collapse_expand_filter_state) 
            return ops_to_json(client),custom_feature, currentFigure, currentChildren, custom_name, currentDropdownChildren,list_custom_features, feature_filter_dropdown_opts, feature_filter_dropdown, feature_filter_min_range, feature_filter_max_range, feature_filter_list, [], apply_filters_state, collapse_expand_filter_disabled
        
        if not currentFigure:
            #return client_data,custom_feature,empty,data_features, currentFigure, currentChildren, custom_dropdow_children,custom_name,list_custom_features, feature_filter_dropdown_opts, feature_filter_default_opts, feature_filter_min_range, feature_filter_max_range, feature_filter_list, empty_array, apply_filters_state, collapse_expand_filter_disabled
            return restore_session(client, apply_filters_state, collapse_expand_filter_state, collapse_expand_filter_disabled,feature_filter_min_range, feature_filter_max_range, extract_values_custom_feature(currentDropdownChildren))

        else: 
            raise exceptions.PreventUpdate
     