# External imports
import os, json
from fastapi import APIRouter, BackgroundTasks
from pathlib import Path
from pydantic import BaseModel

# Local imports
from app.config.config import UPLOAD_DIR, LOG_LEVEL_DEBUG, APPLICATION_LOG_FILE
from app.core.process_prompt import ProcessPrompt
from app.core.logger import setup_logger
from app.db.manager import session_exists

# Initialization
router = APIRouter()
pp = ProcessPrompt()
logger = setup_logger(__name__, APPLICATION_LOG_FILE, LOG_LEVEL_DEBUG)
UPLOAD_DIR = Path(UPLOAD_DIR)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Models
class Prompt(BaseModel):
    session_id: str
    prompt: str

# Logic
@router.post("/prompt")
async def process_prompt(data: Prompt, background_tasks: BackgroundTasks):

    # background_tasks.add_task(pp.process, data.session_id, data.prompt)
    if session_exists(session_id=data.session_id):
        answer = pp.process(data.session_id, data.prompt)
        answer = json.loads(answer)
        return {"success": True, "message": "Prompt processed successfully", "data": {"session_id": data.session_id, "response": answer}}
    else:
        return {"success": False, "message": "Provided session_id does not exists in database", "data": {"session_id": data.session_id}}