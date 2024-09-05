from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.healthcheck, name='healthcheck'),
    path("", views.train_schedules, name='train_schedules'),
    path("<str:train_number>/", views.get_train_detail, name='train_detail'),
]
