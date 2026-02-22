"""
Enhanced Image Preprocessing Module for Certificate OCR
Improved pipeline with better noise reduction and text enhancement
"""

import cv2
import numpy as np
from typing import Tuple, Optional, Dict
import os


class EnhancedImagePreprocessor:
    """Enhanced image preprocessing with advanced techniques"""
    
    def __init__(self):
        self.original_image = None
        self.processed_image = None
    
    def load_image(self, image_path: str) -> bool:
        """Load image from file path"""
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found at: {image_path}")
        
        self.original_image = cv2.imread(image_path)
        
        if self.original_image is None:
            raise ValueError(f"Failed to load image from: {image_path}")
        
        print(f"✓ Image loaded successfully: {image_path}")
        print(f"  Dimensions: {self.original_image.shape[1]}x{self.original_image.shape[0]}")
        return True
    
    def convert_to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """Convert image to grayscale"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            return gray
        return image
    
    def denoise(self, image: np.ndarray) -> np.ndarray:
        """Apply advanced denoising"""
        denoised = cv2.fastNlMeansDenoising(image, None, h=10, templateWindowSize=7, searchWindowSize=21)
        return denoised
    
    def enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """Enhance contrast using CLAHE"""
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
        return enhanced
    
    def apply_gaussian_blur(self, image: np.ndarray) -> np.ndarray:
        """Apply Gaussian blur to reduce noise"""
        blurred = cv2.GaussianBlur(image, (3, 3), 0)
        return blurred
    
    def apply_adaptive_threshold(self, image: np.ndarray) -> np.ndarray:
        """Apply adaptive thresholding for better text extraction"""
        thresh = cv2.adaptiveThreshold(
            image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            15,  # Increased block size for better results
            3    # Increased constant
        )
        return thresh
    
    def morphological_operations(self, image: np.ndarray) -> np.ndarray:
        """Apply morphological operations to clean up the image"""
        # Remove small noise
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        opening = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=1)
        
        # Close small gaps
        kernel2 = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        closing = cv2.morphologyEx(opening, cv2.MORPH_CLOSE, kernel2, iterations=1)
        
        return closing
    
    def sharpen(self, image: np.ndarray) -> np.ndarray:
        """Sharpen the image for better OCR"""
        kernel = np.array([[-1,-1,-1],
                          [-1, 9,-1],
                          [-1,-1,-1]])
        sharpened = cv2.filter2D(image, -1, kernel)
        return sharpened
    
    def ensure_resolution(self, image: np.ndarray, target_dpi: int = 300) -> np.ndarray:
        """Ensure image resolution is at least 300 DPI equivalent"""
        height, width = image.shape[:2]
        
        # Assume original is 72 DPI (screen resolution)
        current_dpi = 72
        scale_factor = target_dpi / current_dpi
        
        # Only upscale if image is small
        if width < 2000 or height < 2000:
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            
            resized = cv2.resize(
                image,
                (new_width, new_height),
                interpolation=cv2.INTER_CUBIC
            )
            return resized
        else:
            return image
    
    def deskew(self, image: np.ndarray) -> np.ndarray:
        """Deskew the image if it's rotated"""
        coords = np.column_stack(np.where(image > 0))
        if len(coords) == 0:
            return image
        
        angle = cv2.minAreaRect(coords)[-1]
        
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        # Only deskew if angle is significant
        if abs(angle) > 0.5:
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            rotated = cv2.warpAffine(
                image,
                M,
                (w, h),
                flags=cv2.INTER_CUBIC,
                borderMode=cv2.BORDER_REPLICATE
            )
            return rotated
        
        return image
    
    def preprocess(self, image_path: str, save_intermediate: bool = False) -> Optional[np.ndarray]:
        """
        Complete optimized preprocessing pipeline
        
        Pipeline:
        1. Load image
        2. Convert to grayscale
        3. Simple resolution check
        4. CLAHE Contrast enhancement
        5. Gaussian blur (Denoising)
        6. Adaptive thresholding
        7. Morphological operations
        8. Deskew
        9. Sharpen
        
        Args:
            image_path: Path to certificate image
            save_intermediate: Whether to save intermediate processing steps
            
        Returns:
            Preprocessed image ready for OCR, or None if failed
        """
        print("\n" + "="*70)
        print("ENHANCED IMAGE PREPROCESSING PIPELINE (HIGH QUALITY)")
        print("="*70)
        
        try:
            # Step 1: Load image
            if not self.load_image(image_path):
                return None
            
            # Step 2: Convert to grayscale
            gray = self.convert_to_grayscale(self.original_image)
            
            # Step 3: Upscale significantly (4x) for better OCR
            # This matches aggressive_ocr.py logic
            h, w = gray.shape[:2]
            print(f"Original size: {w}x{h}")
            
            if w < 3000: # Upscale most images
                print("Upscaling image (4x) for better OCR...")
                scale = 4.0
                # Use INTER_CUBIC for better quality
                gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
                print(f"New size: {gray.shape[1]}x{gray.shape[0]}")
            
            # Step 4: Denoise - using fastNlMeansDenoising (Stronger)
            print("Applying heavy denoising...")
            denoised = cv2.fastNlMeansDenoising(gray, None, h=10, templateWindowSize=7, searchWindowSize=21)
            
            # Step 5: Enhance contrast
            print("Enhancing contrast (CLAHE)...")
            enhanced = self.enhance_contrast(denoised)
            
            # Step 6: Sharpen BEFORE thresholding
            print("Sharpening...")
            sharpened = self.sharpen(enhanced)
            
            # Step 7: Apply adaptive thresholding
            # Using Gaussian C with slightly different parameters for cleaner text
            print("Applying adaptive thresholding...")
            thresh = cv2.adaptiveThreshold(
                sharpened,
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                15, # Block size
                5   # C constant (higher removes more noise)
            )
            
            # Step 8: Morphological operations (Clean up)
            cleaned = self.morphological_operations(thresh)
            
            # Step 9: Deskew
            deskewed = self.deskew(cleaned)
            
            self.processed_image = deskewed
            
            if save_intermediate:
                # Save debug image
                base_dir = os.path.dirname(image_path)
                debug_path = os.path.join(base_dir, "..", "output", "debug_preprocessed.jpg")
                os.makedirs(os.path.dirname(debug_path), exist_ok=True)
                cv2.imwrite(debug_path, self.processed_image)
                print(f"Debug image saved to: {debug_path}")
            
            return self.processed_image
            
        except Exception as e:
            print(f"\n✗ Preprocessing failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def get_preprocessing_variations(self, image_path: str) -> Dict[str, np.ndarray]:
        """
        Generate multiple preprocessing variations to find the best one for OCR.
        
        Returns:
            Dictionary of {name: processed_image_array}
        """
        variations = {}
        
        if not self.load_image(image_path):
            return variations
            
        # Base: Grayscale
        gray = self.convert_to_grayscale(self.original_image)
        variations['1_Standard_Gray'] = gray
        
        # Variation 1: Simple Threshold (Otsu) - Good for clean scans
        _, bin_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        variations['2_Binary_Otsu'] = bin_otsu
        
        # Variation 2: Adaptive Threshold (Gaussian) - Good for shadows/gradients
        # Block size 15, C=5 (Moderate)
        adaptive = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 5)
        variations['3_Adaptive_Gaussian'] = adaptive
        
        # Variation 3: High Contrast + Upscale (The "Aggressive" one)
        # Upscale 2x
        h, w = gray.shape[:2]
        upscaled = cv2.resize(gray, None, fx=2.0, fy=2.0, interpolation=cv2.INTER_CUBIC)
        # Denoise
        denoised = cv2.fastNlMeansDenoising(upscaled, None, h=10, templateWindowSize=7, searchWindowSize=21)
        # Contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        contrast = clahe.apply(denoised)
        # Threshold
        aggressive_thresh = cv2.adaptiveThreshold(contrast, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 5)
        variations['4_Aggressive_Upscale'] = aggressive_thresh
        
        # Variation 4: Denoised + Threshold (No upscale) - Good for noisy patterns
        denoised_simple = cv2.GaussianBlur(gray, (5, 5), 0)
        clean_thresh = cv2.adaptiveThreshold(denoised_simple, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        variations['5_Denoised_Threshold'] = clean_thresh

        return variations


# Backward compatibility
class ImagePreprocessor(EnhancedImagePreprocessor):
    """Wrapper for backward compatibility"""
    pass


def preprocess_certificate(image_path: str, save_steps: bool = False) -> Optional[np.ndarray]:
    """
    Convenience function to preprocess a certificate image
    
    Args:
        image_path: Path to certificate image
        save_steps: Whether to save intermediate processing steps
        
    Returns:
        Preprocessed image or None
    """
    preprocessor = EnhancedImagePreprocessor()
    return preprocessor.preprocess(image_path, save_intermediate=save_steps)


if __name__ == "__main__":
    # Test the preprocessing module
    import sys
    
    if len(sys.argv) > 1:
        test_image = sys.argv[1]
    else:
        test_image = "test.png"
    
    if os.path.exists(test_image):
        print(f"Testing preprocessing on: {test_image}")
        result = preprocess_certificate(test_image, save_steps=True)
        if result is not None:
            print("\n✓ Preprocessing test successful!")
            print(f"  Output shape: {result.shape}")
    else:
        print(f"Test image '{test_image}' not found.")
        print("Usage: python preprocess.py <image_path>")
