from django.db import models
from .service.command_service import TrainCommandService


class TrainSchedule(models.Model):
    train_number = models.CharField(max_length=100)
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()

    class Meta:
        app_label = "trains"
        db_table = "train_schedule"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        service = TrainCommandService()

        if is_new:
            service.create_train_schedule(self.train_number, self.departure_time, self.arrival_time)
        else:
            service.update_train_schedule(self.train_number, self.departure_time, self.arrival_time)

    def delete(self, *args, **kwargs):
        service = TrainCommandService()
        service.delete_train_schedule(self.train_number, self.departure_time)
