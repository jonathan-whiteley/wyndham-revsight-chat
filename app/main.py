"""RevSight Chat: Wyndham power-user chat over curated Genie agents and Genie One."""

import logging
import os

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from api import router as api_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="RevSight Chat", description="Wyndham revenue chat powered by Genie", version="1.0.0")
app.include_router(api_router)

frontend_path = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.isdir(frontend_path):
    app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
else:
    logger.warning(f"Frontend dist directory not found: {frontend_path}")
