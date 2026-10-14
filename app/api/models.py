"""Models endpoint."""

import logging
from fastapi import APIRouter
from services.models_config import get_all_models, get_app_config

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/models")
def get_models():
    """Get available data models for Genie."""
    return get_all_models()


@router.get("/config")
def get_config():
    """Catalog and schema this deployment reads from."""
    return get_app_config()
