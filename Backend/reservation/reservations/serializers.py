from rest_framework import serializers


class ReservationSerializer(serializers.Serializer):
    train_number = serializers.CharField(max_length=255)
    departure_time = serializers.DateTimeField()
    arrival_time = serializers.DateTimeField()
    reserved_seats = serializers.IntegerField(min_value=1)
    version = serializers.CharField(required=False)

    def validate(self, data):
        if data['departure_time'] >= data['arrival_time']:
            raise serializers.ValidationError("Departure time must be before arrival time.")
        if data['reserved_seats'] <= 0:
            raise serializers.ValidationError("Reserved seats must be greater than zero.")
        return data
