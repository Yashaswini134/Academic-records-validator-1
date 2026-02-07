"""
Main OCR Engine for Certificate Verification System
Orchestrates the complete OCR pipeline
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Optional
import pytesseract
from PIL import Image
import cv2
import numpy as np

# Import custom modules
from ocr.preprocess import ImagePreprocessor
from ocr.extract_fields import FieldExtractor
from security.hash_generator import HashGenerator


class CertificateOCREngine:
    """Main OCR engine that orchestrates the complete pipeline"""
    
    def __init__(self, tesseract_path: Optional[str] = None):
        """
        Initialize OCR Engine
        
        Args:
            tesseract_path: Optional path to Tesseract executable
        """
        self.preprocessor = ImagePreprocessor()
        self.extractor = FieldExtractor()
        self.hash_generator = HashGenerator()
        
        # Set Tesseract path if provided
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # Try to detect Tesseract
        self._check_tesseract()
    
    def _check_tesseract(self):
        """Check if Tesseract is available"""
        try:
            version = pytesseract.get_tesseract_version()
            print(f"✓ Tesseract OCR detected: v{version}")
        except Exception as e:
            print("="*60)
            print("WARNING: Tesseract OCR not found!")
            print("="*60)
            print("Please install Tesseract OCR:")
            print("  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
            print("  Linux: sudo apt-get install tesseract-ocr")
            print("  Mac: brew install tesseract")
            print("\nOr set the path manually:")
            print("  pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'")
            print("="*60)
    
    def perform_ocr(self, image: np.ndarray, config: str = '--psm 6') -> str:
        """
        Perform OCR on preprocessed image
        
        Args:
            image: Preprocessed image (numpy array)
            config: Tesseract configuration string
                   --psm 6: Assume a single uniform block of text
                   --psm 3: Fully automatic page segmentation (default)
        
        Returns:
            Extracted text
        """
        print("\n" + "="*60)
        print("PERFORMING OCR")
        print("="*60)
        
        try:
            # Convert numpy array to PIL Image
            pil_image = Image.fromarray(image)
            
            # Perform OCR
            text = pytesseract.image_to_string(pil_image, config=config)
            
            print(f"✓ OCR completed")
            print(f"  Extracted {len(text)} characters")
            print(f"  Lines: {len(text.splitlines())}")
            
            return text
            
        except Exception as e:
            print(f"✗ OCR failed: {str(e)}")
            return ""
    
    def process_certificate(
        self,
        image_path: str,
        output_dir: str = "output",
        save_intermediate: bool = False
    ) -> Dict:
        """
        Complete certificate processing pipeline
        
        Args:
            image_path: Path to certificate image
            output_dir: Directory to save output
            save_intermediate: Whether to save intermediate steps
            
        Returns:
            Dictionary with processing results
        """
        print("\n" + "="*70)
        print("CERTIFICATE OCR PROCESSING PIPELINE")
        print("="*70)
        print(f"Input: {image_path}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        
        result = {
            'certificate_id': None,
            'student_name': None,
            'roll_number': None,
            'course': None,
            'university': None,
            'year': None,
            'hash': None,
            'status': 'FAIL',
            'errors': [],
            'raw_text': '',
            'processing_time': None,
            'image_path': image_path
        }
        
        start_time = datetime.now()
        
        try:
            # Step 1: Generate file hash
            print("\n[STEP 1/4] Generating file hash...")
            file_hash = self.hash_generator.generate_sha256(image_path)
            if file_hash:
                result['hash'] = file_hash
            else:
                result['errors'].append("Failed to generate file hash")
            
            # Step 2: Preprocess image
            print("\n[STEP 2/4] Preprocessing image...")
            preprocessed = self.preprocessor.preprocess(image_path, save_intermediate)
            
            if preprocessed is None:
                result['errors'].append("Image preprocessing failed")
                return result
            
            # Step 3: Perform OCR
            print("\n[STEP 3/4] Performing OCR...")
            ocr_text = self.perform_ocr(preprocessed)
            
            if not ocr_text or len(ocr_text.strip()) < 10:
                result['errors'].append("OCR extraction failed or insufficient text")
                return result
            
            result['raw_text'] = ocr_text
            
            # Save raw OCR text
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                text_file = os.path.join(output_dir, "ocr_raw_text.txt")
                with open(text_file, 'w', encoding='utf-8') as f:
                    f.write(ocr_text)
                print(f"✓ Raw OCR text saved to: {text_file}")
            
            # Step 4: Extract fields
            print("\n[STEP 4/4] Extracting fields...")
            extracted_fields = self.extractor.extract_all_fields(ocr_text)
            
            # Update result with extracted fields
            result.update(extracted_fields)
            
            # Get extraction errors
            extraction_errors = self.extractor.get_errors()
            result['errors'].extend(extraction_errors)
            
            # Validate fields
            is_valid, validation_errors = self.extractor.validate_fields()
            result['errors'].extend(validation_errors)
            
            # Determine status
            if is_valid and len(extraction_errors) == 0:
                result['status'] = 'PASS'
            elif len(extraction_errors) <= 2:  # Allow some missing optional fields
                result['status'] = 'PARTIAL'
            else:
                result['status'] = 'FAIL'
            
        except Exception as e:
            result['errors'].append(f"Processing error: {str(e)}")
            print(f"\n✗ Error during processing: {str(e)}")
        
        # Calculate processing time
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        result['processing_time'] = f"{processing_time:.2f}s"
        
        # Save results
        if output_dir:
            self._save_results(result, output_dir)
        
        # Print summary
        self._print_summary(result)
        
        return result
    
    def _save_results(self, result: Dict, output_dir: str):
        """Save results to JSON file"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Create a clean copy without raw_text for the main output
        output_data = {k: v for k, v in result.items() if k != 'raw_text'}
        
        output_file = os.path.join(output_dir, "ocr_result.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✓ Results saved to: {output_file}")
    
    def _print_summary(self, result: Dict):
        """Print processing summary"""
        print("\n" + "="*70)
        print("PROCESSING SUMMARY")
        print("="*70)
        
        print(f"\nStatus: {result['status']}")
        print(f"Processing Time: {result['processing_time']}")
        
        print("\nExtracted Fields:")
        fields = ['certificate_id', 'student_name', 'roll_number', 'course', 'university', 'year']
        for field in fields:
            value = result.get(field)
            status = "✓" if value else "✗"
            print(f"  {status} {field.replace('_', ' ').title()}: {value or 'NOT FOUND'}")
        
        print(f"\nFile Hash: {result['hash']}")
        
        if result['errors']:
            print(f"\nErrors/Warnings ({len(result['errors'])}):")
            for error in result['errors']:
                print(f"  - {error}")
        
        print("\n" + "="*70)
        print("PROCESSING COMPLETE")
        print("="*70 + "\n")


