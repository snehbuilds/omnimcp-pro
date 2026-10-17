"""Tests for Anti-Ban SafetyGuard and Write Gate."""

from src.core.safety import SafetyGuard


def test_write_gate_dry_run_when_unconfirmed():
    guard = SafetyGuard()
    # When confirm_post=False, must force dry-run
    is_dry, reason = guard.should_dry_run(confirm_post=False, requested_dry_run=False)
    assert is_dry is True
    assert "confirm_post" in reason


def test_write_gate_dry_run_when_env_disabled(monkeypatch):
    monkeypatch.delenv("OMNI_WRITE_ENABLED", raising=False)
    guard = SafetyGuard()
    is_dry, reason = guard.should_dry_run(confirm_post=True, requested_dry_run=False)
    assert is_dry is True
    assert "OMNI_WRITE_ENABLED" in reason


def test_write_gate_allows_live_when_authorized(monkeypatch):
    monkeypatch.setenv("OMNI_WRITE_ENABLED", "true")
    guard = SafetyGuard()
    is_dry, reason = guard.should_dry_run(confirm_post=True, requested_dry_run=False)
    assert is_dry is False
    assert reason is None


def test_cooldown_enforcement():
    guard = SafetyGuard(cooldown_seconds=10)
    # Record a live post
    guard.record_post("linkedin", "post-1", dry_run=False)

    can_post, reason = guard.check_can_post_live("linkedin")
    assert can_post is False
    assert "Active cooldown" in reason


def test_daily_limit_enforcement():
    guard = SafetyGuard(cooldown_seconds=0, daily_limit=3)
    # Post 3 times
    guard.record_post("linkedin", "p1", dry_run=False)
    guard.record_post("linkedin", "p2", dry_run=False)
    guard.record_post("linkedin", "p3", dry_run=False)

    can_post, reason = guard.check_can_post_live("linkedin")
    assert can_post is False
    assert "Daily limit" in reason
