"""
Hash Generator Module for Certificate Verification
Generates SHA-256 hash of certificate files
"""

import hashlib
import os
from typing import Optional


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


def generate_certificate_hash(certificate_path: str) -> Optional[str]:
    """
    Convenience function to generate SHA-256 hash of certificate
    
    Args:
        certificate_path: Path to certificate file
        
    Returns:
        SHA-256 hash or None
    """
    return HashGenerator.generate_sha256(certificate_path)


if __name__ == "__main__":
    # Test the hash generator
    test_file = "test.png"
    
    if os.path.exists(test_file):
        print("="*60)
        print("TESTING HASH GENERATOR")
        print("="*60)
        
        # Generate hash
        hash_value = generate_certificate_hash(test_file)
        
        if hash_value:
            print("\n" + "="*60)
            print("HASH GENERATION SUCCESSFUL")
            print("="*60)
            
            # Test verification
            print("\nTesting hash verification...")
            HashGenerator.verify_hash(test_file, hash_value)
            
            # Test with wrong hash
            print("\nTesting with incorrect hash...")
            HashGenerator.verify_hash(test_file, "0" * 64)
        
        # Test text hashing
        print("\n" + "="*60)
        print("Testing text hashing...")
        text_hash = HashGenerator.generate_text_hash("Hello, World!")
        print(f"Text hash: {text_hash}")
        
        # Test data hashing
        print("\nTesting data hashing...")
        sample_data = {
            "name": "John Doe",
            "roll": "12345",
            "year": "2023"
        }
        data_hash = HashGenerator.generate_data_hash(sample_data)
        print(f"Data hash: {data_hash}")
        
    else:
        print(f"Test file '{test_file}' not found.")
