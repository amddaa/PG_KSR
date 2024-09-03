from django.urls import path

from . import views

urlpatterns = [
    path("health/", views.healthcheck, name='healthcheck'),
    path("", views.get_train_list, name='train_list'),
    path("", views.create_train_schedule, name='create_train_schedule'),
    path("<int:pk>/", views.get_train_detail, name='train_detail'),
    path("<int:pk>/", views.update_train_schedule, name='update_train_schedule'),
    path("<int:pk>/", views.delete_train_schedule, name='delete_train_schedule'),
    path("search/", views.search_train_schedule, name='search_train_schedule'),
]
