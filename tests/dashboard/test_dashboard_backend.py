import pytest
from django.urls import reverse
from rest_framework import status
from users.models import CustomUser


@pytest.mark.django_db
class TestDashboardBackendAPI:

    def test_update_user_bio(self, api_client, user):
        api_client.force_authenticate(user=user)
        url = reverse("users:user-detail", args=[user.id])

        payload = {"bio": "Updated bio for testing"}
        response = api_client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.bio == "Updated bio for testing"

    def test_change_password_success(self, api_client, user):
        api_client.force_authenticate(user=user)
        url = reverse("users:user-change-password")

        payload = {
            "old_password": "testpass123",
            "new_password": "newpass123456",
            "new_password_confirm": "newpass123456",
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "message" in response.data

        user.refresh_from_db()
        assert user.check_password("newpass123456")

    def test_change_password_wrong_old_password(self, api_client, user):
        api_client.force_authenticate(user=user)
        url = reverse("users:user-change-password")

        payload = {
            "old_password": "wrongpassword",
            "new_password": "newpass123456",
            "new_password_confirm": "newpass123456",
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "old_password" in response.data

    def test_change_password_mismatch(self, api_client, user):
        api_client.force_authenticate(user=user)
        url = reverse("users:user-change-password")

        payload = {
            "old_password": "testpass123",
            "new_password": "newpass123456",
            "new_password_confirm": "differentpass",
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
