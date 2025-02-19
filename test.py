
from backend import Class
from datetime import datetime
import pandas as pd

# Example list of sorted datetime objects
datetime_axis = [
    datetime(2025, 1, 1, 8, 0),
    datetime(2025, 1, 1, 9, 0),
    datetime(2025, 1, 1, 10, 0),
    datetime(2025, 1, 1, 12, 30),  # Break in sequence (>1 hour)
    datetime(2025, 1, 1, 13, 30),
    datetime(2025, 1, 1, 14, 0),
]


from datetime import timedelta

def get_first_consecutive_datetime(datetime_axis):
    """
    Identifies and returns the first datetime in consecutive groups from a sorted list.

    Args:
        datetime_axis (list): List of datetime objects, sorted in ascending order.

    Returns:
        list: List of first datetime objects from each consecutive group.
    """
    result = []  # Final result list

    # Initialize with the first element as the start of a group
    current_group_first = datetime_axis[0]
    result.append(current_group_first)  # Save the first element of the first group
    
    # Iterate to identify consecutive groups
    for i in range(1, len(datetime_axis)):
        if datetime_axis[i] - datetime_axis[i - 1] > timedelta(hours=1):  # Adjust interval if needed
            current_group_first = datetime_axis[i]  # Update to the start of the next group
            result.append(current_group_first)  # Save the first element of the new group
    
    return result


# result = get_first_consecutive_datetime(datetime_axis)

def get_stats(df, start_date, end_date, hour_filters, day_filters, buy_node, sell_node): #start_date, end_date, hour_filters, day_filters, buy_node, sell_node
    
    net  = Class.Ops()
    net.update_data_button(start_date, end_date, [sell_node, buy_node])   
    net.create_custom_feature_button([{'Feature': sell_node}, {'Feature': buy_node, 'Operation': '-'}], False, "reg spread")
    net.create_custom_feature_button([{'Feature': sell_node}, {'Feature': buy_node, 'Operation': '-'}], True, "cum spread")
    net.apply_datetime_filters_button(hour_filters, day_filters, net.month_filters, net.year_filters)
    
    
    wins = Class.Ops()
    wins = net.copy()
    loss = Class.Ops()
    loss = net.copy()
    
    wins.add_feature_filter_button('reg spread', 0.000, None)
    loss.add_feature_filter_button('reg spread', None, 0.000)

    new_row = pd.DataFrame({'Total MWH': [len(net.filter_df)], 'Net Profit': [round(net.filter_df['cum spread'].tail(1).values[0], 2)], '#Wins': [len(wins.filter_df)], '$Won': [round(wins.filter_df['cum spread'].tail(1).values[0],2)], '#Losses': [len(loss.filter_df)], '$Lost': [round(loss.filter_df['cum spread'].tail(1).values[0],2)]})
    df = pd.concat([df, new_row], ignore_index=True)
    return df
    # print(f'Total MWH: {len(net.filter_df)}, Net Profit: {round(net.filter_df['cum spread'].tail(1).values[0], 2)}, #Wins: {len(wins.filter_df)}, $Won: {round(wins.filter_df['cum spread'].tail(1).values[0],2)}, #Losses: {len(loss.filter_df)}, $Lost: {round(loss.filter_df['cum spread'].tail(1).values[0],2)}')

# get_stats('2024-11-1', '2025-1-14', [18], [0,1,2,3,4,5,6], "PJM DAY_RESID_AGG RTV", "PJM DAY_RESID_AGG DA")

# start_date = '2024-11-1'
# end_date = '2025-1-14'
light_load = [0,1,2,3,4,5,6,7,10,11,12,13,14,15,16,19,20,21,22,23]
peak_load = [7,8,17,18]
all_hours = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
all_days = [0,1,2,3,4,5,6]
weekdays = [0,1,2,3,4]
weekends = [5,6]
mon_thurs = [0,1,2,3]
fri_sun = [4,5,6]
mon = [0]
tues = [1]
wed = [2]
thurs = [3]
fri = [4]
sat = [5]
sun = [6]
buy_node = "PJ DAY DA"
sell_node = "PJ DAY RTV"

