from rest_framework import serializers
from .models import TrainScheduleCommand


class TrainScheduleSerializer(serializers.Serializer):
    train_number = serializers.CharField(max_length=100)
    departure_time = serializers.DateTimeField()
    arrival_time = serializers.DateTimeField()
    version = serializers.IntegerField(required=False)

    def validate(self, data):
        if data['departure_time'] >= data['arrival_time']:
            raise serializers.ValidationError("Departure time must be earlier than arrival time.")
        return data

    def create(self, validated_data):
        return TrainScheduleCommand(**validated_data)

    def update(self, instance, validated_data):
        instance.train_number = validated_data.get('train_number', instance.train_number)
        instance.departure_time = validated_data.get('departure_time', instance.departure_time)
        instance.arrival_time = validated_data.get('arrival_time', instance.arrival_time)
        return instance
