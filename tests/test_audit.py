"""Tests for AI-Slop & Quality AuditEngine."""

from src.core.audit import AuditEngine


def test_slop_detection_clean_text():
    human_text = "Yesterday at 3 AM our PostgreSQL primary node ran out of disk space. Here is how we fixed it in 15 minutes."
    audit = AuditEngine.audit_content(human_text)
    assert audit.slop_score <= 15
    assert "Pristine" in audit.slop_rating
    assert len(audit.flagged_terms) == 0


def test_slop_detection_heavy_synthetic():
    ai_slop_text = (
        "In today's fast-paced world, it is paramount to delve into the rich tapestry of modern software. "
        "This groundbreaking framework seamlessly integrates into your workflow to unlock the power of agentic tools. "
        "Moreover, it stands as a testament to innovation."
    )
    audit = AuditEngine.audit_content(ai_slop_text)
    assert audit.slop_score >= 50
    assert len(audit.flagged_terms) >= 4
    categories = [f.category for f in audit.flagged_terms]
    assert "delve" in categories
    assert "tapestry" in categories
    assert "in today's world" in categories


def test_hook_classification_obituary():
    text = "Docker is dead. Here is why WebAssembly micro-runtimes will replace containers in 2026."
    audit = AuditEngine.audit_content(text)
    assert audit.hook is not None
    assert audit.hook.formula_id == "F01"
    assert audit.hook.formula_name == "The Obituary"


def test_hook_classification_hard_numbers():
    text = "We cut our monthly cloud bill by $42,000 in 14 days without changing a single line of application code."
    audit = AuditEngine.audit_content(text)
    assert audit.hook is not None
    assert audit.hook.formula_id == "F05"
    assert audit.hook.formula_name == "Hard Numbers"


def test_hook_classification_contrarian():
    text = "Everyone thinks microservices improve development velocity. They are completely wrong."
    audit = AuditEngine.audit_content(text)
    assert audit.hook is not None
    assert audit.hook.formula_id == "F03"
    assert audit.hook.formula_name == "The Contrarian"
