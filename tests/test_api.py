"""Tests for FastAPI Web Gateway Endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from src.api.main import app


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "healthy"
        assert "version" in data


@pytest.mark.asyncio
async def test_audit_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {"text": "In today's fast-paced world, we delve into the tapestry of cloud microservices."}
        resp = await ac.post("/api/posts/audit", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["slop_score"] > 30
        assert len(data["flagged_terms"]) >= 3


@pytest.mark.asyncio
async def test_preview_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        payload = {
            "text": "Announcing OmniMCP Pro! Learn more at https://omnimcp.pro",
            "targets": ["linkedin", "twitter"],
        }
        resp = await ac.post("/api/posts/preview", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "linkedin" in data["transformed"]
        assert "twitter" in data["transformed"]


@pytest.mark.asyncio
async def test_calendar_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/calendar")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 35


@pytest.mark.asyncio
async def test_safety_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        resp = await ac.get("/api/safety")
        assert resp.status_code == 200
        data = resp.json()
        assert "cooldown_seconds" in data
        assert "daily_limit" in data
