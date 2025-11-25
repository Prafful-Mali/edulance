from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LoginAPIView,
    RegisterAPIView,
    VerifyEmailView,
    login_view,
    register_view,
    dashboard_view,
    UserViewSet,
    LogoutAPIView,
    CustomTokenView,
    ForgotPasswordAPIView
)

app_name = "users"

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("verify-email/<str:token>/", VerifyEmailView.as_view(), name="verify_email"),
    path("api/login/", LoginAPIView.as_view(), name="api_login"),
    path("api/register/", RegisterAPIView.as_view(), name="api_register"),
    path("api/logout/", LogoutAPIView.as_view(), name="api_logout"),
    path("api/token/", CustomTokenView.as_view(), name="api_token"),
    path("api/forget-password/", ForgotPasswordAPIView.as_view(), name="api_forget_password"),
    path("api/", include(router.urls)),
]
