"""
Verifier Controller for Certificate Verification
Implements complete verifier-side verification workflow
"""

import os
import sys
from datetime import datetime
from typing import Dict, Optional

# Add parent directory to path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)

# Import existing modules
from ocr.ocr_engine import CertificateOCREngine
from security.hash_generator import HashGenerator, generate_certificate_hash, generate_academic_record_hash
from blockchain.blockchain_service import get_blockchain_service
from ai.predict_forgery import predict_forgery


class VerifierController:
    """
    Verifier-side certificate verification controller
    
    Workflow:
    1. Certificate Upload
    2. OCR Extraction
    3. AI Forgery Detection
    4. Hash Generation
    5. Blockchain Hash Retrieval
    6. Hash Comparison
    7. Final Decision Logic
    """
    
    def __init__(self, verbose: bool = True):
        """
        Initialize verifier controller
        
        Args:
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        
        # Initialize modules
        self.ocr_engine = CertificateOCREngine()
        self.hash_generator = HashGenerator()
        self.blockchain_service = get_blockchain_service()
        
        if self.verbose:
            print("✓ Verifier Controller initialized")
    
    def verify_certificate(self, certificate_path: str, output_dir: str = "output", **kwargs) -> Dict:
        """
        Complete verifier-side certificate verification workflow
        
        Args:
            certificate_path: Path to uploaded certificate file
            output_dir: Directory to save output files
            
        Returns:
            Dictionary containing verification results
        """
        
        if self.verbose:
            print("\n" + "="*80)
            print("VERIFIER CERTIFICATE VERIFICATION")
            print("="*80)
            print(f"Certificate: {certificate_path}")
            print(f"Timestamp: {datetime.now().isoformat()}")
            print("="*80)
        
        # Initialize result structure
        result = {
            'ocr_data': {},
            'ai_score': None,
            'ai_result': None,
            'generated_hash': None,
            'blockchain_hash': None,
            'hash_match': False,
            'final_status': 'UNKNOWN',
            'errors': [],
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # ========================================
            # STEP 1: CERTIFICATE UPLOAD (Already done)
            # ========================================
            if not os.path.exists(certificate_path):
                result['errors'].append('Certificate file not found')
                result['final_status'] = 'ERROR'
                return result
            
            if self.verbose:
                print("\n[STEP 1/7] Certificate uploaded ✓")
            
            # ========================================
            # STEP 2: OCR EXTRACTION
            # ========================================
            if self.verbose:
                print("\n[STEP 2/7] Extracting certificate data via OCR...")
            
            ocr_result = self._perform_ocr_extraction(certificate_path, output_dir)
            
            if ocr_result['status'] == 'FAIL':
                result['errors'].append('OCR extraction failed')
                result['ocr_data'] = ocr_result
                result['final_status'] = 'SUSPICIOUS'
                # Continue with verification even if OCR fails
            else:
                result['ocr_data'] = {
                    'certificate_id': ocr_result.get('certificate_id'),
                    'student_name': ocr_result.get('student_name'),
                    'roll_number': ocr_result.get('roll_number'),
                    'registration_number': ocr_result.get('registration_number') or ocr_result.get('certificate_id'),
                    'course': ocr_result.get('course'),
                    'university': ocr_result.get('university'),
                    'year': ocr_result.get('year'),
                    'cgpa': ocr_result.get('cgpa'),
                    'academic_data': ocr_result.get('academic_data')
                }
                
                if self.verbose:
                    print(f"  ✓ Certificate ID: {result['ocr_data']['certificate_id']}")
                    print(f"  ✓ Student Name: {result['ocr_data']['student_name']}")
                    print(f"  ✓ CGPA: {result['ocr_data']['cgpa']}")

            # Ownership verification step removed as per user request.
            
            # ========================================
            # STEP 3: AI FORGERY DETECTION
            # ========================================
            if self.verbose:
                print("\n[STEP 3/7] Running AI forgery detection...")
            
            ai_result = self._perform_ai_detection(certificate_path)
            
            if 'error' in ai_result:
                result['errors'].append(f"AI detection failed: {ai_result['error']}")
                result['ai_result'] = 'UNKNOWN'
                result['final_status'] = 'SUSPICIOUS'
            else:
                result['ai_score'] = ai_result.get('ai_score')
                result['ai_result'] = ai_result.get('ai_result')
                
                if self.verbose:
                    print(f"  ✓ AI Result: {result['ai_result']}")
                    print(f"  ✓ AI Score: {result['ai_score']}")
            
            # ========================================
            # STEP 4: HASH GENERATION
            # ========================================
            if self.verbose:
                print("\n[STEP 4/7] Generating certificate hash...")
            
            generated_hash = self._generate_certificate_hash(result['ocr_data'])
            
            if not generated_hash:
                result['errors'].append('Hash generation failed')
                result['final_status'] = 'ERROR'
                return result
            
            result['generated_hash'] = generated_hash
            
            if self.verbose:
                print(f"  ✓ Generated Hash: {generated_hash[:32]}...")
            
            # ========================================
            # STEP 5: BLOCKCHAIN VERIFICATION
            # ========================================
            if self.verbose:
                print("\n[STEP 5/7] Verifying against blockchain...")
            
            certificate_id = result['ocr_data'].get('certificate_id')
            
            if not certificate_id:
                result['errors'].append('Certificate ID not found - cannot verify on blockchain')
                result['final_status'] = 'Not Registered'
                result['blockchain_hash'] = None
                if self.verbose:
                    print("  ✗ Certificate ID missing in OCR results")
                return result
            else:
                # Use the improved verification logic from blockchain service
                # This handles normalization, comparison, and logging internally
                match, status = self.blockchain_service.verify_certificate(
                    certificate_id=certificate_id,
                    certificate_hash=result['generated_hash']
                )
                
                result['hash_match'] = match
                result['blockchain_status'] = status
                
                # Fetch the blockchain hash for display purposes
                h_result = self.blockchain_service.get_certificate_hash(certificate_id)
                result['blockchain_hash'] = h_result.get('hash')
                
                if status == "Not Registered":
                    result['final_status'] = 'Not Registered'
                    result['remarks'] = "the certificates are not registered"
                    if self.verbose:
                        print(f"  ✗ Status: {status} (Registration check failed)")
                    
                    # 5. Handle Not Registered Case: Immediately return
                    self._save_results(result, output_dir)
                    return result

                elif status == "Tampered":
                    result['final_status'] = 'Tampered'
                    result['remarks'] = "Hash Mismatch - Certificate Has Been Tampered"
                    if self.verbose:
                        print("  ✗ Status: Tampered (Hash Mismatch)")
                
                elif status == "Genuine":
                    result['final_status'] = 'Genuine'
                    result['remarks'] = "Certificate is valid and untampered (Blockchain Match)"
                    if self.verbose:
                        print("  ✓ Status: Genuine (Hash Match)")
                
                if self.verbose and result['blockchain_hash']:
                    print(f"  ✓ Blockchain Hash: {str(result['blockchain_hash'])[:32]}...")

            # ========================================
            # STEP 6: (Completed in Step 5 Logic)
            # ========================================
            # ========================================
            # STEP 7: FINAL DECISION (Already partially handled by status mapping)
            # ========================================
            
            if self.verbose:
                print(f"\n{'='*80}")
                print(f"FINAL STATUS: {result['final_status']}")
                print(f"{'='*80}")
            
            # Save results
            self._save_results(result, output_dir)
            
            return result
            
        except Exception as e:
            result['errors'].append(f"Verification error: {str(e)}")
            result['final_status'] = 'ERROR'
            
            if self.verbose:
                print(f"\n✗ Verification failed: {str(e)}")
            
            return result
    
    def _perform_ocr_extraction(self, certificate_path: str, output_dir: str) -> Dict:
        """
        Step 2: Perform OCR extraction
        
        Args:
            certificate_path: Path to certificate
            output_dir: Output directory
            
        Returns:
            OCR result dictionary
        """
        try:
            ocr_result = self.ocr_engine.process_certificate(
                image_path=certificate_path,
                output_dir=output_dir,
                save_intermediate=False
            )
            return ocr_result
            
        except Exception as e:
            return {
                'status': 'FAIL',
                'errors': [f"OCR extraction failed: {str(e)}"],
                'certificate_id': None,
                'student_name': None,
                'roll_number': None,
                'course': None,
                'university': None,
                'year': None
            }
    
    def _perform_ai_detection(self, certificate_path: str) -> Dict:
        """
        Step 3: Perform AI forgery detection
        
        Args:
            certificate_path: Path to certificate
            
        Returns:
            AI prediction result
        """
        try:
            ai_result = predict_forgery(certificate_path)
            return ai_result
            
        except Exception as e:
            return {'error': str(e)}
    
    def _generate_certificate_hash(self, ocr_data: Dict) -> Optional[str]:
        """
        Step 4: Generate SHA-256 hash of certificate data
        
        Args:
            ocr_data: Extracted certificate data
            
        Returns:
            SHA-256 hash string or None
        """
        try:
            # 1. Check if this is a multi-certificate academic dossier
            academic_data = ocr_data.get('academic_data')
            if academic_data:
                if self.verbose:
                    print("  ℹ Detected Academic Dossier - generating combined hash...")
                return generate_academic_record_hash(academic_data)
                
            # 2. Fallback to standard single certificate hash
            cert_hash = generate_certificate_hash(ocr_data)
            return cert_hash
            
        except Exception as e:
            if self.verbose:
                print(f"  ✗ Hash generation failed: {str(e)}")
            return None
    
    def _retrieve_blockchain_hash(self, certificate_id: str) -> Dict:
        """
        Step 5: Retrieve hash from blockchain
        
        Args:
            certificate_id: Certificate identifier
            
        Returns:
            Dictionary with success status and hash
        """
        try:
            if not self.blockchain_service.is_available():
                return {
                    'success': False,
                    'hash': None,
                    'error': 'Blockchain service not available'
                }
            
            result = self.blockchain_service.get_certificate_hash(certificate_id)
            return result
            
        except Exception as e:
            return {
                'success': False,
                'hash': None,
                'error': f'Blockchain retrieval failed: {str(e)}'
            }
    
    def _make_final_decision(
        self,
        hash_match: bool,
        ai_result: Optional[str],
        blockchain_hash: Optional[str]
    ) -> str:
        """
        Step 7: Make final verification decision
        
        Decision Logic:
        - If hash_match AND ai_result == "Genuine" → VERIFIED
        - If NOT hash_match → FAKE
        - Otherwise → SUSPICIOUS
        
        Args:
            hash_match: Whether hashes match
            ai_result: AI prediction result
            blockchain_hash: Hash from blockchain (None if not found)
            
        Returns:
            Final status: VERIFIED, FAKE, or SUSPICIOUS
        """
        
        # If certificate not registered on blockchain → FAKE
        if blockchain_hash is None:
            return "FAKE"
        
        # If hash doesn't match → FAKE (tampered)
        if not hash_match:
            return "FAKE"
        
        # If hash matches AND AI says Genuine → VERIFIED
        if hash_match and ai_result == "Genuine":
            return "VERIFIED"
        
        # All other cases → SUSPICIOUS
        return "SUSPICIOUS"
    
    def _save_results(self, result: Dict, output_dir: str):
        """
        Save verification results to JSON file
        
        Args:
            result: Verification result dictionary
            output_dir: Output directory
        """
        try:
            import json
            
            os.makedirs(output_dir, exist_ok=True)
            
            output_file = os.path.join(output_dir, 'verifier_result.json')
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            if self.verbose:
                print(f"\n✓ Results saved to: {output_file}")
                
        except Exception as e:
            if self.verbose:
                print(f"\n✗ Failed to save results: {str(e)}")


# Convenience function for direct use
def verify_certificate(certificate_path: str, output_dir: str = "output", verbose: bool = True, **kwargs) -> Dict:
    """
    Verify a certificate using the complete verifier workflow
    
    Args:
        certificate_path: Path to certificate file
        output_dir: Output directory for results
        verbose: Enable verbose logging
        **kwargs: Additional parameters (e.g., claimant_id)
        
    Returns:
        Verification result dictionary
    """
    controller = VerifierController(verbose=verbose)
    return controller.verify_certificate(certificate_path, output_dir, **kwargs)


if __name__ == "__main__":
    """Test the verifier controller"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python verifier_controller.py <certificate_path>")
        sys.exit(1)
    
    cert_path = sys.argv[1]
    
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║     VERIFIER CERTIFICATE VERIFICATION                        ║
    ║     Complete Verification Workflow                           ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    result = verify_certificate(cert_path, verbose=True)
    
    print("\n" + "="*80)
    print("VERIFICATION COMPLETE")
    print("="*80)
    print(f"\nFinal Status: {result['final_status']}")
    print(f"Hash Match: {result['hash_match']}")
    print(f"AI Result: {result['ai_result']}")
    print(f"Certificate ID: {result['ocr_data'].get('certificate_id')}")
    
    if result['errors']:
        print(f"\nErrors: {len(result['errors'])}")
        for error in result['errors']:
            print(f"  - {error}")
