import pandas as pd
from datetime import datetime
from backend.db_dictionaries import feature_units_dict
import numpy as np
from scipy.stats import linregress
import plotly.express as px
import plotly.graph_objects as go


def convert_df_to_dict(df):
    """
    Converts a Pandas DataFrame into a list of dictionaries for storage in Dash's dcc.Store component.

    Parameters:
        df (pd.DataFrame): The DataFrame to be converted.

    Returns:
        list: A list of dictionaries with each dictionary representing a row in the DataFrame.
    """
    # Reset the index (Datetime) to include it as a column, then convert to dict
    df_reset = df.reset_index()
    new_dict = df_reset.to_dict(orient="records")
    return new_dict

def convert_dict_to_df(dict):
    """
    Converts a list of dictionaries back into a Pandas DataFrame and adjusts the 'datetime' column have a datetime dtype and set the datetime column as the index.

    Parameters:
        dict (list): A list of dictionaries, where each dictionary represents a row of data.

    Returns:
        pd.DataFrame: A DataFrame with the 'datetime' column as the index.
    """
    # Convert dict to df
    df = pd.DataFrame(dict)

    # Convert the datetime column to datetime dtype (of timestamp type if not done)
    df["datetime"] = pd.to_datetime(df["datetime"])

    # Set the index and drop the column
    df.set_index("datetime", inplace=True)

    return df

def get_excluded_datetimes(
    df, hour_filters, day_of_week_filters, month_filters, year_filters, feature_filters
):
    dates_to_exclude = []

    for filter in feature_filters:
        feature_name = filter["feature_name"]
        min_value = filter["range"][0]
        max_value = filter["range"][1]
        min_value = float("-inf") if min_value is None else min_value
        max_value = float("inf") if max_value is None else max_value
        dates_to_exclude_series = df.index[
            (df[feature_name] <= min_value) | (df[feature_name] >= max_value)
        ]
        dates_to_exclude.extend(dates_to_exclude_series.to_list())
    dates_to_exclude = list(set(dates_to_exclude))

    dates_to_exclude_series = df.index[
        ~(df.index.hour.isin(hour_filters))
        | ~(df.index.weekday.isin(day_of_week_filters))
        | ~(df.index.month.isin(month_filters))
        | ~(df.index.year.isin(year_filters))
    ]
    dates_to_exclude.extend(dates_to_exclude_series.to_list())
    
    # for idx, datetimes in enumerate(dates_to_exclude):
    #     dates_to_exclude[idx] = datetimes.to_datetime64()

    # print(dates_to_exclude)
    dates_to_exclude = sorted(list(set(dates_to_exclude)))
    
    # print(dates_to_exclude)
    return dates_to_exclude

def get_feature_units(feature_name):
    return feature_units_dict[feature_name]
    
def add_custom_feature_column(df: pd.DataFrame, custom_feature):
    available_features = df.columns.to_list()
    for features in custom_feature["equation"]:
        feature_name = features["Feature"]
        if feature_name not in available_features:
            return df
        
    custom_feature_series = pd.Series
    for idx, features in enumerate(custom_feature["equation"]):
        if idx == 0:
            custom_feature_series = df[features["Feature"]]

        elif features["Operation"] == '+':
            custom_feature_series = custom_feature_series + df[features["Feature"]]

        elif features["Operation"] == '-':
            custom_feature_series = custom_feature_series - df[features["Feature"]]
    
    if custom_feature["cumulative?"]:
        custom_feature_series = custom_feature_series.cumsum()

    df[custom_feature["feature_name"]] = custom_feature_series

    return df

def create_linear_best_fit(x, y, x_smooth):
    slope, intercept, r_value, _, _ = linregress(x, y)
    r_squared = r_value ** 2
    # Generate the line of best fit equation
    y_fit_smooth = slope * x_smooth + intercept
    equation = f"y = {slope:.2f}x + {intercept:.2f}"
    # print("Line of best fit:", equation)
    return y_fit_smooth, equation, r_squared

