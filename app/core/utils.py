# External imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from google import genai
from google.genai import types

# Local imports
from app.core.logger import setup_logger
from app.config.config import (
    LOG_LEVEL_DEBUG,
    APPLICATION_LOG_FILE,
    GEMINI_API_KEY,
    EMBEDDING_MODEL,
)

# Initialization
logger = setup_logger(__name__, APPLICATION_LOG_FILE, LOG_LEVEL_DEBUG)
client = genai.Client(
    api_key=GEMINI_API_KEY, http_options=types.HttpOptions(timeout=30_000)
)


def get_embeddings(data_list: list[str], embedding_type: str) -> list[list[float]]:
    try:
        result = client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=data_list,
            config=types.EmbedContentConfig(task_type=embedding_type),
        )
        embeddings = []
        for em in result.embeddings:
            embeddings.append(em.values)
        return embeddings
    except Exception as e:
        logger.error("Error while converting text to embeddings.")


def make_chunks(text: str, size: int, overlap: int) -> list[str]:
    try:
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=size,
            chunk_overlap=overlap,
            length_function=len,
            is_separator_regex=False,
        )
    except Exception as e:
        logger.error(f"Something went wrong while converting text into chunks")
    chunks = text_splitter.split_text(text)
    logger.info(f"Total chunks formed: {len(chunks)}")
    logger.info(f"Chunks:\n{chunks}\n---")
    return chunks
