import pytest
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient

from users.models import CustomUser
from collaborate.models import Skill, Post


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return CustomUser.objects.create_user(
        email="test@example.com",
        username="testuser",
        password="testpass123",
        is_email_verified=True,
        role="user",
    )


@pytest.fixture
def admin_user():
    return CustomUser.objects.create_user(
        email="admin@example.com",
        username="adminuser",
        password="adminpass123",
        is_email_verified=True,
        role="admin",
    )


@pytest.fixture
def skill():
    return Skill.objects.create(name="Python")


@pytest.fixture
def post(user, skill):
    post = Post.objects.create(
        user=user,
        title="Test Hackathon",
        slug="test-hackathon-123",
        description="A test hackathon project",
        project_type="hackathon",
        people_required=3,
        last_date=timezone.now() + timedelta(days=7),
        event_start_date=timezone.now() + timedelta(days=10),
        event_last_date=timezone.now() + timedelta(days=12),
        is_active=True,
    )
    post.skills.add(skill)
    return post
