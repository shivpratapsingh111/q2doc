# External imports
from google import genai
from google.genai import types
from pydantic import BaseModel

# Local imports
from app.core.logger import setup_logger
from app.core.utils import get_embeddings
from app.db.manager import semantic_search_by_session
from app.config.config import (
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
        for data in context:
            formatted.append(
                f'Chunk {data["chunk_index"]} from {data["doc_path"]}: "{data["chunk"]}"'
            )

        return "\n".join(formatted)

    def ask_llm_with_context(self, user_prompt: str, context: list[dict]) -> dict:
        context = self.build_context_for_llm(context=context)

        # Model to get answer in the same fomat
        class Answer(BaseModel):
            answer: str
            source_file: list[str]

        SYSTEM_INSTRUCTION = """
                    You are an assistant. Follow these rules:
                    Rules:
                    1. Use ONLY provided chunks; quote directly. Ignore out-of-context questions.
                    2. Do not invent content.
                    3. Always cite sources. If multiple from same file, list once: `"source_file": ["file.doc"]` (base name only).
                """
        PROMPT = (
            """
            Answer using the context below.
            CONTEXT:
            {context}
            QUESTION: {question}
        """
        ).format(context=context, question=user_prompt)
        response = client.models.generate_content(
            model=CHAT_MODEL,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0),
                response_mime_type="application/json",
                response_schema=Answer,
                system_instruction=str(SYSTEM_INSTRUCTION),
            ),
            contents=PROMPT,
        )
        logger.info(response.text)
        return response.text
