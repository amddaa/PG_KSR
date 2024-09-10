import json
import logging
import uuid
from datetime import datetime

from django.db import transaction, DatabaseError

from ..events.train_event_types import TrainEventBrokerNames, TrainEventType
from ..repository.event_repository import EventRepository
from ..repository.train_repository_query import TrainRepositoryQuery

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrainQueryService:
    def __init__(self, train_repository: TrainRepositoryQuery, event_repository: EventRepository):
        self.train_repository = train_repository
        self.event_repository = event_repository

    def create_schedule(self, train_number, departure_time, arrival_time, max_seats, expected_version):
        try:
            event_data = {'train_number': train_number,
                          'departure_time': departure_time.isoformat(),
                          'arrival_time': arrival_time.isoformat(),
                          'max_seats': max_seats,
                          'event_id': str(uuid.uuid4()),
                          'timestamp': datetime.utcnow().isoformat()}
            success = self.event_repository.append_event(
                str(TrainEventBrokerNames.TRAIN_EVENT_STREAM_NAME),
                str(TrainEventType.TRAIN_SCHEDULE_CREATED),
                event_data,
                expected_version)

            if success:
                with transaction.atomic():
                    self.train_repository.create_schedule(
                        train_number=train_number,
                        departure_time=departure_time,
                        arrival_time=arrival_time,
                        max_seats=max_seats,
                    )
        except DatabaseError as db_error:
            logger.error(f"Database error while creating train schedule: {db_error}")
            raise
        except Exception as ex:
            logger.error(f"Unexpected error in create_schedule: {ex}")
            raise

        if not success:
            raise Exception("Failed to create train schedule")

    @staticmethod
    def get_trains_with_max_seats(event_repository: EventRepository):
        from ..models import TrainScheduleQuery
        events = event_repository.read_events(TrainEventBrokerNames.TRAIN_EVENT_STREAM_NAME.value)
        trains_with_seats = {}

        for event in events:
            event_data = json.loads(event.data)
            event_data['departure_time'] = event_data['arrival_time']  # TODO, just add it somewhere and save
            train_schedule = TrainScheduleQuery.data_to_obj(event_data)

            if event.type == TrainEventType.TRAIN_SCHEDULE_CREATED.value:
                trains_with_seats[(train_schedule.train_number, train_schedule.arrival_time)] = trains_with_seats.get((train_schedule.train_number, train_schedule.arrival_time), 0)
                trains_with_seats[(train_schedule.train_number, train_schedule.arrival_time)] = train_schedule.max_seats

            elif event.type == TrainEventType.TRAIN_SCHEDULE_UPDATED.value:
                raise NotImplementedError

            elif event.type == TrainEventType.TRAIN_SCHEDULE_DELETED.value:
                raise NotImplementedError

        return trains_with_seats
