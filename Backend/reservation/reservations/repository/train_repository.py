class TrainRepository:

    def create_schedule(self, train_number, departure_time, arrival_time, max_seats):
        from ..models import TrainScheduleQuery
        TrainScheduleQuery.objects.create(
            train_number=train_number,
            departure_time=departure_time,
            arrival_time=arrival_time,
            max_seats=max_seats,
        )
