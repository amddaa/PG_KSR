from django.apps import AppConfig

from .events.api_event_processor import APIEventProcessor
from .events.event_handler import EventHandler
from .events.event_processor import EventProcessor
from .events.train_event_processor import TrainEventProcessor
from .repository.read_repository import ReadRepository
from .repository.train_repository_query import TrainRepositoryQuery
from .repository.event_repository import EventRepository
from .service.command_service import CommandService
from .service.query_service import QueryService
from .service.train_service import TrainQueryService


class ReservationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "reservations"

    def ready(self):
        reservation_eventstore = EventRepository()

        # Train microservice event propagation handling
        train_db = TrainRepositoryQuery()
        service = TrainQueryService(train_db, reservation_eventstore)
        train_event_processor = TrainEventProcessor(service)
        train_event_processor.start()

        # API command calls & Eventstore, command processing
        reservation_event_propagator = EventHandler()
        api_service = CommandService(reservation_eventstore, reservation_event_propagator)
        api_processor = APIEventProcessor(api_service)
        api_processor.start()

        # Reservation propagation handling to query db
        reservation_db = ReadRepository()
        query_service = QueryService(reservation_db)
        reservation_event_processor = EventProcessor(query_service)
        reservation_event_processor.start()
        pass
