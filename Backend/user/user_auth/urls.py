from django.urls import path

from . import views

urlpatterns = [
    path("auth/register/", views.register, name="register"),
    path("auth/verify-email/<str:uidb64>/<str:token>/", views.verify_email, name="verify_email"),
    path("auth/token/", views.CookieTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", views.CookieTokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/blacklist/", views.CookieTokenBlacklistView.as_view(), name='token_blacklist'),
    path("auth/token/verify/", views.CookieTokenVerifyView.as_view(), name='token_verify')
]
