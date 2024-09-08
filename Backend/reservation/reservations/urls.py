from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.healthcheck, name='healthcheck'),
]
