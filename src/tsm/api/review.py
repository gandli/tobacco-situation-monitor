"""Review API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from tsm.services import review_service

router = APIRouter()


class ReviewIn(BaseModel):
    """Schema for review input."""
    action: str
    comment: Optional[str] = None


class ReviewResponse(BaseModel):
    """Schema for review response."""
    id: int
    intel_id: int
    action: str
    comment: Optional[str] = None


def get_db_path() -> Optional[str]:
    """Get the database path (can be overridden in tests)."""
    return None


@router.post("/api/intels/{intel_id}/review", response_model=ReviewResponse)
def review_intel(
    intel_id: int,
    payload: ReviewIn,
    db_path: Optional[str] = Depends(get_db_path)
) -> ReviewResponse:
    """Submit a review action for an intel record."""
    review_log = review_service.submit_review(
        intel_id,
        review_service.ReviewIn(action=payload.action, comment=payload.comment),
        db_path=db_path
    )
    return ReviewResponse(
        id=review_log.id,
        intel_id=review_log.intel_id,
        action=review_log.action,
        comment=review_log.comment
    )