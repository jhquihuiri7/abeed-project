import dash_mantine_components as dmc
from dash_iconify import DashIconify

def show_notification(message):
    return dmc.Notification(
        title="Hey there!",
        #id="simple-notify",
        action="show",
        message=message,
        icon=DashIconify(icon="meteocons:code-yellow-fill", height=50, color="yellow"),
        withBorder=True,
        color="red",
        autoClose=2000
        )
    