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
        
        Raises:
            FileNotFoundError: If image file doesn't exist
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image file not found at: {image_path}")
        
        self.original_image = cv2.imread(image_path)
        
        if self.original_image is None:
            raise ValueError(f"Failed to load image from: {image_path}")
        
        print(f"✓ Image loaded successfully: {image_path}")
        print(f"  Dimensions: {self.original_image.shape[1]}x{self.original_image.shape[0]}")
        return True
    
    def convert_to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """
        Convert image to grayscale
        
        Args:
            image: Input image
            
        Returns:
            Grayscale image
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            print("✓ Converted to grayscale")
            return gray
        return image
    
    def apply_gaussian_blur(self, image: np.ndarray) -> np.ndarray:
        """
        Apply Gaussian blur to reduce noise
        
        Args:
            image: Input grayscale image
            
        Returns:
            Blurred image
        """
        blurred = cv2.GaussianBlur(image, (5, 5), 0)
        print("✓ Gaussian blur applied")
        return blurred
    
    def apply_adaptive_threshold(self, image: np.ndarray) -> np.ndarray:
        """
        Apply adaptive thresholding for better text extraction
        Uses Gaussian adaptive thresholding
        
        Args:
            image: Input grayscale image
            
        Returns:
            Thresholded binary image
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
    
    def morphological_opening(self, image: np.ndarray) -> np.ndarray:
        """
        Apply morphological opening to remove noise
        Opening = Erosion followed by Dilation
        
        Args:
            image: Input binary image
            
        Returns:
            Cleaned image
        """
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        opening = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel, iterations=1)
        print("✓ Morphological opening applied (noise removed)")
        return opening
    
    def enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """
        Enhance image contrast using CLAHE
        (Contrast Limited Adaptive Histogram Equalization)
        
        Args:
            image: Input grayscale image
            
        Returns:
            Contrast-enhanced image
        """
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(image)
        print("✓ Contrast enhanced (CLAHE)")
        return enhanced
    
    def ensure_resolution(self, image: np.ndarray, target_dpi: int = 300) -> np.ndarray:
        """
        Ensure image resolution is at least 300 DPI equivalent
        Upscale if necessary
        
        Args:
            image: Input image
            target_dpi: Target DPI (default 300)
            
        Returns:
            Resized image if needed
        """
        height, width = image.shape[:2]
        
        # Assume original is 72 DPI (screen resolution)
        # Calculate required scale to reach target DPI
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
            print(f"✓ Image upscaled to {new_width}x{new_height} (~{target_dpi} DPI)")
            return resized
        else:
            print(f"✓ Image resolution sufficient: {width}x{height}")
            return image
    
    def deskew(self, image: np.ndarray) -> np.ndarray:
        """
        Deskew the image if it's rotated
        Detects and corrects skew angle
        
        Args:
            image: Input binary image
            
        Returns:
            Deskewed image
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
    
    def preprocess(self, image_path: str, save_intermediate: bool = False) -> Optional[np.ndarray]:
        """
        Complete preprocessing pipeline optimized for OCR
        
        Pipeline:
        1. Load image
        2. Convert to grayscale
        3. Ensure minimum resolution (300 DPI)
        4. Enhance contrast
        5. Apply Gaussian blur
        6. Apply adaptive thresholding
        7. Morphological opening (noise removal)
        8. Deskew if needed
        
        Args:
            image_path: Path to the certificate image
            save_intermediate: Whether to save intermediate processing steps
            
        Returns:
            Preprocessed image ready for OCR, or None if failed
        """
        print("\n" + "="*70)
        print("STARTING IMAGE PREPROCESSING FOR OCR")
        print("="*70)
        
        try:
            # Load image
            self.load_image(image_path)
            
            # Create output directory for intermediate images
            if save_intermediate:
                output_dir = os.path.join(os.path.dirname(image_path), "preprocessing_steps")
                os.makedirs(output_dir, exist_ok=True)
                # Save original
                cv2.imwrite(os.path.join(output_dir, "0_original.png"), self.original_image)
            
            # Step 1: Convert to grayscale
            gray = self.convert_to_grayscale(self.original_image)
            if save_intermediate:
                cv2.imwrite(os.path.join(output_dir, "1_grayscale.png"), gray)

            # Step 2: Apply Gaussian blur
            blurred = self.apply_gaussian_blur(gray)
            if save_intermediate:
                cv2.imwrite(os.path.join(output_dir, "2_gaussian_blur.png"), blurred)

            # Step 3: Apply adaptive thresholding
            thresh = self.apply_adaptive_threshold(blurred)
            if save_intermediate:
                cv2.imwrite(os.path.join(output_dir, "3_adaptive_threshold.png"), thresh)

            # Step 4: Morphological opening (remove noise)
            cleaned = self.morphological_opening(thresh)
            if save_intermediate:
                cv2.imwrite(os.path.join(output_dir, "4_morphological_opening.png"), cleaned)

            # Step 5: Enhance contrast
            enhanced = self.enhance_contrast(cleaned)
            if save_intermediate:
                cv2.imwrite(os.path.join(output_dir, "5_contrast_enhanced.png"), enhanced)

            # Step 6: Ensure minimum resolution (300 DPI equivalent)
            high_res = self.ensure_resolution(enhanced, target_dpi=300)
            if save_intermediate:
                cv2.imwrite(os.path.join(output_dir, "6_high_resolution.png"), high_res)

            # Optional: Deskew at the end
            final = self.deskew(high_res)
            if save_intermediate:
                cv2.imwrite(os.path.join(output_dir, "7_final_deskewed.png"), final)

            self.processed_image = final
            
            print("="*70)
            print("PREPROCESSING COMPLETE - IMAGE READY FOR OCR")
            print("="*70 + "\n")
            
            return final
            
        except Exception as e:
            print(f"✗ Preprocessing failed: {str(e)}")
            return None


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
