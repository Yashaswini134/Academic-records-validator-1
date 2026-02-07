"""
Field Extraction Module for Certificate OCR
Extracts structured data from OCR text using regex patterns
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime


class FieldExtractor:
    """Extracts structured fields from OCR text"""
    
    def __init__(self):
        self.raw_text = ""
        self.extracted_data = {}
        self.errors = []
    
    def set_text(self, text: str):
        """Set the OCR text to extract from"""
        self.raw_text = text
        self.extracted_data = {}
        self.errors = []
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters that might interfere
        text = text.strip()
        return text
    
    def extract_certificate_id(self) -> Optional[str]:
        """
        Extract certificate ID using multiple patterns
        Common patterns:
        - Certificate No: ABC123
        - Cert ID: 12345
        - Registration No: XYZ/2023/001
        """
        patterns = [
            r'(?:certificate|cert)[\s\-_]*(?:no|number|id|#)[\s\-_:]*([A-Z0-9\-\/]+)',
            r'(?:registration|reg)[\s\-_]*(?:no|number|id)[\s\-_:]*([A-Z0-9\-\/]+)',
            r'(?:serial|reference)[\s\-_]*(?:no|number)[\s\-_:]*([A-Z0-9\-\/]+)',
            r'\b([A-Z]{2,4}[\/\-]?\d{4,}[\/\-]?[A-Z0-9]*)\b',  # Pattern like ABC/2023/001
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.raw_text, re.IGNORECASE)
            if match:
                cert_id = match.group(1).strip()
                if len(cert_id) >= 4:  # Minimum length check
                    print(f"✓ Certificate ID found: {cert_id}")
                    return cert_id
        
        self.errors.append("Certificate ID not found")
        print("✗ Certificate ID not found")
        return None
    
    def extract_student_name(self) -> Optional[str]:
        """
        Extract student name using multiple patterns
        Handles: Title Case, ALL CAPS, mixed case
        Common patterns:
        - This is to certify that [Name]
        - Name: John Doe / JOHN DOE
        - Student Name: Jane Smith / JANE SMITH
        """
        patterns = [
            # Pattern 1: ALL CAPS names (e.g., "RAHUL SHARMA")
            r'(?:this is to certify that|certify that|certified that|awarded to|presented to)[\s:]+([A-Z]+(?:\s+[A-Z]+)+)',
            
            # Pattern 2: Title Case names (e.g., "Rahul Sharma")
            r'(?:this is to certify that|certify that|certified that|awarded to|presented to)[\s:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            
            # Pattern 3: Name after "certify that" with typos (handles OCR errors like "cectlty tat")
            r'(?:certif|cectlty|certity)[\s\w]*(?:that|tat)[\s:]+([A-Z]+(?:\s+[A-Z]+)+)',
            
            # Pattern 4: Student/Candidate name (ALL CAPS)
            r'(?:student|candidate)[\s\-_]*name[\s\-_:]+([A-Z]+(?:\s+[A-Z]+)+)',
            
            # Pattern 5: Student/Candidate name (Title Case)
            r'(?:student|candidate)[\s\-_]*name[\s\-_:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            
            # Pattern 6: Standalone ALL CAPS name (2-4 words) on its own line
            r'^\s*([A-Z]{2,}(?:\s+[A-Z]{2,}){1,3})\s*$',
            
            # Pattern 7: Name followed by "Roll No" or similar
            r'\b([A-Z]+(?:\s+[A-Z]+)+)[\s\n]+(?:Roll|Reg|Registration)',
            
            # Pattern 8: Title Case name followed by "Roll No"
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)[\s\n]+(?:Roll|Reg|Registration)',
            
            # Pattern 9: Generic name pattern (Title Case)
            r'(?:name|mr|ms|miss)[\s\-_:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
            
            # Pattern 10: Name before "has/have/is/was"
            r'\b([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b(?=\s+(?:has|have|is|was))',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.raw_text, re.IGNORECASE | re.MULTILINE)
            if match:
                name = match.group(1).strip()
                # Validate name (at least 2 words, reasonable length)
                words = name.split()
                if len(words) >= 2 and len(name) <= 50:
                    # Additional validation: avoid common false positives
                    # Skip if it looks like a course name or institution
                    skip_words = ['BACHELOR', 'MASTER', 'DIPLOMA', 'CERTIFICATE', 'INSTITUTE', 'UNIVERSITY', 'COLLEGE', 'TECHNOLOGY', 'SCIENCE', 'ARTS', 'COMMERCE']
                    if not any(skip_word in name.upper() for skip_word in skip_words):
                        print(f"✓ Student name found: {name}")
                        return name
        
        self.errors.append("Student name not found")
        print("✗ Student name not found")
        return None
    
    def extract_roll_number(self) -> Optional[str]:
        """
        Extract roll/registration number
        Common patterns:
        - Roll No: 12345
        - Reg No: ABC123
        - Student ID: 2023001
        """
        patterns = [
            r'(?:roll|reg|registration|student)[\s\-_]*(?:no|number|id)[\s\-_:]*([A-Z0-9\-\/]+)',
            r'(?:enrollment|enrolment)[\s\-_]*(?:no|number)[\s\-_:]*([A-Z0-9\-\/]+)',
            r'\b(\d{6,})\b',  # 6+ digit number
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.raw_text, re.IGNORECASE)
            if match:
                roll_no = match.group(1).strip()
                if len(roll_no) >= 4:
                    print(f"✓ Roll number found: {roll_no}")
                    return roll_no
        
        self.errors.append("Roll number not found")
        print("✗ Roll number not found")
        return None
    
    def extract_course(self) -> Optional[str]:
        """
        Extract course/degree name
        Common patterns:
        - Bachelor of Science
        - B.Tech in Computer Science
        - Master of Arts
        """
        patterns = [
            r'(?:bachelor|master|diploma|phd|doctorate)[\s\-_]+(?:of|in|degree)[\s\-_]+([A-Za-z\s&,]+?)(?:\s+(?:from|at|in the year|year|\d{4}))',
            r'(?:course|degree|program)[\s\-_:]+([A-Za-z\s&,\.]+?)(?:\s+(?:from|at|in the year|year|\d{4}))',
            r'\b(B\.?(?:Tech|E|Sc|A|Com)|M\.?(?:Tech|E|Sc|A|Com)|MBA|MCA|BBA|BCA)(?:\s+(?:in|of)?\s+([A-Za-z\s&,]+?))?(?:\s+(?:from|at|in the year|year|\d{4}))',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.raw_text, re.IGNORECASE)
            if match:
                course = match.group(1).strip() if match.lastindex >= 1 else match.group(0).strip()
                if match.lastindex >= 2 and match.group(2):
                    course = f"{match.group(1)} {match.group(2)}".strip()
                
                # Clean up course name
                course = re.sub(r'\s+', ' ', course)
                if len(course) >= 3:
                    print(f"✓ Course found: {course}")
                    return course
        
        self.errors.append("Course/Degree not found")
        print("✗ Course/Degree not found")
        return None
    
    def extract_university(self) -> Optional[str]:
        """
        Extract university name
        Handles: Title Case, ALL CAPS, mixed case
        Common patterns:
        - University of XYZ / UNIVERSITY OF XYZ
        - ABC University / ABC UNIVERSITY
        - XYZ Institute of Technology / XYZ INSTITUTE OF TECHNOLOGY
        """
        patterns = [
            # Pattern 1: ALL CAPS institution names (e.g., "INDIAN INSTITUTE OF TECHNOLOGY")
            r'\b([A-Z]+(?:\s+[A-Z]+)*\s+(?:UNIVERSITY|INSTITUTE|COLLEGE)(?:\s+(?:OF|FOR)\s+[A-Z]+(?:\s+[A-Z]+)*)?)\b',
            
            # Pattern 2: "from" followed by ALL CAPS institution
            r'(?:from|froma)[\s\n]+([A-Z]+(?:\s+[A-Z]+)*\s+(?:UNIVERSITY|INSTITUTE|COLLEGE)(?:\s+(?:OF|FOR)\s+[A-Z]+(?:\s+[A-Z]+)*)?)',
            
            # Pattern 3: Title Case - "University/Institute/College of [Name]"
            r'(?:university|college|institute)[\s\-_]+(?:of|for)[\s\-_]+([A-Za-z\s&,]+?)(?:\s+(?:certifies|hereby|has|in the year|year|\d{4}))',
            
            # Pattern 4: Title Case - "[Name] University/Institute/College"
            r'([A-Za-z\s&,]+?)[\s\-_]+(?:university|college|institute)(?:\s+(?:certifies|hereby|has|in the year|year|\d{4}))',
            
            # Pattern 5: "from/at/issued by" followed by institution name
            r'(?:from|at|issued by)[\s\-_]+([A-Za-z\s&,]+?(?:university|college|institute))',
            
            # Pattern 6: Standalone ALL CAPS institution on its own line (after "from")
            r'(?:from|froma)[\s\n]+([A-Z]{3,}(?:\s+[A-Z]{3,})+)',
            
            # Pattern 7: Institution name before "Year of Passing"
            r'\b([A-Z]+(?:\s+[A-Z]+)*\s+(?:UNIVERSITY|INSTITUTE|COLLEGE)(?:\s+(?:OF|FOR)\s+[A-Z]+(?:\s+[A-Z]+)*)?)[\s\n]+(?:Year|year)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.raw_text, re.IGNORECASE | re.MULTILINE)
            if match:
                university = match.group(1).strip()
                # Clean up university name
                university = re.sub(r'\s+', ' ', university)
                
                # Validate length
                if len(university) >= 5:
                    # Additional validation: must contain institution keyword
                    institution_keywords = ['UNIVERSITY', 'INSTITUTE', 'COLLEGE', 'SCHOOL']
                    if any(keyword in university.upper() for keyword in institution_keywords):
                        print(f"✓ University found: {university}")
                        return university
                    # If pattern explicitly matched institution, accept it
                    elif len(university) >= 10:
                        print(f"✓ University found: {university}")
                        return university
        
        self.errors.append("University name not found")
        print("✗ University name not found")
        return None
    
    def extract_year(self) -> Optional[str]:
        """
        Extract year of passing
        Common patterns:
        - Year: 2023
        - In the year 2022
        - Passed in 2021
        """
        current_year = datetime.now().year
        
        patterns = [
            r'(?:year|passed|completed|graduated)[\s\-_:]+(?:in|on)?[\s\-_]*(\d{4})',
            r'(?:in the year|academic year)[\s\-_:]+(\d{4})',
            r'\b((?:19|20)\d{2})\b',  # Any 4-digit year
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, self.raw_text, re.IGNORECASE)
            for year_str in matches:
                year = int(year_str)
                # Validate year (reasonable range)
                if 1950 <= year <= current_year + 1:
                    print(f"✓ Year found: {year}")
                    return str(year)
        
        self.errors.append("Year of passing not found")
        print("✗ Year of passing not found")
        return None
    
    def extract_cgpa(self) -> Optional[str]:
        """
        Extract CGPA/GPA from certificate
        Common patterns:
        - CGPA: 8.5
        - GPA: 3.5/4.0
        - Grade: 8.5 out of 10
        - Percentage: 85%
        """
        patterns = [
            # Pattern 1: CGPA/GPA with value (e.g., "CGPA: 8.5", "GPA: 3.5")
            r'(?:cgpa|gpa|grade point|cumulative grade)[\s\-_:]+(\d+\.?\d*)',
            
            # Pattern 2: CGPA/GPA with "out of" (e.g., "8.5 out of 10", "3.5/4.0")
            r'(?:cgpa|gpa|grade)[\s\-_:]+(\d+\.?\d*)[\s/]+(?:out of|outof|of)[\s/]+(\d+\.?\d*)',
            
            # Pattern 3: Standalone decimal number with CGPA/GPA nearby
            r'(?:cgpa|gpa)[\s\-_:]*(\d+\.\d+)',
            
            # Pattern 4: Grade/CGPA followed by slash notation (e.g., "8.5/10")
            r'(?:cgpa|gpa|grade)[\s\-_:]*(\d+\.?\d*)[\s]*[/][\s]*(\d+\.?\d*)',
            
            # Pattern 5: Percentage (e.g., "85%", "85.5%")
            r'(?:percentage|marks|score)[\s\-_:]+(\d+\.?\d*)[\s]*%',
            
            # Pattern 6: Just "CGPA" followed by number on next line or nearby
            r'(?:cgpa|gpa)[\s\n:]+(\d+\.\d+)',
            
            # Pattern 7: Decimal number between 0-10 or 0-4 with context
            r'\b(\d+\.\d{1,2})\s*(?:/\s*(?:10|4)\.?0?|out of (?:10|4)\.?0?)\b',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.raw_text, re.IGNORECASE | re.MULTILINE)
            if match:
                # Get CGPA value
                cgpa_value = match.group(1).strip()
                
                # If there's a second group (max value), include it
                if match.lastindex >= 2 and match.group(2):
                    max_value = match.group(2).strip()
                    cgpa = f"{cgpa_value}/{max_value}"
                else:
                    cgpa = cgpa_value
                
                # Validate CGPA (should be a reasonable number)
                try:
                    cgpa_float = float(cgpa_value)
                    # CGPA typically ranges from 0-10 or 0-4
                    if 0 <= cgpa_float <= 10:
                        print(f"✓ CGPA found: {cgpa}")
                        return cgpa
                    elif 10 < cgpa_float <= 100:
                        # Might be percentage, convert to CGPA
                        print(f"✓ CGPA found (from percentage): {cgpa}%")
                        return f"{cgpa}%"
                except ValueError:
                    continue
        
        # CGPA is optional, so don't add to errors
        print("ℹ CGPA not found (optional field)")
        return None

    
    def extract_all_fields(self, ocr_text: str) -> Dict[str, Optional[str]]:
        """
        Extract all fields from OCR text
        
        Args:
            ocr_text: Raw text from OCR
            
        Returns:
            Dictionary with extracted fields
        """
        print("\n" + "="*60)
        print("EXTRACTING FIELDS FROM OCR TEXT")
        print("="*60)
        
        self.set_text(ocr_text)
        
        # Extract all fields
        self.extracted_data = {
            'certificate_id': self.extract_certificate_id(),
            'student_name': self.extract_student_name(),
            'roll_number': self.extract_roll_number(),
            'course': self.extract_course(),
            'university': self.extract_university(),
            'year': self.extract_year(),
            'cgpa': self.extract_cgpa(),
        }
        
        print("="*60)
        print("FIELD EXTRACTION COMPLETE")
        print("="*60 + "\n")
        
        return self.extracted_data
    
    def get_errors(self) -> List[str]:
        """Get list of extraction errors"""
        return self.errors
    
    def validate_fields(self) -> Tuple[bool, List[str]]:
        """
        Validate extracted fields
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        validation_errors = []
        
        # Check required fields
        required_fields = ['certificate_id', 'student_name', 'university']
        
        for field in required_fields:
            if not self.extracted_data.get(field):
                validation_errors.append(f"Required field '{field}' is missing")
        
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


if __name__ == "__main__":
    # Test the extraction module
    sample_text = """
    CERTIFICATE OF COMPLETION
    
    This is to certify that John Smith
    Roll No: 2023001
    has successfully completed the course
    Bachelor of Technology in Computer Science
    from ABC University
    in the year 2023
    
    Certificate No: ABC/2023/CS/001
    """
    
    extractor = FieldExtractor()
    fields = extractor.extract_all_fields(sample_text)
    
    print("\nExtracted Fields:")
    for key, value in fields.items():
        print(f"  {key}: {value}")
    
    is_valid, errors = extractor.validate_fields()
    print(f"\nValidation: {'PASS' if is_valid else 'FAIL'}")
    if errors:
        print("Errors:")
        for error in errors:
            print(f"  - {error}")
