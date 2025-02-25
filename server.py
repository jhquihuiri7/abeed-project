from flask import Flask, request, render_template, session, jsonify, redirect, url_for
from app import create_dash_app
import json
from utils.functions import ops_to_json
from backend.Class import Ops
from datetime import date
from utils.functions import json_to_ops

# We create the Flask application
server = Flask(__name__)
server.secret_key = 'your_secret_key'

app = create_dash_app(server)

@server.route("/")
def index():
    return render_template("index.html")

@server.route('/save-json', methods=['POST'])
def save_json():
    try:
        # Get JSON data from the request body
        json_data = request.get_json()

        # Optionally store it in session or process it
        session['json_data'] = json_data  # Store in Flask session
        print(json_data)
        # Respond with success message
        return jsonify({'status': 'success', 'message': 'OK'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

# Flask function to render the home route
@server.route('/home')
def home():
    """
    Main route where the data is generated and passed to the Dash callback.
    """
    arg = request.args.get('session_flag', None)
    json_data = session.get('json_data', None)
    new_app = app
    if arg == "restore":
        try:
            new_app.layout.children[1].data = json_data

            return new_app.index()
        except json.JSONDecodeError:
            return "Invalid JSON format", 400
    else:
        empty_data =  ops_to_json(Ops())
        new_app.layout.children[1].data = empty_data 
        return new_app.index()


if __name__ == '__main__':
    server.run(debug=True)
