# External imports
import psycopg2
from psycopg2.extras import execute_values
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from typing import List

# Local imports
from core.logger import setup_logger
from config.config import DB_HOST, DB_NAME, DB_USER, DB_PASSWORD, DB_PORT, LOG_LEVEL_DEBUG, APPLICATION_LOG_FILE
logger = setup_logger(__name__, APPLICATION_LOG_FILE, LOG_LEVEL_DEBUG)


# ---
# Connection helpers
# ---

def get_connection(dbname=DB_NAME):
    conn = psycopg2.connect(
        dbname=dbname,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = True
    return conn

# ---
# Database setup
# ---

def init_db():
    """Create the database if it does not exist"""
    conn = get_connection("postgres")  # connect to default postgres db
    cur = conn.cursor()
    cur.execute(f"SELECT 1 FROM pg_database WHERE datname='{DB_NAME}';")
    if not cur.fetchone():
        cur.execute(f"CREATE DATABASE {DB_NAME};")
        logger.info(f"Database '{DB_NAME}' created.")
    else:
        logger.info(f"Database '{DB_NAME}' already exists.")
    cur.close()
    conn.close()

def create_documents_table(embedding_dim: int = 3072):
    """Create the documents table if it does not exist"""
    conn = get_connection(DB_NAME)
    cur = conn.cursor()
    cur.execute(f"""
        CREATE EXTENSION IF NOT EXISTS vector;

        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            doc_path TEXT,
            chunk_index INT,
            content TEXT,
            embedding VECTOR({embedding_dim})
        );
    """)
    logger.info("Table 'documents' created or already exists.")
    cur.close()
    conn.close()

def reset_db():
    """Reset db, delete everything"""
    conn = get_connection(DB_NAME)
    cur = conn.cursor()
    logger.warning("ResettingdDatabase.")
    cur.execute("DELETE FROM documents;")
    logger.info("Resetting database completed.")
    cur.close()
    conn.close()

# ---
# Data operations
# ---

def insert_document_chunks(doc_path: str, chunks: List[str], embeddings: List[List[float]]):
    conn = get_connection(DB_NAME)
    cur = conn.cursor()
    values = [(doc_path, idx, chunk, emb) for idx, (chunk, emb) in enumerate(zip(chunks, embeddings))]
    execute_values(
        cur,
        "INSERT INTO documents (doc_path, chunk_index, content, embedding) VALUES %s",
        values
    )
    logger.info(f"{len(chunks)} chunks inserted for {doc_path}.")
    cur.close()
    conn.close()