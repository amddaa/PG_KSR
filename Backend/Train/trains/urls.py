from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.healthcheck, name='healthcheck'),
    path("", views.train_schedules, name='train_schedules'),
    path("<str:train_number>/", views.get_train_detail, name='train_detail'),
    path("<str:train_number>/update/", views.update_train_schedule, name='update_train_schedule'),
    path("<str:train_number>/delete/", views.delete_train_schedule, name='delete_train_schedule'),
    path("search/", views.search_train_schedule, name='search_train_schedule'),
]
