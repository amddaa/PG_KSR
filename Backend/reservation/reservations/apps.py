from django.apps import AppConfig

from .events.event_processor import EventProcessor
from .repository.train_repository import TrainRepository
from .service.train_service import TrainQueryService


class ReservationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "reservations"

    def ready(self):
        repository = TrainRepository()
        service = TrainQueryService(repository)
        event_processor = EventProcessor(service)
        event_processor.start()
        pass
