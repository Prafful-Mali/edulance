import pytest
from rest_framework.test import APIClient
from users.models import CustomUser


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
