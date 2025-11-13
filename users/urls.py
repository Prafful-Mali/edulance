from django.urls import path
from .views import CustomTokenObtainPairView, CustomTokenRefreshView, login_view, register_view

app_name = "users"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("register/", register_view, name="register"),
    path("api/token/", CustomTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", CustomTokenRefreshView.as_view(), name="token_refresh"),
]
