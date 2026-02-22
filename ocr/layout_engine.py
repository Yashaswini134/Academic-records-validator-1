"""
Layout-Aware OCR Engine
Uses coordinate data to extract fields based on physical document layout
rather than just text pattern matching.
"""

import pytesseract
from pytesseract import Output
import numpy as np
from typing import Dict, List, Optional, Any

class LayoutOCREngine:
    def __init__(self, tesseract_cmd: Optional[str] = None):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    def analyze_layout(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Run OCR and return list of dicts: {'left': int, 'top': int, 'width': int, 'height': int, 'conf': int, 'text': str}
        """
        data = pytesseract.image_to_data(image, output_type=Output.DICT)
        extracted_words = []
        
        num_boxes = len(data['text'])
        for i in range(num_boxes):
            text = data['text'][i].strip()
            conf = int(data['conf'][i])
            
            if conf > 30 and text:
                extracted_words.append({
                    'left': data['left'][i],
                    'top': data['top'][i],
                    'width': data['width'][i],
                    'height': data['height'][i],
                    'conf': conf,
                    'text': text
                })
        
        return extracted_words

    def find_text_right_of(self, words: List[Dict[str, Any]], label_keywords: List[str], x_margin=100, y_margin=20) -> Optional[str]:
        """
        Find text that is physically to the RIGHT of a label.
        Useful for "Name: John Doe" or "Roll No: 12345"
        """
        # Find the label candidate
        label_word = None
        for word in words:
            for keyword in label_keywords:
                if keyword.lower() in word['text'].lower():
                    label_word = word
                    break
            if label_word:
                break
        
        if not label_word:
            return None
            
        label_right = label_word['left'] + label_word['width']
        label_top = label_word['top']
        label_bottom = label_word['top'] + label_word['height']
        
        # Find value words
        values = []
        for word in words:
            # Word must be to the right of the label, roughly same vertical line
            if (word['left'] > label_right) and \
               (word['top'] >= label_top - y_margin) and \
               (word['top'] <= label_bottom + y_margin):
                values.append(word)
        
        # Sort by left coordinate (reading order)
        values.sort(key=lambda x: x['left'])
        
        if not values:
            return None
            
        return " ".join([w['text'] for w in values])

    def find_text_below(self, words: List[Dict[str, Any]], label_keywords: List[str], y_search_limit=200, x_margin=50) -> Optional[str]:
        """
        Find text that is physically BELOW a label.
        Useful for extracting Name if it's under a "Student Name" header.
        """
        label_word = None
        for word in words:
            for keyword in label_keywords:
                if keyword.lower() in word['text'].lower():
                    label_word = word
                    break
            if label_word:
                break
                
        if not label_word:
            return None
            
        label_bottom = label_word['top'] + label_word['height']
        
        # Find candidates strictly below
        candidates = []
        for word in words:
            if (word['top'] > label_bottom) and \
               (word['top'] < label_bottom + y_search_limit) and \
               (abs(word['left'] - label_word['left']) < x_margin + 200): # Roughly column aligned
                candidates.append(word)
        
        if not candidates:
            return None
            
        # Sort top-to-bottom, left-to-right
        candidates.sort(key=lambda x: (x['top'], x['left']))
        
        # Simple line grouping
        lines = []
        current_line = []
        last_top = -100
        
        for w in candidates:
            if abs(w['top'] - last_top) > 20: # New line threshold
                if current_line:
                    lines.append(" ".join([wl['text'] for wl in current_line]))
                current_line = []
                last_top = w['top']
            current_line.append(w)
            
        if current_line:
            lines.append(" ".join([wl['text'] for wl in current_line]))
            
        return "\n".join(lines[:2]) # Return max 2 lines

