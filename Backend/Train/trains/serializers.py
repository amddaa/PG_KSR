from rest_framework import serializers
from train.trains.models import TrainSchedule


class TrainScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainSchedule
        fields = ['id', 'train_number', 'departure_time', 'arrival_time']
