import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestDashboardPage:

    def test_dashboard_contains_feature_cards(self, client):
        url = reverse("users:dashboard")
        response = client.get(url)
        html = response.content.decode()

        assert "What is Edulance?" in html
        assert "Why Collaborate?" in html
        assert "How It Works" in html

    def test_dashboard_contains_quick_actions(self, client):
        url = reverse("users:dashboard")
        response = client.get(url)
        html = response.content.decode()

        assert "Profile Settings" in html
        assert "Password" in html or "Security Settings" in html

    def test_dashboard_contains_profile_modal(self, client):
        url = reverse("users:dashboard")
        response = client.get(url)
        html = response.content.decode()

        assert 'id="profileModal"' in html
        assert 'id="userName"' in html
        assert 'id="userEmail"' in html
        assert 'id="userRole"' in html

    def test_dashboard_contains_edit_profile_modal(self, client):
        url = reverse("users:dashboard")
        response = client.get(url)
        html = response.content.decode()

        assert 'id="editProfileModal"' in html
        assert 'id="editProfileForm"' in html
        assert 'id="editUsername"' in html
        assert 'id="editUserEmail"' in html
        assert 'id="editUserBio"' in html

    def test_dashboard_contains_security_modal(self, client):
        url = reverse("users:dashboard")
        response = client.get(url)
        html = response.content.decode()

        assert 'id="securityModal"' in html
        assert 'id="changePasswordForm"' in html
        assert 'id="oldPassword"' in html
        assert 'id="newPassword"' in html
        assert 'id="newPasswordConfirm"' in html

    def test_dashboard_contains_profile_fab_button(self, client):
        url = reverse("users:dashboard")
        response = client.get(url)
        html = response.content.decode()

        assert 'class="profile-fab"' in html

    def test_dashboard_contains_alert_container(self, client):
        url = reverse("users:dashboard")
        response = client.get(url)
        html = response.content.decode()

        assert 'id="alertContainer"' in html
