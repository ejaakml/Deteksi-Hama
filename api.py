from flask import Flask, jsonify, request, redirect, url_for
from flask_cors import CORS
import mysql.connector
import os
from werkzeug.utils import secure_filename
import detect
import argparse
from pathlib import Path
import sys

from utils.general import (
    LOGGER,
    Profile,
    check_file,
    check_img_size,
    check_imshow,
    check_requirements,
    colorstr,
    cv2,
    increment_path,
    non_max_suppression,
    print_args,
    scale_boxes,
    strip_optimizer,
    xyxy2xywh,
)
import pathlib
temp = pathlib.PosixPath
pathlib.PosixPath = pathlib.WindowsPath

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="db_hama",
        port=3307
    )

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/hama', methods=['GET'])
def get_hama():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM hama ORDER BY id DESC")
    hama_data = cursor.fetchall()
    cursor.close()
    connection.close()
    return jsonify(hama_data)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Optionally, save the file path or other data to the database
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("INSERT INTO hama (nama, deskripsi, img) VALUES (%s, %s, %s)", ('example name', 'example description', filepath))
        connection.commit()
        cursor.close()
        connection.close()

        return jsonify({"message": "File successfully uploaded"}), 201
    else:
        return jsonify({"error": "File type not allowed"}), 400

if __name__ == '__main__':
    app.run(debug=True)
