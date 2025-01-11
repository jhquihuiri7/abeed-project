from flask import Flask
from app import create_dash_app

# We create the Flask application
server = Flask(__name__)

app = create_dash_app(server)

# Flask function to render the home route
@server.route('/')
def home():
    """
    Main route where the data is generated and passed to the Dash callback.
    """
    # Generate the data when accessing /home
    #data = generate_data(100)  # Generates 100 records by default
    #print(data)
    # Convert the data to JSON format (for the dcc.Store)
    #data_json = data.to_dict()
    new_app = app
    # Now, you can modify the state of `dcc.Store` in the Dash application directly.
    #new_app.layout.children[2].data = data_json  # This updates the dcc.Store with the new data

    # Return the Dash page and pass the generated data to the dcc.Store component
    return new_app.index()

if __name__ == '__main__':
    server.run(debug=True)
