# External imports
import os, pymupdf, uuid
from fastapi import APIRouter, UploadFile, BackgroundTasks
from pathlib import Path

# Local imports
from app.config.config import UPLOAD_DIR, LOG_LEVEL_DEBUG, APPLICATION_LOG_FILE, MAX_FILE_SIZE
from app.core.logger import setup_logger
from app.core.process_document import ProcessDocument

# Initialization
router = APIRouter()
pd = ProcessDocument()
logger = setup_logger(__name__, APPLICATION_LOG_FILE, LOG_LEVEL_DEBUG)
UPLOAD_DIR = Path(UPLOAD_DIR)
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.put("/upload")
async def process_file(file: UploadFile, background_tasks: BackgroundTasks):
    
    file_path = UPLOAD_DIR / file.filename
    session_id = uuid.uuid4() # To map each document with the ID
    
    try:
        contents = await file.read()
        size = len(contents)

        if size > MAX_FILE_SIZE:
            return {"success": False, "message": "Only files with size under 1 MB are supported", "data": {"filename": file.filename, "size": size}}


        await file.seek(0)
        try: 
            pymupdf.open(stream=contents, filetype="pdf")
        except Exception as e:
            logger.error(f"Invalid PDF file provided, Name: {file.filename}, Size: {size} bytes, Error: {e}")
            return {"success": False, "message": "Invalid PDF provided", "data": {"filename": file.filename, "size": size, "exception": str(e)}}
        
        with open(file_path, "wb") as f:
            f.write(contents)
        logger.info(f"Uploaded file saved in {file_path}")

    except Exception as e:
        logger.error("Error while saving the provided file")
    
    background_tasks.add_task(pd.process, file_path, str(session_id))
    return {"success": True, "message": "File uploaded successfully", "data": {"session_id": str(session_id), "filename": file.filename, "size": size}}

