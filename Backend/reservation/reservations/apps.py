from django.apps import AppConfig

from .events.api_event_processor import APIEventProcessor
from .events.event_handler import EventHandler
from .events.train_event_processor import TrainEventProcessor
from .repository.train_repository_query import TrainRepositoryQuery
from .repository.event_repository import EventRepository
from .service.command_service import CommandService
from .service.train_service import TrainQueryService


class ReservationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "reservations"

    def ready(self):
        train_db = TrainRepositoryQuery()
        reservation_eventstore = EventRepository()

        service = TrainQueryService(train_db, reservation_eventstore)
        event_processor = TrainEventProcessor(service)  # Train microservice event propagation
        event_processor.start()

        reservation_event_propagator = EventHandler()
        api_service = CommandService(reservation_eventstore, reservation_event_propagator)
        api_processor = APIEventProcessor(api_service)
        api_processor.start()
        pass
