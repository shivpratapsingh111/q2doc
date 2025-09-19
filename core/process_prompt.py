# External imports
import os
from google import genai

# Local imports
from core.logger import setup_logger
from core.utils import make_chunks, get_embeddings
from db.manager import insert_document_chunks
from config.config import LOG_LEVEL_DEBUG, APPLICATION_LOG_FILE, GEMINI_API_KEY

# Initialization
logger = setup_logger(__name__, APPLICATION_LOG_FILE, LOG_LEVEL_DEBUG)
client = genai.Client(api_key=GEMINI_API_KEY)

# Logic
class ProcessPrompt:
    def __init__(self):
        self.prompt = None

    def process(self, prompt: str) -> None:
        self.prompt = prompt
        logger.info(f"Processing provided prompt {self.prompt}")
        
		# convert text string to small chunks
        chunks = make_chunks(
            text=prompt, size=100, overlap=20
        )
        
		# get the text converted into embeddings
        embeddings = get_embeddings(data_list=chunks, embedding_type="RETRIEVAL_QUERY")

        # write one time so don't have to make calls to DB
        os.makedirs("embeddings", exist_ok=True)
        with open("embeddings/prompt_embeddings.txt", "w") as f:
            for em in embeddings:
                f.write(",".join(map(str, em)) + "\n")

        try:
            insert_document_chunks(str(self.doc_path), chunks, embeddings)
        except Exception as e:
            logger.debug(f"Error while inserting embeddings for [{self.doc_name}] in DB: {e}")


