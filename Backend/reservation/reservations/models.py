from django.db import models


class TrainScheduleQuery(models.Model):
    train_number = models.CharField(max_length=255)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    max_seats = models.PositiveIntegerField()

    class Meta:
        app_label = 'reservations'
        indexes = [
            models.Index(fields=['train_number', 'departure_time']),
        ]
