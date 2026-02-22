"""
Hash Generator Module for Certificate Verification
Generates SHA-256 hash of certificate data
"""

import hashlib
import os
import re
from typing import Optional, Dict, Any, Union


class HashGenerator:
    """Generates cryptographic hashes for certificate files"""
    
    @staticmethod
    def generate_file_hash(file_path: str, algorithm: str = 'sha256') -> Optional[str]:
        """
        Generate hash of a file
        
        Args:
            file_path: Path to the file
            algorithm: Hash algorithm to use (default: sha256)
            
        Returns:
            Hexadecimal hash string or None if failed
        """
        if not os.path.exists(file_path):
            print(f"Error: File not found at {file_path}")
            return None
        
        try:
            # Create hash object
            if algorithm == 'sha256':
                hash_obj = hashlib.sha256()
            elif algorithm == 'md5':
                hash_obj = hashlib.md5()
            elif algorithm == 'sha1':
                hash_obj = hashlib.sha1()
            else:
                print(f"Error: Unsupported algorithm '{algorithm}'")
                return None
            
            # Read file in chunks to handle large files
            chunk_size = 8192
            file_size = os.path.getsize(file_path)
            
            print(f"\nGenerating {algorithm.upper()} hash for: {os.path.basename(file_path)}")
            print(f"File size: {file_size:,} bytes")
            
            with open(file_path, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    hash_obj.update(chunk)
            
            hash_value = hash_obj.hexdigest()
            print(f"✓ Hash generated: {hash_value}")
            
            return hash_value
            
        except Exception as e:
            print(f"Error generating hash: {str(e)}")
            return None
    
    @staticmethod
    def generate_sha256(file_path: str) -> Optional[str]:
        """
        Generate SHA-256 hash (convenience method)
        
        Args:
            file_path: Path to the file
            
        Returns:
            SHA-256 hash string or None
        """
        return HashGenerator.generate_file_hash(file_path, 'sha256')
    
    @staticmethod
    def verify_hash(file_path: str, expected_hash: str, algorithm: str = 'sha256') -> bool:
        """
        Verify if file hash matches expected hash
        
        Args:
            file_path: Path to the file
            expected_hash: Expected hash value
            algorithm: Hash algorithm used
            
        Returns:
            True if hash matches, False otherwise
        """
        actual_hash = HashGenerator.generate_file_hash(file_path, algorithm)
        
        if actual_hash is None:
            return False
        
        matches = actual_hash.lower() == expected_hash.lower()
        
        if matches:
            print("✓ Hash verification PASSED")
        else:
            print("✗ Hash verification FAILED")
            print(f"  Expected: {expected_hash}")
            print(f"  Actual:   {actual_hash}")
        
        return matches
    
    @staticmethod
    def generate_text_hash(text: str, algorithm: str = 'sha256') -> str:
        """
        Generate hash of text content
        
        Args:
            text: Text to hash
            algorithm: Hash algorithm to use
            
        Returns:
            Hexadecimal hash string
        """
        if algorithm == 'sha256':
            hash_obj = hashlib.sha256()
        elif algorithm == 'md5':
            hash_obj = hashlib.md5()
        elif algorithm == 'sha1':
            hash_obj = hashlib.sha1()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
        
        hash_obj.update(text.encode('utf-8'))
        return hash_obj.hexdigest()
    
    @staticmethod
    def generate_data_hash(data: dict) -> str:
        """
        Generate hash of structured data (dictionary)
        Useful for hashing extracted certificate data
        
        Args:
            data: Dictionary of data to hash
            
        Returns:
            SHA-256 hash of the data
        """
        # Convert dict to sorted string for consistent hashing
        import json
        data_str = json.dumps(data, sort_keys=True)
        return HashGenerator.generate_text_hash(data_str)


def generate_certificate_hash(data: Dict[str, Any]) -> str:
    """
    Generate SHA-256 hash of certificate data using specific fields and normalization.
    
    Fields required:
    - Certificate ID
    - Student Name
    - University Name
    - Roll / Registration Number
    - Year of Passing
    - Course / Degree
    
    Process:
    1. Extract fields
    2. Normalize (trim, lowercase, single space, remove commas)
    3. Concatenate using '|' delimiter
    4. Generate SHA-256 hash
    
    Args:
        data: Dictionary containing certificate data
        
    Returns:
        SHA-256 hash string
        
    Raises:
        ValueError: If any required field is missing or empty
    """
    
    # Map of required fields to possible keys in input data
    # Priority: Exact match -> Alternate keys
    field_mappings = {
        'certificate_id': ['certificate_id', 'cert_id', 'id'],
        'student_name': ['student_name', 'name', 'student'],
        'university': ['university_name', 'university', 'college'],
        'roll_number': ['roll_number', 'roll', 'roll_no', 'registration_number', 'reg_no', 'registration', 'seat_no'],
        'year': ['year', 'passing_year', 'year_of_passing'],
        'course': ['course', 'degree', 'programme'],
        'cgpa': ['cgpa', 'gpa', 'percentage', 'marks']
    }
    
    # Order for concatenation: Certificate ID | Student Name | University Name | Roll / Registration Number | Year of Passing | Course / Degree | CGPA
    # Note: CGPA is added at the end for backward compatibility support if needed
    ordered_keys = ['certificate_id', 'student_name', 'university', 'roll_number', 'year', 'course', 'cgpa']
    
    normalized_values = []
    
    for key in ordered_keys:
        possible_keys = field_mappings[key]
        value = None
        
        # Find value across possible keys
        for k in possible_keys:
            if k in data:
                # Check directly if key exists, then check value
                val = data[k]
                if val is not None and str(val).strip() != "":
                    value = val
                    break
        
        # Check if value is found and not empty
        if value is None:
            # OPTIONAL FIELDS HANDLE (CGPA is optional for now to avoid breaking existing flows)
            if key == 'cgpa':
                normalized_values.append("0.00") # Default for missing CGPA
                continue
            raise ValueError(f"Missing required field: {key.replace('_', ' ').title()}")
            
        # Normalize
        # 1. Convert to string
        val_str = str(value)
        # 2. Trim leading/trailing spaces
        val_str = val_str.strip()
        # 3. Convert to lowercase
        val_str = val_str.lower()
        # 4. Remove unnecessary commas
        val_str = val_str.replace(',', '')
        # 5. Replace multiple spaces with single space
        val_str = re.sub(r'\s+', ' ', val_str)
        
        normalized_values.append(val_str)
        
    # Concatenate with '|'
    final_string = "|".join(normalized_values)
    
    # DEBUG: Print exact string being hashed
    print(f"\n[HASH DEBUG] String to Hash: {final_string}")
    
    # Create hash
    hash_obj = hashlib.sha256()
    hash_obj.update(final_string.encode('utf-8'))
    
    hash_hex = hash_obj.hexdigest()
    print(f"[HASH DEBUG] Final Hash: {hash_hex}\n")
    
    return hash_hex

if __name__ == "__main__":
    # Test the hash generator
    print("="*60)
    print("TESTING HASH GENERATOR - REVISED LOGIC")
    print("="*60)

    # Test Case 1: All fields present (Example from prompt)
    test_data = {
        'certificate_id': 'CERT123',
        'student_name': 'Yashaswini',
        'university_name': 'JNTU Hyderabad',
        'roll_number': '2406',
        'year': '2025',
        'course': 'BTech CSE'
    }
    
    try:
        print("\nTest 1 (Valid Data)...")
        hash_val = generate_certificate_hash(test_data)
        print(f"Generated Hash: {hash_val}")
        
        # Verify manual reconstruction
        # normalized: cert123|yashaswini|jntu hyderabad|2406|2025|btech cse
        expected_str = "cert123|yashaswini|jntu hyderabad|2406|2025|btech cse"
        expected_hash = hashlib.sha256(expected_str.encode('utf-8')).hexdigest()
        
        if hash_val == expected_hash:
            print("✓ Hash matches expected output")
        else:
            print(f"✗ Hash mismatch! Expected: {expected_hash}, Got: {hash_val}")
            
    except Exception as e:
        print(f"Test 1 Failed: {e}")

    # Test Case 2: Comma handling
    test_data_comma = {
        'certificate_id': 'CERT,123',
        'student_name': 'Yashaswini,',
        'university_name': 'JNTU, Hyderabad',
        'roll_number': '2406',
        'year': '2025',
        'course': 'BTech, CSE'
    }
    
    try:
        print("\nTest 2 (Comma Handling)...")
        hash_val = generate_certificate_hash(test_data_comma)
        print(f"Generated Hash: {hash_val}")
        if hash_val == expected_hash:
            print("✓ Commas removed correctly")
        else:
            print("✗ Commas removal failed")
    except Exception as e:
        print(f"Test 2 Failed: {e}")

    # Test Case 3: Missing field
    test_data_missing = {
        'student_name': 'Yashaswini',
        'university_name': 'JNTU Hyderabad'
    }
    
    try:
        print("\nTest 3 (Missing Field)...")
        generate_certificate_hash(test_data_missing)
        print("FAILED (Should have raised error)")
    except ValueError as e:
        print(f"PASSED (Caught expected error: {e})")

    print("\n" + "="*60)
