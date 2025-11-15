import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator


class Skill(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True, default=None)

    def __str__(self):
        return self.name


class Post(models.Model):
    PROJECT_TYPE_CHOICES = [
        ('hackathon', 'Hackathon'),
        ('group_project', 'Group Project'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True)
    description = models.TextField()
    project_type = models.CharField(
        max_length=20,
        choices=PROJECT_TYPE_CHOICES,
        blank=True,
        null=True
    )
    people_required = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    last_date = models.DateTimeField()
    event_start_date = models.DateTimeField()
    event_last_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    skills = models.ManyToManyField(Skill, through="PostSkill", related_name="posts")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True, default=None)

    def __str__(self):
        return self.title


class PostSkill(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="post_skills")
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name="skill_posts")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True, default=None)

    class Meta:
        unique_together = ("post", "skill")

    def __str__(self):
        return f"{self.post_id} - {self.skill.name}"


class Application(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="applications"
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="applications")
    message = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True, default=None)

    class Meta:
        unique_together = ("applicant", "post")

    def __str__(self):
        return f"Application({self.applicant_id} -> {self.post_id})"
