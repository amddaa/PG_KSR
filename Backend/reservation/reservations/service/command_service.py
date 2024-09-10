import uuid
from datetime import datetime
import logging
from rest_framework.utils import json

from .train_service import TrainQueryService
from ..events.event_handler import EventHandler
from ..events.event_types import EventBrokerNames, EventType
from ..repository.event_repository import EventRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CommandService:
    def __init__(self, repository: EventRepository, handler: EventHandler):
        self.stream_name = EventBrokerNames.TRAIN_RESERVATION_EVENT_STREAM_NAME.value
        self.event_repository = repository
        self.event_handler = handler

    def get_current_reservations(self):
        from ..models import ReservationCommand
        events = self.event_repository.read_events(self.stream_name)
        reservations = {}

        for event in events:
            event_data = json.loads(event.data)
            event_data['departure_time'] = event_data['arrival_time']  # TODO, just add it somewhere and save
            reservation = ReservationCommand.data_to_obj(event_data)

            if event.type == EventType.TRAIN_RESERVED.value:
                reservations[(reservation.train_number, reservation.arrival_time)] = reservations.get(
                    (reservation.train_number, reservation.arrival_time), 0)
                reservations[(reservation.train_number, reservation.arrival_time)] += reservation.reserved_seats

            elif event.type == EventType.TRAIN_RESERVATION_UPDATED.value:
                raise NotImplementedError
                # old_departure_time = datetime.fromisoformat(event_data.get('old_departure_time'))
                # old_arrival_time = datetime.fromisoformat(event_data.get('old_arrival_time'))
                # new_departure_time = departure_time
                # new_arrival_time = arrival_time
                #
                # if train_number not in train_schedules:
                #     logger.error("Couldn't find TrainSchedule to be updated")
                #     continue
                #
                # for i, (existing_departure_time, existing_arrival_time) in enumerate(train_schedules[train_number]):
                #     if existing_departure_time == old_departure_time and existing_arrival_time == old_arrival_time:
                #         train_schedules[train_number][i] = (new_departure_time, new_arrival_time)
                #         break

            elif event.type == EventType.TRAIN_RESERVATION_CANCELLED.value:
                raise NotImplementedError

        return reservations

    def can_add_new_reservation(self, reservation):
        if reservation.reserved_seats > 10:
            logger.error("Can't add new reservation with 10 or more seats")
            return False

        trains_and_max_seats = TrainQueryService.get_trains_with_max_seats(self.event_repository)
        if (reservation.train_number, reservation.arrival_time) not in trains_and_max_seats:
            logger.error("Can't find this train in propagated eventstore")
            return False

        current_reservation = self.get_current_reservations()
        if not current_reservation:
            logger.error("Can't find this train in current eventstore")
            return True

        new_reservations = current_reservation.get((reservation.train_number, reservation.arrival_time), 0)
        new_reservations += reservation.reserved_seats
        max_seats = trains_and_max_seats[(reservation.train_number, reservation.arrival_time)]
        if new_reservations > max_seats:
            logger.error("Reserved seat number exceeds maximum seats")
            return False

        return True

    # def can_update_schedule(self, train_number, old_departure_time, old_arrival_time, departure_time, arrival_time):
    #     current_schedules = self.get_current_train_schedules()
    #
    #     if train_number not in current_schedules:
    #         logger.info("Didn't find train number to update")
    #         return False
    #
    #     found_schedule_to_update = False
    #     for i in range(len(current_schedules[train_number])):
    #         d = current_schedules[train_number][i][0]
    #         a = current_schedules[train_number][i][1]
    #         if d == old_departure_time and a == old_arrival_time:
    #             current_schedules[train_number].pop(i)
    #             found_schedule_to_update = True
    #             break
    #
    #     if not found_schedule_to_update:
    #         logger.info("Didn't find candidate to update")
    #         return False
    #
    #     for existing_departure_time, existing_arrival_time in current_schedules[train_number]:
    #         if existing_departure_time <= departure_time <= existing_arrival_time:
    #             logger.info(
    #                 f"Departure time overlap {existing_departure_time} <= {departure_time} <= {existing_arrival_time}")
    #             return False
    #         if existing_departure_time <= arrival_time <= existing_arrival_time:
    #             logger.info(
    #                 f"Arrival time overlap {existing_departure_time} <= {arrival_time} <= {existing_arrival_time}")
    #             return False
    #
    #     return True

    def _save_to_eventstore_and_publish_event(self, stream_name, event_type, event_data, expected_version):
        event_data['event_id'] = str(uuid.uuid4())
        event_data['timestamp'] = datetime.utcnow().isoformat()
        event_data['is_finished'] = str(True)
        success = self.event_repository.append_event(stream_name, event_type, event_data, expected_version)
        if success:
            event_data['expected_version'] = str(expected_version)  # propagation for other microservices
            self.event_handler.publish_event(event_type, event_data)
        return success

    def create_train_reservation(self, command, expected_version):
        event_data = command.to_data()
        return self._save_to_eventstore_and_publish_event(self.stream_name, EventType.TRAIN_RESERVED.value, event_data,
                                                          expected_version)

    # def update_train_schedule(self, train_number, old_departure_time, old_arrival_time, new_departure_time, new_arrival_time, expected_version):
    #     event_data = {
    #         "train_number": train_number,
    #         "departure_time": new_departure_time.isoformat(),
    #         "arrival_time": new_arrival_time.isoformat(),
    #         "old_departure_time": old_departure_time.isoformat(),
    #         "old_arrival_time": old_arrival_time.isoformat(),
    #     }
    #     return self._save_to_eventstore_and_publish_event(self.stream_name, TrainEventType.TRAIN_SCHEDULE_UPDATED.value, event_data, expected_version)

    def send_status_to_query_db_if_failed(self, event_type, command):
        try:
            event_data = command.to_data()
            self.event_handler.publish_event(event_type, event_data)
        except Exception as e:
            logger.error("Couldn't publish status update to DB because of error: {}".format(e))
