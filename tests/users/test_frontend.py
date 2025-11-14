import pytest
from django.urls import reverse

@pytest.mark.django_db
class TestLoginPage:

    def test_login_page_loads(self, client):
        url = reverse("users:login")
        response = client.get(url)

        assert response.status_code == 200
        assert b"Login" in response.content
        assert b"Email address" in response.content
        assert b"Password" in response.content

    def test_login_page_uses_correct_template(self, client):
        url = reverse("users:login")
        response = client.get(url)

        templates = [t.name for t in response.templates]
        assert "users/login.html" in templates

    def test_login_page_includes_js_file(self, client):
        url = reverse("users:login")
        response = client.get(url)

        assert b"users/js/login.js" in response.content

    def test_login_page_contains_form_fields(self, client):
        url = reverse("users:login")
        response = client.get(url)

        html = response.content.decode()

        assert 'id="emailInput"' in html
        assert 'id="passwordInput"' in html
        assert 'id="loginBtn"' in html
        assert "<form" in html

    def test_login_page_register_link(self, client):
        url = reverse("users:login")
        response = client.get(url)

        html = response.content.decode()

        register_url = reverse("users:register")
        assert f'href="{register_url}"' in html

    def test_message_param_verified(self, client):
        url = reverse("users:login") + "?message=verified"
        response = client.get(url)

        html = response.content.decode()

        assert "Email verified" in html or "messageAlert" in html

    def test_message_param_invalid(self, client):
        url = reverse("users:login") + "?message=invalid"
        response = client.get(url)

        html = response.content.decode()

        assert "Invalid verification" in html or "messageAlert" in html