def create_log_best_fit(x, y, x_smooth):
    # Take the natural logarithm of x values
    log_x = np.log(x)
    # print(f'x value: {x}, y value: {y}')

    # Perform linear regression on log(x) vs y
    slope, intercept, r_value, _, _ = linregress(log_x, y)
    r_squared = r_value ** 2
    print(x_smooth)
    y_fit_smooth = slope * np.log(x_smooth) + intercept
    # Generate the logarithmic line of best fit equation
    equation = f"y = {slope:.2f} * ln(x) + {intercept:.2f}"
    # print("Logarithmic line of best fit:", equation)
    return y_fit_smooth, equation, r_squared

def create_poly_best_fit(x, y, x_smooth):
    degree = 2  # Change this to the desired polynomial degree
    coefficients = np.polyfit(x, y, degree)
    polynomial = np.poly1d(coefficients)
    y_fit_smooth = polynomial(x_smooth)
    y_fit = polynomial(x)
    ss_res = np.sum((y - y_fit) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)
    equation_terms = [f"{coeff:.2f}x^{i}" for i, coeff in enumerate(coefficients[::-1])]
    equation = " + ".join(equation_terms)
    # print("Polynomial line of best fit:", equation)
    return y_fit_smooth, equation, r_squared

def create_power_best_fit(x, y, x_smooth):
    log_x = np.log(x)
    log_y = np.log(y)

    # Perform linear regression on log(x) vs log(y)
    slope, intercept, _, _, _ = linregress(log_x, log_y)

    # Calculate the coefficients for the power function y = a * x^b
    a = np.exp(intercept)  # a is e^intercept
    b = slope  # b is the slope from the log-log regression

    y_fit_smooth = a * np.power(x_smooth, b)

    # Generate the power line of best fit equation
    equation = f"y = {a:.2f} * x^{b:.2f}"
    
    # Calculate fitted y values using the power function
    y_fit = a * np.power(x, b)
    
    # Calculate R^2
    ss_res = np.sum((y - y_fit) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot)
    
    # print("Power line of best fit:", equation)
    return y_fit_smooth, equation, r_squared

def create_scatter_plot_fig(df):
    features = list(df.columns.values)
    x = df[features[0]]
    y = df[features[1]]
    print(x)
    print(y)

    x_smooth = np.linspace(x.min(), x.max(), 500)

    linear_y_fit_smooth, linear_equation, linear_r_squared = create_linear_best_fit(x, y, x_smooth)
    log_y_fit_smooth, log_equation, log_r_squared = create_log_best_fit(x, y, x_smooth)
    poly_y_fit_smooth, poly_equation, poly_r_squared = create_poly_best_fit(x, y, x_smooth)
    power_y_fit_smooth, power_equation, power_r_squared = create_power_best_fit(x, y, x_smooth)

    # Add a single scatter trace for MISO pjm RT vs Meteologica MISO Load forecast
    fig = px.scatter(
        df,
        x=features[0],
        y=features[1],
        # mode='markers',
        # name=f'{features[0]} vs {features[1]})'
    )

    fig.update_layout(
        title=f'{features[0]} vs {features[1]}',
        xaxis_title=f'{features[0]}',
        yaxis_title=f'{features[1]}',
    )

    fig.add_trace(go.Scatter(
        x=x_smooth,
        y=linear_y_fit_smooth,
        mode='lines',
        name=f'Linear Fit: {linear_equation}, R^2 = {linear_r_squared:.4f}'
    ))

    fig.add_trace(go.Scatter(
        x=x_smooth,
        y=log_y_fit_smooth,
        mode='lines',
        name=f'Logarithmic Fit: {log_equation}, R^2 = {log_r_squared:.4f}'
    ))

    fig.add_trace(go.Scatter(
        x=x_smooth,
        y=poly_y_fit_smooth,
        mode='lines',
        name=f'Polynomial Fit: {poly_equation}, R^2 = {poly_r_squared:.4f}'
    ))

    fig.add_trace(go.Scatter(
        x=x_smooth,
        y=power_y_fit_smooth,
        mode='lines',
        name=f'Power Fit: {power_equation}, R^2 = {power_r_squared:.4f}'
    ))

    return fig