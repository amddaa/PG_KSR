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

    def _save_to_eventstore_and_publish_event(self, stream_name, event_type, event_data, expected_version):
        event_data['event_id'] = str(uuid.uuid4())
        event_data['timestamp'] = datetime.utcnow().isoformat()
        success = self.event_repository.append_event(stream_name, event_type, event_data, expected_version)
        if success:
            event_data['expected_version'] = str(expected_version)  # propagation for other microservices
            self.event_handler.publish_event(event_type, event_data)
            # TODO Handle failure here: retries, scheduled transfer
        return success

    def create_train_reservation(self, command, expected_version):
        command.is_finished = True
        command.is_successful = True
        command.message = "Reserved successfully"
        event_data = command.to_data()
        return self._save_to_eventstore_and_publish_event(self.stream_name, EventType.TRAIN_RESERVED.value, event_data,
                                                          expected_version)

    def send_status_to_query_db_if_failed(self, event_type, command, reason):
        try:
            command.is_finished = True
            command.is_successful = False
            command.message = reason
            event_data = command.to_data()
            self.event_handler.publish_event(event_type, event_data)
        except Exception as e:
            logger.error("Couldn't publish event status update to DB because of error: {}".format(e))
