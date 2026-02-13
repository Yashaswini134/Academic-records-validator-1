import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime

# ==================================================
# PATH SETUP
# ==================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')

sys.path.insert(0, BASE_DIR)

from backend.main_controller import CertificateVerificationController
from backend.decision_engine import DecisionEngine

# ==================================================
# APP INIT
# ==================================================
app = Flask(__name__)
CORS(app)

# ==================================================
# STORAGE CONFIG (FIXED)
# ==================================================
UPLOAD_FOLDER = os.path.join(BACKEND_DIR, 'uploads')
CERTIFICATE_UPLOAD = os.path.join(UPLOAD_FOLDER, 'certificates')
OUTPUT_FOLDER = os.path.join(BACKEND_DIR, 'output')

os.makedirs(CERTIFICATE_UPLOAD, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = CERTIFICATE_UPLOAD

# ==================================================
# TEMP USER STORE
# ==================================================
users = {
    "university": [],
    "verifier": []
}

# ==================================================
# CONTROLLER INIT
# ==================================================
controller = CertificateVerificationController(verbose=True)

# ==================================================
# HEALTH
# ==================================================
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

# ==================================================
# AUTH ROUTES
# ==================================================
@app.route('/signup', methods=['POST'])
def signup():
    data = request.json
    role = data.get('role')
    username = data.get('username')
    password = data.get('password')

    if role not in users:
        return jsonify({'message': 'Invalid role'}), 400

    for u in users[role]:
        if u['username'] == username:
            return jsonify({'message': 'User already exists'}), 409

    users[role].append({
        'username': username,
        'password': password
    })

    return jsonify({'message': f'{role} signup successful'})


@app.route('/signin', methods=['POST'])
def signin():
    data = request.json
    role = data.get('role')
    username = data.get('username')
    password = data.get('password')

    for u in users.get(role, []):
        if u['username'] == username and u['password'] == password:
            return jsonify({
                'message': 'Login successful',
                'token': f'mock-jwt-{role}',
                'role': role
            })

    return jsonify({'message': 'Invalid credentials'}), 401

# ==================================================
# UNIVERSITY ROUTES
# ==================================================
@app.route('/university/upload', methods=['POST'])
def university_upload():
    if 'certificate' not in request.files:
        return jsonify({'message': 'No certificate file provided'}), 400

    file = request.files['certificate']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    print("📁 University uploaded:", filepath)

    try:
        ocr_result = controller.ocr_engine.process_certificate(
            image_path=filepath,
            output_dir=OUTPUT_FOLDER,
            save_intermediate=False
        )
        return jsonify(ocr_result)

    except Exception as e:
        return jsonify({'message': str(e)}), 500


@app.route('/university/confirm', methods=['POST'])
def university_confirm():
    return jsonify({
        'status': 'confirmed',
        'hash': 'mock-hash-' + datetime.now().strftime('%Y%m%d%H%M%S')
    })

# ==================================================
# VERIFIER ROUTES
# ==================================================
@app.route('/verifier/verify', methods=['POST'])
def verifier_verify():
    data = request.json
    filename = data.get("filename")

    if not filename:
        return jsonify({'message': 'Filename required'}), 400

    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if not os.path.exists(filepath):
        return jsonify({'message': 'Certificate not found'}), 404

    print("🔍 Verifier verifying:", filepath)

    try:
        result = controller.verify_certificate(
            certificate_path=filepath,
            output_dir=OUTPUT_FOLDER
        )
        return jsonify(result)

    except Exception as e:
        return jsonify({'message': str(e)}), 500


@app.route('/verifier/verify-by-id', methods=['POST'])
def verify_by_id():
    return jsonify({
        'final_decision': 'VERIFIED',
        'remarks': 'Mock verification',
        'confidence': 'HIGH'
    })

# ==================================================
# RUN SERVER
# ==================================================
if __name__ == '__main__':
    print("🚀 Backend running on port 5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