def main():
    """Main entry point"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║     CERTIFICATE OCR VERIFICATION SYSTEM                      ║
    ║     Academic Certificate Data Extraction                     ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Configuration
    IMAGE_PATH = "test.png"  # Change this to your certificate image
    OUTPUT_DIR = "output"
    SAVE_INTERMEDIATE = True  # Set to True to save preprocessing steps
    
    # Optional: Set Tesseract path for Windows
    # Uncomment and modify if Tesseract is not in PATH
    # TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    TESSERACT_PATH = None
    
    # Check if image exists
    if not os.path.exists(IMAGE_PATH):
        print(f"Error: Certificate image not found at '{IMAGE_PATH}'")
        print("\nPlease:")
        print("  1. Place your certificate image in the project directory")
        print("  2. Name it 'test.png' or update IMAGE_PATH in ocr_engine.py")
        print("  3. Supported formats: PNG, JPG, JPEG")
        sys.exit(1)
    
    # Initialize OCR engine
    engine = CertificateOCREngine(tesseract_path=TESSERACT_PATH)
    
    # Process certificate
    result = engine.process_certificate(
        image_path=IMAGE_PATH,
        output_dir=OUTPUT_DIR,
        save_intermediate=SAVE_INTERMEDIATE
    )
    
    # Exit with appropriate code
    if result['status'] == 'PASS':
        sys.exit(0)
    elif result['status'] == 'PARTIAL':
        sys.exit(1)
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
