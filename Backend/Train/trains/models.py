from django.db import models
from dj_cqrs.mixins import MasterMixin

from train.trains.events.handlers import TrainEventHandler


class TrainSchedule(MasterMixin, models.Model):
    CQRS_ID = 'train_schedule'

    train_number = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    class Meta:
        db_table = 'train_schedule'

    def save(self, *args, **kwargs):
        is_new = self.pk is None

        event_handler = TrainEventHandler()
        event_data = {
            'train_number': self.train_number,
            'departure_time': self.departure_time.isoformat(),
            'arrival_time': self.arrival_time.isoformat(),
        }

        if is_new:
            event_handler.publish_event('TrainScheduleCreated', event_data, 'train-schedule-stream')
        else:
            event_handler.publish_event('TrainScheduleUpdated', event_data, 'train-schedule-stream')

        event_handler.close()

    def delete(self, *args, **kwargs):
        event_handler = TrainEventHandler()
        event_data = {
            'train_number': self.train_number,
            'departure_time': self.departure_time.isoformat(),
            'arrival_time': self.arrival_time.isoformat(),
        }
        event_handler.publish_event('TrainScheduleDeleted', event_data, 'train-schedule-stream')
        event_handler.close()
