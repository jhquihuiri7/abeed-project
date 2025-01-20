from flask import Flask, request, render_template
from app import create_dash_app
import json
from utils.functions import ops_to_json
from backend.Class import Ops

# We create the Flask application
server = Flask(__name__)

app = create_dash_app(server)

@server.route("/")
def index():
    return render_template("index.html")

# Flask function to render the home route
@server.route('/home')
def home():
    """
    Main route where the data is generated and passed to the Dash callback.
    """
    
    json_data = request.args.get("data")
    new_app = app
    if json_data:
        try:
            # Parse the JSON string into a Python dictionary
            data_dict = json.loads(json_data)
            
            new_app.layout.children[1].data = data_dict 
            # Use the data (e.g., pass it to a template or process it)
            return new_app.index()
        except json.JSONDecodeError:
            return "Invalid JSON format", 400
    else:
        empty_data =  ops_to_json(Ops())
        new_app.layout.children[1].data = empty_data 
        return new_app.index()
    
    
    # Now, you can modify the state of `dcc.Store` in the Dash application directly.
   # new_app.layout.children[2].data = data_json  # This updates the dcc.Store with the new data

    # Return the Dash page and pass the generated data to the dcc.Store component


if __name__ == '__main__':
    server.run(debug=True)
