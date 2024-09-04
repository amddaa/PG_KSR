from rest_framework.utils import json
from django.db import models
from .events.handlers import TrainEventHandler
from esdbclient import EventStoreDBClient, NewEvent, StreamState
from django.conf import settings


class TrainSchedule(models.Model):
    train_number = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    stream_name = 'train-schedule-stream'

    class Meta:
        app_label = "trains"
        db_table = "train_schedule"

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        event_data = {
            "train_number": self.train_number,
            "departure_time": self.departure_time.isoformat(),
            "arrival_time": self.arrival_time.isoformat(),
        }
        event_data_bytes = json.dumps(event_data).encode('utf-8')

        esdb_client = EventStoreDBClient(uri=f"esdb://{settings.ESDB_HOST}:{settings.ESDB_PORT}?Tls=false")
        try:
            if is_new:
                event_type = 'TrainScheduleCreated'
            else:
                event_type = 'TrainScheduleUpdated'

            event = NewEvent(type=event_type, data=event_data_bytes)
            esdb_client.append_to_stream(stream_name=self.stream_name, events=[event], current_version=StreamState.ANY)

            event_handler = TrainEventHandler()
            event_handler.publish_event(event_type, event_data, self.stream_name)
        finally:
            esdb_client.close()

    def delete(self, *args, **kwargs):
        event_data = {
            'train_number': self.train_number,
            'departure_time': self.departure_time.isoformat(),
            'arrival_time': self.arrival_time.isoformat(),
        }
        event_data_bytes = json.dumps(event_data).encode('utf-8')

        esdb_client = EventStoreDBClient(uri=f"esdb://{settings.ESDB_HOST}:{settings.ESDB_PORT}?Tls=false")
        try:
            event_type = 'TrainScheduleDeleted'
            event = NewEvent(type=event_type, data=event_data_bytes)
            esdb_client.append_to_stream(self.stream_name, [event])

            event_handler = TrainEventHandler()
            event_handler.publish_event(event_type, event_data, self.stream_name)
        finally:
            esdb_client.close()
