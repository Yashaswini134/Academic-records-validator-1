import re
from typing import Dict, List, Optional, Tuple
from ai.extract_fields_ai import AIExtractor

# Import backup extractor
try:
    from ocr.extract_fields_improved import ImprovedFieldExtractor
except ImportError:
    from ocr.extract_fields import FieldExtractor as ImprovedFieldExtractor

class AIFieldExtractor:
    """Wrapper class for AI-based extraction with Regex fallback"""
    
    def __init__(self):
        self.ai_engine = AIExtractor()
        self.regex_extractor = ImprovedFieldExtractor()
        self.extracted_data = {}
        self.errors = []
        self.confidence_scores = {}
        
    def extract_id_course(self, text: str):
        """Extract ID and Course using robust regex (AI is bad at random alphanumeric codes)"""
        # Certificate ID
        id_match = re.search(r'(?:Certificate|Cert|H\.?T|Hall\s+Ticket|CCF|EDP)\s*(?:No|Number|ID|S\.?\s*No)?\s*[:\-]?\s*([A-Z0-9\-\/:]{4,})', text, re.IGNORECASE)
        cert_id = id_match.group(1) if id_match else None
        
        if cert_id:
            # REMOVE CCF: prefix (User Request)
            cert_id = re.sub(r'^(CCF|EDP):?', '', cert_id, flags=re.IGNORECASE).strip()
        
        # Course (B.Tech, etc.)
        course_match = re.search(r'(B\.?Tech|M\.?Tech|Bachelor|Master|B\.?Sc\.?)\s*(?:of\s+[A-Za-z\s]+)?\s*(?:in\s+[A-Za-z\s]+)?', text, re.IGNORECASE)
        course = course_match.group(0) if course_match else None
        
        if course:
            # REMOVE PREFIX (User Request for PTU)
            course = re.sub(r'^Bachelor of Technology in\s+', '', course, flags=re.IGNORECASE).strip()
        
        return cert_id, course
        
    def extract_all_fields(self, ocr_text: str) -> Dict[str, Optional[str]]:
        """
        Use AI model + Regex + Traditional Fallback
        """
        print("\n" + "="*70)
        print("AI FIELD EXTRACTION (Hybrid: Deep Learning + Regex)")
        print("="*70)
        
        try:
            # 1. AI Prediction
            ai_results = self.ai_engine.predict_fields(ocr_text)
            
            # 2. Regex for Codes
            cert_id, course = self.extract_id_course(ocr_text)
            
            # 3. Traditional Fallback (if AI missed critical fields)
            regex_results = {}
            # If AI missed Name OR University, trust the regex extractor to backup
            if not ai_results.get('student_name') or not ai_results.get('university'):
                print("⚠ AI returned partial results. Triggering Regex Fallback...")
                regex_results = self.regex_extractor.extract_all_fields(ocr_text)
            
            # Merge Results (AI Priority > Regex > Fallback)
            self.extracted_data = {
                'student_name': ai_results.get('student_name') or regex_results.get('student_name'),
                'roll_number': ai_results.get('roll_number') or regex_results.get('roll_number'),
                'university': ai_results.get('university') or regex_results.get('university'),
                'year': ai_results.get('year') or regex_results.get('year'),
                'course': course or regex_results.get('course'),
                'certificate_id': cert_id or regex_results.get('certificate_id'),
                'cgpa': ai_results.get('cgpa') or regex_results.get('cgpa')
            }
            
            # Update scores logic
            for key, val in self.extracted_data.items():
                if val:
                    # If from AI, give 85. If from fallback, use fallback score.
                    if ai_results.get(key) == val:
                         self.confidence_scores[key] = 85
                    elif regex_results.get(key) == val:
                         self.confidence_scores[key] = self.regex_extractor.confidence_scores.get(key, 60)
                    else:
                         self.confidence_scores[key] = 90 # Regex code match
            
            # Print results
            print("\nFinal Hybrid Extraction Results:")
            for key, val in self.extracted_data.items():
                status = "✓" if val else "✗"
                print(f"  {status} {key}: {val if val else 'Not found'}")
                
            return self.extracted_data
            
        except Exception as e:
            print(f"Extraction failed: {e}")
            import traceback
            traceback.print_exc()
            self.errors.append(str(e))
            return {}

    def get_errors(self) -> List[str]:
        base_errors = self.errors
        if hasattr(self, 'regex_extractor'):
            base_errors.extend(self.regex_extractor.errors)
        return list(set(base_errors)) # Unique errors only

    def validate_fields(self) -> Tuple[bool, List[str]]:
        """Use regex extractor's validation if available"""
        if self.regex_extractor:
            # Sync data to regex extractor for validation logic
            self.regex_extractor.extracted_data = self.extracted_data
            self.regex_extractor.confidence_scores = self.confidence_scores
            return self.regex_extractor.validate_fields()
        
        # Simple fallback validation
        errors = []
        if not self.extracted_data.get('student_name'):
            errors.append("Student Name missing")
        return len(errors) == 0, errors
