from django.apps import AppConfig
from .events.event_processor import EventProcessor
from .repository.read_repository import TrainReadRepository
from .service.query_service import TrainQueryService


class TrainsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "train"

    def ready(self):
        repository = TrainReadRepository()
        service = TrainQueryService(repository)
        event_processor = EventProcessor(service)
        event_processor.start()
