from django.urls import re_path
from . import views

urlpatterns = [
    re_path("api/login", views.login, name="login"),
    re_path("api/register", views.register, name="register"),
    re_path("api/test_token", views.test_token, name="test_token"),
]
