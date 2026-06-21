import os
import json
import re
import hashlib
from typing import Dict, Any, List
from ocr.pdf_handler import PDFHandler
from ocr.preprocess_enhanced import EnhancedImagePreprocessor
from ocr.ocr_engine import CertificateOCREngine
from ocr.smart_extractor import SmartExtractor

class AcademicOCRPipeline:
    """
    Implements a robust PDF OCR Processing and Academic Field Extraction Engine.
    Specifically designed for scanned (image-based) multi-page academic dossiers.
    """
    
    def __init__(self, output_dir: str = "output/academic_records"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        self.pdf_handler = PDFHandler(os.path.join(output_dir, "pages"))
        self.preprocessor = EnhancedImagePreprocessor()
        self.ocr_engine = CertificateOCREngine()
        self.extractor = SmartExtractor()
        
    def _detect_certificate_type(self, text: str) -> str:
        """
        Categorizes page based on extracted OCR keywords.
        """
        text_upper = text.upper()
        
        # SSC/10th Logic
        if any(k in text_upper for k in ["SSC", "SECONDARY SCHOOL", "10TH", "X CLASS", "CLASS X", "BOARD OF SECONDARY EDUCATION"]):
            return "tenth_certificate"
            
        # Intermediate/12th Logic
        if any(k in text_upper for k in ["INTERMEDIATE", "BOARD OF INTERMEDIATE", "12TH", "XII CLASS", "CLASS XII", "HIGHER SECONDARY"]):
            return "intermediate_certificate"
            
        # Degree/University Logic
        if any(k in text_upper for k in ["BACHELOR", "UNIVERSITY", "DEGREE", "CONVOCATION", "PROVISIONAL CERTIFICATE", "B.TECH", "B.SC", "B.COM", "B.A"]):
            return "degree_certificate"
            
        return "unknown"

    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        Complete Pipeline: Split -> Convert -> Preprocess -> OCR -> Categorize -> Extract
        """
        # STEP 1: Split the uploaded PDF into individual pages
        pages = self.pdf_handler.split_and_convert(file_path)
        
        if not pages:
            return {"error": "Failed to process document pages."}
            
        final_result = {
            "tenth_certificate": {f: None for f in self.extractor.required_fields},
            "intermediate_certificate": {f: None for f in self.extractor.required_fields},
            "degree_certificate": {f: None for f in self.extractor.required_fields}
        }
        
        # STEP 2 & 3: Process each page independently
        for i, page_img in enumerate(pages):
            
            # Preprocessing (Step 2: Conversion to image at 300 DPI is done in pdf_handler)
            processed_img = self.preprocessor.preprocess(page_img, save_intermediate=True)
            
            if processed_img is None:
                continue
                
            # Perform OCR (Step 2: Grayscale/Thresholding done in preprocess)
            ocr_text = self.ocr_engine.perform_ocr(processed_img)
            
            if not ocr_text:
                continue
                
            # STEP 4: Detect certificate type
            cert_type = self._detect_certificate_type(ocr_text)
            
            if cert_type == "unknown":
                continue
                
            # STEP 5: Extract ONLY the requested fields
            structured_data = self.extractor.extract(ocr_text)
            
            # Map to final output
            if cert_type in final_result:
                # Merge logic: if multiple pages of same type, prioritize existing non-null values
                for field, value in structured_data.items():
                    if value and not final_result[cert_type][field]:
                        final_result[cert_type][field] = value
                        
        # STEP 5 & 6 & 7: Canonical structured format and hashing
        canonical_lines = []
        certs_order = [
            ("TENTH", "tenth_certificate"),
            ("INTERMEDIATE", "intermediate_certificate"),
            ("DEGREE", "degree_certificate")
        ]
        fields_order = [
            "certificate_id",
            "student_name",
            "roll_number",
            "year_of_passing",
            "course_or_degree",
            "university_or_board_name",
            "cgpa_or_percentage"
        ]
        
        for prefix, cert_key in certs_order:
            cert_data = final_result.get(cert_key, {})
            row = [prefix]
            for f in fields_order:
                val = cert_data.get(f)
                row.append(str(val) if val is not None else "null")
            canonical_lines.append("|".join(row))
            
        combined_string = "\n".join(canonical_lines)
        combined_hash = hashlib.sha256(combined_string.encode('utf-8')).hexdigest()
        
        output_payload = {
            "academic_record": {
                "tenth_certificate": final_result["tenth_certificate"],
                "intermediate_certificate": final_result["intermediate_certificate"],
                "degree_certificate": final_result["degree_certificate"]
            },
            "combined_hash": combined_hash
        }
                        
        # Save JSON output
        output_file = os.path.join(self.output_dir, "academic_extraction.json")
        with open(output_file, 'w') as f:
            json.dump(output_payload, f, indent=2)
            
        return output_payload

if __name__ == "__main__":
    # Test script usage
    import sys
    if len(sys.argv) > 1:
        pipeline = AcademicOCRPipeline()
        results = pipeline.process_document(sys.argv[1])
        print(json.dumps(results, indent=2))
