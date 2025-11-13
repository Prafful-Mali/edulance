from django.urls import path
from .views import CustomTokenObtainPairView, CustomTokenRefreshView, RegisterView, VerifyEmailView, login_view, register_view, dashboard_view
app_name = "users"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("api/register/", RegisterView.as_view(), name="api_register"),
    path("verify-email/<str:token>/", VerifyEmailView.as_view(), name="verify_email"),
]