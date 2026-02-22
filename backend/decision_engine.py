"""
Decision Engine for Certificate Verification System
Contains rule-based logic to determine certificate verification status
"""

from typing import Dict, List
import os
import sys

# Add parent directory to path for AI module import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import AI prediction function
try:
    from ai.predict_forgery import predict_forgery
    AI_AVAILABLE = True
except Exception as e:
    AI_AVAILABLE = False
    print(f"Warning: AI module load failed: {e}. Proceeding without AI analysis.")
except ImportError: 
    # Catch ImportError explicitly just in case Exception misses some specific import errors in older python
    AI_AVAILABLE = False
    print("Warning: AI module not found. Proceeding without AI analysis.")


class DecisionEngine:
    """
    Rule-based decision engine for certificate verification
    
    Responsibilities:
    - Evaluate OCR and hash results
    - Apply verification rules
    - Classify certificates as VERIFIED or SUSPICIOUS
    - Provide confidence levels and remarks
    - Flag potential issues
    
    Design:
    - Modular rule system (easy to extend)
    - No AI or blockchain (prepared for future integration)
    - Clear decision logic for academic presentation
    """
    
    # Decision constants
    DECISION_VERIFIED = "VERIFIED"
    DECISION_SUSPICIOUS = "SUSPICIOUS"
    
    # Confidence levels
    CONFIDENCE_HIGH = "HIGH"
    CONFIDENCE_MEDIUM = "MEDIUM"
    CONFIDENCE_LOW = "LOW"
    
    # Critical fields that must be present
    CRITICAL_FIELDS = ['certificate_id', 'student_name', 'university']
    
    # Important fields (should be present)
    IMPORTANT_FIELDS = ['roll_number', 'course', 'year']
    
    def __init__(self):
        """Initialize the decision engine"""
        self.rules_applied = []
    
    def make_decision(self, ocr_result: Dict, hash_result: Dict, certificate_image_path: str = None) -> Dict:
        """
        Make final verification decision based on OCR, hash, and AI results
        
        Args:
            ocr_result: Results from OCR processing
            hash_result: Results from hash generation
            certificate_image_path: Path to certificate image for AI analysis
            
        Returns:
            Dictionary containing:
            - decision: VERIFIED or SUSPICIOUS
            - confidence: HIGH, MEDIUM, or LOW
            - remarks: Explanation of decision
            - flags: List of issues found
            - ai_analysis: AI prediction results (if available)
        """
        self.rules_applied = []
        flags = []
        
        # STEP 0: Run AI Analysis (if available and image path provided)
        ai_analysis = self._run_ai_analysis(certificate_image_path)
        
        # RULE 1: Check OCR Status
        ocr_status = ocr_result.get('status', 'FAIL')
        
        if ocr_status == 'FAIL':
            return self._create_decision(
                decision=self.DECISION_SUSPICIOUS,
                confidence=self.CONFIDENCE_HIGH,
                remarks="OCR processing failed. Cannot extract certificate data.",
                flags=['OCR_FAILED'],
                rule_applied="RULE_1: OCR_STATUS_CHECK"
            )
        
        # RULE 2: Check Critical Fields
        missing_critical = self._check_critical_fields(ocr_result)
        
        if missing_critical:
            return self._create_decision(
                decision=self.DECISION_SUSPICIOUS,
                confidence=self.CONFIDENCE_HIGH,
                remarks=f"Critical fields missing: {', '.join(missing_critical)}",
                flags=['MISSING_CRITICAL_FIELDS'] + [f'MISSING_{field.upper()}' for field in missing_critical],
                rule_applied="RULE_2: CRITICAL_FIELDS_CHECK"
            )
        
        # RULE 3: Check Hash Generation
        if not hash_result.get('success', False):
            flags.append('HASH_GENERATION_FAILED')
            # Don't reject, but flag it
        
        # RULE 4: Check for OCR Errors
        ocr_errors = ocr_result.get('errors', [])
        if ocr_errors:
            flags.append('OCR_ERRORS_PRESENT')
            # Don't reject if status is PASS or PARTIAL, but flag it
        
        # RULE 5: Check Important Fields
        missing_important = self._check_important_fields(ocr_result)
        
        if missing_important:
            flags.extend([f'MISSING_{field.upper()}' for field in missing_important])
        
        # RULE 6: Validate Field Content
        content_issues = self._validate_field_content(ocr_result)
        
        if content_issues:
            flags.extend(content_issues)
        
        # RULE 7: Check OCR Status for PARTIAL
        if ocr_status == 'PARTIAL':
            flags.append('PARTIAL_OCR_EXTRACTION')
        
        # DECISION LOGIC
        
        # AI OVERRIDE: If AI detects forgery with high confidence, mark as SUSPICIOUS
        if ai_analysis.get('ai_enabled') and ai_analysis.get('ai_result') == 'Suspicious':
            if ai_analysis.get('ai_score', 0) >= 0.7:  # High confidence suspicious
                return self._create_decision_with_ai(
                    decision=self.DECISION_SUSPICIOUS,
                    confidence=self.CONFIDENCE_HIGH,
                    remarks=f"AI detected potential forgery (confidence: {ai_analysis.get('ai_score', 0):.2f}). Manual review required.",
                    flags=flags + ['AI_FORGERY_DETECTED'],
                    rule_applied="RULE_AI: AI_FORGERY_DETECTION",
                    ai_analysis=ai_analysis
                )
        
        # Case 1: OCR PASS + Hash Success + No Critical Issues + AI Genuine = VERIFIED
        if (ocr_status == 'PASS' and 
            hash_result.get('success', False) and 
            not missing_critical and
            len(content_issues) == 0):
            
            if missing_important:
                # Some optional fields missing, but core data is good
                return self._create_decision_with_ai(
                    decision=self.DECISION_VERIFIED,
                    confidence=self.CONFIDENCE_MEDIUM,
                    remarks=f"Certificate verified with minor data gaps. Missing: {', '.join(missing_important)}",
                    flags=flags,
                    rule_applied="RULE_8: VERIFIED_WITH_MINOR_GAPS",
                    ai_analysis=ai_analysis
                )
            else:
                # All fields present and valid
                return self._create_decision_with_ai(
                    decision=self.DECISION_VERIFIED,
                    confidence=self.CONFIDENCE_HIGH,
                    remarks="Certificate verified successfully. All critical data extracted and validated.",
                    flags=flags,
                    rule_applied="RULE_9: FULLY_VERIFIED",
                    ai_analysis=ai_analysis
                )
        
        # Case 2: OCR PARTIAL + Hash Success = VERIFIED with LOW confidence
        if (ocr_status == 'PARTIAL' and 
            hash_result.get('success', False) and
            not missing_critical):
            
            return self._create_decision(
                decision=self.DECISION_VERIFIED,
                confidence=self.CONFIDENCE_LOW,
                remarks="Certificate verified with low confidence. Some data extraction issues detected.",
                flags=flags,
                rule_applied="RULE_10: PARTIAL_VERIFICATION"
            )
        
        # Case 3: OCR PASS but Hash Failed = SUSPICIOUS
        if ocr_status == 'PASS' and not hash_result.get('success', False):
            return self._create_decision(
                decision=self.DECISION_SUSPICIOUS,
                confidence=self.CONFIDENCE_MEDIUM,
                remarks="Hash generation failed. Cannot ensure file integrity.",
                flags=flags + ['HASH_INTEGRITY_ISSUE'],
                rule_applied="RULE_11: HASH_FAILURE"
            )
        
        # Case 4: Content validation issues = SUSPICIOUS
        if len(content_issues) > 2:
            return self._create_decision(
                decision=self.DECISION_SUSPICIOUS,
                confidence=self.CONFIDENCE_HIGH,
                remarks=f"Multiple content validation issues detected: {len(content_issues)} problems found.",
                flags=flags,
                rule_applied="RULE_12: CONTENT_VALIDATION_FAILED"
            )
        
        # Case 5: Too many missing fields = SUSPICIOUS
        if len(missing_important) >= 2:
            return self._create_decision(
                decision=self.DECISION_SUSPICIOUS,
                confidence=self.CONFIDENCE_MEDIUM,
                remarks=f"Too many important fields missing: {', '.join(missing_important)}",
                flags=flags,
                rule_applied="RULE_13: TOO_MANY_MISSING_FIELDS"
            )
        
        # Default Case: SUSPICIOUS (catch-all for edge cases)
        return self._create_decision(
            decision=self.DECISION_SUSPICIOUS,
            confidence=self.CONFIDENCE_MEDIUM,
            remarks="Certificate verification inconclusive. Manual review recommended.",
            flags=flags + ['INCONCLUSIVE'],
            rule_applied="RULE_14: DEFAULT_SUSPICIOUS"
        )
    
    def _run_ai_analysis(self, certificate_image_path: str) -> Dict:
        """
        Run AI forgery detection on certificate image
        
        Args:
            certificate_image_path: Path to certificate image file
            
        Returns:
            Dictionary containing AI analysis results
        """
        if not AI_AVAILABLE:
            return {
                'ai_enabled': False,
                'ai_score': None,
                'ai_result': None,
                'error': 'AI module not available'
            }
        
        if not certificate_image_path or not os.path.exists(certificate_image_path):
            return {
                'ai_enabled': False,
                'ai_score': None,
                'ai_result': None,
                'error': 'Certificate image path not provided or file not found'
            }
        
        try:
            # Call AI prediction function
            ai_result = predict_forgery(certificate_image_path)
            
            # Check for errors
            if 'error' in ai_result:
                return {
                    'ai_enabled': False,
                    'ai_score': None,
                    'ai_result': None,
                    'error': ai_result['error']
                }
            
            # Return successful AI analysis
            return {
                'ai_enabled': True,
                'ai_score': ai_result.get('ai_score', 0.0),
                'ai_result': ai_result.get('ai_result', 'Unknown'),
                'error': None
            }
            
        except Exception as e:
            # AI prediction failed, but don't crash - mark as SUSPICIOUS
            return {
                'ai_enabled': False,
                'ai_score': None,
                'ai_result': 'Suspicious',  # Default to suspicious on error
                'error': f'AI prediction failed: {str(e)}'
            }
    
    
    def _check_critical_fields(self, ocr_result: Dict) -> List[str]:
        """
        Check if critical fields are present and non-empty
        
        Args:
            ocr_result: OCR processing results
            
        Returns:
            List of missing critical field names
        """
        missing = []
        
        for field in self.CRITICAL_FIELDS:
            value = ocr_result.get(field)
            if not value or (isinstance(value, str) and not value.strip()):
                missing.append(field)
        
        return missing
    
    def _check_important_fields(self, ocr_result: Dict) -> List[str]:
        """
        Check if important fields are present and non-empty
        
        Args:
            ocr_result: OCR processing results
            
        Returns:
            List of missing important field names
        """
        missing = []
        
        for field in self.IMPORTANT_FIELDS:
            value = ocr_result.get(field)
            if not value or (isinstance(value, str) and not value.strip()):
                missing.append(field)
        
        return missing
    
    def _validate_field_content(self, ocr_result: Dict) -> List[str]:
        """
        Validate the content of extracted fields
        
        Args:
            ocr_result: OCR processing results
            
        Returns:
            List of validation issue flags
        """
        issues = []
        
        # Validate Certificate ID
        cert_id = ocr_result.get('certificate_id', '')
        if cert_id and len(cert_id) < 4:
            issues.append('INVALID_CERTIFICATE_ID_LENGTH')
        
        # Validate Student Name
        student_name = ocr_result.get('student_name', '')
        if student_name:
            if len(student_name) < 4:
                issues.append('INVALID_STUDENT_NAME_LENGTH')
            # Check for suspicious characters or patterns
            if any(char.isdigit() for char in student_name[:10]):
                issues.append('SUSPICIOUS_NAME_PATTERN')
        
        # Validate Roll Number
        roll_number = ocr_result.get('roll_number', '')
        if roll_number and len(roll_number) < 4:
            issues.append('INVALID_ROLL_NUMBER_LENGTH')
        
        # Validate University
        university = ocr_result.get('university', '')
        if university and len(university) < 5:
            issues.append('INVALID_UNIVERSITY_LENGTH')
        
        # Validate Year
        year = ocr_result.get('year')
        if year:
            try:
                year_int = int(year)
                current_year = 2026  # Can be made dynamic
                if year_int < 1950 or year_int > current_year + 1:
                    issues.append('INVALID_YEAR_RANGE')
            except (ValueError, TypeError):
                issues.append('INVALID_YEAR_FORMAT')
        
        
        return issues
    
    def _create_decision(
        self,
        decision: str,
        confidence: str,
        remarks: str,
        flags: List[str],
        rule_applied: str
    ) -> Dict:
        """
        Create a decision result dictionary
        
        Args:
            decision: VERIFIED or SUSPICIOUS
            confidence: HIGH, MEDIUM, or LOW
            remarks: Explanation of the decision
            flags: List of issue flags
            rule_applied: Which rule was applied
            
        Returns:
            Decision result dictionary
        """
        self.rules_applied.append(rule_applied)
        
        return {
            'decision': decision,
            'confidence': confidence,
            'remarks': remarks,
            'flags': flags,
            'rules_applied': self.rules_applied.copy()
        }
    
    def _create_decision_with_ai(
        self,
        decision: str,
        confidence: str,
        remarks: str,
        flags: List[str],
        rule_applied: str,
        ai_analysis: Dict
    ) -> Dict:
        """
        Create a decision result dictionary with AI analysis included
        
        Args:
            decision: VERIFIED or SUSPICIOUS
            confidence: HIGH, MEDIUM, or LOW
            remarks: Explanation of the decision
            flags: List of issue flags
            rule_applied: Which rule was applied
            ai_analysis: AI analysis results
            
        Returns:
            Decision result dictionary with AI data
        """
        self.rules_applied.append(rule_applied)
        
        return {
            'decision': decision,
            'confidence': confidence,
            'remarks': remarks,
            'flags': flags,
            'rules_applied': self.rules_applied.copy(),
            'ai_analysis': ai_analysis
        }
    
    
    def get_decision_explanation(self, decision_result: Dict) -> str:
        """
        Generate human-readable explanation of the decision
        
        Args:
            decision_result: Decision result from make_decision()
            
        Returns:
            Formatted explanation string
        """
        explanation = []
        
        explanation.append(f"Decision: {decision_result['decision']}")
        explanation.append(f"Confidence: {decision_result['confidence']}")
        explanation.append(f"Remarks: {decision_result['remarks']}")
        
        if decision_result['flags']:
            explanation.append("\nFlags:")
            for flag in decision_result['flags']:
                explanation.append(f"  - {flag}")
        
        if decision_result.get('rules_applied'):
            explanation.append("\nRules Applied:")
            for rule in decision_result['rules_applied']:
                explanation.append(f"  - {rule}")
        
        return "\n".join(explanation)


