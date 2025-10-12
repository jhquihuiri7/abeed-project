from flask import (
    Flask,
    request,
    render_template,
    session,
    jsonify,
)
from app import create_dash_app
from app_upload import create_dash_upload_app
import json
from utils.functions import ops_to_json
from backend.Class import Ops
from utils.functions import ops_to_json_upload
import pandas as pd
import io

server = Flask(__name__)
server.secret_key = "your_secret_key"

app = create_dash_app(server)
app_upload = create_dash_upload_app(server)

uploaded_data = pd.DataFrame()

@server.route("/")
def launcher():
    return render_template("launcher.html")

@server.route("/predefined/<file_name>")
def predefined(file_name):
    file_path = f"./assets/predefined/{file_name}"
    try:
        with open(file_path, "r") as f:
            json_data = json.load(f)
            session["json_data"] = json_data  # Store in Flask session
            return "OK", 200
    except FileNotFoundError:
        return f"File {file_name} not found", 404

@server.route("/save-json", methods=["POST"])
def save_json():
    try:
        json_data = request.get_json()

        session["json_data"] = json_data  # Store in Flask session

        return jsonify({"status": "success", "message": "OK"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@server.route("/home")
def home():
    """
    Main route where the data is generated and passed to the Dash callback.
    """
    arg = request.args.get("session_flag", None)
    json_data = session.get("json_data", None)
    new_app = app
    if arg == "restore":
        try:
            new_app.layout.children[1].data = json_data
            return new_app.index()
        except json.JSONDecodeError:
            return "Invalid JSON format", 400
    else:
        empty_data = ops_to_json(Ops())
        new_app.layout.children[1].data = empty_data
        return new_app.index()

@server.route("/save-csv", methods=["POST"])
def home_upload():
    global uploaded_data

    if "file" not in request.files:
        return jsonify({"error": "No se envió ningún archivo"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "El nombre del archivo está vacío"}), 400

    if file and file.filename.endswith(".csv"):
        try:
            uploaded_data = pd.read_csv(io.StringIO(file.stream.read().decode("utf-8")))
            uploaded_data.iloc[:, 0] = pd.to_datetime(uploaded_data.iloc[:, 0])
            uploaded_data.set_index(uploaded_data.columns[0], inplace=True)

            return jsonify({"message": "Archivo CSV recibido"}), 200
        except Exception as e:
            return (
                jsonify({"error": f"Error al procesar el archivo CSV: {str(e)}"}),
                500,
            )

    return jsonify({"error": "Archivo no válido. Solo se aceptan archivos CSV."}), 400

@server.route("/custom_dash", methods=["GET"])
def custom_dash():
    global uploaded_data
    new_app2 = app_upload

    if not uploaded_data.empty:
        client = Ops()
        client.df = uploaded_data
        client.start_date = client.df.index.min()
        client.end_date = client.df.index.max()
        json_data = ops_to_json_upload(client)
        uploaded_data = pd.DataFrame()
        new_app2.layout.children[1].data = json_data
        return new_app2.index()
    else:
        return render_template("not_found.html")

if __name__ == "__main__":
    server.run(debug=True, host="0.0.0.0", port=8000)
