import os
import shutil
from fastapi import UploadFile

def save_uploaded_file(file: UploadFile, file_path: str):
    """
    Saves the uploaded file to the specified path.
    """
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
