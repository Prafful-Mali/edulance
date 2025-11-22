import pytest
from django.urls import reverse
from rest_framework import status
from collaborate.models import Post, Application
from users.models import CustomUser
from django.utils import timezone
from datetime import timedelta


@pytest.mark.django_db
class TestSkillAPI:

    def test_list_skills_authenticated(self, api_client, user, skill):
        api_client.force_authenticate(user=user)
        url = reverse("collaborate:skill-list")

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1
        assert response.data[0]["name"] == skill.name

    def test_list_skills_unauthenticated(self, api_client, skill):
        url = reverse("collaborate:skill-list")

        response = api_client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestPostAPI:

    def test_create_post_success(self, api_client, user, skill):
        api_client.force_authenticate(user=user)
        url = reverse("collaborate:post-list")

        payload = {
            "title": "New Hackathon",
            "description": "Join our hackathon",
            "project_type": "hackathon",
            "people_required": 5,
            "last_date": (timezone.now() + timedelta(days=7)).isoformat(),
            "event_start_date": (timezone.now() + timedelta(days=10)).isoformat(),
            "event_last_date": (timezone.now() + timedelta(days=12)).isoformat(),
            "skill_ids": [str(skill.id)],
        }

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert Post.objects.filter(title="New Hackathon").exists()

    def test_filter_posts_by_project_type(self, api_client, user):
        api_client.force_authenticate(user=user)
        url = reverse("collaborate:post-list")

        response = api_client.get(url, {"project_type": "hackathon"})

        assert response.status_code == status.HTTP_200_OK
        assert all(p["project_type"] == "hackathon" for p in response.data)

    def test_get_post_by_slug(self, api_client, user, post):
        api_client.force_authenticate(user=user)
        url = reverse("collaborate:post-detail", args=[post.slug])

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == post.title
        assert response.data["slug"] == post.slug

    def test_update_other_user_post_forbidden(self, api_client, post):
        other_user = CustomUser.objects.create_user(
            email="other@example.com",
            username="otheruser",
            password="pass123",
            is_email_verified=True,
        )

        api_client.force_authenticate(user=other_user)
        url = reverse("collaborate:post-detail", args=[post.slug])

        payload = {"description": "Hacking attempt"}
        response = api_client.patch(url, payload, format="json")

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_own_post(self, api_client, user, post):
        api_client.force_authenticate(user=user)
        url = reverse("collaborate:post-detail", args=[post.slug])

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        post.refresh_from_db()
        assert post.deleted_at is not None

    def test_delete_other_user_post_forbidden(self, api_client, post):
        other_user = CustomUser.objects.create_user(
            email="other@example.com",
            username="otheruser",
            password="pass123",
            is_email_verified=True,
        )

        api_client.force_authenticate(user=other_user)
        url = reverse("collaborate:post-detail", args=[post.slug])

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestApplicationAPI:

    def test_create_application_success(self, api_client, post):
        applicant = CustomUser.objects.create_user(
            email="applicant@example.com",
            username="applicant",
            password="pass123",
            is_email_verified=True,
        )

        api_client.force_authenticate(user=applicant)
        url = reverse("collaborate:application-list")

        payload = {"post_id": str(post.id), "message": "I want to join!"}

        response = api_client.post(url, payload, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert Application.objects.filter(applicant=applicant, post=post).exists()

    def test_list_applications_for_post(self, api_client, user, post):
        applicant = CustomUser.objects.create_user(
            email="applicant@example.com",
            username="applicant",
            password="pass123",
            is_email_verified=True,
        )

        Application.objects.create(
            applicant=applicant, post=post, message="Test message"
        )

        api_client.force_authenticate(user=user)
        url = reverse("collaborate:application-list")

        response = api_client.get(url, {"post": str(post.id)})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1


@pytest.mark.django_db
class TestAdminUserViewSet:

    def test_admin_list_users(self, api_client, admin_user, user):
        api_client.force_authenticate(user=admin_user)
        url = reverse("collaborate:admin-user-list")

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 2

    def test_regular_user_cannot_list_users(self, api_client, user):
        api_client.force_authenticate(user=user)
        url = reverse("collaborate:admin-user-list")

        response = api_client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_delete_user(self, api_client, admin_user, user):
        api_client.force_authenticate(user=admin_user)
        url = reverse("collaborate:admin-user-detail", args=[user.id])

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        user.refresh_from_db()
        assert user.deleted_at is not None

    def test_admin_cannot_delete_self(self, api_client, admin_user):
        api_client.force_authenticate(user=admin_user)
        url = reverse("collaborate:admin-user-detail", args=[admin_user.id])

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestAdminPostViewSet:

    def test_admin_list_posts(self, api_client, admin_user, post):
        api_client.force_authenticate(user=admin_user)
        url = reverse("collaborate:admin-post-list")

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) >= 1

    def test_admin_delete_post(self, api_client, admin_user, post):
        api_client.force_authenticate(user=admin_user)
        url = reverse("collaborate:admin-post-detail", args=[post.slug])

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT
        post.refresh_from_db()
        assert post.deleted_at is not None

    def test_regular_user_cannot_delete_via_admin_endpoint(
        self, api_client, user, post
    ):
        api_client.force_authenticate(user=user)
        url = reverse("collaborate:admin-post-detail", args=[post.slug])

        response = api_client.delete(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
