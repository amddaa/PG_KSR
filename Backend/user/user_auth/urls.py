from django.urls import path

from . import views

urlpatterns = [
    path("api/auth/register/", views.register, name="register"),
    path("api/auth/verify-email/<str:uidb64>/<str:token>/", views.verify_email, name="verify_email"),
    path("api/auth/token/", views.CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/token/refresh/", views.CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/token/blacklist/", views.CookieTokenBlacklistView.as_view(), name='token_blacklist'),
]
