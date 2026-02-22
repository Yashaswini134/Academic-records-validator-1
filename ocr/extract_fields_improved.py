"""
Improved Field Extraction Module for Certificate OCR
Enhanced with multi-pass extraction, confidence scoring, and better patterns
"""

import re
import difflib
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from ocr.layout_engine import LayoutOCREngine

class ImprovedFieldExtractor:
    """Enhanced field extractor with multi-pass extraction and confidence scoring"""
    
    def __init__(self):
        self.raw_text = ""
        self.cleaned_text = ""
        self.extracted_data = {}
        self.confidence_scores = {}
        self.errors = []
        self.layout_engine = LayoutOCREngine()
        self.layout_data = None  # To store layout analysis result
        
    def set_layout_data(self, layout_data: List[Dict[str, Any]]):
        """Set layout data for spatial extraction"""
        self.layout_data = layout_data
        
    def extract_from_layout(self):
        """Attempt to extract missing fields using layout analysis"""
        if not self.layout_data:
            return

        print("\n[Layout-Aware Extraction Fallback]")
        
        # 1. Student Name (Right of "Name", "Student Name", etc.)
        if not self.extracted_data.get('student_name'):
            name = self.layout_engine.find_text_right_of(self.layout_data, ["Name", "Student"], x_margin=300)
            if name and len(name) > 3:
                print(f"✓ Found Name via Layout: {name}")
                self.extracted_data['student_name'] = name
                self.confidence_scores['student_name'] = 70

        # 2. Roll Number (Right of "Roll No", "H.T No", etc.)
        if not self.extracted_data.get('roll_number'):
            roll = self.layout_engine.find_text_right_of(self.layout_data, ["Roll", "Reg", "H.T", "Hall"], x_margin=150)
            if roll and len(roll) > 5:
                print(f"✓ Found Roll No via Layout: {roll}")
                self.extracted_data['roll_number'] = roll
                self.confidence_scores['roll_number'] = 75

        # 3. College (Below "College", "Institute", etc.)
        if not self.extracted_data.get('university'):
            college = self.layout_engine.find_text_below(self.layout_data, ["College", "Institute", "University"], y_search_limit=100)
            if college and len(college) > 5:
                 print(f"✓ Found College via Layout (Below header): {college}")
                 self.extracted_data['university'] = college
                 self.confidence_scores['university'] = 65
    
    def set_text(self, text: str):
        """Set the OCR text to extract from"""
        self.raw_text = text
        self.cleaned_text = self.clean_text(text)
        self.extracted_data = {}
        self.confidence_scores = {}
        self.errors = []
    
    def clean_text(self, text: str) -> str:
        """Advanced text cleaning and normalization"""
        # Normalize newlines and spaces
        text = text.replace('\r', '\n')
        
        # Fix common OCR errors
        text = text.replace('|', 'I')  # Pipe to I
        # DO NOT globally replace '0' -> 'O' because it breaks IDs, years, and roll numbers.
        # If needed, handle character confusion in field-specific extraction.
        text = re.sub(r'[`\']', '', text)  # Remove backticks and quotes
        
        # Collapse multiple spaces/tabs
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Normalize multiple newlines
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        
        # Remove special characters that interfere with extraction
        text = re.sub(r'[•●○◦▪▫]', '', text)  # Remove bullet points
        
        return text.strip()
    
    def extract_with_confidence(self, patterns: List[Tuple[str, int]], field_name: str) -> Optional[str]:
        """
        Extract field using multiple patterns with confidence scoring
        
        Args:
            patterns: List of (pattern, confidence_score) tuples
            field_name: Name of the field being extracted
            
        Returns:
            Extracted value or None
        """
        best_match = None
        best_confidence = 0
        
        for pattern, confidence in patterns:
            try:
                match = re.search(pattern, self.cleaned_text, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = match.group(1).strip()
                    if value and confidence > best_confidence:
                        best_match = value
                        best_confidence = confidence
            except Exception as e:
                continue
        
        if best_match:
            self.confidence_scores[field_name] = best_confidence
            return best_match
        return None
    
    def extract_certificate_id(self) -> Optional[str]:
        """Extract certificate ID with improved patterns"""
        print("\n[Extracting Certificate ID]")
        
        # Patterns ordered by confidence (high to low)
        patterns = [
            # JNTUH Specific: PC No found in debug text (PC No 25046704834)
            (r'PC\s*No\.?\s*[:\-]?\s*([0-9]{8,})', 100),
            
            # Explicit labels (high confidence)
            (r'Certificate\s+(?:No|Number|ID)\s*[:\-]?\s*([A-Z0-9\-\/]+)', 90),
            (r'Cert\s*(?:No|ID)\s*[:\-]?\s*([A-Z0-9\-\/]+)', 85),
            
            # JNTUH specific patterns
            (r'H\.?T\.?\s*No\.?\s*[:\-]?\s*([A-Z0-9]{10,})', 95),
            (r'Hall\s+Ticket\s+(?:No|Number)\s*[:\-]?\s*([A-Z0-9]{10,})', 95),
            (r'TG\s+(\d{7})', 90),
            
            # Registration/Serial patterns
            (r'EDP\s*S\.?\s*No\.?\s*[:\-]?\s*([0-9]{5,})', 100),
            (r'Registration\s+(?:No|Number)\s*[:\-]?\s*([A-Z0-9\-\/]+)', 85),
            (r'Serial\s+(?:No|Number)\s*[:\-]?\s*([A-Z0-9\-\/]+)', 80),
            
            # Generic patterns (lower confidence)
            (r'\b([A-Z]{2,4}[\-\/]\d{4}[\-\/][A-Z0-9]+)\b', 70),
            (r'\b(\d{10,12})\b', 60),  # 10-12 digit number (matches PC No without label)
        ]
        
        cert_id = self.extract_with_confidence(patterns, 'certificate_id')
        
        if cert_id:
            # Clean up the ID
            cert_id = re.sub(r'\s+', '', cert_id)
            
            # REMOVE CCF: prefix (User Request)
            cert_id = re.sub(r'^CCF:', '', cert_id, flags=re.IGNORECASE)
            
            # Validate minimum length
            if len(cert_id) >= 4:
                print(f"✓ Certificate ID found: {cert_id} (confidence: {self.confidence_scores.get('certificate_id', 0)}%)")
                return cert_id
        
        self.errors.append("Certificate ID not found")
        print("✗ Certificate ID not found")
        return None
    
    def extract_student_name(self) -> Optional[str]:
        """Extract student name with context-aware validation"""
        print("\n[Extracting Student Name]")
        
        patterns = [
            # Explicit "certify that" patterns (high confidence)
            (r'(?:This is to )?certify that\s+(?:Mr\.?|Ms\.?|Miss\.?)?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', 95),
            (r'(?:This is to )?certify that\s+([A-Z]+(?:\s+[A-Z]+)+)', 90),
            
            # Name label patterns
            (r'(?:Student|Candidate)\s+Name\s*[:\-]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', 90),
            (r'(?:Student|Candidate)\s+Name\s*[:\-]?\s*([A-Z]+(?:\s+[A-Z]+)+)', 85),
            
            # Name near "fulfilled" (Contextual - Very likely for JNTUH)
            # Looks for uppercase words before "having fulfilled"
            (r'([A-Z\s]{5,30})\s+having fulfilled', 85),
             # Looks for uppercase words before "has been admitted"
            (r'([A-Z\s]{5,30})\s+has been admitted', 85),
            
            # Mr/Ms patterns
            (r'(?:Mr\.?|Ms\.?|Miss\.?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', 85),
            
            # S/o D/o patterns (JNTUH specific)
            (r'([A-Z\s]+)\s+S/o', 90),
            (r'([A-Z\s]+)\s+D/o', 90),
        ]
        
        name = self.extract_with_confidence(patterns, 'student_name')
        
        # AGGRESSIVE FALLBACK: Look for likely name lines
        if not name:
            print("⚠ Strict name not found. Trying aggressive fallback...")
            lines = self.cleaned_text.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                # Skip short lines or lines with numbers
                if len(line) < 5 or any(c.isdigit() for c in line):
                    continue
                
                # Check if line is ALL CAPS (common for names)
                if line.isupper() and len(line.split()) >= 2 and len(line.split()) <= 4:
                     # Check against common keywords to avoid false positives
                     keywords = ['BACHELOR', 'MASTER', 'COLLEGE', 'UNIVERSITY', 'TECHNOLOGY', 'ENGINEERING', 'CERTIFICATE', 'INSTITUTE']
                     if not any(k in line for k in keywords):
                         name = line
                         self.confidence_scores['student_name'] = 50
                         break

        if name:
            # Clean and validate
            name = re.sub(r'\s+', ' ', name).strip()
            # Remove common prefixes/suffixes
            name = re.sub(r'^(Mr\.|Ms\.|Mrs\.|Miss)\s+', '', name, flags=re.IGNORECASE)
            
            if len(name) > 3:
                # Convert to title case for consistency
                name = name.title()
                print(f"✓ Student Name found: {name} (confidence: {self.confidence_scores.get('student_name', 0)}%)")
                return name
        
        self.errors.append("Student name not found")
        print("✗ Student name not found")
        return None
    
    def extract_roll_number(self) -> Optional[str]:
        """Extract roll/registration number (including Hall Ticket No)"""
        print("\n[Extracting Roll Number]")
        
        patterns = [
            # Hall Ticket Number (Specific request: Roll No = Hall Ticket No)
            (r'H\.?T\.?\s*No\.?\s*[:\-]?\s*([A-Z0-9]{10,})', 100),
            (r'Hall\s+Ticket\s+(?:No|Number)\s*[:\-]?\s*([A-Z0-9]{10,})', 100),
            
            # Generic HT pattern for noisy text (matches 10 alphanumeric chars starting with digit or letter)
            (r'\b(\d{2}[A-Z0-9]{8})\b', 90), 
            
            # Explicit labels
            (r'Roll\s+(?:No|Number)\s*[:\-]?\s*([A-Z0-9\-\/]+)', 95),
            (r'Registration\s+(?:No|Number)\s*[:\-]?\s*([A-Z0-9\-\/]+)', 90),
            (r'Reg\.?\s+(?:No|Number)\s*[:\-]?\s*([A-Z0-9\-\/]+)', 90),
            (r'Student\s+ID\s*[:\-]?\s*([A-Z0-9\-\/]+)', 85),
        ]
        
        roll_no = self.extract_with_confidence(patterns, 'roll_number')
        
        # AGGRESSIVE FALLBACK
        if not roll_no:
             print("⚠ Strict roll number not found. Trying fallback...")
             # Look for typical 10-char JNTUH ID format: 2 digits + 2 chars + 2 digits + ...
             match = re.search(r'\b(\d{2}[A-Z][A-Z0-9]\d{2}[A-Z0-9]{4})\b', self.cleaned_text)
             if match:
                 roll_no = match.group(1)
                 self.confidence_scores['roll_number'] = 60
        
        if roll_no:
            roll_no = re.sub(r'\s+', '', roll_no)
            if len(roll_no) >= 4:
                print(f"✓ Roll Number found: {roll_no}")
                return roll_no
        
        # Try finding certificate ID as backup
        if self.extracted_data.get('certificate_id'):
            print("ℹ Using Certificate ID as Roll Number fallback")
            return self.extracted_data.get('certificate_id')
            
        print("✗ Roll number not found")
        return None

    def extract_student_name(self) -> Optional[str]:
        """Extract full student name"""
        print("\n[Extracting Student Name]")
        
        # Regex to capture 2-5 words, allowing for dots (e.g., K. P. Singh)
        name_regex = r'([A-Z][a-z\.]+(?:\s+[A-Z][a-z\.]+){1,5})'
        caps_regex = r'([A-Z\.]+(?:\s+[A-Z\.]+){1,5})'
        
        patterns = [
            # Explicit "certify that" patterns
            (r'(?:This is to )?certify that\s+(?:Mr\.?|Ms\.?|Miss\.?)?\s*' + name_regex, 95),
            (r'(?:This is to )?certify that\s+' + caps_regex, 90),
            
            # Name label
            (r'Name\s*[:\-]?\s*' + name_regex, 90),
            (r'Name\s*[:\-]?\s*' + caps_regex, 85),
            
            # Mr/Ms patterns
            (r'(?:Mr\.?|Ms\.?|Miss\.?)\s+' + name_regex, 85),
            
            # S/o D/o patterns (Capture the name BEFORE S/o)
            (r'([A-Z][a-z\.]+(?:\s+[A-Z][a-z\.]+){1,5})\s+(?:S/o|D/o|W/o)', 95),
            
            # JNTUH specific layout: Name is often on a line by itself or after "Mr."
            # We look for the line ABOVE "S/o" or "D/o"
            # (Handled by multiline scan below)
        ]
        
        name = self.extract_with_confidence(patterns, 'student_name')
        
        # AGGRESSIVE FALLBACK: Look for name line relative to S/o
        if not name:
            lines = self.cleaned_text.splitlines()
            for i, line in enumerate(lines):
                if "S/o" in line or "D/o" in line or "S/O" in line or "D/O" in line:
                    # Check the CURRENT line for text before S/o
                    parts = re.split(r'S/o|D/o|S/O|D/O', line)
                    if len(parts) > 0 and len(parts[0].strip()) > 5:
                        candidate = parts[0].strip()
                        # Remove Mr/Ms
                        candidate = re.sub(r'^(Mr|Ms|Mrs)\.?\s*', '', candidate, flags=re.IGNORECASE)
                        print(f"✓ Found name before S/o on same line: {candidate}")
                        return candidate
                    
                    # Check the PREVIOUS line
                    if i > 0:
                        prev = lines[i-1].strip()
                        if len(prev.split()) >= 2 and len(prev) < 50:
                             # Remove Mr/Ms
                            prev = re.sub(r'^(Mr|Ms|Mrs)\.?\s*', '', prev, flags=re.IGNORECASE)
                            print(f"✓ Found name on line before S/o: {prev}")
                            return prev

        if name:
             # Cleanup
            name = re.sub(r'^(Mr|Ms|Mrs)\.?\s*', '', name, flags=re.IGNORECASE)
            return name.strip()

        print("✗ Student name not found")
        return None

    def _smart_correct(self, text: str, candidates: List[str], cutoff: float = 0.6) -> Optional[str]:
        """Use difflib to find the best match from a list of known valid strings."""
        if not text:
            return None
        matches = difflib.get_close_matches(text, candidates, n=1, cutoff=cutoff)
        if matches:
            return matches[0]
        return None

    def extract_university(self) -> Optional[str]:
        """Extract full university/college name with smart correction"""
        print("\n[Extracting University]")
        
        # known_universities = [
        #     "JAWAHARLAL NEHRU TECHNOLOGICAL UNIVERSITY HYDERABAD",
        #     "Jawaharlal Nehru Technological University",
        #     "G.B. Institute of Engineering & Technology",
        #     "BNAA Institute of Technology",
        #     "Vardhaman College of Engineering",
        #     "C.B. Institute of Technology",
        #     "Malla Reddy Engineering College",
        #     "Hyderabad Institute of Technology and Management"
        # ]
        
        # 1. JNTUH Specific Check (Highest Priority)
        # Look for partial matches of "Jawaharlal Nehru Technological University" because usually OCR gets parts of it right
        # e.g., "JAWAHARLAL NEHRU TECHNOLOGICAL" or "JAWAHARLAL NEHRU"
        keyword_score = 0
        if "JAWAHARLAL" in self.cleaned_text.upper(): keyword_score += 1
        if "NEHRU" in self.cleaned_text.upper(): keyword_score += 1
        if "TECHNOLOGICAL" in self.cleaned_text.upper(): keyword_score += 1
        if "UNIVERSITY" in self.cleaned_text.upper(): keyword_score += 1
        
        if keyword_score >= 2:
            print("✓ Detected JNTUH Context (2+ keywords found). Forcing JNTUH Name.")
            # We assume it's JNTUH if we see these words
            return "JAWAHARLAL NEHRU TECHNOLOGICAL UNIVERSITY HYDERABAD"

        # 2. Extract Generic University/College Name
        patterns = [
            # "College:" label - Capture everything after until end of line
            (r'College\s*[:\-]\s*([A-Za-z\s&,\.\-]+)', 90),
            
            # Capture full line if it contains "College" or "Institute"
            (r'^.*?(?:College|Institute|University).*?$', 60) 
        ]
        
        uni_name = self.extract_with_confidence(patterns, 'university')
        
        # Smart Correct against known list? (Can add later if needed)
        
        if uni_name:
             # Basic cleanup
             uni_name = re.sub(r'^(College|Institute|University)\s*[:\-]\s*', '', uni_name, flags=re.IGNORECASE)
             print(f"✓ University/College found: {uni_name}")
             return uni_name.strip()

        # AGGRESSIVE LINE SCAN (Primary method for this request)
        # Scan for lines with keywords and take the *entire* line or relevant part
        keywords = ['UNIVERSITY', 'INSTITUTE', 'COLLEGE', 'VIDYALAYA', 'ACADEMY']
        
        for line in self.cleaned_text.splitlines():
            line = line.strip()
            upper_line = line.upper()
            
            if any(k in upper_line for k in keywords):
                # Filter out obvious labels/sentences
                if "CERTIFY" in upper_line or "RECOGNIZED" in upper_line or len(line) < 10:
                    continue
                
                # If it starts with "College:" or similar, assume the name is the whole thing
                # But remove the label if present
                clean_line = re.sub(r'^(College|Institute|University)\s*[:\-]\s*', '', line, flags=re.IGNORECASE)
                
                print(f"✓ Found university/college line via scan: {clean_line}")
                return clean_line

        return None
    
    def extract_course(self) -> Optional[str]:
        """Extract course/degree with fuzzy matching support"""
        print("\n[Extracting Course]")
        
        patterns = [
            (r'Degree\s+of\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', 95),
            (r'Degree\s+of\s+([A-Z\s]+)', 90),
            (r'in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\s+Branch', 85),
            (r'Stream\s*[:\-]?\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', 85),
             # JNTUH specific
            (r'to\s+the\s+Degree\s+of\s+(.+?)(?:\s+in\s+|$)', 85),
             # Look for "Bachelor of Technology" specifically
            (r'(Bachelor\s+of\s+Technology)', 95),
            (r'(Master\s+of\s+Technology)', 95),
            (r'(B\.?Tech|M\.?Tech|B\.?E|M\.?E)', 90)
        ]
        
        course = self.extract_with_confidence(patterns, 'course')
        
        # FUZZY MATCHING for bad OCR (e.g., "Budkebrof Telroloy")
        if not course:
            print("⚠ Strict course not found. Applying fuzzy matching...")
            # Check for corrupted version of "Bachelor of Technology"
            # Matches words starting with B... of T...
            match = re.search(r'\b(B\w+\s+of\s+T\w+)\b', self.cleaned_text, re.IGNORECASE)
            if match:
                print(f"✓ Fuzzy matched '{match.group(1)}' -> 'Bachelor of Technology'")
                return "Bachelor of Technology"
                
            # Check for "Master of Technology" variants
            match = re.search(r'\b(M\w+\s+of\s+T\w+)\b', self.cleaned_text, re.IGNORECASE)
            if match:
                print(f"✓ Fuzzy matched '{match.group(1)}' -> 'Master of Technology'")
                return "Master of Technology"

        if course:
            # Clean up
            course = re.sub(r'\s+', ' ', course).strip()
            
            # REMOVE PREFIX (User Request for PTU)
            course = re.sub(r'^Bachelor of Technology in\s+', '', course, flags=re.IGNORECASE)
            
            print(f"✓ Course found: {course}")
            return course
            
        self.errors.append("Course/Degree not found")
        return None

    def extract_year(self) -> Optional[str]:
        """Extract year of passing or issue"""
        print("\n[Extracting Year]")
        
        patterns = [
            (r'Year\s+of\s+Passing\s*[:\-]?\s*([A-Z]+\s+\d{4})', 95), # Month Year
            (r'Year\s+of\s+Passing\s*[:\-]?\s*(\d{4})', 90),
            (r'Passed\s+in\s+([A-Z]+\s+\d{4})', 85),
            
            # Bottom date pattern (JNTUH)
            (r'Date\s*[:\-]?\s*(\d{2}[\-\/]\d{2}[\-\/]\d{4})', 90),
            (r'Given\s+under\s+the\s+Seal.*Date\s*[:\-]?\s*(\d{2}[\-\/]\d{2}[\-\/]\d{4})', 95),
            
            # Look for month and year at the end
            (r'\b((?:JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)[A-Z]*\s+\d{4})\b', 70),
        ]
        
        year = self.extract_with_confidence(patterns, 'year')
        
        if year:
            print(f"✓ Year found: {year}")
            return year
            
        if year:
            print(f"✓ Year found: {year}")
            return year
            
        self.errors.append("Year of passing not found")
        return None
        
        specialization_patterns = [
            (r'(Computer\s+Science\s*(?:&|and)?\s*Engineering)', 95),
            (r'(Information\s+Technology)', 95),
            (r'(Mechanical\s+Engineering)', 95),
            (r'(Civil\s+Engineering)', 95),
            (r'(Electrical\s*(?:&|and)?\s*Electronics\s+Engineering)', 95),
            (r'(Electronics\s*(?:&|and)?\s*Communication\s+Engineering)', 95),
            (r'(Chemical\s+Engineering)', 95),
            (r'(Biotechnology)', 95),
        ]
        
        degree = self.extract_with_confidence(degree_patterns, 'degree')
        specialization = self.extract_with_confidence(specialization_patterns, 'specialization')
        
        # Combine degree and specialization
        if degree and specialization:
            course = f"{degree} in {specialization}"
            self.confidence_scores['course'] = min(
                self.confidence_scores.get('degree', 0),
                self.confidence_scores.get('specialization', 0)
            )
        elif degree:
            course = degree
            self.confidence_scores['course'] = self.confidence_scores.get('degree', 0)
        elif specialization:
            course = specialization
            self.confidence_scores['course'] = self.confidence_scores.get('specialization', 0)
        else:
            # Try combined patterns
            combined_patterns = [
                (r'Course\s*[:\-]?\s*([A-Za-z\s&,\.]+?)(?:\s+from|\s+at|\s+in\s+the\s+year|\n)', 80),
                (r'(Bachelor\s+of\s+[A-Za-z\s&,]+?)\s+(?:from|at|in)', 75),
                (r'(Master\s+of\s+[A-Za-z\s&,]+?)\s+(?:from|at|in)', 75),
            ]
            course = self.extract_with_confidence(combined_patterns, 'course')
        
        if course:
            course = re.sub(r'\s+', ' ', course).strip()
            if len(course) >= 3:
                print(f"✓ Course found: {course} (confidence: {self.confidence_scores.get('course', 0)}%)")
                return course
        
        self.errors.append("Course/Degree not found")
        print("✗ Course/Degree not found")
        return None
    
    def extract_university(self) -> Optional[str]:
        """Extract university name with better validation"""
        print("\n[Extracting University]")
        
        patterns = [
            # JNTUH specific (high confidence)
            (r'(JAWAHARLAL\s+NEHRU\s+TECHNOLOGICAL\s+UNIVERSITY\s+HYDERABAD)', 100),
            (r'(JNTUH)', 95),
            (r'(JAWAHARLAL\s+NEHRU\s+[A-Z\s]+UNIVERSITY)', 95),
            
            # Explicit "from" patterns
            (r'from\s+([A-Z]+(?:\s+[A-Z]+)*\s+(?:UNIVERSITY|INSTITUTE|COLLEGE)(?:\s+OF\s+[A-Z]+(?:\s+[A-Z]+)*)?)', 90),
            (r'from\s+the\s+([A-Z]+(?:\s+[A-Z]+)*\s+(?:UNIVERSITY|INSTITUTE|COLLEGE))', 90),
            
            # University/Institute/College patterns
            (r'([A-Z]+(?:\s+[A-Z]+)*\s+UNIVERSITY(?:\s+OF\s+[A-Z]+(?:\s+[A-Z]+)*)?)', 85),
            (r'([A-Z]+(?:\s+[A-Z]+)*\s+INSTITUTE\s+OF\s+[A-Z]+(?:\s+[A-Z]+)*)', 85),
            (r'([A-Z]+(?:\s+[A-Z]+)*\s+COLLEGE)', 80),
            
            # Title case patterns (lower confidence)
            (r'from\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:University|Institute|College))', 75),
            (r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+University)', 70),
        ]
        
        university = self.extract_with_confidence(patterns, 'university')
        
        # AGGRESSIVE FALLBACK: Scan line by line for keywords
        if not university:
            print("⚠ Strict university not found. Trying aggressive fallback...")
            keywords = ['UNIVERSITY', 'INSTITUTE', 'COLLEGE', 'VIDYALAYA', 'ACADEMY']
            
            # Iterate through lines
            for line in self.cleaned_text.splitlines():
                line = line.strip()
                upper_line = line.upper()
                
                # If line contains a keyword and is decently long but not a sentence
                if any(k in upper_line for k in keywords) and len(line) > 10 and len(line) < 100:
                    # Avoid lines that are likely just labels or sentences
                    if "CERTIFY" in upper_line or "RECARD" in upper_line:
                        continue
                        
                    print(f"✓ Found university via keyword scan: {line}")
                    self.confidence_scores['university'] = 60
                    return line

        if university:
            university = re.sub(r'\s+', ' ', university).strip()
            
            # REMOVE AFFILIATION SUFFIXES (User Request)
            university = re.sub(r'\(Affiliated to JNTUH\)', '', university, flags=re.IGNORECASE)
            university = re.sub(r'\(affiliated By JNTUH\)', '', university, flags=re.IGNORECASE)
            university = re.sub(r'\(Affiliated to University of Mumbai\)', '', university, flags=re.IGNORECASE)
            university = university.strip()
            
            # Validate it contains institution keywords
            institution_keywords = ['UNIVERSITY', 'INSTITUTE', 'COLLEGE', 'JNTUH']
            if any(keyword in university.upper() for keyword in institution_keywords):
                if len(university) >= 5:
                    print(f"✓ University found: {university} (confidence: {self.confidence_scores.get('university', 0)}%)")
                    return university
        
        self.errors.append("University name not found")
        print("✗ University name not found")
        return None
    
    def extract_year(self) -> Optional[str]:
        """Extract year of passing with validation"""
        print("\n[Extracting Year]")
        
        current_year = datetime.now().year
        
        patterns = [
            # Explicit year labels
            (r'Year\s+of\s+Passing\s*[:\-]?\s*(\d{4})', 95),
            (r'Year\s*[:\-]?\s*(\d{4})', 90),
            (r'Passed\s+in\s+(\d{4})', 90),
            (r'Completed\s+in\s+(\d{4})', 90),
            
            # Month + Year patterns (JNTUH)
            (r'(?:April|May|June|July|August|September|October|November|December|January|February|March)\s*[\-,]?\s*(\d{4})', 85),
            
            # Academic year patterns
            (r'Academic\s+Year\s*[:\-]?\s*(\d{4})', 85),
            
            # Generic 4-digit year
            (r'\b(20\d{2})\b', 60),
            (r'\b(19\d{2})\b', 50),
        ]
        
        # Extract all potential years
        potential_years = []
        for pattern, confidence in patterns:
            matches = re.findall(pattern, self.cleaned_text, re.IGNORECASE)
            for year_str in matches:
                try:
                    year = int(year_str)
                    if 1950 <= year <= current_year + 1:
                        potential_years.append((year, confidence))
                except ValueError:
                    continue
        
        # Select the most recent valid year with highest confidence
        if potential_years:
            # Sort by confidence first, then by year (most recent)
            potential_years.sort(key=lambda x: (x[1], x[0]), reverse=True)
            year = str(potential_years[0][0])
            self.confidence_scores['year'] = potential_years[0][1]
            print(f"✓ Year found: {year} (confidence: {self.confidence_scores.get('year', 0)}%)")
            return year
        
        self.errors.append("Year of passing not found")
        print("✗ Year of passing not found")
        return None
        
    def extract_cgpa(self) -> Optional[str]:
        """Extract CGPA/GPA/Percentage/Marks"""
        print("\n[Extracting CGPA/Marks]")
        
        patterns = [
            # Explicit labels
            (r'(?:CGPA|GPA|Grade Point|Cumulative Grade)\s*[:\-]?\s*(\d+\.?\d*)', 95),
            (r'(?:Grade|CGPA|GPA)\s*[:\-]?\s*(\d+\.?\d*)\s*[/]\s*(?:10|4)\.?0?', 90),
            (r'(\d+\.?\d*)\s*(?:CGPA|GPA|Grade Point)', 85),
            
            # Percentage
            (r'(?:Percentage|Marks|Score)\s*[:\-]?\s*(\d+\.?\d*)\s*%', 90),
            (r'Grade\s+with\s*(\d+\.?\d*)\s*(?:CGPA|GPA)', 95), # Pillai Format
            
            # Generic decimal 0.00 to 10.00 with context
            (r'\b([0-9]\.\d{1,2})\b', 50) 
        ]
        
        cgpa = self.extract_with_confidence(patterns, 'cgpa')
        
        if cgpa:
            # Clean up
            cgpa = cgpa.strip()
            print(f"✓ CGPA/Marks found: {cgpa} (confidence: {self.confidence_scores.get('cgpa', 0)}%)")
            return cgpa
            
        print("✗ CGPA/Marks not found")
        return None
    
    
    def extract_all_fields(self, ocr_text: str) -> Dict[str, Optional[str]]:
        """
        Extract all fields from OCR text with improved accuracy
        
        Args:
            ocr_text: Raw text from OCR
            
        Returns:
            Dictionary with extracted fields
        """
        print("\n" + "="*70)
        print("IMPROVED FIELD EXTRACTION")
        print("="*70)
        
        # Set and clean text
        self.set_text(ocr_text)
        
        # Debug: Show cleaned text
        print("\n" + "-"*70)
        print("CLEANED TEXT (First 400 characters):")
        print("-"*70)
        print(self.cleaned_text[:400] if len(self.cleaned_text) > 400 else self.cleaned_text)
        print("-"*70 + "\n")
        
        # Extract all fields
        print("Extracting individual fields...")
        self.extracted_data = {
            'certificate_id': self.extract_certificate_id(),
            'student_name': self.extract_student_name(),
            'roll_number': self.extract_roll_number(),
            'course': self.extract_course(),
            'university': self.extract_university(),
            'year': self.extract_year(),
            'cgpa': self.extract_cgpa(),
        }

        # Template-aware post-processing for your real certificate layouts
        self._postprocess_jntuh_degree()
        self._postprocess_vtu_gradecard()
        self._postprocess_shankara_project()
        
        # Show extraction summary
        print("\n" + "-"*70)
        print("EXTRACTION SUMMARY:")
        print("-"*70)
        for key, value in self.extracted_data.items():
            status = "✓" if value else "✗"
            confidence = self.confidence_scores.get(key, 0)
            conf_str = f"[{confidence}%]" if value else ""
            print(f"  {status} {key}: {value if value else 'NOT FOUND'} {conf_str}")
        print("-"*70)
        
        # Calculate overall confidence
        if self.confidence_scores:
            avg_confidence = sum(self.confidence_scores.values()) / len(self.confidence_scores)
            print(f"\nOverall Confidence: {avg_confidence:.1f}%")
        
        print("\n" + "="*70)
        print("FIELD EXTRACTION COMPLETE")
        print("="*70 + "\n")
        
        return self.extracted_data

    # ------------------------------------------------------------------
    # Template-specific helpers for certificates you provided
    # ------------------------------------------------------------------

    def _postprocess_jntuh_degree(self) -> None:
        text = self.cleaned_text or ""
        upper = text.upper()
        if "JAWAHARLAL NEHRU TECHNOLOGICAL UNIVERSITY" not in upper:
            return

        # TG number as certificate ID
        if not self.extracted_data.get("certificate_id"):
            m = re.search(r"\bTG\s*([0-9]{5,})\b", text, re.IGNORECASE)
            if m:
                self.extracted_data["certificate_id"] = m.group(1).strip()
                self.confidence_scores["certificate_id"] = max(self.confidence_scores.get("certificate_id", 0), 85)

        # H.T. No as roll number
        if not self.extracted_data.get("roll_number"):
            m = re.search(r"H\.?\s*T\.?\s*No\.?\s*[:\-]?\s*([A-Z0-9]{8,})", text, re.IGNORECASE)
            if m:
                self.extracted_data["roll_number"] = m.group(1).strip()
                self.confidence_scores["roll_number"] = max(self.confidence_scores.get("roll_number", 0), 85)

        # Name from Mr./Ms.
        if not self.extracted_data.get("student_name"):
            m = re.search(r"\bMr\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b", text, re.IGNORECASE)
            if not m:
                m = re.search(r"\bMs\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)\b", text, re.IGNORECASE)
            if m:
                name = re.sub(r"\s+", " ", m.group(1).strip())
                self.extracted_data["student_name"] = name
                self.confidence_scores["student_name"] = max(self.confidence_scores.get("student_name", 0), 75)

        # Course from B.Tech + CSE
        if not self.extracted_data.get("course"):
            deg = re.search(r"(Bachelor\s+of\s+Technology)", text, re.IGNORECASE)
            spec = re.search(r"(Computer\s+Science\s*&?\s*Engineering)", text, re.IGNORECASE)
            if deg and spec:
                course = f"{deg.group(1).strip()} in {spec.group(1).strip()}"
                self.extracted_data["course"] = re.sub(r"\s+", " ", course)
                self.confidence_scores["course"] = max(self.confidence_scores.get("course", 0), 70)

        # Year from "April - 2023"
        if not self.extracted_data.get("year"):
            m = re.search(r"April\s*[-–]?\s*(\d{4})", text, re.IGNORECASE)
            if m:
                self.extracted_data["year"] = m.group(1)
                self.confidence_scores["year"] = max(self.confidence_scores.get("year", 0), 70)

        # University header
        if not self.extracted_data.get("university"):
            m = re.search(r"(JAWAHARLAL\s+NEHRU\s+TECHNOLOGICAL\s+UNIVERSITY\s+HYDERABAD)", text, re.IGNORECASE)
            if m:
                self.extracted_data["university"] = re.sub(r"\s+", " ", m.group(1).title())
                self.confidence_scores["university"] = max(self.confidence_scores.get("university", 0), 80)

    def _postprocess_vtu_gradecard(self) -> None:
        text = self.cleaned_text or ""
        upper = text.upper()

        # Be tolerant: OCR corrupts VISVESVARAYA but usually keeps "TECHNOLOGICAL UNIVER..."
        if "TECHNOLOGICAL UNIVER" not in upper:
            return

        # USN heuristic: either labeled USN or first 8-12 alnum token with digits
        if not self.extracted_data.get("roll_number"):
            m = re.search(r"\bUSN[:\s]+([A-Z0-9]+)\b", text, re.IGNORECASE)
            if m:
                usn = m.group(1).strip()
                self.extracted_data["roll_number"] = usn
                self.confidence_scores["roll_number"] = max(self.confidence_scores.get("roll_number", 0), 80)
            else:
                candidates = re.findall(r"\b[A-Za-z0-9]{8,12}\b", text)
                candidates = [c for c in candidates if any(ch.isdigit() for ch in c)]
                if candidates:
                    self.extracted_data["roll_number"] = candidates[0]
                    self.confidence_scores["roll_number"] = max(self.confidence_scores.get("roll_number", 0), 45)

        # Student name heuristic: ALL-CAPS-ish token before institute line
        if not self.extracted_data.get("student_name"):
            m = re.search(r"\b([A-Z]{3,}\s+[A-Z])\b.*INSTITUTE OF TECHNOLOGY", upper, re.DOTALL)
            if m:
                name = re.sub(r"\s+", " ", m.group(1).title())
                self.extracted_data["student_name"] = name
                self.confidence_scores["student_name"] = max(self.confidence_scores.get("student_name", 0), 40)

        # Course heuristic around "Computer Science"
        if not self.extracted_data.get("course"):
            m = re.search(r"(Computer\s+Science\s*&?\s*En[gq]ineer(?:ing)?)", text, re.IGNORECASE)
            if m:
                course = "B.E. " + re.sub(r"\s+", " ", m.group(1).strip())
                self.extracted_data["course"] = course
                self.confidence_scores["course"] = max(self.confidence_scores.get("course", 0), 55)

        # Year from "August 2020" or any 20xx
        if not self.extracted_data.get("year"):
            m = re.search(r"August\s+(\d{4})", text, re.IGNORECASE)
            if not m:
                m = re.search(r"\b(20\d{2})\b", text)
            if m:
                self.extracted_data["year"] = m.group(1)
                self.confidence_scores["year"] = max(self.confidence_scores.get("year", 0), 55)

        # University
        if not self.extracted_data.get("university"):
            m = re.search(r"([A-Z]{5,}(?:\s+[A-Z]{3,})*\s+TECHNOLOGICAL\s+UNIVER\w+)", upper)
            if m:
                uni = re.sub(r"\s+", " ", m.group(1)).title()
                self.extracted_data["university"] = uni
                self.confidence_scores["university"] = max(self.confidence_scores.get("university", 0), 50)

    def _postprocess_shankara_project(self) -> None:
        text = self.cleaned_text or ""
        upper = text.upper()
        if "SHANKARA INSTITUTE OF TECHNOLOGY" not in upper:
            return

        # Name in quotes
        if not self.extracted_data.get("student_name"):
            m = re.search(r"This\s+is\s+to\s+certify\s+that\s+[\"“']?([A-Z][A-Z\s]+)[\"”']?", text, re.IGNORECASE)
            if m:
                name = re.sub(r"\s+", " ", m.group(1).strip()).title()
                self.extracted_data["student_name"] = name
                self.confidence_scores["student_name"] = max(self.confidence_scores.get("student_name", 0), 70)

        # Course from "final year of ..."
        if not self.extracted_data.get("course"):
            m = re.search(r"final\s+year\s+of\s+([A-Za-z\s]+?Engineering)", text, re.IGNORECASE)
            if m:
                course = re.sub(r"\s+", " ", m.group(1).strip())
                self.extracted_data["course"] = course
                self.confidence_scores["course"] = max(self.confidence_scores.get("course", 0), 65)

        # University mention
        if not self.extracted_data.get("university"):
            m = re.search(r"(Rajasthan\s+Technical\s+University,\s*Kota)", text, re.IGNORECASE)
            if m:
                self.extracted_data["university"] = re.sub(r"\s+", " ", m.group(1).strip())
                self.confidence_scores["university"] = max(self.confidence_scores.get("university", 0), 70)
    
    def get_errors(self) -> List[str]:
        """Get list of extraction errors"""
        return self.errors
    
    def get_confidence_scores(self) -> Dict[str, int]:
        """Get confidence scores for extracted fields"""
        return self.confidence_scores
    
    def validate_fields(self) -> Tuple[bool, List[str]]:
        """
        Validate extracted fields with confidence thresholds
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        validation_errors = []
        
        # Check required fields
        required_fields = ['certificate_id', 'student_name', 'university']
        
        for field in required_fields:
            if not self.extracted_data.get(field):
                validation_errors.append(f"Required field '{field}' is missing")
            elif self.confidence_scores.get(field, 0) < 50:
                validation_errors.append(f"Low confidence for '{field}' ({self.confidence_scores.get(field, 0)}%)")
        
        # Additional validations
        if self.extracted_data.get('student_name'):
            name = self.extracted_data['student_name']
            if len(name.split()) < 2:
                validation_errors.append("Student name should have at least 2 words")
        
        if self.extracted_data.get('year'):
            try:
                year = int(self.extracted_data['year'])
                current_year = datetime.now().year
                if year < 1950 or year > current_year + 1:
                    validation_errors.append(f"Year {year} is out of valid range")
            except ValueError:
                validation_errors.append("Year is not a valid number")
        
        is_valid = len(validation_errors) == 0
        return is_valid, validation_errors


# Backward compatibility wrapper
class FieldExtractor(ImprovedFieldExtractor):
    """Wrapper for backward compatibility"""
    pass


if __name__ == "__main__":
    # Test the improved extraction module
    sample_text = """
    JAWAHARLAL NEHRU TECHNOLOGICAL UNIVERSITY HYDERABAD
    HYDERABAD - 500 085, TELANGANA, INDIA
    
    TG 2068615
    H.T No.: 21671A0517
    
    College: JNTUH AFFILIATED AUTONOMOUS COLLEGE
    67 - J.B. Institute of Engineering & Technology
    
    Mr. Ganeek Shivasai
    S/o. Ganeek Rajeshwar Rao
    
    having fulfilled the academic requirements and passed the examination
    held during April - 2025 in First Class With Distinction
    has been admitted by the Executive Council to the Degree of
    
    Bachelor of Technology
    Computer Science & Engineering
    """
    
    extractor = ImprovedFieldExtractor()
    fields = extractor.extract_all_fields(sample_text)
    
    print("\n\nFinal Extracted Fields:")
    for key, value in fields.items():
        print(f"  {key}: {value}")
    
    print("\n\nConfidence Scores:")
    for key, score in extractor.get_confidence_scores().items():
        print(f"  {key}: {score}%")
    
    is_valid, errors = extractor.validate_fields()
    print(f"\nValidation: {'PASS' if is_valid else 'FAIL'}")
    if errors:
        print("Validation Errors:")
        for error in errors:
            print(f"  - {error}")
