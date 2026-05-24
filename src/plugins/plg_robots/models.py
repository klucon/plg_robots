from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import Boolean, DateTime, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from src.database.base import Base

_DEFAULT_RULES = """\
User-agent: *
Disallow: /admin/
Disallow: /internal/
Disallow: /api/

Sitemap: /sitemap.xml
"""


def _now() -> datetime:
    return datetime.now(UTC)


class RobotsSettings(Base):
    __tablename__ = "plg_robots_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    rules: Mapped[str] = mapped_column(Text, default=_DEFAULT_RULES, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now, nullable=False
    )
