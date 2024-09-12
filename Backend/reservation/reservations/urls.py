from django.urls import path
from . import views
from .views import ReservationCommandView, ReservationStatusView

urlpatterns = [
    path("health/", views.healthcheck, name='healthcheck'),
    path("version/", views.get_stream_version, name='train_schedules'),
    path("status/<str:operation_id>/", ReservationStatusView.as_view(), name='reservation_status'),
    path("", ReservationCommandView.as_view(), name='reservation_command'),
]
