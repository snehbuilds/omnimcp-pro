"""Tests for FastMCP Protocol Server Tools."""

import pytest

from src.mcp_server.server import mcp


@pytest.mark.asyncio
async def test_mcp_tools_registration():
    expected_tools = [
        "omni_broadcast_post",
        "omni_preview_broadcast",
        "omni_audit_content",
        "omni_get_calendar",
        "omni_publish_scheduled_post",
        "omni_record_reach_metrics",
        "omni_get_safety_status",
        "linkedin_check_session",
        "linkedin_scrape_profile",
    ]

    for tool_name in expected_tools:
        tool = await mcp.get_tool(tool_name)
        assert tool is not None
        assert tool.name == tool_name


@pytest.mark.asyncio
async def test_mcp_audit_tool_invocation():
    tool = await mcp.get_tool("omni_audit_content")
    result = await tool.run(arguments={"text": "Microservices are dead. Here is what replaced them."})
    # FastMCP tools return result
    assert result is not None
