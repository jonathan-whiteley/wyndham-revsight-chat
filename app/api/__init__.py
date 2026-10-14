"""API router for RevSight Chat."""

from fastapi import APIRouter

router = APIRouter(prefix="/api")

from . import health, models, fields, genie, genie_one  # noqa: E402

router.include_router(health.router)
router.include_router(models.router)
router.include_router(fields.router)
router.include_router(genie.router)
router.include_router(genie_one.router)
