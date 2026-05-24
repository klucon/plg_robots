from __future__ import annotations

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.admin.deps import CurrentAdminUser
from src.api.admin.render import admin_render
from src.core.acl import require_admin_permission
from src.database.base import get_db_session

from .service import get_or_create_settings, save_settings

router = APIRouter(prefix="/admin/plg_robots", tags=["plg_robots"])


@router.get("", response_class=HTMLResponse)
async def index(
    request: Request,
    current_user: CurrentAdminUser,
    _acl: object = Depends(require_admin_permission("robots.manage")),
    db: AsyncSession = Depends(get_db_session),
) -> HTMLResponse:
    settings = await get_or_create_settings(db)
    flash = request.session.pop("flash", None)
    return await admin_render(
        "admin/plg_robots/index.html",
        request,
        db,
        user=current_user,
        settings=settings,
        flash=flash,
    )


@router.post("", response_class=HTMLResponse)
async def save(
    request: Request,
    current_user: CurrentAdminUser,
    _acl: object = Depends(require_admin_permission("robots.manage")),
    db: AsyncSession = Depends(get_db_session),
    enabled: str | None = Form(None),
    rules: str = Form(""),
) -> RedirectResponse:
    await save_settings(db, enabled=enabled is not None, rules=rules)
    request.session["flash"] = {"type": "success", "text": "Nastavení uloženo."}
    return RedirectResponse("/admin/plg_robots", status_code=303)
