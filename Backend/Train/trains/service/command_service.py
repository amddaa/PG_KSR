import uuid
from datetime import datetime
import logging

from rest_framework.utils import json

from ..events.event_handler import TrainEventHandler
from ..repository.event_repository import TrainEventRepository
from ..events.event_types import TrainEventType, TrainEventBrokerNames

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrainCommandService:
    def __init__(self):
        self.stream_name = TrainEventBrokerNames.TRAIN_EVENT_STREAM_NAME.value
        self.event_repository = TrainEventRepository()
        self.event_handler = TrainEventHandler()

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
                old_departure_time = datetime.fromisoformat(event_data.get('old_departure_time'))
                old_arrival_time = datetime.fromisoformat(event_data.get('old_arrival_time'))
                new_departure_time = departure_time
                new_arrival_time = arrival_time

                if train_number not in train_schedules:
                    logger.error("Couldn't find TrainSchedule to be updated")
                    continue

                for i, (existing_departure_time, existing_arrival_time) in enumerate(train_schedules[train_number]):
                    if existing_departure_time == old_departure_time and existing_arrival_time == old_arrival_time:
                        train_schedules[train_number][i] = (new_departure_time, new_arrival_time)
                        break

            elif event.type == TrainEventType.TRAIN_SCHEDULE_DELETED.value:
                raise NotImplementedError

        return train_schedules

    def can_add_new_schedule(self, train_number, departure_time, arrival_time):
        current_schedules = self.get_current_train_schedules()

        if train_number in current_schedules:
            for existing_departure_time, existing_arrival_time in current_schedules[train_number]:
                if existing_departure_time <= departure_time <= existing_arrival_time:
                    return False
                if existing_departure_time <= arrival_time <= existing_arrival_time:
                    return False
        return True

    def can_update_schedule(self, train_number, old_departure_time, old_arrival_time, departure_time, arrival_time):
        current_schedules = self.get_current_train_schedules()

        if train_number not in current_schedules:
            logger.info("Didn't find train number to update")
            return False

        found_schedule_to_update = False
        for i in range(len(current_schedules[train_number])):
            d = current_schedules[train_number][i][0]
            a = current_schedules[train_number][i][1]
            if d == old_departure_time and a == old_arrival_time:
                current_schedules[train_number].pop(i)
                found_schedule_to_update = True
                break

        if not found_schedule_to_update:
            logger.info("Didn't find candidate to update")
            return False

        for existing_departure_time, existing_arrival_time in current_schedules[train_number]:
            if existing_departure_time <= departure_time <= existing_arrival_time:
                logger.info(
                    f"Departure time overlap {existing_departure_time} <= {departure_time} <= {existing_arrival_time}")
                return False
            if existing_departure_time <= arrival_time <= existing_arrival_time:
                logger.info(
                    f"Arrival time overlap {existing_departure_time} <= {arrival_time} <= {existing_arrival_time}")
                return False

        return True

    def _save_to_eventstore_and_publish_event(self, stream_name, event_type, event_data):
        event_data['event_id'] = str(uuid.uuid4())
        event_data['timestamp'] = datetime.utcnow().isoformat()
        success = self.event_repository.append_event(stream_name, event_type, event_data)
        if success:
            self.event_handler.publish_event(event_type, event_data)

    def create_train_schedule(self, train_number, departure_time, arrival_time):
        event_data = {
            "train_number": train_number,
            "departure_time": departure_time.isoformat(),
            "arrival_time": arrival_time.isoformat(),
        }
        self._save_to_eventstore_and_publish_event(self.stream_name, TrainEventType.TRAIN_SCHEDULE_CREATED.value, event_data)

    def update_train_schedule(self, train_number, old_departure_time, old_arrival_time, new_departure_time, new_arrival_time):
        event_data = {
            "train_number": train_number,
            "departure_time": new_departure_time.isoformat(),
            "arrival_time": new_arrival_time.isoformat(),
            "old_departure_time": old_departure_time.isoformat(),
            "old_arrival_time": old_arrival_time.isoformat(),
        }
        self._save_to_eventstore_and_publish_event(self.stream_name, TrainEventType.TRAIN_SCHEDULE_UPDATED.value, event_data)

