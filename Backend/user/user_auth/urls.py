from django.urls import path
from . import views
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path("api/auth/login/", views.login, name="login"),
    path("api/auth/register/", views.register, name="register"),
    path("api/auth/verify-email/<str:uidb64>/<str:token>/", views.verify_email, name="verify_email"),
    path("api/auth/token/", jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/token/verify/", jwt_views.TokenVerifyView.as_view(), name="token_verify"),
]
