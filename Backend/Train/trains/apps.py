import threading
from django.apps import AppConfig
from .events.processor import EventProcessor


class TrainsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "train"

    def ready(self):
        processor = EventProcessor()
        threading.Thread(target=processor.start, daemon=True).start()
