
class ReadRepository:
    def create_reservation(self, command):
        command.save()

    def get_reservation(self, user_id, operation_id):
        from ..models import ReservationCommand
        try:
            return (ReservationCommand.objects.filter(user_id=user_id, operation_id=operation_id)
                    .values('is_finished', 'is_successful', 'message').first())
        except ReservationCommand.DoesNotExist:
            return None
