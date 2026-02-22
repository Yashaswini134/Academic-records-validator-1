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

# Optional: EasyOCR (better accuracy on complex certificates)
try:
    import easyocr
    _EASYOCR_AVAILABLE = True
except Exception as e:
    print(f"⚠ EasyOCR not available or failed to import: {e}")
    easyocr = None
    _EASYOCR_AVAILABLE = False

# --- Defensive Imports ---

# 1. Image Preprocessor
try:
    from ocr.preprocess_enhanced import EnhancedImagePreprocessor as ImagePreprocessor
except ImportError as e:
    print(f"⚠ Warning: Could not import ImagePreprocessor: {e}")
    ImagePreprocessor = None

# 2. Field Extractor
try:
    from ocr.extract_fields_improved import ImprovedFieldExtractor as FieldExtractor
except ImportError as e:
    print(f"⚠ Warning: Could not import FieldExtractor: {e}")
    FieldExtractor = None

# 3. Hash Generator
try:
    from security.hash_generator import HashGenerator
except ImportError as e:
    print(f"⚠ Warning: Could not import HashGenerator: {e}")
    HashGenerator = None

# 4. Layout Engine
try:
    from ocr.layout_engine import LayoutOCREngine
except ImportError as e:
    print(f"⚠ Warning: Could not import LayoutOCREngine: {e}")
    LayoutOCREngine = None


