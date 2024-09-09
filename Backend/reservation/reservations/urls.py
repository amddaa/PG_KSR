from django.urls import path
from . import views
from .views import ReservationCommandView

urlpatterns = [
    path("health/", views.healthcheck, name='healthcheck'),
    path("version/", views.get_stream_version, name='train_schedules'),
    path("", ReservationCommandView.as_view(), name='reservation_command'),
]
