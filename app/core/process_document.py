# External imports
import os, pymupdf
from google import genai

# Local imports
from app.core.logger import setup_logger
from app.db.manager import insert_document_chunks
from app.core.utils import make_chunks, get_embeddings
from app.config.config import LOG_LEVEL_DEBUG, APPLICATION_LOG_FILE, GEMINI_API_KEY

# Initialization
logger = setup_logger(__name__, APPLICATION_LOG_FILE, LOG_LEVEL_DEBUG)

# Logic
class ProcessDocument:
    def __init__(self):
        self.doc_path = None
        self.doc_name = None

    def process(self, doc_path: str, session_id: str) -> None:
        self.doc_path = doc_path
        self.doc_name = os.path.basename(doc_path)
        logger.info(f"Processing provided document [{self.doc_name}], Session ID [{session_id}]")
        text = self.get_text_from_doc(doc_path) # extract text from document
        chunks = make_chunks(
            text=text, size=500, overlap=100
        )  # convert text string to small chunks

        logger.debug(f"Converting text to embeddings for [{self.doc_name}]")
        embeddings = get_embeddings(data_list=chunks, embedding_type="RETRIEVAL_DOCUMENT")

        try:
            logger.debug(f"Inserting embeddings for [{self.doc_name}] in DB")
            insert_document_chunks(str(session_id), str(self.doc_path), chunks, embeddings)
        except Exception as e:
            logger.debug(f"Error while inserting embeddings for [{self.doc_name}] in DB: {e}")
        
        os.remove(doc_path) # remove uploaded file

    def get_text_from_doc(self, doc_path: str) -> str:
        if not os.path.exists(doc_path):
            msg = f"Provided document not found {doc_path}"
            logger.error(msg)
            raise FileNotFoundError(msg)
        try:
            doc = pymupdf.open(doc_path)
        except Exception as e:
            logger.error(f"Error in parsing the document [{self.doc_name}]: {e}")
        all_text = []
        for page in doc:
            text = (
                page.get_text().encode("utf8").decode()
            )  # keeping non ascii characters intentionally for emojis
            all_text.append(text)
        logger.info(
            f"Number of pages in document [{self.doc_name}], {len(doc)}"
        )
        all_text = " ".join(all_text)
        return all_text


# pd = ProcessDocument()
# pd.process("files/1.pdf")
