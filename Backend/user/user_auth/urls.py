from django.urls import re_path
from . import views

urlpatterns = [
    re_path("login", views.login, name="login"),
    re_path("register", views.register, name="register"),
    re_path("test_token", views.test_token, name="test_token"),
]
