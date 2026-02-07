"""
Configuration file for OCR Engine
Customize these settings for your specific use case
"""

# ============================================================================
# TESSERACT CONFIGURATION
# ============================================================================

# Path to Tesseract executable (Windows)
# Set this if Tesseract is not in your system PATH
# Example: r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSERACT_PATH = None  # None = use system PATH

# Tesseract OCR configuration
# Page Segmentation Modes (PSM):
#   0 = Orientation and script detection (OSD) only
#   1 = Automatic page segmentation with OSD
#   3 = Fully automatic page segmentation (default)
#   4 = Assume a single column of text of variable sizes
#   6 = Assume a single uniform block of text
#   7 = Treat the image as a single text line
#   11 = Sparse text. Find as much text as possible
TESSERACT_CONFIG = '--psm 6'  # Single uniform block of text

# OCR Engine Mode (OEM):
#   0 = Legacy engine only
#   1 = Neural nets LSTM engine only
#   2 = Legacy + LSTM engines
#   3 = Default, based on what is available
TESSERACT_OEM = 3

# Language (default is English)
# For multiple languages: 'eng+hin' (English + Hindi)
TESSERACT_LANG = 'eng'


# ============================================================================
# IMAGE PREPROCESSING CONFIGURATION
# ============================================================================

# Grayscale conversion
ENABLE_GRAYSCALE = True

# Noise removal (bilateral filter)
ENABLE_NOISE_REMOVAL = True
BILATERAL_FILTER_D = 9          # Diameter of pixel neighborhood
BILATERAL_FILTER_SIGMA_COLOR = 75
BILATERAL_FILTER_SIGMA_SPACE = 75

# Contrast enhancement (CLAHE)
ENABLE_CONTRAST_ENHANCEMENT = True
CLAHE_CLIP_LIMIT = 2.0
CLAHE_TILE_GRID_SIZE = (8, 8)

# Deskewing
ENABLE_DESKEWING = True
DESKEW_ANGLE_THRESHOLD = 0.5    # Only deskew if angle > this value

# Adaptive thresholding
ENABLE_THRESHOLDING = True
THRESHOLD_BLOCK_SIZE = 11
THRESHOLD_C = 2

# Image resizing for better OCR
ENABLE_RESIZE = True
RESIZE_SCALE_FACTOR = 2.0       # 2.0 = double the size

# Save intermediate preprocessing steps (for debugging)
SAVE_INTERMEDIATE_STEPS = False


# ============================================================================
# FIELD EXTRACTION CONFIGURATION
# ============================================================================

# Minimum field lengths (validation)
MIN_CERTIFICATE_ID_LENGTH = 4
MIN_STUDENT_NAME_LENGTH = 4
MIN_ROLL_NUMBER_LENGTH = 4
MIN_COURSE_LENGTH = 3
MIN_UNIVERSITY_LENGTH = 5

# Year validation range
MIN_YEAR = 1950
MAX_YEAR_OFFSET = 1  # Current year + offset

# Required fields (must be present for PASS status)
REQUIRED_FIELDS = [
    'certificate_id',
    'student_name',
    'university'
]

# Optional fields (can be missing for PARTIAL status)
OPTIONAL_FIELDS = [
    'roll_number',
    'course',
    'year'
]

# Maximum allowed errors for PARTIAL status
MAX_ERRORS_FOR_PARTIAL = 2


# ============================================================================
# OUTPUT CONFIGURATION
# ============================================================================

# Default output directory
OUTPUT_DIR = "output"

# Output file names
OUTPUT_JSON_FILE = "ocr_result.json"
OUTPUT_RAW_TEXT_FILE = "ocr_raw_text.txt"
PREPROCESSING_STEPS_DIR = "preprocessing_steps"

# JSON output formatting
JSON_INDENT = 2
JSON_ENSURE_ASCII = False  # Allow Unicode characters


# ============================================================================
# HASH GENERATION CONFIGURATION
# ============================================================================

# Hash algorithm (sha256, sha1, md5)
HASH_ALGORITHM = 'sha256'

# Chunk size for reading large files (bytes)
HASH_CHUNK_SIZE = 8192


# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

# Enable verbose logging
VERBOSE_LOGGING = True

# Show progress indicators
SHOW_PROGRESS = True

# Print OCR raw text to console
PRINT_RAW_TEXT = False  # Set to True for debugging


# ============================================================================
# CUSTOM REGEX PATTERNS
# ============================================================================

# Add your custom regex patterns here for specific certificate formats
# These will be tried in addition to the default patterns

CUSTOM_CERTIFICATE_ID_PATTERNS = [
    # Example: r'ID[\s\-_:]*([A-Z0-9\-\/]+)',
]

CUSTOM_STUDENT_NAME_PATTERNS = [
    # Example: r'Student[\s\-_:]+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)',
]

CUSTOM_ROLL_NUMBER_PATTERNS = [
    # Example: r'Roll[\s\-_:]*([A-Z0-9\-\/]+)',
]

CUSTOM_COURSE_PATTERNS = [
    # Example: r'Course[\s\-_:]+([A-Za-z\s&,]+)',
]

CUSTOM_UNIVERSITY_PATTERNS = [
    # Example: r'University[\s\-_:]+([A-Za-z\s&,]+)',
]

CUSTOM_YEAR_PATTERNS = [
    # Example: r'Year[\s\-_:]+(\d{4})',
]


# ============================================================================
# PERFORMANCE CONFIGURATION
# ============================================================================

# Maximum image size (pixels) - resize if larger
MAX_IMAGE_WIDTH = 4000
MAX_IMAGE_HEIGHT = 4000

# Timeout for OCR processing (seconds)
OCR_TIMEOUT = 60


# ============================================================================
# INTEGRATION CONFIGURATION
# ============================================================================

# Enable integration with other modules
ENABLE_AI_INTEGRATION = False
ENABLE_BLOCKCHAIN_INTEGRATION = False
ENABLE_DATABASE_INTEGRATION = False

# API endpoints (if using REST APIs)
AI_VERIFICATION_API = "http://localhost:5000/api/verify"
BLOCKCHAIN_API = "http://localhost:8545"
DATABASE_API = "mongodb://localhost:27017/certificates"


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

"""
To use this configuration:

1. Import in your code:
   from config import *

2. Or load specific settings:
   from config import TESSERACT_PATH, OUTPUT_DIR

3. Override settings programmatically:
   import config
   config.TESSERACT_PATH = r"C:\Custom\Path\tesseract.exe"
   config.SAVE_INTERMEDIATE_STEPS = True

4. Use in ocr_engine.py:
   engine = CertificateOCREngine(tesseract_path=TESSERACT_PATH)
   result = engine.process_certificate(
       image_path="test.png",
       output_dir=OUTPUT_DIR,
       save_intermediate=SAVE_INTERMEDIATE_STEPS
   )
"""
