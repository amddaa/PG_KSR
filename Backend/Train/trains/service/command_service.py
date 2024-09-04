import uuid
from datetime import datetime

from ..events.handlers import TrainEventHandler
from ..repository.event_repository import TrainEventRepository


class TrainCommandService:
    def __init__(self):
        self.event_repository = TrainEventRepository()
        self.event_handler = TrainEventHandler()
        self.stream_name = 'train-schedule-stream'

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
        self._save_to_eventstore_and_publish_event(self.stream_name, 'TrainScheduleCreated', event_data)

    def update_train_schedule(self, train_number, departure_time, arrival_time):
        event_data = {
            "train_number": train_number,
            "departure_time": departure_time.isoformat(),
            "arrival_time": arrival_time.isoformat(),
        }
        self._save_to_eventstore_and_publish_event(self.stream_name, 'TrainScheduleUpdated', event_data)

    def delete_train_schedule(self, train_number, departure_time):
        event_data = {
            "train_number": train_number,
            "departure_time": departure_time.isoformat(),
        }
        self._save_to_eventstore_and_publish_event(self.stream_name, 'TrainScheduleDeleted', event_data)


