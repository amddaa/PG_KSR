

class TrainReadRepository:

    def create_schedule(self, train_number, departure_time, arrival_time):
        from ..models import TrainScheduleQuery
        TrainScheduleQuery.objects.create(
            train_number=train_number,
            departure_time=departure_time,
            arrival_time=arrival_time
        )

    def update_schedule(self, train_number, old_departure_time, old_arrival_time, new_departure_time, new_arrival_time):
        from ..models import TrainScheduleQuery
        TrainScheduleQuery.objects.filter(
            train_number=train_number,
            departure_time=old_departure_time,
            arrival_time=old_arrival_time
        ).update(
            departure_time=new_departure_time,
            arrival_time=new_arrival_time
        )

    def delete_schedule(self, train_number, departure_time, arrival_time):
        from ..models import TrainScheduleQuery
        TrainScheduleQuery.objects.filter(
            train_number=train_number,
            departure_time=departure_time,
            arrival_time=arrival_time
        ).delete()

    def get_all_schedules(self):
        from ..models import TrainScheduleQuery
        return TrainScheduleQuery.objects.all()
