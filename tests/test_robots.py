from __future__ import annotations

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.plugins.plg_robots.service import (
    get_or_create_settings,
    get_robots_txt,
    save_settings,
)

# ---------------------------------------------------------------------------
# service layer
# ---------------------------------------------------------------------------


async def test_get_or_create_returns_defaults(db_session: AsyncSession):
    s = await get_or_create_settings(db_session)
    assert s.id == 1
    assert s.enabled is True
    assert "User-agent" in s.rules
    assert "/admin/" in s.rules


async def test_get_or_create_idempotent(db_session: AsyncSession):
    s1 = await get_or_create_settings(db_session)
    s2 = await get_or_create_settings(db_session)
    assert s1.id == s2.id


async def test_save_settings(db_session: AsyncSession):
    await save_settings(db_session, enabled=False, rules="User-agent: *\nDisallow: /")
    s = await get_or_create_settings(db_session)
    assert s.enabled is False
    assert "Disallow: /" in s.rules


async def test_get_robots_txt_enabled(db_session: AsyncSession):
    content = await get_robots_txt(db_session)
    assert content is not None
    assert "User-agent" in content


async def test_get_robots_txt_disabled_returns_none(db_session: AsyncSession):
    await save_settings(db_session, enabled=False, rules="User-agent: *\nDisallow: /")
    result = await get_robots_txt(db_session)
    assert result is None


async def test_get_robots_txt_custom_rules(db_session: AsyncSession):
    custom = "User-agent: Googlebot\nAllow: /\nDisallow: /private/"
    await save_settings(db_session, enabled=True, rules=custom)
    content = await get_robots_txt(db_session)
    assert content == custom


# ---------------------------------------------------------------------------
# web route
# ---------------------------------------------------------------------------


async def test_robots_txt_endpoint(client: AsyncClient):
    resp = await client.get("/robots.txt")
    assert resp.status_code == 200
    assert "text/plain" in resp.headers["content-type"]
    assert b"User-agent" in resp.content


async def test_robots_txt_disabled_returns_404(client: AsyncClient, db_session: AsyncSession):
    await save_settings(db_session, enabled=False, rules="")
    resp = await client.get("/robots.txt")
    assert resp.status_code == 404


async def test_robots_txt_content_matches_settings(client: AsyncClient, db_session: AsyncSession):
    custom = "User-agent: *\nDisallow: /secret/"
    await save_settings(db_session, enabled=True, rules=custom)
    resp = await client.get("/robots.txt")
    assert resp.status_code == 200
    assert b"Disallow: /secret/" in resp.content


# ---------------------------------------------------------------------------
# admin routes
# ---------------------------------------------------------------------------


async def test_admin_requires_auth(client: AsyncClient):
    resp = await client.get("/admin/plg_robots", follow_redirects=False)
    assert resp.status_code in (302, 303)


async def test_admin_index_authenticated(auth_client: AsyncClient):
    resp = await auth_client.get("/admin/plg_robots", follow_redirects=False)
    assert resp.status_code == 200
    assert b"robots" in resp.content.lower()


async def test_admin_save_redirects(auth_client: AsyncClient):
    resp = await auth_client.post(
        "/admin/plg_robots",
        data={"enabled": "on", "rules": "User-agent: *\nDisallow: /"},
        follow_redirects=False,
    )
    assert resp.status_code == 303
    assert "/admin/plg_robots" in resp.headers["location"]


async def test_admin_save_persists(auth_client: AsyncClient, db_session: AsyncSession):
    await auth_client.post(
        "/admin/plg_robots",
        data={"rules": "User-agent: *\nDisallow: /custom/"},
        follow_redirects=False,
    )
    s = await get_or_create_settings(db_session)
    assert s.enabled is False
    assert "Disallow: /custom/" in s.rules