df = pd.DataFrame(columns=['Total MWH', 'Net Profit', '#Wins', '$Won', '#Losses', '$Lost'])
# df = get_stats(df, '2025-1-26', '2025-2-3', all_hours, all_days, buy_node, sell_node)
# df = get_stats(df, '2025-1-26', '2025-2-3', light_load, all_days, buy_node, sell_node)
# df = get_stats(df, '2025-1-26', '2025-2-3', light_load, weekdays, buy_node, sell_node)
# df = get_stats(df, '2025-1-26', '2025-2-3', light_load, mon_thurs, buy_node, sell_node)
# df = get_stats(df, '2025-1-26', '2025-2-3', all_hours, fri, buy_node, sell_node)
# df = get_stats(df, '2025-1-26', '2025-2-3', all_hours, sat, buy_node, sell_node)
# df = get_stats(df, '2025-1-26', '2025-2-3', all_hours, sun, buy_node, sell_node)
# df = get_stats(df, '2025-1-26', '2025-2-3', [6], all_days, buy_node, sell_node)
# df = get_stats(df, '2025-1-26', '2025-2-3', [8], all_days, buy_node, sell_node)
# df = get_stats(df, '2025-1-26', '2025-2-3', [17], all_days, buy_node, sell_node)
# df = get_stats(df, '2025-1-26', '2025-2-3', [18], all_days, buy_node, sell_node)
# df = get_stats(df, '2025-1-26', '2025-2-3', all_hours, weekdays, buy_node, sell_node)
df = get_stats(df, '2025-1-26', '2025-2-3', peak_load, all_days, buy_node, sell_node)
df = get_stats(df, '2025-1-26', '2025-2-3', peak_load, weekends, buy_node, sell_node)
df = get_stats(df, '2025-1-26', '2025-2-3', all_hours, weekends, buy_node, sell_node)
df = get_stats(df, '2025-1-26', '2025-2-3', [5], all_days, buy_node, sell_node)
df = get_stats(df, '2025-1-26', '2025-2-3', [6], all_days, buy_node, sell_node)
df = get_stats(df, '2025-1-26', '2025-2-3', [7], all_days, buy_node, sell_node)
df = get_stats(df, '2025-1-26', '2025-2-3', [8], all_days, buy_node, sell_node)
df = get_stats(df, '2025-1-26', '2025-2-3', [9], all_days, buy_node, sell_node)
df = get_stats(df, '2025-1-26', '2025-2-3', [16], all_days, buy_node, sell_node)
df = get_stats(df, '2025-1-26', '2025-2-3', [17], all_days, buy_node, sell_node)
df = get_stats(df, '2025-1-26', '2025-2-3', [18], all_days, buy_node, sell_node)
df = get_stats(df, '2025-1-26', '2025-2-3', [19], all_days, buy_node, sell_node)






print(buy_node)
print (df)

df.to_csv("C:\\Users\\achowdhury\\Downloads\\node_analysis.csv")







def tester():
    # wins  = Class.Ops()
    # wins.update_data_button('2024-11-1', '2025-1-14', ["PJM COMED_RESID_AGG DA", "PJM COMED_RESID_AGG RTV"])   
    # wins.create_custom_feature_button([{'Feature': "PJM COMED_RESID_AGG DA"}, {'Feature': "PJM COMED_RESID_AGG RTV", 'Operation': '-'}], False, "reg spread")
    # wins.create_custom_feature_button([{'Feature': "PJM COMED_RESID_AGG DA"}, {'Feature': "PJM COMED_RESID_AGG RTV", 'Operation': '-'}], True, "cum spread")
    # wins.apply_datetime_filters_button([0,1,2,3,4,5,7,8,9,10,11,12,13,14,15,16,19,20,21,22,23], [0,1,2,3, 4], wins.month_filters, wins.year_filters)
    # print(wins.filter_df)
    # wins.add_feature_filter_button('reg spread', 0.000, None)

    # loss = Class.Ops()
    # loss.update_data_button('2024-11-1', '2025-1-14', ["PJM COMED_RESID_AGG DA", "PJM COMED_RESID_AGG RTV"])   
    # loss.create_custom_feature_button([{'Feature': "PJM COMED_RESID_AGG DA"}, {'Feature': "PJM COMED_RESID_AGG RTV", 'Operation': '-'}], False, "reg spread")
    # loss.create_custom_feature_button([{'Feature': "PJM COMED_RESID_AGG DA"}, {'Feature': "PJM COMED_RESID_AGG RTV", 'Operation': '-'}], True, "cum spread")
    # loss.apply_datetime_filters_button(wins.hour_filters, wins.day_of_week_filters, loss.month_filters, loss.year_filters)
    # loss.add_feature_filter_button('reg spread', None, 0.000)

    wins  = Class.Ops()
    wins.update_data_button('2024-11-1', '2025-1-14', ["PJM DAY_RESID_AGG DA", "PJM DAY_RESID_AGG RTV"])   
    wins.create_custom_feature_button([{'Feature': "PJM DAY_RESID_AGG DA"}, {'Feature': "PJM DAY_RESID_AGG RTV", 'Operation': '-'}], False, "reg spread")
    wins.create_custom_feature_button([{'Feature': "PJM DAY_RESID_AGG DA"}, {'Feature': "PJM DAY_RESID_AGG RTV", 'Operation': '-'}], True, "cum spread")
    wins.apply_datetime_filters_button([18], [0,1,2,3,4,5,6], wins.month_filters, wins.year_filters)
    print(wins.filter_df)
    wins.add_feature_filter_button('reg spread', 0.000, None)

    loss = Class.Ops()
    loss.update_data_button('2024-11-1', '2025-1-14', ["PJM DAY_RESID_AGG DA", "PJM DAY_RESID_AGG RTV"])   
    loss.create_custom_feature_button([{'Feature': "PJM DAY_RESID_AGG DA"}, {'Feature': "PJM DAY_RESID_AGG RTV", 'Operation': '-'}], False, "reg spread")
    loss.create_custom_feature_button([{'Feature': "PJM DAY_RESID_AGG DA"}, {'Feature': "PJM DAY_RESID_AGG RTV", 'Operation': '-'}], True, "cum spread")
    loss.apply_datetime_filters_button(wins.hour_filters, wins.day_of_week_filters, loss.month_filters, loss.year_filters)
    loss.add_feature_filter_button('reg spread', None, 0.000)
  
    print(wins.filter_df)
    print(len(wins.filter_df))
    print(loss.filter_df)
    print(len(loss.filter_df))
# tester()