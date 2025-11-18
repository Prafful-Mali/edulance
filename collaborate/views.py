from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Skill, Post, Application
from .serializers import SkillSerializer, PostSerializer, ApplicationSerializer
from users.models import CustomUser
from users.serializers import UserProfileSerializer
from rest_framework.exceptions import PermissionDenied


def collaborate_view(request):
    return render(request, "collaborate/collaborate.html")


def post_detail_view(request, slug):
    return render(request, "collaborate/post_detail.html", {"slug": slug})


def admin_panel_view(request):
    return render(request, "admin/admin_panel.html")


class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SkillSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Skill.objects.filter(deleted_at__isnull=True).order_by("name")


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "slug"

    def get_queryset(self):
        queryset = (
            Post.objects.filter(deleted_at__isnull=True)
            .select_related("user")
            .prefetch_related("skills")
        )

        project_type = self.request.query_params.get("project_type", None)
        if project_type:
            queryset = queryset.filter(project_type=project_type)

        return queryset.order_by("-created_at")

    def perform_create(self, serializer):
        if self.request.user.role == "admin":
            raise PermissionDenied("Admins cannot create posts")

        serializer.save(user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {"error": "You can only update your own posts"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.user != request.user:
            return Response(
                {"error": "You can only delete your own posts"},
                status=status.HTTP_403_FORBIDDEN,
            )
        instance.deleted_at = timezone.now()
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["get"])
    def my_posts(self, request):
        posts = self.get_queryset().filter(user=request.user)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)


class ApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "post"]

    def get_queryset(self):
        queryset = Application.objects.filter(deleted_at__isnull=True).select_related(
            "applicant", "post"
        )

        post_id = self.request.query_params.get("post", None)
        if post_id:
            queryset = queryset.filter(post_id=post_id)

        return queryset.order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(applicant=self.request.user)

    def create(self, request, *args, **kwargs):
        post_id = request.data.get("post_id")
        existing = Application.objects.filter(
            applicant=request.user, post_id=post_id, deleted_at__isnull=True
        ).exists()

        if existing:
            return Response(
                {"error": "You have already applied to this post"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return super().create(request, *args, **kwargs)


class AdminUserViewSet(viewsets.ModelViewSet):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["get", "delete"]

    def get_queryset(self):
        if self.request.user.role != "admin":
            return CustomUser.objects.none()
        return CustomUser.objects.filter(deleted_at__isnull=True).order_by(
            "-created_at"
        )

    def list(self, request, *args, **kwargs):
        if request.user.role != "admin":
            return Response(
                {"error": "Only admins can access this endpoint"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user.role != "admin":
            return Response(
                {"error": "Only admins can delete users"},
                status=status.HTTP_403_FORBIDDEN,
            )

        instance = self.get_object()

        if instance.id == request.user.id:
            return Response(
                {"error": "You cannot delete your own account"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        instance.deleted_at = timezone.now()
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminPostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "slug"
    http_method_names = ["get", "delete"]

    def get_queryset(self):
        if self.request.user.role != "admin":
            return Post.objects.none()
        return (
            Post.objects.filter(deleted_at__isnull=True)
            .select_related("user")
            .prefetch_related("skills")
            .order_by("-created_at")
        )

    def list(self, request, *args, **kwargs):
        if request.user.role != "admin":
            return Response(
                {"error": "Only admins can access this endpoint"},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().list(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        if request.user.role != "admin":
            return Response(
                {"error": "Only admins can delete posts"},
                status=status.HTTP_403_FORBIDDEN,
            )

        instance = self.get_object()
        instance.deleted_at = timezone.now()
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
