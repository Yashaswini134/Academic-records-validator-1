"""
AI-based Certificate Forgery Detection - Prediction Module
This module loads the trained CNN model and predicts forgery on certificate images.

FIXED VERSION - Improved path handling and image loading
"""

import os
import json
import numpy as np
import tensorflow as tf
from tensorflow import keras
import cv2
import sys

# Configuration
IMG_SIZE = 224
# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(SCRIPT_DIR, 'model', 'certificate_forgery_model.h5')

def load_model():
    """
    Load the trained CNN model.
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model not found at {MODEL_PATH}. "
            "Please train the model first by running train_model.py"
        )
    
    model = keras.models.load_model(MODEL_PATH)
    return model

def resolve_image_path(image_path):
    """
    Resolve image path to absolute path, handling both relative and absolute paths.
    
    Args:
        image_path: Input path (can be relative or absolute)
    
    Returns:
        Absolute path to the image
    """
    # If already absolute and exists, return it
    if os.path.isabs(image_path) and os.path.exists(image_path):
        return image_path
    
    # Try relative to current working directory
    cwd_path = os.path.abspath(image_path)
    if os.path.exists(cwd_path):
        return cwd_path
    
    # Try relative to script directory
    script_relative_path = os.path.join(SCRIPT_DIR, image_path)
    if os.path.exists(script_relative_path):
        return script_relative_path
    
    # Return the original path (will fail validation later with clear error)
    return image_path

def preprocess_image(image_path):
    """
    Preprocess the certificate image for prediction.
    Args:
        image_path: Path to the certificate image
    Returns:
        Preprocessed image array
    """
    # Resolve the path
    resolved_path = resolve_image_path(image_path)
    
    # Check if file exists
    if not os.path.exists(resolved_path):
        # Provide helpful error message
        raise FileNotFoundError(
            f"Image not found: {image_path}\n"
            f"Resolved path: {resolved_path}\n"
            f"Current working directory: {os.getcwd()}\n"
            f"Script directory: {SCRIPT_DIR}\n"
            f"Please check:\n"
            f"  1. File exists at the specified path\n"
            f"  2. File extension is correct (.jpg, .jpeg, .png, etc.)\n"
            f"  3. Path is correct (use forward slashes or double backslashes on Windows)"
        )
    
    # Read image
    img = cv2.imread(resolved_path)
    if img is None:
        raise ValueError(
            f"Failed to load image: {resolved_path}\n"
            f"The file exists but cannot be opened as an image.\n"
            f"Please check:\n"
            f"  1. File is a valid image format (PNG, JPG, JPEG, BMP, TIFF)\n"
            f"  2. File is not corrupted\n"
            f"  3. File has proper read permissions"
        )
    
    # Resize to model input size
    img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
    
    # Convert BGR to RGB
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Normalize pixel values to [0, 1]
    img = img.astype(np.float32) / 255.0
    
    # Add batch dimension
    img = np.expand_dims(img, axis=0)
    
    return img

def predict_forgery(image_path, output_json=True):
    """
    Predict whether a certificate is genuine or suspicious.
    
    Args:
        image_path: Path to the certificate image
        output_json: If True, return JSON string; if False, return dict
    
    Returns:
        JSON string or dict with ai_score and ai_result
    """
    # Load model
    model = load_model()
    
    # Preprocess image
    img = preprocess_image(image_path)
    
    # Make prediction
    prediction = model.predict(img, verbose=0)[0][0]
    
    # Convert prediction to score (0.0 = genuine, 1.0 = fake)
    ai_score = float(prediction)
    
    # Determine result based on threshold (0.5)
    if ai_score >= 0.5:
        ai_result = "Suspicious"
    else:
        ai_result = "Genuine"
    
    # Create result dictionary
    result = {
        "ai_score": round(ai_score, 3),
        "ai_result": ai_result
    }
    
    if output_json:
        return json.dumps(result, indent=2)
    else:
        return result

def run_tests():
    """
    Run built-in tests with sample images from dataset folders.
    """
    print("\n" + "=" * 60)
    print("Running Built-in Tests")
    print("=" * 60)
    
    # Find test images
    genuine_folder = os.path.join(SCRIPT_DIR, 'dataset', 'genuine')
    fake_folder = os.path.join(SCRIPT_DIR, 'dataset', 'fake')
    
    test_cases = []
    
    # Find one genuine image
    if os.path.exists(genuine_folder):
        genuine_files = [f for f in os.listdir(genuine_folder) 
                        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))
                        and not f.startswith('.')]
        if genuine_files:
            test_cases.append(('GENUINE', os.path.join(genuine_folder, genuine_files[0])))
    
    # Find one fake image
    if os.path.exists(fake_folder):
        fake_files = [f for f in os.listdir(fake_folder) 
                     if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))
                     and not f.startswith('.')]
        if fake_files:
            test_cases.append(('FAKE', os.path.join(fake_folder, fake_files[0])))
    
    if not test_cases:
        print("\n❌ No test images found in dataset folders!")
        print(f"   Genuine folder: {genuine_folder}")
        print(f"   Fake folder: {fake_folder}")
        return
    
    # Run tests
    for label, image_path in test_cases:
        print(f"\n[Testing {label} certificate]")
        print(f"File: {os.path.basename(image_path)}")
        try:
            result = predict_forgery(image_path, output_json=False)
            print(f"Result: {result['ai_result']} (score: {result['ai_score']})")
            
            # Check if prediction matches expected label
            if label == 'GENUINE' and result['ai_result'] == 'Genuine':
                print("✅ CORRECT prediction!")
            elif label == 'FAKE' and result['ai_result'] == 'Suspicious':
                print("✅ CORRECT prediction!")
            else:
                print("⚠️  INCORRECT prediction - model may need retraining")
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)

def main():
    """
    Main function for command-line usage.
    """
    # Check if running in test mode
    if len(sys.argv) == 1:
        print("\n" + "=" * 60)
        print("AI Certificate Forgery Detection - Prediction Tool")
        print("=" * 60)
        print("\nUsage:")
        print("  python predict_forgery.py <certificate_image_path>")
        print("  python predict_forgery.py --test")
        print("\nExamples:")
        print("  python predict_forgery.py test.png")
        print("  python predict_forgery.py dataset/genuine/cert1.jpg")
        print("  python predict_forgery.py ../input/certificate.jpg")
        print("  python predict_forgery.py --test")
        print("\n" + "=" * 60)
        sys.exit(0)
    
    # Check for test flag
    if sys.argv[1] == '--test' or sys.argv[1] == '-t':
        run_tests()
        sys.exit(0)
    
    image_path = sys.argv[1]
    
    try:
        # Make prediction
        result_json = predict_forgery(image_path, output_json=True)
        
        # Print result
        print("\n" + "=" * 60)
        print("AI-based Certificate Forgery Detection - Prediction Result")
        print("=" * 60)
        print(f"\nCertificate: {os.path.basename(image_path)}")
        print("\nResult:")
        print(result_json)
        print("\n" + "=" * 60)
        
    except Exception as e:
        error_result = {
            "ai_score": 0.0,
            "ai_result": "Error",
            "error_message": str(e)
        }
        print(json.dumps(error_result, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()
