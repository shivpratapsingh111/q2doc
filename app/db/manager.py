# External imports
import psycopg
from pgvector.psycopg import register_vector

# Local imports
from app.core.logger import setup_logger
from app.config.config import (
    DB_HOST,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
    DB_PORT,
    LOG_LEVEL_DEBUG,
    APPLICATION_LOG_FILE,
)

logger = setup_logger(__name__, APPLICATION_LOG_FILE, LOG_LEVEL_DEBUG)


# ---
# Connection helpers
# ---


def get_connection(dbname=DB_NAME):
    conn = psycopg.connect(
        dbname=dbname, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT
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
    cur.execute(
        f"""
        CREATE EXTENSION IF NOT EXISTS vector;

        CREATE TABLE IF NOT EXISTS documents (
            id SERIAL PRIMARY KEY,
            session_id UUID NOT NULL,
            doc_path TEXT NOT NULL,
            chunk_index INT NOT NULL,
            chunk TEXT NOT NULL,
            embedding VECTOR({embedding_dim})
        );
    """
    )
    logger.info("Table 'documents' created or already exists.")
    cur.close()
    conn.close()


def reset_db():
    """Reset db, delete everything"""
    conn = get_connection(DB_NAME)
    cur = conn.cursor()
    logger.warning("Resetting Database.")
    cur.execute("DELETE FROM documents;")
    logger.info("Resetting database completed.")
    cur.close()
    conn.close()


# ---
# Data operations
# ---

def insert_document_chunks(
    session_id: str, doc_path: str, chunks: list[str], embeddings: list[list[float]]
):
    conn = get_connection(DB_NAME)
    cur = conn.cursor()
    values = [
        (session_id, doc_path, idx, chunk, emb)
        for idx, (chunk, emb) in enumerate(zip(chunks, embeddings))
    ]
    cur.executemany(
        "INSERT INTO documents (session_id, doc_path, chunk_index, chunk, embedding) VALUES (%s, %s, %s, %s, %s)",
        values,
    )
    conn.commit()
    logger.info(f"{len(chunks)} chunks inserted, Name: {doc_path}, ID: {session_id}")
    cur.close()
    conn.close()


def session_exists(session_id: str) -> bool:
    """Check if session_id exists in the documents table."""
    conn = get_connection(DB_NAME)
    cur = conn.cursor()

    query = "SELECT 1 FROM documents WHERE session_id = %s LIMIT 1"
    cur.execute(query, (session_id,))
    exists = cur.fetchone() is not None

    cur.close()
    conn.close()
    return exists


def semantic_search_by_session(
    session_id: str, query_embedding: list[float], top_k: int = 5
):
    """Perform semantic search on for a specific session."""
    conn = get_connection(DB_NAME)
    register_vector(conn)
    cur = conn.cursor()

    # Convert list to pgvector literal
    vector_literal = f"[{','.join(map(str, query_embedding))}]"

    query = f"""
        SELECT session_id, doc_path, chunk_index, chunk, embedding <=> %s::vector AS distance
        FROM documents
        WHERE session_id = %s
        ORDER BY embedding <=> %s::vector
        LIMIT %s
    """

    cur.execute(query, (vector_literal, session_id, vector_literal, top_k))
    results = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {
            "session_id": r[0],
            "doc_path": r[1],
            "chunk_index": r[2],
            "chunk": r[3],
            "distance": r[4],
        }
        for r in results
    ]
