import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER")
