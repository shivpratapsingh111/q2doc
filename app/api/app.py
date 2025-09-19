# External imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Local imports
from app.api.upload import routes as upload
from app.api.prompt import routes as prompt
from app.db.manager import init_db, create_documents_table
from app.core.logger import setup_logger
from app.config.config import LOG_LEVEL_DEBUG, APPLICATION_LOG_FILE


# ---------------------
# Initialization
# ---------------------

logger = setup_logger(__name__, APPLICATION_LOG_FILE, LOG_LEVEL_DEBUG)

@asynccontextmanager
async def lifespan(app: FastAPI):
	# Before Application Startup
	logger.info("Initializing database")
	try:
		init_db()
		create_documents_table()
		logger.info("Database initialized")
	except Exception as e:
		logger.error(f"Error while initializing database: {e}")

	yield

	# Before Application Shutdown
	logger.warning("Application Shutting down")


app = FastAPI(lifespan=lifespan)

# Setup Cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # for sample project I have intentionally used wildacard here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(upload.router)
app.include_router(prompt.router)


# ---------------------
# Logic
# ---------------------

# Root route
@app.get("/")
async def main():
	return {"status": "running"}