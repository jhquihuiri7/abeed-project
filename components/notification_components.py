import dash_mantine_components as dmc
from dash_iconify import DashIconify

# Function to display a notification
def show_notification(message):
    """
    Creates and returns a notification component with a custom message and style.

    Args:
        message (str): The message to display in the notification.

    Returns:
        dmc.Notification: A Dash Mantine Notification component with the specified properties.
    """
    return dmc.Notification(
        title="Hey there!",  # Title of the notification
        # id="simple-notify",  # Optional unique identifier (commented out in this case)
        action="show",  # Action to trigger the notification (e.g., show or hide)
        message=message,  # Custom message to display in the notification
        icon=DashIconify(
            icon="meteocons:code-yellow-fill",  # Icon to display in the notification
            height=50,  # Height of the icon
            color="yellow"  # Color of the icon
        ),
        withBorder=True,  # Whether to display a border around the notification
        color="red",  # Color of the notification (red in this case)
        autoClose=False # Time (in milliseconds) before the notification auto-closes
    )

def show_modal():
    return dmc.Modal(
            id="input-modal",
            children=[
                dmc.TextInput(
                    id="user-session",
                    label="Name your session",
                    placeholder="Type here...",
                ),
                dmc.Space(h=10),
                dmc.Button("Save", id="save-button"),
            ],
            opened=False,  # Initially closed
        )