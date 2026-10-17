"""Tests for ContentScheduler and Reach-Learning Loop."""

from src.core.scheduler import ContentScheduler


def test_calendar_initialization(tmp_path):
    storage_file = tmp_path / "test_calendar.json"
    scheduler = ContentScheduler(storage_path=storage_file)

    posts = scheduler.get_all_posts()
    assert len(posts) == 35  # 7 days * 5 slots = 35 posts
    assert posts[0].day == 1
    assert posts[0].slot == 1
    assert posts[0].status == "PENDING"
    assert posts[-1].day == 7
    assert posts[-1].slot == 5


def test_update_post_status(tmp_path):
    storage_file = tmp_path / "test_calendar.json"
    scheduler = ContentScheduler(storage_path=storage_file)

    updated = scheduler.update_post_status(
        "post-d1-s1",
        "PUBLISHED",
        published_urls={"linkedin": "https://linkedin.com/feed/update/123"},
    )
    assert updated is not None
    assert updated.status == "PUBLISHED"
    assert updated.published_urls["linkedin"] == "https://linkedin.com/feed/update/123"


def test_reach_learning_velocity_score(tmp_path):
    storage_file = tmp_path / "test_calendar.json"
    scheduler = ContentScheduler(storage_path=storage_file)

    # Record metrics: 1,000 impressions, 50 reactions, 10 comments
    # Velocity: (50*2 + 10*5) / 1000 = (100 + 50) / 1000 = 0.15 = 15.0%
    metrics = scheduler.record_metrics(
        post_id="post-d1-s1",
        impressions=1000,
        reactions=50,
        comments=10,
    )
    assert metrics is not None
    assert metrics.velocity_score == 15.0

    analytics = scheduler.get_reach_analytics()
    assert analytics["total_impressions"] == 1000
    assert analytics["total_reactions"] == 50
    assert analytics["total_comments"] == 10
    assert len(analytics["hook_rankings"]) > 0
