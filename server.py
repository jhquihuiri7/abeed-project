from flask import Flask, request, render_template, session, jsonify, redirect, url_for, g
from app import create_dash_app
from app_upload import create_dash_upload_app
import json
from utils.functions import ops_to_json
from backend.Class import Ops
from datetime import date
from utils.functions import json_to_ops, ops_to_json_upload
import pandas as pd
import io

# We create the Flask application
server = Flask(__name__)
server.secret_key = 'your_secret_key'

app = create_dash_app(server)
app_upload = create_dash_upload_app(server)

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
    
uploaded_data = pd.DataFrame()

@server.route('/upload', methods=['POST'])
def home_upload():
    global uploaded_data
    
    if 'file' not in request.files:
        return jsonify({'error': 'No se envió ningún archivo'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'El nombre del archivo está vacío'}), 400

    if file and file.filename.endswith('.csv'):
        try:
            uploaded_data = pd.read_csv(io.StringIO(file.stream.read().decode('utf-8')))
            uploaded_data.iloc[:, 0] = pd.to_datetime(uploaded_data.iloc[:, 0])
            uploaded_data.set_index(uploaded_data.columns[0], inplace=True)
           
            # Enviar la respuesta con los datos procesados
            return jsonify({'message': 'Archivo CSV recibido'}), 200
        except Exception as e:
            return jsonify({'error': f'Error al procesar el archivo CSV: {str(e)}'}), 500
        
    # Si no es un CSV válido
    return jsonify({'error': 'Archivo no válido. Solo se aceptan archivos CSV.'}), 400

# Función para gestionar los datos y actualizar la aplicación de Dash
@server.route('/custom_dash', methods=['GET'])
def custom_dash():
    global uploaded_data
    new_app2 = app_upload
    # Si 'data' contiene datos, actualizamos la app
    if not uploaded_data.empty:
        client = Ops()
        client.df = uploaded_data
        client.start_date = client.df.index.min()
        client.end_date = client.df.index.max()
        json_data = ops_to_json_upload(client)
        uploaded_data = pd.DataFrame()
        # Aquí puedes actualizar la aplicación de Dash con los nuevos datos
        new_app2.layout.children[1].data = json_data
        
        return new_app2.index()
    else:
        return render_template("not_found.html")
        

if __name__ == '__main__':
    server.run(debug=True)
