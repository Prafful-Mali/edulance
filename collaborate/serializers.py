from rest_framework import serializers
from .models import Skill, Post, PostSkill, Application
from users.serializers import UserProfileSerializer
from django.utils.text import slugify
import uuid


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'created_at']
        read_only_fields = ['id', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    user = UserProfileSerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    skill_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False
    )
    applications_count = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    has_applied = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id', 'user', 'title', 'slug', 'description', 'project_type',
            'people_required', 'last_date', 'event_start_date', 'event_last_date',
            'is_active', 'skills', 'skill_ids', 'applications_count',
            'is_owner', 'has_applied', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'user', 'created_at', 'updated_at']
    
    def get_applications_count(self, obj):
        return obj.applications.filter(deleted_at__isnull=True).count()
    
    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.user.id == request.user.id
        return False
    
    def get_has_applied(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.applications.filter(
                applicant=request.user,
                deleted_at__isnull=True
            ).exists()
        return False
    
    def validate_skill_ids(self, value):
        """Validate that all skill IDs exist in the database"""
        if not value:
            return value
        
        existing_skills = Skill.objects.filter(
            id__in=value, 
            deleted_at__isnull=True
        ).values_list('id', flat=True)
        
        if len(existing_skills) != len(value):
            missing_ids = set(value) - set(existing_skills)
            raise serializers.ValidationError(
                f"Invalid skill IDs: {', '.join(str(id) for id in missing_ids)}. "
                "Please select only existing skills from the list."
            )
        
        return value
    
    def create(self, validated_data):
        skill_ids = validated_data.pop('skill_ids', [])
        
        base_slug = slugify(validated_data['title'])
        validated_data['slug'] = f"{base_slug}-{str(uuid.uuid4())[:8]}"
        
        post = Post.objects.create(**validated_data)
        
        for skill_id in skill_ids:
            try:
                skill = Skill.objects.get(id=skill_id, deleted_at__isnull=True)
                PostSkill.objects.create(post=post, skill=skill)
            except Skill.DoesNotExist:
                pass
        
        return post
    
    def update(self, instance, validated_data):
        skill_ids = validated_data.pop('skill_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if skill_ids is not None:
            PostSkill.objects.filter(post=instance).delete()
            
            for skill_id in skill_ids:
                try:
                    skill = Skill.objects.get(id=skill_id, deleted_at__isnull=True)
                    PostSkill.objects.create(post=instance, skill=skill)
                except Skill.DoesNotExist:
                    pass
        
        return instance


class ApplicationSerializer(serializers.ModelSerializer):
    applicant = UserProfileSerializer(read_only=True)
    post_id = serializers.UUIDField(write_only=True)
    
    class Meta:
        model = Application
        fields = [
            'id', 'applicant', 'post_id', 'message',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'applicant', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        post_id = validated_data.pop('post_id')
        try:
            post = Post.objects.get(id=post_id, deleted_at__isnull=True, is_active=True)
        except Post.DoesNotExist:
            raise serializers.ValidationError({"post_id": "Post not found or inactive"})
        
        validated_data['post'] = post
        return Application.objects.create(**validated_data)