from django.db import transaction
from ..repository.read_repository import TrainReadRepository


class TrainQueryService:
    def __init__(self, repository: TrainReadRepository):
        self.repository = repository

    def create_schedule(self, train_number, departure_time, arrival_time):
        with transaction.atomic():
            self.repository.create_schedule(
                train_number=train_number,
                departure_time=departure_time,
                arrival_time=arrival_time
            )

    def update_schedule(self, train_number, old_departure_time, old_arrival_time, new_departure_time, new_arrival_time):
        with transaction.atomic():
            self.repository.update_schedule(
                train_number=train_number,
                old_departure_time=old_departure_time,
                old_arrival_time=old_arrival_time,
                new_departure_time=new_departure_time,
                new_arrival_time=new_arrival_time
            )

    def delete_schedule(self, train_number, departure_time, arrival_time):
        with transaction.atomic():
            self.repository.delete_schedule(
                train_number=train_number,
                departure_time=departure_time,
                arrival_time=arrival_time
            )

    def get_all_schedules(self):
        return self.repository.get_all_schedules()
