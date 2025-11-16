from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import collaborate_view, post_detail_view, SkillViewSet, PostViewSet, ApplicationViewSet

app_name = "collaborate"

router = DefaultRouter()
router.register(r'skills', SkillViewSet, basename='skill')
router.register(r'posts', PostViewSet, basename='post')
router.register(r'applications', ApplicationViewSet, basename='application')

urlpatterns = [
    path('collaborate/', collaborate_view, name='collaborate'),
    path('collaborate/post/<slug:slug>/', post_detail_view, name='post_detail'),
    path('api/', include(router.urls)),
]