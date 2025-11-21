import pytest
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch
from users.models import CustomUser
from users.utils import generate_verification_token


@pytest.mark.django_db
class TestAuthAPI:

    def test_register_success(self, api_client):
        payload = {
            "email": "prafful@gkmit.co",
            "username": "newuser",
            "password": "newpassword123",
            "password_confirm": "newpassword123",
        }

        url = reverse("users:api_register")
        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "message" in response.data
        assert "email" in response.data
        assert CustomUser.objects.filter(email="prafful@gkmit.co").exists()

    def test_register_missing_field(self, api_client):
        payload = {"email": "prafful@gkmit.co"}

        url = reverse("users:api_register")
        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username" in response.data
        assert "password" in response.data

    @patch("users.views.send_mail", side_effect=Exception("SMTP error"))
    def test_register_email_send_failure(self, mock_email, api_client):
        payload = {
            "email": "fail@example.com",
            "username": "failuser",
            "password": "abc12345",
            "password_confirm": "abc12345",
        }

        url = reverse("users:api_register")
        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert "error" in response.data
        assert not CustomUser.objects.filter(email="fail@example.com").exists()

    def test_login_success(self, api_client, user):
        payload = {
            "email": user.email,
            "password": "testpass123",
        }

        url = reverse("users:api_login")
        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_login_invalid_password(self, api_client, user):
        payload = {"email": user.email, "password": "wrongpass"}

        url = reverse("users:api_login")
        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "error" in response.data

    def test_login_user_not_verified(self, api_client):
        user = CustomUser.objects.create_user(
            email="nov@example.com",
            username="novUser",
            password="pass12345",
            is_email_verified=False,
        )

        payload = {"email": user.email, "password": "pass12345"}

        url = reverse("users:api_login")
        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_verify_email_success(self, api_client):
        user = CustomUser.objects.create_user(
            email="v@example.com",
            username="verifyuser",
            password="pass0000",
            is_email_verified=False,
        )

        token = generate_verification_token(user)
        url = reverse("users:verify_email", args=[token])

        response = api_client.get(url)
        user.refresh_from_db()

        assert user.is_email_verified
        assert response.status_code == 302

    def test_verify_email_invalid_token(self, api_client):
        url = reverse("users:verify_email", args=["invalidtoken123"])

        response = api_client.get(url)

        assert response.status_code == 302
        assert "invalid" in response.url
