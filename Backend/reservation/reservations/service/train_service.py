import logging
from django.db import transaction, DatabaseError

from ..repository.train_repository import TrainRepository

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TrainQueryService:
    def __init__(self, repository: TrainRepository):
        self.repository = repository

    def create_schedule(self, train_number, departure_time, arrival_time, max_seats):
        try:
            with transaction.atomic():
                self.repository.create_schedule(
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
