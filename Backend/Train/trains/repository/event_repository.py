from esdbclient import EventStoreDBClient, NewEvent, StreamState
from django.conf import settings
from rest_framework.utils import json
import logging

logger = logging.getLogger(__name__)


class TrainEventRepository:
    def __init__(self):
        self.esdb_client = EventStoreDBClient(uri=f"esdb://{settings.ESDB_HOST}:{settings.ESDB_PORT}?Tls=false")

    def append_event(self, stream_name, event_type, event_data):
        success = True
        try:
            event_data_bytes = json.dumps(event_data).encode('utf-8')
            event = NewEvent(type=event_type, data=event_data_bytes)
            self.esdb_client.append_to_stream(stream_name=stream_name, events=[event], current_version=StreamState.ANY)
            logger.info(f"Successfully added {event_type} to eventstore")
        except Exception as e:
            logger.error(f"Error while appending {event_type} to eventstore: {e}")
            success = False
        finally:
            self.esdb_client.close()
            return success

    def read_events(self, stream_name):
        try:
            return self.esdb_client.get_stream(stream_name=stream_name)
        except Exception as e:
            logger.error(f"Error while reading stream {stream_name}: {e}")
            return []
        finally:
            self.esdb_client.close()