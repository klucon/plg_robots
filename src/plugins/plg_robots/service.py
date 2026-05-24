from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import RobotsSettings, _DEFAULT_RULES


async def get_or_create_settings(db: AsyncSession) -> RobotsSettings:
    s = (
        await db.execute(select(RobotsSettings).where(RobotsSettings.id == 1))
    ).scalar_one_or_none()
    if s is None:
        s = RobotsSettings(id=1, rules=_DEFAULT_RULES)
        db.add(s)
        await db.commit()
        await db.refresh(s)
    return s


async def save_settings(
    db: AsyncSession,
    *,
    enabled: bool,
    rules: str,
) -> RobotsSettings:
    s = await get_or_create_settings(db)
    s.enabled = enabled
    s.rules = rules
    s.updated_at = datetime.now(UTC)
    await db.commit()
    await db.refresh(s)
    return s


async def get_robots_txt(db: AsyncSession) -> str | None:
    s = await get_or_create_settings(db)
    if not s.enabled:
        return None
    return s.rules
