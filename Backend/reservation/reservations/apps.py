from django.apps import AppConfig

from .events.event_processor import EventProcessor
from .repository.train_repository_query import TrainRepositoryQuery
from .repository.event_repository import EventRepository
from .service.train_service import TrainQueryService


class ReservationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "reservations"

    def ready(self):
        train_db = TrainRepositoryQuery()
        train_eventstore = EventRepository()
        service = TrainQueryService(train_db, train_eventstore)
        event_processor = EventProcessor(service)
        event_processor.start()
        pass
