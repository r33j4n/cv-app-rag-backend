from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename

from get_cv_upload_response import query_ragcv
from rag_service_query import query_rag
from extract_details import populate_dbcv, clear_vector_db
from flask_cors import CORS
import os
import json
from get_job_upload_response import query_rag_job

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
UPLOAD_FOLDER = 'cv-library'
UPLOAD_FOLDER_JOB = 'job-library'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(UPLOAD_FOLDER_JOB):
    os.makedirs(UPLOAD_FOLDER_JOB)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER_JOB'] = UPLOAD_FOLDER_JOB


@app.route('/')
def hello_world():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000, timeout=10000)


@app.route('/upload-cv', methods=['POST'])
def upload_cv():
    try:
        file = request.files['file']
        user_id = request.form['userID']
        if not file:
            return jsonify({'error': 'No file provided'}), 400
        if not user_id:
            return jsonify({'error': 'No user ID provided'}), 400

        app.logger.info(f"Received file: {file.filename} from user: {user_id}")

        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Clear the vector DB before adding new CV
        clear_vector_db()

        # Populate the vector DB with the new CV
        documents = populate_dbcv([file_path])
        add_db_message = documents[1]

        return jsonify({'success': 'File successfully uploaded', 'db_message': add_db_message}), 200
    except Exception as e:
        app.logger.error(f"Error uploading file: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/upload-job', methods=['POST'])
def upload_job():
    try:
        file = request.files['file']
        user_id = request.form['userID']
        if not file:
            return jsonify({'error': 'No file provided'}), 400
        if not user_id:
            return jsonify({'error': 'No user ID provided'}), 400
        app.logger.info(f"Received file: {file.filename} from user: {user_id}")
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER_JOB'], filename)
        file.save(file_path)
        # Clear the vector DB before adding new CV
        # clear_vector_db()
        # Populate the vector DB with the new CV
        documents = populate_dbcv([file_path])
        add_db_message = documents[1]

        return jsonify({'success': 'File successfully uploaded', 'db_message': add_db_message}), 200
    except Exception as e:
        app.logger.error(f"Error uploading file: {e}")
        return jsonify({'error': str(e)}), 500



@app.route('/clear-db', methods=['GET'])
def clear_db():
    try:
        clear_vector_db()
        return jsonify({'message': 'DB cleared'}), 200
    except:
        return jsonify({'message': 'Error clearing DB'}), 500


@app.route('/query-rag', methods=['POST'])
def handle_query_rag():
    request_data = request.get_json()
    query_text = request_data.get('query_text', '')
    if query_text:
        response_text = query_rag(query_text)
        return jsonify({'response': response_text}), 200
    else:
        return jsonify({'error': 'No query text provided'}), 400


@app.route('/update-cv-data', methods=['POST'])
def update_cv_data():
    try:
        user_id = request.json.get('userID')  # Retrieve userID from the request body
        if user_id is None:
            return jsonify({'error': 'UserID not provided'}), 400
        response_txt = query_ragcv()

        # Find the start and end of the JSON string
        start_index = response_txt.find("{")
        end_index = response_txt.rfind("}") + 1  # +1 to include the closing brace

        # Extract the JSON string
        json_string = response_txt[start_index:end_index]

        # Parse the JSON string into a Python dictionary
        data = json.loads(json_string)

        # Update the UserID in the response data
        data['UserID'] = user_id

        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/update-job-data', methods=['POST'])
def update_job_data():
    try:
        user_id = request.json.get('userID')  # Retrieve userID from the request body
        if user_id is None:
            return jsonify({'error': 'UserID not provided'}), 400
        response_txt = query_rag_job()

        # Find the start and end of the JSON string
        start_index = response_txt.find("{")
        end_index = response_txt.rfind("}") + 1  # +1 to include the closing brace

        # Extract the JSON string
        json_string = response_txt[start_index:end_index]

        # Parse the JSON string into a Python dictionary
        data = json.loads(json_string)

        # Update the UserID in the response data
        data['UserID'] = user_id

        return jsonify(data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear-db-job', methods=['GET'])
def clear_db_job():
    try:
        clear_vector_db()
        return jsonify({'message': 'DB cleared'}), 200
    except:
        return jsonify({'message': 'Error clearing DB'}), 500


