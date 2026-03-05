"""Intels API endpoints for querying case intelligence records."""

import sqlite3
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter()

# Default database path, can be overridden for testing
DB_PATH: str = "tsm.db"


class IntelResponse(BaseModel):
    """Schema for intel response."""
    id: int
    article_id: int
    is_case_related: bool
    case_type: Optional[str] = None
    region: Optional[str] = None
    risk_score: int = 0
    risk_level: str = "low"
    keywords_matched: Optional[str] = None
    status: str = "new"


class IntelListResponse(BaseModel):
    """Schema for intel list response."""
    items: List[IntelResponse]
    total: int


def get_db_path() -> Optional[str]:
    """Get the database path (can be overridden in tests)."""
    return None


@router.get("/api/intels", response_model=IntelListResponse)
def list_intels(
    status: Optional[str] = None,
    risk_level: Optional[str] = None,
    region: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db_path: Optional[str] = Depends(get_db_path)
) -> IntelListResponse:
    """Query intel records with optional filters."""
    db = db_path or DB_PATH
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    # Build query with filters
    conditions = []
    params = []

    if status:
        conditions.append("status = ?")
        params.append(status)
    if risk_level:
        conditions.append("risk_level = ?")
        params.append(risk_level)
    if region:
        conditions.append("region = ?")
        params.append(region)

    where_clause = " AND ".join(conditions) if conditions else "1=1"

    # Get total count
    cursor.execute(f"SELECT COUNT(*) FROM case_intels WHERE {where_clause}", params)
    total = cursor.fetchone()[0]

    # Get items
    cursor.execute(
        f"SELECT id, article_id, is_case_related, case_type, region, risk_score, risk_level, keywords_matched, status FROM case_intels WHERE {where_clause} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        params + [limit, offset]
    )
    rows = cursor.fetchall()
    conn.close()

    items = [
        IntelResponse(
            id=row[0],
            article_id=row[1],
            is_case_related=bool(row[2]),
            case_type=row[3],
            region=row[4],
            risk_score=row[5],
            risk_level=row[6],
            keywords_matched=row[7],
            status=row[8]
        )
        for row in rows
    ]

    return IntelListResponse(items=items, total=total)


@router.get("/api/intels/{intel_id}", response_model=IntelResponse)
def get_intel(
    intel_id: int,
    db_path: Optional[str] = Depends(get_db_path)
) -> IntelResponse:
    """Get a single intel record by ID."""
    db = db_path or DB_PATH
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, article_id, is_case_related, case_type, region, risk_score, risk_level, keywords_matched, status FROM case_intels WHERE id = ?",
        (intel_id,)
    )
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="Intel not found")

    return IntelResponse(
        id=row[0],
        article_id=row[1],
        is_case_related=bool(row[2]),
        case_type=row[3],
        region=row[4],
        risk_score=row[5],
        risk_level=row[6],
        keywords_matched=row[7],
        status=row[8]
    )