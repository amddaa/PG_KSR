from django.urls import path
from . import views

urlpatterns = [
    path("api/login", views.login, name="login"),
    path("api/register", views.register, name="register"),
    path("api/test_token", views.test_token, name="test_token"),
    path("api/verify-email/<str:uidb64>/<str:token>/", views.verify_email, name="verify_email"),\
]