class CertificateOCREngine:
    """Main OCR engine that orchestrates the complete pipeline"""
    
    def __init__(self, tesseract_path: Optional[str] = None, tessdata_prefix: Optional[str] = None):
        """Initialize OCR Engine with safe fallback"""
        
        # Initialize components securely
        if ImagePreprocessor:
            try:
                self.preprocessor = ImagePreprocessor()
            except Exception as e:
                print(f"⚠ Preprocessor init failed: {e}")
                self.preprocessor = None
        else:
            self.preprocessor = None

        if FieldExtractor:
            try:
                self.extractor = FieldExtractor()
            except Exception as e:
                print(f"⚠ Extractor init failed: {e}")
                self.extractor = None
        else:
            self.extractor = None

        if HashGenerator:
            try:
                self.hash_generator = HashGenerator()
            except Exception as e:
                print(f"⚠ HashGenerator init failed: {e}")
                self.hash_generator = None
        else:
            self.hash_generator = None

        if LayoutOCREngine:
            try:
                self.layout_engine = LayoutOCREngine()
            except Exception as e:
                print(f"⚠ LayoutEngine init failed: {e}")
                self.layout_engine = None
        else:
            self.layout_engine = None
        
        # Initialize EasyOCR reader if available
        self.easyocr_reader = None
        if _EASYOCR_AVAILABLE:
            try:
                # English-only reader, CPU mode for compatibility
                self.easyocr_reader = easyocr.Reader(['en'], gpu=False)
                print("✓ EasyOCR reader initialized (en, gpu=False)")
            except Exception as e:
                print(f"⚠ EasyOCR initialization failed, will fall back to Tesseract: {e}")
                self.easyocr_reader = None

        # Set Tesseract path if provided, otherwise try to auto-detect on Windows
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            print(f"✓ Tesseract path set to: {tesseract_path}")
        else:
            if os.name == "nt":
                # Common Windows installation paths
                default_paths = [
                    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                ]
                for p in default_paths:
                    if os.path.exists(p):
                        pytesseract.pytesseract.tesseract_cmd = p
                        print(f"✓ Auto-detected Tesseract at: {p}")
                        if not tessdata_prefix:
                            parent_dir = os.path.dirname(p)
                            # Explicitly check for tessdata folder and point to it
                            tessdata_path = os.path.join(parent_dir, 'tessdata')
                            if os.path.exists(tessdata_path):
                                tessdata_prefix = tessdata_path
                            else:
                                tessdata_prefix = parent_dir
                        break
        
        # Set TESSDATA_PREFIX environment variable if provided or auto-detected
        if tessdata_prefix:
            os.environ['TESSDATA_PREFIX'] = tessdata_prefix
            print(f"✓ TESSDATA_PREFIX set to: {tessdata_prefix}")
        
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
            print(f"Error: {e}")
            print("="*60)
            print("Please install Tesseract OCR:")
            print("  Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki")
            print("  Linux: sudo apt-get install tesseract-ocr")
            print("  Mac: brew install tesseract")
            print("\nOr set the path manually:")
            print("  pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'")
            print("="*60)
    
    def perform_ocr(self, image: np.ndarray, config: str = '--oem 3 --psm 6') -> str:
        """
        Perform OCR on preprocessed image.
        If EasyOCR is available, prefer it; otherwise use Tesseract with multiple configs.
        """
        print("\n" + "="*70)
        print("PERFORMING OCR")
        print("="*70)

        try:
            # -------------------------
            # 1) EasyOCR path
            # -------------------------
            if self.easyocr_reader is not None:
                print("Using EasyOCR reader...")
                # EasyOCR expects RGB numpy array
                if len(image.shape) == 2:
                    rgb_image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
                else:
                    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                results = self.easyocr_reader.readtext(
                    rgb_image,
                    detail=0,
                    paragraph=True
                )
                text = "\n".join(results)
                print(f"EasyOCR extracted {len(text.strip())} characters")
                return text

            # -------------------------
            # 2) Tesseract path
            # -------------------------
            print("EasyOCR not available; falling back to Tesseract (multi-config).")
            pil_image = Image.fromarray(image)

            configs = [
                '--oem 3 --psm 6',   # single uniform block
                '--oem 3 --psm 4',   # single column
                '--oem 3 --psm 11',  # sparse text
            ]

            best_text = ""
            best_score = -1

            for cfg in configs:
                print(f"Trying config: {cfg}")
                text = pytesseract.image_to_string(pil_image, config=cfg)
                stripped = text.strip()

                if not stripped:
                    score = 0
                else:
                    alpha_num = sum(c.isalnum() for c in stripped)
                    score = alpha_num

                print(f"  -> chars: {len(stripped)}, alnum: {score}")

                if score > best_score:
                    best_score = score
                    best_text = text

            print(f"✓ Selected Tesseract result with best score: {best_score}")
            return best_text or ""

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
            if self.hash_generator:
                file_hash = self.hash_generator.generate_sha256(image_path)
                if file_hash:
                    result['hash'] = file_hash
                else:
                    result['errors'].append("Failed to generate file hash")
            else:
                print("⚠ Hash Generator unavailable.")

            # Step 2 & 3: Multi-pass Preprocessing & OCR ("Tournament Mode")
            print("\n[STEP 2 & 3] Multi-pass Preprocessing & OCR (Tournament Mode)...")
            
            ocr_text = ""
            best_score = 0
            best_variant_name = "None"
            
            candidates = {}

            if self.preprocessor:
                try:
                    # Get all preprocessing variations
                    variations = self.preprocessor.get_preprocessing_variations(image_path)
                    
                    if not variations:
                        print("⚠ No variations generated, trying raw fallback...")
                        try:
                            pil_img = Image.open(image_path).convert('L')
                            variations['0_Raw_Fallback'] = np.array(pil_img)
                        except Exception as e:
                            print(f"✗ Raw fallback failed: {e}")

                    # Iterate through all variations
                    for name, processed_img in variations.items():
                        print(f"--- Attempt: {name} ---")
                        try:
                            # Run OCR on this variation
                            text = self.perform_ocr(processed_img)
                            cleaned_len = len(text.strip())
                            
                            # Simple scoring: length of text
                            score = cleaned_len
                            print(f"  -> extracted {score} chars")
                            
                            candidates[name] = text
                            
                            if score > best_score:
                                best_score = score
                                ocr_text = text
                                best_variant_name = name
                                
                        except Exception as e:
                            print(f"  ✗ {name} failed: {e}")
                            
                except Exception as e:
                    print(f"⚠ Variation processing error: {e}")
            else:
                 print("⚠ Preprocessor unavailable.")

            print(f"\n✓ WINNER: {best_variant_name} with {best_score} chars")

            # Final check
            if not ocr_text or len(ocr_text.strip()) < 10:
                result['errors'].append("OCR extraction failed (insufficient text in all passes)")
                return result
            
            # Step 3: Set Final Text
            print("\n[STEP 3/4] Finalizing text...")
            # ocr_text is already populated by the multi-pass loop above
            
            result['raw_text'] = ocr_text
            
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                # Always save debug text for inspection
                debug_file = os.path.join(output_dir, "debug_ocr_text.txt")
                with open(debug_file, 'w', encoding='utf-8') as f:
                    f.write(ocr_text)
                print(f"✓ Debug OCR text saved to: {debug_file}")
            
            # Step 4: Extract fields
            print("\n[STEP 4/4] Extracting fields (Regex + Layout)...")
            self.extractor.extract_all_fields(ocr_text)
            
            # --- LAYOUT AWARE EXTRACTION (RESTORING & REFINING) ---
            try:
                print("Performing layout analysis for robust extraction...")
                layout_data = self.layout_engine.analyze_layout(preprocessed)
                if hasattr(self.extractor, 'set_layout_data'):
                    self.extractor.set_layout_data(layout_data)
                    self.extractor.extract_from_layout()
            except Exception as e:
                print(f"⚠ Layout analysis skipped due to error: {e}")
            # -----------------------------------------------------
            
            # Get final extracted data
            extracted_fields = self.extractor.extracted_data
            
            # Update result with extracted fields
            result.update(extracted_fields)
            
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
