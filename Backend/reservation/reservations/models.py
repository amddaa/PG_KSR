from datetime import datetime

from django.db import models


class TrainScheduleQuery(models.Model):
    train_number = models.CharField(max_length=255)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    max_seats = models.PositiveIntegerField()
    old_departure_time = models.DateTimeField(null=True, blank=True)
    old_arrival_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        app_label = 'reservations'
        indexes = [
            models.Index(fields=['train_number', 'departure_time']),
        ]

    @staticmethod
    def data_to_obj(data):
        train_number = data.get('train_number')
        departure_time = datetime.fromisoformat(data.get('departure_time'))
        arrival_time = datetime.fromisoformat(data.get('arrival_time'))
        max_seats = int(data.get('max_seats'))

        old_departure_time = data.get('old_departure_time')
        old_arrival_time = data.get('old_arrival_time')
        old_departure_time = datetime.fromisoformat(old_departure_time) if old_departure_time else None
        old_arrival_time = datetime.fromisoformat(old_arrival_time) if old_arrival_time else None

        return TrainScheduleQuery(train_number=train_number,
                                  departure_time=departure_time,
                                  arrival_time=arrival_time,
                                  max_seats=max_seats,
                                  old_departure_time=old_departure_time,
                                  old_arrival_time=old_arrival_time
                                  )


class ReservationCommand(models.Model):
    train_number = models.CharField(max_length=255)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    reserved_seats = models.PositiveIntegerField()
    operation_id = models.UUIDField()
    is_finished = models.BooleanField(default=False)
    message = models.TextField(default="")

    @staticmethod
    def data_to_obj(data):
        train_number = data.get('train_number')
        departure_time = datetime.fromisoformat(data.get('departure_time'))
        arrival_time = datetime.fromisoformat(data.get('arrival_time'))
        reserved_seats = int(data.get('reserved_seats'))
        operation_id = data.get('operation_id')
        is_finished = bool(data.get('is_finished'))
        message = data.get('message')

        return ReservationCommand(train_number=train_number,
                                  departure_time=departure_time,
                                  arrival_time=arrival_time,
                                  reserved_seats=reserved_seats,
                                  operation_id=operation_id,
                                  is_finished=is_finished,
                                  message=message)

    def to_data(self):
        return {
            "train_number": self.train_number,
            "arrival_time": self.arrival_time.isoformat(),
            "reserved_seats": self.reserved_seats,
            "operation_id": self.operation_id,
            "is_finished": self.is_finished,
            "message": self.message
        }
