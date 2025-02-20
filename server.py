from flask import Flask, request, render_template
from app import create_dash_app
import json
from utils.functions import ops_to_json
from backend.Class import Ops
from datetime import date
from utils.functions import json_to_ops

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
            client = json_to_ops(data_dict)
            print(type(client.start_date))
            new_app.layout.children[1].data = data_dict
            new_app.layout.children[0].children[1].children[1].children[0].start_date =  client.start_date
            new_app.layout.children[0].children[1].children[1].children[0].end_date =  client.end_date
            return new_app.index()
        except json.JSONDecodeError:
            return "Invalid JSON format", 400
    else:
        empty_data =  ops_to_json(Ops())
        new_app.layout.children[1].data = empty_data 
        return new_app.index()


if __name__ == '__main__':
    server.run(debug=False, host= "0.0.0.0", port=8000)
