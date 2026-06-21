import os
import cv2
import numpy as np
from PIL import Image
from typing import List, Optional

class PDFHandler:
    """
    Handles PDF splitting into pages and conversion to images for OCR.
    """
    
    def __init__(self, output_dir: str = "temp_pages"):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
    def split_and_convert(self, pdf_path: str) -> List[str]:
        """
        Splits PDF into pages and converts each to an image.
        Returns a list of image file paths.
        """
        if not pdf_path.lower().endswith('.pdf'):
            return [pdf_path] # Assume it's already an image
            
        print(f"Processing PDF: {pdf_path}")
        image_paths = []
        
        try:
            import fitz # PyMuPDF
            doc = fitz.open(pdf_path)
            for i in range(len(doc)):
                page = doc.load_page(i)
                pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72)) # 300 DPI
                img_path = os.path.join(self.output_dir, f"page_{i}.jpg")
                pix.save(img_path)
                image_paths.append(img_path)
            doc.close()
            print(f"✓ Split {len(image_paths)} pages from PDF via PyMuPDF")
            return image_paths
        except ImportError:
            print("⚠ PyMuPDF (fitz) not installed. Trying pdf2image...")
        except Exception as e:
            print(f"⚠ PyMuPDF failed: {e}")
            
        try:
            from pdf2image import convert_from_path
            images = convert_from_path(pdf_path, dpi=300)
            for i, image in enumerate(images):
                img_path = os.path.join(self.output_dir, f"page_{i}.jpg")
                image.save(img_path, 'JPEG')
                image_paths.append(img_path)
            print(f"✓ Split {len(image_paths)} pages from PDF via pdf2image")
            return image_paths
        except ImportError:
            print("⚠ pdf2image not installed.")
        except Exception as e:
            print(f"⚠ pdf2image failed: {e}")
            
        print("✗ No PDF processing library available. Please install PyMuPDF (pip install pymupdf).")
        return []
