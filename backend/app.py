import os
import sys
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.main_controller import CertificateVerificationController
from backend.decision_engine import DecisionEngine

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'uploads')
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'output')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize Controller
# Note: We rely on system PATH for tesseract unless specified in config.py
controller = CertificateVerificationController(verbose=True)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})

# ==========================================
# University Routes
# ==========================================

@app.route('/university/login', methods=['POST'])
def university_login():
    # Mock login
    data = request.json
    if data.get('username') and data.get('password'):
        return jsonify({
            'token': 'mock-jwt-token-university',
            'user': {
                'id': 'uni_123',
                'name': 'Demo University',
                'role': 'university'
            }
        })
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/university/upload', methods=['POST'])
def university_upload():
    if 'certificate' not in request.files:
        return jsonify({'message': 'No certificate file provided'}), 400
    
    file = request.files['certificate']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # For university upload, we just want to extract data (OCR)
            # Accessing the OCR engine directly from the controller
            ocr_result = controller.ocr_engine.process_certificate(
                image_path=filepath,
                output_dir=OUTPUT_FOLDER,
                save_intermediate=False
            )
            
            if ocr_result['status'] == 'SUCCESS':
                return jsonify(ocr_result)
            else:
                return jsonify({'message': 'OCR extraction failed', 'errors': ocr_result.get('errors', [])}), 500
                
        except Exception as e:
            return jsonify({'message': str(e)}), 500

@app.route('/university/confirm', methods=['POST'])
def university_confirm():
    data = request.json
    # In a real app, this would save to blockchain/database
    # Here we just acknowledge receipt
    return jsonify({
        'status': 'confirmed',
        'message': 'Certificate confirmed and registered',
        'hash': 'mock-hash-' + datetime.now().strftime('%Y%m%d%H%M%S')
    })

# ==========================================
# Verifier Routes
# ==========================================

@app.route('/verifier/login', methods=['POST'])
def verifier_login():
    # Mock login
    data = request.json
    if data.get('username') and data.get('password'):
        return jsonify({
            'token': 'mock-jwt-token-verifier',
            'user': {
                'id': 'ver_123',
                'name': 'Demo Verifier',
                'role': 'verifier'
            }
        })
    return jsonify({'message': 'Invalid credentials'}), 401

@app.route('/verifier/verify', methods=['POST'])
def verifier_verify():
    if 'certificate' not in request.files:
        return jsonify({'message': 'No certificate file provided'}), 400
    
    file = request.files['certificate']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Run full verification
            result = controller.verify_certificate(
                certificate_path=filepath,
                output_dir=OUTPUT_FOLDER
            )
            
            return jsonify(result)
                
        except Exception as e:
            return jsonify({'message': str(e)}), 500

@app.route('/verifier/verify-by-id', methods=['POST'])
def verify_by_id():
    # Mock verification by ID since we don't have a DB
    return jsonify({
        'final_decision': 'VERIFIED',
        'remarks': 'Mock verification for ID lookup',
        'student_name': 'John Doe',
        'course': 'Computer Science',
        'university': 'Demo University',
        'decision_confidence': 'HIGH'
    })

if __name__ == '__main__':
    print("Starting Backend Server on port 5000...")
    app.run(debug=True, host='0.0.0.0', port=5000)
