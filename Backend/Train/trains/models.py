from django.db import models


class TrainScheduleCommand:
    def __init__(self, train_number, departure_time, arrival_time):
        self.train_number = train_number
        self.departure_time = departure_time
        self.arrival_time = arrival_time


class TrainScheduleQuery(models.Model):
    train_number = models.CharField(max_length=255)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    class Meta:
        app_label = 'trains'
        indexes = [
            models.Index(fields=['train_number', 'departure_time']),
        ]
