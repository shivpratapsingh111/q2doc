# External imports
import os, pymupdf
from langchain_text_splitters import RecursiveCharacterTextSplitter
from google import genai
from google.genai import types
from google.genai import types

# Local imports
from core.logger import setup_logger
from db.manager import insert_document_chunks, init_db, create_documents_table
from config.config import LOG_LEVEL_DEBUG, APPLICATION_LOG_FILE, GEMINI_API_KEY

# Initialization
logger = setup_logger(__name__, APPLICATION_LOG_FILE, LOG_LEVEL_DEBUG)
client = genai.Client(api_key=GEMINI_API_KEY)
init_db()
create_documents_table()

# Logic
class ProcessDocument:
    def __init__(self):
        self.doc_path = None
        self.doc_name = None

    def process(self, doc_path: str) -> list[list[float]]:
        self.doc_path = doc_path
        self.doc_name = os.path.basename(doc_path)

        text = self.get_text_from_doc(doc_path)  # extract text from document
        chunks = self.make_chunks(
            text=text, size=100, overlap=20
        )  # convert text string to small chunks
        embeddings = self.get_embeddings(data_list=chunks)
        
        # write one time so don't have to make calls to DB
        os.makedirs("embeddings", exist_ok=True)
        with open("embeddings/embeddings_1_pdf.txt", "w") as f:
            for em in embeddings:
                f.write(",".join(map(str, em)) + "\n")

        try:
            insert_document_chunks(self.doc_path, chunks, embeddings)
        except Exception as e:
            logger.debug(f"Error while inserting embeddings for [{self.doc_name}] in DB: {e}")

    def get_embeddings(self, data_list: list[str]) -> list[types.ContentEmbedding]:

        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=data_list,
            config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT")
        )
        embeddings = []
        print(f"Embedding Type: {type(result)}")
        for em in result.embeddings:
            embeddings.append(em.values)
        return embeddings
    
    def make_chunks(self, text: str, size: int, overlap: int) -> list[str]:
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=size,
                chunk_overlap=overlap,
                length_function=len,
                is_separator_regex=False,
            )
        except Exception as e:
            logger.error(
                f"Something went wrong while converting text into chunks for [{self.doc_name}]"
            )
        chunks = text_splitter.split_text(text)
        logger.info(f"Total chunks formed [{self.doc_name}]: {len(chunks)}")
        logger.info(f"Chunks [{self.doc_name}]\n{chunks}\n---")
        return chunks

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


pd = ProcessDocument()
pd.process("files/1.pdf")
