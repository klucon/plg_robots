from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base import get_db_session

from .service import get_robots_txt

router = APIRouter(tags=["plg_robots"])


@router.get("/robots.txt")
async def robots_txt(
    request: Request,
    db: AsyncSession = Depends(get_db_session),
) -> Response:
    content = await get_robots_txt(db)
    if content is None:
        raise HTTPException(status_code=404)
    return Response(content=content, media_type="text/plain; charset=utf-8")
