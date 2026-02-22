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
        self.cleaned_text = ""
        self.extracted_data = {}
        self.errors = []
    
    def set_text(self, text: str):
        """Set the OCR text to extract from"""
        self.raw_text = text or ""
        # Precompute cleaned version once for all regex searches
        self.cleaned_text = self.clean_text(self.raw_text)
        self.extracted_data = {}
        self.errors = []
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Normalize newlines and spaces
        text = (text or "").replace('\r', '\n')
        # Collapse multiple spaces/tabs
        text = re.sub(r'[ \t]+', ' ', text)
        # Normalize multiple newlines
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        return text.strip()
    
    def extract_certificate_id(self) -> Optional[str]:
        """
        Extract certificate ID using multiple patterns
        Common patterns:
        - Certificate No: ABC123
        - Cert ID: 12345
        - Registration No: XYZ/2023/001
        - Hall Ticket No: 21671A0517 (JNTUH format)
        - TG 2068615 (JNTUH format)
        """
        # First try strict pattern based on label "Certificate ID/No"
        label_pattern = re.compile(
            r"(Certificate\s*(ID|No)?\s*[:\-]?\s*)([A-Z0-9\-\/]+)",
            re.IGNORECASE
        )
        m = label_pattern.search(self.cleaned_text)
        if m:
            cert_id = m.group(3).strip()
            cert_id = re.sub(r'\s+', '', cert_id)
            if cert_id:
                print(f"✓ Certificate ID (label-based) found: {cert_id}")
                return cert_id

        patterns = [
            # JNTUH-specific patterns
            r'H\.?T\.?\s*No\.?[\s:]*(\d{10})',  # H.T No.: 21671A0517
            r'Hall\s*Ticket[\s:]+([A-Z0-9]{10,})',  # Hall Ticket: 21671A0517
            r'TG[\s]*(\d{7})',  # TG 2068615
            
            # Standard patterns
            r'EDP\s*S\.?\s*No\.?[\s:]*(\d{5,})',
            r'(?:certificate|cert)[\s\-_]*(?:no|number|id|#)[\s\-_:]*([A-Z0-9\-\/]+)',
            r'(?:registration|reg)[\s\-_]*(?:no|number|id)[\s\-_:]*([A-Z0-9\-\/]+)',
            r'(?:serial|reference)[\s\-_]*(?:no|number)[\s\-_:]*([A-Z0-9\-\/]+)',
            
            # Generic patterns
            r'\b(\d{10})\b',  # 10-digit number (common for hall tickets)
            r'\b([A-Z]{2,4}[\/\-]?\d{4,}[\/\-]?[A-Z0-9]*)\b',  # Pattern like ABC/2023/001
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.cleaned_text, re.IGNORECASE)
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
        # First try explicit "Name:" label pattern (ALL CAPS as specified)
        name_label_pattern = re.compile(
            r"(Name\s*[:\-]?\s*)([A-Z ]+)",
            re.IGNORECASE
        )
        m = name_label_pattern.search(self.cleaned_text)
        if m:
            raw_name = m.group(2).strip()
            # Normalize spaces and convert to title case
            cleaned_name = re.sub(r'\s+', ' ', raw_name)
            if cleaned_name:
                name = cleaned_name.title()
                print(f"✓ Student name (label-based) found: {name}")
                return name

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
            match = re.search(pattern, self.cleaned_text, re.IGNORECASE | re.MULTILINE)
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
        # First try explicit "Roll No/Number" label pattern
        roll_label_pattern = re.compile(
            r"(Roll\s*(No|Number)?\s*[:\-]?\s*)([A-Z0-9]+)",
            re.IGNORECASE
        )
        m = roll_label_pattern.search(self.cleaned_text)
        if m:
            roll_no = m.group(3).strip()
            roll_no = re.sub(r'\s+', '', roll_no)
            if roll_no:
                print(f"✓ Roll number (label-based) found: {roll_no}")
                return roll_no

        patterns = [
            r'(?:roll|reg|registration|student)[\s\-_]*(?:no|number|id)[\s\-_:]*([A-Z0-9\-\/]+)',
            r'(?:enrollment|enrolment)[\s\-_]*(?:no|number)[\s\-_:]*([A-Z0-9\-\/]+)',
            r'\b(\d{6,})\b',  # 6+ digit number
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.cleaned_text, re.IGNORECASE)
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
        - Bachelor of Technology (on one line) + Computer Science & Engineering (on next line)
        """
        # First try simple "Course:" label pattern
        course_label_pattern = re.compile(
            r"(Course\s*[:\-]?\s*)([A-Za-z ]+)",
            re.IGNORECASE
        )
        m = course_label_pattern.search(self.cleaned_text)
        if m:
            raw_course = m.group(2).strip()
            course = re.sub(r'\s+', ' ', raw_course)
            if course:
                print(f"✓ Course (label-based) found: {course}")
                return course

        # Then try to find degree and specialization separately (JNTUH format)
        degree_patterns = [
            r'Degree\s+of\s+(Bachelor\s+of\s+Technology)',
            r'(Bachelor\s+of\s+Technology)',
            r'(Bachelor\s+of\s+Science)',
            r'(Bachelor\s+of\s+Arts)',
            r'(Master\s+of\s+Technology)',
            r'(Master\s+of\s+Science)',
            r'(B\.?Tech)',
            r'(M\.?Tech)',
        ]
        
        specialization_patterns = [
            r'(Computer\s+Science\s*(?:&|and)?\s*Engineering)',
            r'(Mechanical\s+Engineering)',
            r'(Civil\s+Engineering)',
            r'(Electrical\s+(?:&|and)?\s*Electronics\s+Engineering)',
            r'(Electronics\s+(?:&|and)?\s*Communication\s+Engineering)',
            r'(Information\s+Technology)',
        ]
        
        degree = None
        specialization = None
        
        # Try to find degree
        for pattern in degree_patterns:
            match = re.search(pattern, self.cleaned_text, re.IGNORECASE)
            if match:
                degree = match.group(1).strip()
                break
        
        # Try to find specialization
        for pattern in specialization_patterns:
            match = re.search(pattern, self.cleaned_text, re.IGNORECASE)
            if match:
                specialization = match.group(1).strip()
                break
        
        # Combine if both found
        if degree and specialization:
            course = f"{degree} in {specialization}"
        elif degree:
            course = degree
        elif specialization:
            course = specialization
        else:
            course = None

        if course:
            # REMOVE PREFIX (User Request for PTU)
            course = re.sub(r'^Bachelor\s+of\s+Technology\s+in\s+', '', course, flags=re.IGNORECASE).strip()
            print(f"✓ Course found: {course}")
            return course
        
        # Fallback to original patterns
        patterns = [
            r'(?:bachelor|master|diploma|phd|doctorate)[\s\-_]+(?:of|in|degree)[\s\-_]+([A-Za-z\s&,]+?)(?:\s+(?:from|at|in the year|year|\d{4}))',
            r'(?:course|degree|program)[\s\-_:]+([A-Za-z\s&,\.]+?)(?:\s+(?:from|at|in the year|year|\d{4}))',
            r'\b(B\.?(?:Tech|E|Sc|A|Com)|M\.?(?:Tech|E|Sc|A|Com)|MBA|MCA|BBA|BCA)(?:\s+(?:in|of)?\s+([A-Za-z\s&,]+?))?(?:\s+(?:from|at|in the year|year|\d{4}))',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, self.cleaned_text, re.IGNORECASE)
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
            match = re.search(pattern, self.cleaned_text, re.IGNORECASE | re.MULTILINE)
            if match:
                university = match.group(1).strip()
                # Clean up university name
                university = re.sub(r'\s+', ' ', university)
                
                # Validate length
                if len(university) >= 5:
                    # REMOVE AFFILIATION SUFFIXES (User Request)
                    university = re.sub(r'\(Affiliated to JNTUH\)', '', university, flags=re.IGNORECASE)
                    university = re.sub(r'\(affiliated By JNTUH\)', '', university, flags=re.IGNORECASE)
                    university = re.sub(r'\(Affiliated to University of Mumbai\)', '', university, flags=re.IGNORECASE)
                    university = university.strip()

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
        
        # First try explicit "Year:" label pattern
        year_label_pattern = re.compile(
            r"(Year\s*[:\-]?\s*)(\d{4})",
            re.IGNORECASE
        )
        m = year_label_pattern.search(self.cleaned_text)
        if m:
            year_str = m.group(2)
            try:
                year = int(year_str)
                if 1950 <= year <= current_year + 1:
                    print(f"✓ Year (label-based) found: {year}")
                    return str(year)
            except ValueError:
                pass

        patterns = [
            r'(?:year|passed|completed|graduated)[\s\-_:]+(?:in|on)?[\s\-_]*(\d{4})',
            r'(?:in the year|academic year)[\s\-_:]+(\d{4})',
            r'\b((?:19|20)\d{2})\b',  # Any 4-digit year
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, self.cleaned_text, re.IGNORECASE)
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
            match = re.search(pattern, self.cleaned_text, re.IGNORECASE | re.MULTILINE)
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
        print("\n" + "="*70)
        print("EXTRACTING FIELDS FROM OCR TEXT")
        print("="*70)
        
        # Set and clean text
        self.set_text(ocr_text)
        
        # Debug: Show cleaned text
        cleaned = self.cleaned_text
        print("\n" + "-"*70)
        print("CLEANED TEXT (First 300 characters):")
        print("-"*70)
        print(cleaned[:300] if len(cleaned) > 300 else cleaned)
        print("-"*70 + "\n")
        
        # Extract all fields (generic regex-based)
        print("Extracting individual fields...")
        self.extracted_data = {
            'certificate_id': self.extract_certificate_id(),
            'student_name': self.extract_student_name(),
            'roll_number': self.extract_roll_number(),
            'course': self.extract_course(),
            'university': self.extract_university(),
            'year': self.extract_year(),
        }

        # Apply template-specific post-processing for known certificate layouts
        self._postprocess_jntuh_degree()
        self._postprocess_vtu_gradecard()
        self._postprocess_shankara_project()
        
        # Debug: Show extracted dictionary
        print("\n" + "-"*70)
        print("EXTRACTED FIELDS DICTIONARY:")
        print("-"*70)
        for key, value in self.extracted_data.items():
            status = "✓" if value else "✗"
            print(f"  {status} {key}: {value if value else 'NOT FOUND'}")
        print("-"*70)
        
        print("\n" + "="*70)
        print("FIELD EXTRACTION COMPLETE")
        print("="*70 + "\n")
        
        return self.extracted_data

    # ------------------------------------------------------------------
    # Template-specific helpers for certificates you provided
    # ------------------------------------------------------------------

    def _postprocess_jntuh_degree(self) -> None:
        """
        Improve extraction for JNTUH degree certificate (Ganeek Shivasai sample).
        Looks for:
        - JAWAHARLAL NEHRU TECHNOLOGICAL UNIVERSITY HYDERABAD
        - H.T. No. for roll number
        - TG number for certificate ID
        - Bachelor of Technology / Computer Science & Engineering
        - Year in 'April - 2023'
        """
        text = self.cleaned_text or ""
        upper = text.upper()

        if "JAWAHARLAL NEHRU TECHNOLOGICAL UNIVERSITY" not in upper:
            return

        print("ℹ Detected JNTUH degree layout – applying specialized extraction.")

        # Certificate ID from TG number (e.g., TG 2068615)
        if not self.extracted_data.get('certificate_id'):
            m = re.search(r'\bTG\s*([0-9]{5,})\b', text, re.IGNORECASE)
            if m:
                cert_id = m.group(1).strip()
                self.extracted_data['certificate_id'] = cert_id
                print(f"✓ [JNTUH] Certificate ID from TG: {cert_id}")

        # Roll number from H.T. No: 21671A0517
        if not self.extracted_data.get('roll_number'):
            m = re.search(
                r'H\.?\s*T\.?\s*No\.?\s*[:\-]?\s*([A-Z0-9]{8,})',
                text,
                re.IGNORECASE
            )
            if m:
                roll = m.group(1).strip()
                self.extracted_data['roll_number'] = roll
                print(f"✓ [JNTUH] Roll number from H.T. No: {roll}")

        # Student name – "Mr. Ganeek Shivasai" / "Ms."
        if not self.extracted_data.get('student_name'):
            m = re.search(
                r'\bMr\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
                text,
                re.IGNORECASE
            )
            if not m:
                m = re.search(
                    r'\bMs\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
                    text,
                    re.IGNORECASE
                )
            if m:
                name = re.sub(r'\s+', ' ', m.group(1).strip())
                self.extracted_data['student_name'] = name
                print(f"✓ [JNTUH] Student name from Mr./Ms.: {name}")

        # Course – Bachelor of Technology in Computer Science & Engineering
        if not self.extracted_data.get('course'):
            degree = None
            specialization = None

            m = re.search(
                r'(Bachelor\s+of\s+Technology)',
                text,
                re.IGNORECASE
            )
            if m:
                degree = m.group(1).strip()

            m = re.search(
                r'(Computer\s+Science\s*&?\s*Engineering)',
                text,
                re.IGNORECASE
            )
            if m:
                specialization = m.group(1).strip()

            if degree and specialization:
                course = f"{degree} in {specialization}"
            elif degree:
                course = degree
            else:
                course = None

            if course:
                self.extracted_data['course'] = course
                print(f"✓ [JNTUH] Course: {course}")

        # Year – look for "April - 2023"
        if not self.extracted_data.get('year'):
            m = re.search(r'April\s*[-–]?\s*(\d{4})', text, re.IGNORECASE)
            if not m:
                m = re.search(r'\b(20\d{2})\b', text)
            if m:
                year = m.group(1)
                self.extracted_data['year'] = year
                print(f"✓ [JNTUH] Year: {year}")

        # University name
        if not self.extracted_data.get('university'):
            m = re.search(
                r'(JAWAHARLAL\s+NEHRU\s+TECHNOLOGICAL\s+UNIVERSITY\s+HYDERABAD)',
                text,
                re.IGNORECASE
            )
            if m:
                uni = re.sub(r'\s+', ' ', m.group(1).title())
                self.extracted_data['university'] = uni
                print(f"✓ [JNTUH] University: {uni}")

    def _postprocess_vtu_gradecard(self) -> None:
        """
        Improve extraction for VTU grade card (Shreyas K sample).
        """
        text = self.cleaned_text or ""
        upper = text.upper()

        # VTU header sometimes gets badly OCR'd; be tolerant:
        # look for "...TECHNOLOGICAL UNIVER..." rather than exact "VISVESVARAYA ..."
        if "TECHNOLOGICAL UNIVER" not in upper:
            return

        print("ℹ Detected VTU grade card layout – applying specialized extraction.")

        # Roll / USN: explicit USN label or heuristic alphanumeric token
        if not self.extracted_data.get('roll_number'):
            m = re.search(r'\bUSN[:\s]+([A-Z0-9]+)', text, re.IGNORECASE)
            if m:
                usn = m.group(1).strip()
                self.extracted_data['roll_number'] = usn
                print(f"✓ [VTU] USN: {usn}")
            else:
                candidates = re.findall(r'\b[A-Za-z0-9]{8,12}\b', text)
                if candidates:
                    usn = candidates[0]
                    self.extracted_data['roll_number'] = usn
                    print(f"✓ [VTU] Heuristic roll/USN: {usn}")

        # Student name – labelled or heuristic line before institute
        if not self.extracted_data.get('student_name'):
            m = re.search(
                r'Name\s+of\s+the\s+Student\s*[:\-]?\s*([A-Z][A-Za-z]+\s+[A-Z][A-Za-z]+)',
                text,
                re.IGNORECASE
            )
            if m:
                name = re.sub(r'\s+', ' ', m.group(1).strip())
                self.extracted_data['student_name'] = name
                print(f"✓ [VTU] Student name: {name}")
            else:
                # Heuristic: ALL CAPS name on a line directly before "INSTITUTE OF TECHNOLOGY"
                m = re.search(
                    r'([A-Z]{3,}\s+[A-Z])\s*\n.*INSTITUTE OF TECHNOLOGY',
                    upper
                )
                if m:
                    raw_name = m.group(1).title()
                    name = re.sub(r'\s+', ' ', raw_name.strip())
                    self.extracted_data['student_name'] = name
                    print(f"✓ [VTU] Heuristic student name: {name}")

        # Course / Program – approximate match around "Computer Science"
        if not self.extracted_data.get('course'):
            m = re.search(
                r'(Computer\s+Science\s*&?\s*En[gq]ineer(?:ing)?)',
                text,
                re.IGNORECASE
            )
            if m:
                course = "B.E. " + re.sub(r'\s+', ' ', m.group(1).strip())
                self.extracted_data['course'] = course
                print(f"✓ [VTU] Course (heuristic): {course}")

        # Year – from "August 2020" or any 20xx
        if not self.extracted_data.get('year'):
            m = re.search(r'August\s+(\d{4})', text, re.IGNORECASE)
            if not m:
                m = re.search(r'\b(20\d{2})\b', text)
            if m:
                year = m.group(1)
                self.extracted_data['year'] = year
                print(f"✓ [VTU] Year: {year}")

        # University
        if not self.extracted_data.get('university'):
            m = re.search(
                r'(VISVESVARAYA\s+TECHNOLOGICAL\s+UNIVERSITY)',
                text,
                re.IGNORECASE
            )
            if m:
                uni = re.sub(r'\s+', ' ', m.group(1).title())
                self.extracted_data['university'] = uni
                print(f"✓ [VTU] University: {uni}")

    def _postprocess_shankara_project(self) -> None:
        """
        Improve extraction for Shankara Institute project certificate (Rohit Kumar).
        """
        text = self.cleaned_text or ""
        upper = text.upper()

        if "SHANKARA INSTITUTE OF TECHNOLOGY" not in upper:
            return

        print("ℹ Detected Shankara project certificate layout – applying specialized extraction.")

        # Student name – inside quotes after "This is to certify that"
        if not self.extracted_data.get('student_name'):
            m = re.search(
                r'This\s+is\s+to\s+certify\s+that\s+["“]?([A-Z][A-Z\s]+)["”]?',
                text,
                re.IGNORECASE
            )
            if m:
                raw_name = m.group(1).strip()
                name = re.sub(r'\s+', ' ', raw_name).title()
                self.extracted_data['student_name'] = name
                print(f"✓ [Shankara] Student name: {name}")

        # Course – Electronics and Communication Engineering
        if not self.extracted_data.get('course'):
            m = re.search(
                r'final\s+year\s+of\s+([A-Za-z\s]+?Engineering)',
                text,
                re.IGNORECASE
            )
            if m:
                course = re.sub(r'\s+', ' ', m.group(1).strip())
                self.extracted_data['course'] = course
                print(f"✓ [Shankara] Course: {course}")

        # University – Rajasthan Technical University, Kota (mentioned in body)
        if not self.extracted_data.get('university'):
            m = re.search(
                r'(Rajasthan\s+Technical\s+University,\s*Kota)',
                text,
                re.IGNORECASE
            )
            if m:
                uni = re.sub(r'\s+', ' ', m.group(1).strip())
                self.extracted_data['university'] = uni
                print(f"✓ [Shankara] University: {uni}")
    
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
