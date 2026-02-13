"""
Main Controller for Certificate Verification System
Acts as the central orchestrator connecting OCR, Hash, and Decision Engine modules
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import OCR module
from ocr.ocr_engine import CertificateOCREngine

# Import Security module
from security.hash_generator import HashGenerator

# Import Decision Engine (AI-integrated version)
from backend.decision_engine import DecisionEngine



class CertificateVerificationController:
    """
    Main controller that orchestrates the complete certificate verification pipeline
    
    Responsibilities:
    - Coordinate between OCR, Hash, and Decision Engine modules
    - Manage the verification workflow
    - Aggregate results from all modules
    - Generate final verification report
    """
    
    def __init__(self, tesseract_path: Optional[str] = None, verbose: bool = True):
        """
        Initialize the verification controller
        
        Args:
            tesseract_path: Optional path to Tesseract executable
            verbose: Enable verbose logging
        """
        self.verbose = verbose
        
        # Initialize OCR engine
        self.ocr_engine = CertificateOCREngine(tesseract_path=tesseract_path)
        
        # Initialize Decision Engine (with AI integration)
        self.decision_engine = DecisionEngine()
        
        if self.verbose:
            print("=" * 70)
            print("Certificate Verification Controller Initialized")
            print("=" * 70)
    
    def verify_certificate(
        self,
        certificate_path: str,
        output_dir: str = "output",
        save_intermediate: bool = False
    ) -> Dict:
        """
        Complete certificate verification pipeline
        
        Args:
            certificate_path: Path to certificate image file
            output_dir: Directory to save output files
            save_intermediate: Whether to save intermediate OCR processing steps
            
        Returns:
            Dictionary containing complete verification results
        """
        start_time = datetime.now()
        
        if self.verbose:
            print("\n" + "=" * 70)
            print("STARTING CERTIFICATE VERIFICATION")
            print("=" * 70)
            print(f"Certificate: {certificate_path}")
            print(f"Timestamp: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 70)
        
        # Validate input
        if not os.path.exists(certificate_path):
            return self._create_error_result(
                certificate_path,
                "Certificate file not found",
                start_time
            )
        
        try:
            # STEP 1: Run OCR Processing
            if self.verbose:
                print("\n[STEP 1/3] Running OCR Processing...")
            
            ocr_result = self._run_ocr_processing(
                certificate_path,
                output_dir,
                save_intermediate
            )
            
            if self.verbose:
                print(f"✓ OCR Status: {ocr_result.get('status', 'UNKNOWN')}")
            
            # STEP 2: Generate Certificate Hash
            if self.verbose:
                print("\n[STEP 2/3] Generating Certificate Hash...")
            
            hash_result = self._generate_hash(certificate_path)
            
            if self.verbose:
                if hash_result['success']:
                    print(f"✓ Hash Generated: {hash_result['hash'][:16]}...")
                else:
                    print(f"✗ Hash Generation Failed: {hash_result['error']}")
            
            # STEP 3: Run Decision Engine
            if self.verbose:
                print("\n[STEP 3/3] Running Decision Engine...")
            
            final_result = self._run_decision_engine(
                ocr_result,
                hash_result,
                certificate_path,
                start_time
            )
            
            if self.verbose:
                print(f"✓ Final Decision: {final_result['final_decision']}")
            
            # Save final result
            self._save_final_result(final_result, output_dir)
            
            # Print summary
            if self.verbose:
                self._print_verification_summary(final_result)
            
            return final_result
            
        except Exception as e:
            if self.verbose:
                print(f"\n✗ Error during verification: {str(e)}")
            
            return self._create_error_result(
                certificate_path,
                f"Verification failed: {str(e)}",
                start_time
            )
    
    def _run_ocr_processing(
        self,
        certificate_path: str,
        output_dir: str,
        save_intermediate: bool
    ) -> Dict:
        """
        Run OCR processing on certificate
        
        Args:
            certificate_path: Path to certificate file
            output_dir: Output directory
            save_intermediate: Save intermediate steps
            
        Returns:
            OCR processing results
        """
        try:
            result = self.ocr_engine.process_certificate(
                image_path=certificate_path,
                output_dir=output_dir,
                save_intermediate=save_intermediate
            )
            return result
            
        except Exception as e:
            return {
                'status': 'FAIL',
                'errors': [f"OCR processing failed: {str(e)}"],
                'certificate_id': None,
                'student_name': None,
                'roll_number': None,
                'course': None,
                'university': None,
                'year': None,
                'cgpa': None
            }
    
    def _generate_hash(self, certificate_path: str) -> Dict:
        """
        Generate SHA-256 hash of certificate file
        
        Args:
            certificate_path: Path to certificate file
            
        Returns:
            Dictionary with hash generation results
        """
        try:
            hash_value = HashGenerator.generate_sha256(certificate_path)
            
            if hash_value:
                return {
                    'success': True,
                    'hash': hash_value,
                    'algorithm': 'SHA-256',
                    'error': None
                }
            else:
                return {
                    'success': False,
                    'hash': None,
                    'algorithm': 'SHA-256',
                    'error': 'Hash generation returned None'
                }
                
        except Exception as e:
            return {
                'success': False,
                'hash': None,
                'algorithm': 'SHA-256',
                'error': str(e)
            }
    
    def _run_decision_engine(
        self,
        ocr_result: Dict,
        hash_result: Dict,
        certificate_path: str,
        start_time: datetime
    ) -> Dict:
        """
        Run decision engine to determine final verification status
        
        Args:
            ocr_result: Results from OCR processing
            hash_result: Results from hash generation
            certificate_path: Path to certificate file
            start_time: Processing start time
            
        Returns:
            Final verification result
        """
        # Calculate processing time
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Run decision engine (with AI integration)
        decision = self.decision_engine.make_decision(
            ocr_result, 
            hash_result, 
            certificate_image_path=certificate_path
        )
        
        # Compile final result
        final_result = {
            # Certificate data from OCR
            'certificate_id': ocr_result.get('certificate_id'),
            'student_name': ocr_result.get('student_name'),
            'roll_number': ocr_result.get('roll_number'),
            'course': ocr_result.get('course'),
            'university': ocr_result.get('university'),
            'year': ocr_result.get('year'),
            'cgpa': ocr_result.get('cgpa'),
            
            # Hash information
            'hash': hash_result.get('hash'),
            'hash_algorithm': hash_result.get('algorithm'),
            
            # Processing status
            'ocr_status': ocr_result.get('status'),
            'ocr_errors': ocr_result.get('errors', []),
            'hash_status': 'SUCCESS' if hash_result.get('success') else 'FAILED',
            
            # AI analysis (if available)
            'ai_analysis': decision.get('ai_analysis', {}),
            
            # Decision engine results
            'final_decision': decision['decision'],
            'decision_confidence': decision['confidence'],
            'remarks': decision['remarks'],
            'flags': decision['flags'],
            
            # Metadata
            'certificate_path': certificate_path,
            'processing_time': f"{processing_time:.2f}s",
            'timestamp': end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'verification_version': '2.0'  # Updated to 2.0 with AI integration
        }
        
        return final_result
    
    def _create_error_result(
        self,
        certificate_path: str,
        error_message: str,
        start_time: datetime
    ) -> Dict:
        """
        Create error result when verification fails
        
        Args:
            certificate_path: Path to certificate file
            error_message: Error description
            start_time: Processing start time
            
        Returns:
            Error result dictionary
        """
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        return {
            'certificate_id': None,
            'student_name': None,
            'roll_number': None,
            'course': None,
            'university': None,
            'year': None,
            'cgpa': None,
            'hash': None,
            'hash_algorithm': None,
            'ocr_status': 'FAIL',
            'ocr_errors': [error_message],
            'hash_status': 'NOT_ATTEMPTED',
            'final_decision': 'SUSPICIOUS',
            'decision_confidence': 'HIGH',
            'remarks': f"Verification failed: {error_message}",
            'flags': ['PROCESSING_ERROR'],
            'certificate_path': certificate_path,
            'processing_time': f"{processing_time:.2f}s",
            'timestamp': end_time.strftime('%Y-%m-%d %H:%M:%S'),
            'verification_version': '1.0'
        }
    
    def _save_final_result(self, result: Dict, output_dir: str):
        """
        Save final verification result to JSON file
        
        Args:
            result: Verification result dictionary
            output_dir: Output directory
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Save to JSON file
            output_file = os.path.join(output_dir, "verification_result.json")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            if self.verbose:
                print(f"\n✓ Results saved to: {output_file}")
                
        except Exception as e:
            if self.verbose:
                print(f"\n✗ Failed to save results: {str(e)}")
    
    def _print_verification_summary(self, result: Dict):
        """
        Print verification summary to console
        
        Args:
            result: Verification result dictionary
        """
        print("\n" + "=" * 70)
        print("VERIFICATION SUMMARY")
        print("=" * 70)
        
        print(f"\n📋 Certificate Information:")
        print(f"   Certificate ID: {result.get('certificate_id', 'N/A')}")
        print(f"   Student Name:   {result.get('student_name', 'N/A')}")
        print(f"   Roll Number:    {result.get('roll_number', 'N/A')}")
        print(f"   Course:         {result.get('course', 'N/A')}")
        print(f"   University:     {result.get('university', 'N/A')}")
        print(f"   Year:           {result.get('year', 'N/A')}")
        print(f"   CGPA:           {result.get('cgpa', 'N/A')}")
        
        print(f"\n🔐 Security:")
        hash_val = result.get('hash', 'N/A')
        if hash_val and hash_val != 'N/A':
            print(f"   Hash: {hash_val[:32]}...")
        else:
            print(f"   Hash: {hash_val}")
        
        print(f"\n📊 Processing Status:")
        print(f"   OCR Status:     {result.get('ocr_status', 'N/A')}")
        print(f"   Hash Status:    {result.get('hash_status', 'N/A')}")
        print(f"   Processing Time: {result.get('processing_time', 'N/A')}")
        
        # Display AI analysis if available
        ai_analysis = result.get('ai_analysis', {})
        if ai_analysis.get('ai_enabled'):
            print(f"\n🤖 AI Analysis:")
            print(f"   AI Score:       {ai_analysis.get('ai_score', 'N/A'):.3f}")
            print(f"   AI Result:      {ai_analysis.get('ai_result', 'N/A')}")
        else:
            print(f"\n🤖 AI Analysis:    Not available")
        
        print(f"\n⚖️  Final Decision:")
        decision = result.get('final_decision', 'N/A')
        confidence = result.get('decision_confidence', 'N/A')
        
        # Color coding for decision
        if decision == 'VERIFIED':
            decision_display = f"✓ {decision} (Confidence: {confidence})"
        else:
            decision_display = f"⚠ {decision} (Confidence: {confidence})"
        
        print(f"   {decision_display}")
        print(f"   Remarks: {result.get('remarks', 'N/A')}")
        
        # Display flags if any
        flags = result.get('flags', [])
        if flags:
            print(f"\n🚩 Flags:")
            for flag in flags:
                print(f"   - {flag}")
        
        print("\n" + "=" * 70)


def main():
    """
    Main entry point for testing the controller
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Certificate Verification Controller'
    )
    parser.add_argument(
        'certificate',
        help='Path to certificate image file'
    )
    parser.add_argument(
        '--output',
        default='output',
        help='Output directory (default: output)'
    )
    parser.add_argument(
        '--save-intermediate',
        action='store_true',
        help='Save intermediate OCR processing steps'
    )
    parser.add_argument(
        '--tesseract-path',
        help='Path to Tesseract executable'
    )
    
    args = parser.parse_args()
    
    # Initialize controller
    controller = CertificateVerificationController(
        tesseract_path=args.tesseract_path,
        verbose=True
    )
    
    # Run verification
    result = controller.verify_certificate(
        certificate_path=args.certificate,
        output_dir=args.output,
        save_intermediate=args.save_intermediate
    )
    
    # Exit with appropriate code
    if result['final_decision'] == 'VERIFIED':
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
