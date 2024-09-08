import logging

from esdbclient import EventStoreDBClient, NewEvent
from django.conf import settings
from esdbclient.exceptions import WrongCurrentVersion
from rest_framework.utils import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventRepository:
    def __init__(self):
        self.esdb_client = EventStoreDBClient(uri=f"esdb://{settings.ESDB_HOST}:{settings.ESDB_PORT}?Tls=false")

    def append_event(self, stream_name, event_type, event_data, expected_version):
        success = False
        try:
            event_data_bytes = json.dumps(event_data).encode('utf-8')
            event = NewEvent(type=event_type, data=event_data_bytes)

            self.esdb_client.append_to_stream(
                stream_name=stream_name,
                events=[event],
                current_version=expected_version
            )
            logger.info(f"Successfully added {event_type} to eventstore")
            success = True
        except WrongCurrentVersion as e:
            logger.error(f"Error while appending {event_type} - wrong version: {e}")
        except Exception as e:
            logger.error(f"Error while appending {event_type}: {e}")
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

    def get_stream_version(self, stream_name):
        return str(self.esdb_client.get_current_version(stream_name))
