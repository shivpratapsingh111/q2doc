# External imports
from google import genai
from google.genai import types
# Local imports
from core.logger import setup_logger
from core.utils import get_embeddings
from db.manager import semantic_search_by_session
from config.config import (
    LOG_LEVEL_DEBUG,
    APPLICATION_LOG_FILE,
    GEMINI_API_KEY,
    CHAT_MODEL,
)

# Initialization
logger = setup_logger(__name__, APPLICATION_LOG_FILE, LOG_LEVEL_DEBUG)
client = genai.Client(api_key=GEMINI_API_KEY)


# Logic
class ProcessPrompt:
    def __init__(self):
        self.prompt = None
        self.session_id = None

    def process(self, session_id: str, prompt: str) -> list[dict]:
        self.prompt = prompt
        self.session_id = session_id
        logger.info(
            f'Processing provided prompt ["{self.prompt}"] for session_id [session_id]'
        )

        # get the text converted into embeddings
        embeddings_2d = get_embeddings(
            data_list=[prompt], embedding_type="RETRIEVAL_QUERY"
        )
        embedding_1d = embeddings_2d[0]

        try:
            result = semantic_search_by_session(
                session_id=self.session_id, query_embedding=embedding_1d, top_k=3
            )
            logger.info(
                f'Results from semantic search for prompt ["{self.prompt}"]: {result}'
            )
        except Exception as e:
            logger.debug(
                f'Error while doing semantic search for prompt ["{self.prompt}"] in DB: {e}'
            )

        try:
            answer = self.ask_llm_with_context(user_prompt=self.prompt, context=result)
            logger.info(f'LLM\'s answer for ["{self.prompt}"]: {answer}')
            return answer
        except Exception as e:
            logger.debug(
                f'Error while communicating to LLM for prompt ["{self.prompt}"] with additional provided context: {e}'
            )

    # Convert the result dict to string for the LLM to understand better
    def build_context_for_llm(self, context: list[dict]) -> str:
        formatted = []
        for r in context:
            formatted.append(
                f'Chunk {r["chunk_index"]} from {r["doc_path"]}: "{r["chunk"]}"'
            )

        return "\n".join(formatted)


# External imports
from google import genai

# Local imports
from core.logger import setup_logger
from core.utils import get_embeddings
from db.manager import semantic_search_by_session
from config.config import LOG_LEVEL_DEBUG, APPLICATION_LOG_FILE, GEMINI_API_KEY

# Initialization
logger = setup_logger(__name__, APPLICATION_LOG_FILE, LOG_LEVEL_DEBUG)
client = genai.Client(api_key=GEMINI_API_KEY)


# Logic
class ProcessPrompt:
    def __init__(self):
        self.prompt = None
        self.session_id = None

    def process(self, session_id: str, prompt: str) -> list[dict]:
        self.prompt = prompt
        self.session_id = session_id
        logger.info(
            f'Processing provided prompt ["{self.prompt}"] for session_id [{session_id}]'
        )

        # get the text converted into embeddings
        embeddings_2d = get_embeddings(
            data_list=[prompt], embedding_type="RETRIEVAL_QUERY"
        )
        embedding_1d = embeddings_2d[0]

        try:
            result = semantic_search_by_session(
                session_id=self.session_id, query_embedding=embedding_1d, top_k=3
            )
            logger.debug(
                f'Results from semantic search for prompt ["{self.prompt}"]: {result}'
            )
        except Exception as e:
            logger.debug(
                f'Error while doing semantic search for prompt ["{self.prompt}"] in DB: {e}'
            )

        try:
            answer = self.ask_llm_with_context(user_prompt=self.prompt, context=result)
            logger.info(f'LLM\'s answer for ["{self.prompt}"]: {answer}')
            return answer
        except Exception as e:
            logger.debug(
                f'Error while communicating to LLM for prompt ["{self.prompt}"] with additional provided context: {e}'
            )

    # Convert the result dict to string for the LLM to understand better
    def build_context_for_llm(self, context: list[dict]) -> str:
        formatted = []
        for r in context:
            formatted.append(
                f'Chunk {r["chunk_index"]} from {r["doc_path"]}: "{r["chunk"]}"'
            )

        return "\n".join(formatted)

    def ask_llm_with_context(self, user_prompt: str, context: list[dict]) -> str:
        context = self.build_context_for_llm(context=context)
        SYSTEM_INSTRUCTION = ("""
                    You are an assistant, who answers questions utilising the provided additional context.\n
                    Rules:\n
                    1. Answer using ONLY the provided document chunks. Quote directly.\n
                    2. Always include reference after you complete your answer in this format: `Source file: {doc_path}.` If the sources are from same file do not repeat them reference.\n
                    3. Never invent document content that isn't present in the chunks.
            """)
        PROMPT = ("""
            ADDITIONAL CONTEXT: 
            ```
            {context}
            ```
      
            QUESTION: {question}
        """).format(context=context, question=user_prompt)
        response = client.models.generate_content(
            model=CHAT_MODEL,
            config=types.GenerateContentConfig(
                system_instruction=str(SYSTEM_INSTRUCTION)
            ),
            contents=PROMPT,
        )

        return response.text
