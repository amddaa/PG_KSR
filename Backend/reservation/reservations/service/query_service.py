from django.db import transaction


class QueryService:
    from ..repository.read_repository import ReadRepository

    def __init__(self, repository: ReadRepository):
        self.repository = repository

    def create_schedule(self, command):
        with transaction.atomic():
            self.repository.create_reservation(command)

    def get_reservation_status(self, user_id, operation_id):
        reservation = self.repository.get_reservation(user_id, operation_id)
        if not reservation:
            raise ValueError("Reservation not found")
        return reservation
