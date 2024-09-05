import uuid
from datetime import datetime
import logging

from rest_framework.utils import json
from esdbclient import RecordedEvent

from ..events.handlers import TrainEventHandler
from ..repository.event_repository import TrainEventRepository
from ..events.event_types import TrainEventType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrainCommandService:
    def __init__(self):
        self.event_repository = TrainEventRepository()
        self.event_handler = TrainEventHandler()
        self.stream_name = 'train-schedule-stream'

    def get_current_train_schedules(self):
        events = self.event_repository.read_events(self.stream_name)
        train_schedules = {}

        for event in events:
            event_data = json.loads(event.data)
            train_number = event_data.get('train_number')
            departure_time = datetime.fromisoformat(event_data.get('departure_time'))
            arrival_time = datetime.fromisoformat(event_data.get('arrival_time'))

            if event.type == TrainEventType.TRAIN_SCHEDULE_CREATED.value:
                train_schedules[train_number] = train_schedules.get(train_number, [])
                train_schedules[train_number].append((departure_time, arrival_time))
            elif event.type == TrainEventType.TRAIN_SCHEDULE_UPDATED.value:
                raise NotImplementedError
            elif event.type == TrainEventType.TRAIN_SCHEDULE_DELETED.value:
                raise NotImplementedError

        return train_schedules

    def can_add_new_schedule(self, train_number, departure_time, arrival_time):
        current_schedules = self.get_current_train_schedules()

        if train_number in current_schedules:
            for existing_departure_time, existing_arrival_time in current_schedules[train_number]:
                logger.info(existing_departure_time, existing_arrival_time)
                if existing_departure_time <= departure_time <= existing_arrival_time:
                    return False
                if existing_departure_time <= arrival_time <= existing_arrival_time:
                    return False
        return True

    def _save_to_eventstore_and_publish_event(self, stream_name, event_type, event_data):
        event_data['event_id'] = str(uuid.uuid4())
        event_data['timestamp'] = datetime.utcnow().isoformat()
        success = self.event_repository.append_event(stream_name, event_type, event_data)
        if success:
            self.event_handler.publish_event(stream_name, event_type, event_data)

    def create_train_schedule(self, train_number, departure_time, arrival_time):
        event_data = {
            "train_number": train_number,
            "departure_time": departure_time.isoformat(),
            "arrival_time": arrival_time.isoformat(),
        }
        self._save_to_eventstore_and_publish_event(self.stream_name, TrainEventType.TRAIN_SCHEDULE_CREATED.value, event_data)

    def update_train_schedule(self, train_number, departure_time, arrival_time):
        event_data = {
            "train_number": train_number,
            "departure_time": departure_time.isoformat(),
            "arrival_time": arrival_time.isoformat(),
        }
        self._save_to_eventstore_and_publish_event(self.stream_name, TrainEventType.TRAIN_SCHEDULE_UPDATED.value, event_data)

    def delete_train_schedule(self, train_number, departure_time):
        event_data = {
            "train_number": train_number,
            "departure_time": departure_time.isoformat(),
        }
        self._save_to_eventstore_and_publish_event(self.stream_name, TrainEventType.TRAIN_SCHEDULE_DELETED.value, event_data)


