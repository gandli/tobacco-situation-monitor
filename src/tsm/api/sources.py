"""Sources API endpoints."""

from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from tsm.services import source_manager

router = APIRouter()


class SourceCreate(BaseModel):
    """Schema for creating a source."""
    name: str
    list_url: str


class SourceResponse(BaseModel):
    """Schema for source response."""
    id: int
    name: str
    list_url: str


def get_db_path() -> Optional[str]:
    """Get the database path (can be overridden in tests)."""
    return None


@router.post("/api/sources", status_code=201, response_model=SourceResponse)
def create_source(
    payload: SourceCreate,
    db_path: Optional[str] = Depends(get_db_path)
) -> SourceResponse:
    """Create a new source."""
    source = source_manager.create_source(
        source_manager.SourceCreate(name=payload.name, list_url=payload.list_url),
        db_path=db_path
    )
    return SourceResponse(id=source.id, name=source.name, list_url=source.list_url)