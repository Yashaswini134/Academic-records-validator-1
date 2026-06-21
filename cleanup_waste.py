import os

files_to_remove = [
    r"c:\Users\shiva\Downloads\mini-ni\records-validator\ocr\extract_fields.py",
    r"c:\Users\shiva\Downloads\mini-ni\records-validator\ocr\preprocess.py",
    r"c:\Users\shiva\Downloads\mini-ni\records-validator\backend\routes.py"
]

for file_path in files_to_remove:
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Successfully deleted: {file_path}")
        else:
            print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error deleting {file_path}: {e}")

# Also remove all __pycache__ folders
import shutil
for root, dirs, files in os.walk(r"c:\Users\shiva\Downloads\mini-ni\records-validator"):
    if "__pycache__" in dirs:
        pycache_path = os.path.join(root, "__pycache__")
        try:
            shutil.rmtree(pycache_path)
            print(f"Successfully deleted: {pycache_path}")
        except Exception as e:
            print(f"Error deleting {pycache_path}: {e}")
