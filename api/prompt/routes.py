# External imports
import os, pymupdf
from fastapi import APIRouter, UploadFile, BackgroundTasks
from pathlib import Path

# Local imports
from config.config import UPLOAD_DIR, LOG_LEVEL_DEBUG, APPLICATION_LOG_FILE
from core.logger import setup_logger
from core.process_document import ProcessDocument

# Initialization
router = APIRouter()
pd = ProcessDocument()
logger = setup_logger(__name__, APPLICATION_LOG_FILE, LOG_LEVEL_DEBUG)
UPLOAD_DIR = Path(UPLOAD_DIR)
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.put("/prompt")
async def process_prompt(file: UploadFile, background_tasks: BackgroundTasks):
    

    return {"success": True, "message": "File uploaded successfully"}

