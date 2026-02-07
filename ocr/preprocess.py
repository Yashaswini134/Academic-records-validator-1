"""
Image Preprocessing Module for Certificate OCR
Handles image enhancement and preparation for OCR
"""

import cv2
import numpy as np
from typing import Tuple, Optional
import os


class ImagePreprocessor:
    """Handles all image preprocessing operations for OCR"""
    
    def __init__(self):
        self.original_image = None
        self.processed_image = None
    
    def load_image(self, image_path: str) -> bool:
        """
        Load image from file path
        
        Args:
            image_path: Path to the certificate image
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not os.path.exists(image_path):
            print(f"Error: Image file not found at {image_path}")
            return False
        
        self.original_image = cv2.imread(image_path)
        
        if self.original_image is None:
            print(f"Error: Failed to load image from {image_path}")
            return False
        
        print(f"✓ Image loaded successfully: {image_path}")
        print(f"  Dimensions: {self.original_image.shape[1]}x{self.original_image.shape[0]}")
        return True
    
    def convert_to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """Convert image to grayscale"""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            print("✓ Converted to grayscale")
            return gray
        return image
    
    def remove_noise(self, image: np.ndarray) -> np.ndarray:
        """
        Remove noise using bilateral filter
        Preserves edges while removing noise
        """
        denoised = cv2.bilateralFilter(image, 9, 75, 75)
        print("✓ Noise removed (bilateral filter)")
        return denoised
    
    def apply_thresholding(self, image: np.ndarray) -> np.ndarray:
        """
        Apply adaptive thresholding for better text extraction
        Uses Gaussian adaptive thresholding
        """
        thresh = cv2.adaptiveThreshold(
            image,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11,
            2
        )
        print("✓ Adaptive thresholding applied")
        return thresh
    
    def deskew(self, image: np.ndarray) -> np.ndarray:
        """
        Deskew the image if it's rotated
        Detects and corrects skew angle
        """
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
            print(f"✓ Image deskewed by {angle:.2f} degrees")
            return rotated
        
        return image
    
    def enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """
        Enhance image contrast using CLAHE
        (Contrast Limited Adaptive Histogram Equalization)
        """
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
        print("✓ Contrast enhanced (CLAHE)")
        return enhanced
    
    def resize_for_ocr(self, image: np.ndarray, scale_factor: float = 2.0) -> np.ndarray:
        """
        Resize image for better OCR accuracy
        Larger images generally give better OCR results
        """
        height, width = image.shape[:2]
        new_width = int(width * scale_factor)
        new_height = int(height * scale_factor)
        
        resized = cv2.resize(
            image,
            (new_width, new_height),
            interpolation=cv2.INTER_CUBIC
        )
        print(f"✓ Image resized to {new_width}x{new_height} (scale: {scale_factor}x)")
        return resized
    
    def preprocess(self, image_path: str, save_intermediate: bool = False) -> Optional[np.ndarray]:
        """
        Complete preprocessing pipeline
        
        Args:
            image_path: Path to the certificate image
            save_intermediate: Whether to save intermediate processing steps
            
        Returns:
            Preprocessed image ready for OCR, or None if failed
        """
        print("\n" + "="*60)
        print("STARTING IMAGE PREPROCESSING")
        print("="*60)
        
        # Load image
        if not self.load_image(image_path):
            return None
        
        # Create output directory for intermediate images
        if save_intermediate:
            output_dir = os.path.join(os.path.dirname(image_path), "preprocessing_steps")
            os.makedirs(output_dir, exist_ok=True)
        
        # Step 1: Convert to grayscale
        gray = self.convert_to_grayscale(self.original_image)
        if save_intermediate:
            cv2.imwrite(os.path.join(output_dir, "1_grayscale.png"), gray)
        
        # Step 2: Enhance contrast
        enhanced = self.enhance_contrast(gray)
        if save_intermediate:
            cv2.imwrite(os.path.join(output_dir, "2_enhanced.png"), enhanced)
        
        # Step 3: Remove noise
        denoised = self.remove_noise(enhanced)
        if save_intermediate:
            cv2.imwrite(os.path.join(output_dir, "3_denoised.png"), denoised)
        
        # Step 4: Deskew
        deskewed = self.deskew(denoised)
        if save_intermediate:
            cv2.imwrite(os.path.join(output_dir, "4_deskewed.png"), deskewed)
        
        # Step 5: Apply thresholding
        thresh = self.apply_thresholding(deskewed)
        if save_intermediate:
            cv2.imwrite(os.path.join(output_dir, "5_thresholded.png"), thresh)
        
        # Step 6: Resize for better OCR
        final = self.resize_for_ocr(thresh, scale_factor=2.0)
        if save_intermediate:
            cv2.imwrite(os.path.join(output_dir, "6_final.png"), final)
        
        self.processed_image = final
        
        print("="*60)
        print("PREPROCESSING COMPLETE")
        print("="*60 + "\n")
        
        return final


def preprocess_certificate(image_path: str, save_steps: bool = False) -> Optional[np.ndarray]:
    """
    Convenience function to preprocess a certificate image
    
    Args:
        image_path: Path to certificate image
        save_steps: Whether to save intermediate processing steps
        
    Returns:
        Preprocessed image or None
    """
    preprocessor = ImagePreprocessor()
    return preprocessor.preprocess(image_path, save_intermediate=save_steps)


if __name__ == "__main__":
    # Test the preprocessing module
    test_image = "test.png"
    
    if os.path.exists(test_image):
        result = preprocess_certificate(test_image, save_steps=True)
        if result is not None:
            print("✓ Preprocessing test successful!")
    else:
        print(f"Test image '{test_image}' not found. Please provide a certificate image.")
