import os
import json
from typing import Dict, Any, List
from ocr.pdf_handler import PDFHandler
from ocr.preprocess_enhanced import EnhancedImagePreprocessor
from ocr.ocr_engine import CertificateOCREngine
from ocr.smart_extractor import SmartExtractor

class StructuredOCRPipeline:
    """
    Implements the full multi-step OCR pipeline:
    PDF Upload -> Split Pages -> convert to Image -> Preprocess -> OCR -> Extraction Prompt -> JSON
    """
    
    def __init__(self, output_dir: str = "output/structured"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        self.pdf_handler = PDFHandler(os.path.join(output_dir, "pages"))
        self.preprocessor = EnhancedImagePreprocessor()
        # Initialize engine without path (will auto-detect)
        self.ocr_engine = CertificateOCREngine()
        self.extractor = SmartExtractor()
        
        # The prompt requested by the user
        self.extraction_prompt = """
You are a strict academic certificate field extractor.

Input:
OCR extracted raw text from one certificate page.

Task:
Extract structured fields.

Important Rules:
1. Extract only from visible text.
2. Do not infer.
3. If field not found, return null.
4. Look for alternative labels:
   - Roll No / Hall Ticket No / Registration No
   - Certificate No / Certificate ID
   - Year of Pass / Year of Passing
   - CGPA / TOTAL / PERCENTAGE
5. If TOTAL MARKS present, store as cgpa_or_percentage.
6. Preserve original case.
7. Output JSON only.

Required Fields:
- certificate_id
- student_name
- roll_number
- year_of_passing
- course_or_degree
- university_or_board_name
- cgpa_or_percentage
"""

    def process_document(self, file_path: str) -> Dict[str, Any]:
        """
        Run the complete pipeline on a PDF or Image.
        """
        print(f"\n[PIPELINE START] Processing: {file_path}")
        
        # 1 & 2. PDF Upload & Split into Pages
        pages = self.pdf_handler.split_and_convert(file_path)
        
        if not pages:
            return {"error": "Failed to split document into pages or no pages found."}
            
        all_results = []
        
        for i, page_img in enumerate(pages):
            print(f"\n--- Processing Page {i+1} ---")
            
            # 3. Convert Each Page to Image (Done by pdf_handler)
            
            # 4. Preprocess Image (resize, grayscale, etc.)
            # The preprocess method handles resize and grayscale
            processed_img = self.preprocessor.preprocess(page_img, save_intermediate=True)
            
            if processed_img is None:
                print(f"✗ Preprocessing failed for page {i+1}")
                continue
                
            # 5. Apply OCR
            ocr_text = self.ocr_engine.perform_ocr(processed_img)
            
            if not ocr_text:
                print(f"✗ OCR failed for page {i+1}")
                continue
                
            # 6. Send Clean Text to Extraction Prompt
            # In a real LLM scenario, we would call an API with self.extraction_prompt + ocr_text
            # Here, our SmartExtractor follows these exact rules.
            print(f"✓ Page {i+1} OCR Text Extracted ({len(ocr_text)} chars)")
            print("Applying strict extraction rules...")
            
            # 7. Structured JSON
            structured_data = self.extractor.extract(ocr_text)
            
            all_results.append({
                "page": i + 1,
                "data": structured_data
            })
            
        # Merge or select best result
        # For simplicity, we return all pages and a merged best-effort result
        merged_result = self._merge_results(all_results)
        
        final_output = {
            "success": True,
            "document": os.path.basename(file_path),
            "pages_processed": len(pages),
            "extraction_results": all_results,
            "best_match": merged_result
        }
        
        # Save to output folder
        output_file = os.path.join(self.output_dir, "final_extraction.json")
        with open(output_file, 'w') as f:
            json.dump(final_output, f, indent=2)
            
        return final_output

    def _merge_results(self, results: List[Dict]) -> Dict:
        """Merge data from multiple pages into one best result."""
        merged = {field: None for field in self.extractor.required_fields}
        
        for res in results:
            page_data = res["data"]
            for field in merged:
                if not merged[field] and page_data.get(field):
                    merged[field] = page_data[field]
                    
        return merged

if __name__ == "__main__":
    # Test script
    import sys
    if len(sys.argv) > 1:
        pipeline = StructuredOCRPipeline()
        results = pipeline.process_document(sys.argv[1])
        print(json.dumps(results, indent=2))
    else:
        print("Usage: python ocr/structured_pipeline.py <path_to_pdf_or_image>")