# Standalone function for quick decision making
def evaluate_certificate(ocr_result: Dict, hash_result: Dict) -> Dict:
    """
    Convenience function to evaluate certificate without creating engine instance
    
    Args:
        ocr_result: OCR processing results
        hash_result: Hash generation results
        
    Returns:
        Decision result dictionary
    """
    engine = DecisionEngine()
    return engine.make_decision(ocr_result, hash_result)


if __name__ == "__main__":
    """
    Test the decision engine with sample data
    """
    print("=" * 70)
    print("TESTING DECISION ENGINE")
    print("=" * 70)
    
    # Test Case 1: Perfect certificate
    print("\n[TEST 1] Perfect Certificate")
    print("-" * 70)
    
    ocr_result_1 = {
        'status': 'PASS',
        'certificate_id': 'MT2023/CS/001',
        'student_name': 'RAHUL SHARMA',
        'roll_number': '202308001',
        'course': 'Bachelor of Technology in Computer Science',
        'university': 'INDIAN INSTITUTE OF TECHNOLOGY',
        'year': '2023',
        'cgpa': '8.5',
        'errors': []
    }
    
    hash_result_1 = {
        'success': True,
        'hash': 'abc123...',
        'algorithm': 'SHA-256'
    }
    
    engine = DecisionEngine()
    decision_1 = engine.make_decision(ocr_result_1, hash_result_1)
    print(engine.get_decision_explanation(decision_1))
    
    # Test Case 2: Missing critical field
    print("\n[TEST 2] Missing Critical Field")
    print("-" * 70)
    
    ocr_result_2 = {
        'status': 'PARTIAL',
        'certificate_id': None,  # Missing critical field
        'student_name': 'RAHUL SHARMA',
        'roll_number': '202308001',
        'course': 'Bachelor of Technology',
        'university': 'INDIAN INSTITUTE OF TECHNOLOGY',
        'year': '2023',
        'cgpa': None,
        'errors': ['Certificate ID not found']
    }
    
    hash_result_2 = {
        'success': True,
        'hash': 'def456...',
        'algorithm': 'SHA-256'
    }
    
    decision_2 = engine.make_decision(ocr_result_2, hash_result_2)
    print(engine.get_decision_explanation(decision_2))
    
    # Test Case 3: OCR Failed
    print("\n[TEST 3] OCR Failed")
    print("-" * 70)
    
    ocr_result_3 = {
        'status': 'FAIL',
        'certificate_id': None,
        'student_name': None,
        'roll_number': None,
        'course': None,
        'university': None,
        'year': None,
        'cgpa': None,
        'errors': ['OCR processing failed']
    }
    
    hash_result_3 = {
        'success': False,
        'hash': None,
        'algorithm': 'SHA-256',
        'error': 'File not found'
    }
    
    decision_3 = engine.make_decision(ocr_result_3, hash_result_3)
    print(engine.get_decision_explanation(decision_3))
    
    # Test Case 4: Hash Failed but OCR Passed
    print("\n[TEST 4] Hash Failed, OCR Passed")
    print("-" * 70)
    
    ocr_result_4 = {
        'status': 'PASS',
        'certificate_id': 'MT2023/CS/001',
        'student_name': 'RAHUL SHARMA',
        'roll_number': '202308001',
        'course': 'Bachelor of Technology',
        'university': 'INDIAN INSTITUTE OF TECHNOLOGY',
        'year': '2023',
        'cgpa': '8.5',
        'errors': []
    }
    
    hash_result_4 = {
        'success': False,
        'hash': None,
        'algorithm': 'SHA-256',
        'error': 'Hash generation failed'
    }
    
    decision_4 = engine.make_decision(ocr_result_4, hash_result_4)
    print(engine.get_decision_explanation(decision_4))
    
    print("\n" + "=" * 70)
    print("DECISION ENGINE TESTS COMPLETED")
    print("=" * 70)
