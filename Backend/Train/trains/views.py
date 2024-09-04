from rest_framework.decorators import api_view
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from rest_framework import status

from .events.handlers import TrainEventHandler
from .models import TrainSchedule
from .serializers import TrainScheduleSerializer

event_publisher = TrainEventHandler()


@api_view(['GET'])
def healthcheck(request):
    return Response({"status": "ok"}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def train_schedules(request):
    if request.method == 'GET':
        schedules = TrainSchedule.objects.all()
        serializer = TrainScheduleSerializer(schedules, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = TrainScheduleSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_train_detail(request, pk):
    schedule = get_object_or_404(TrainSchedule, pk=pk)
    serializer = TrainScheduleSerializer(schedule)
    return Response(serializer.data)


@api_view(['PUT'])
def update_train_schedule(request, pk):
    schedule = get_object_or_404(TrainSchedule, pk=pk)
    serializer = TrainScheduleSerializer(schedule, data=request.data, partial=True)
    if serializer.is_valid():
        updated_schedule = serializer.save()
        event_data = {
            'id': updated_schedule.id,
            'train_number': updated_schedule.train_number,
            'departure_time': updated_schedule.departure_time.isoformat(),
            'arrival_time': updated_schedule.arrival_time.isoformat(),
        }
        event_publisher.publish_event('TrainScheduleUpdated', event_data, 'train-schedule-stream')
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_train_schedule(request, pk):
    schedule = get_object_or_404(TrainSchedule, pk=pk)
    schedule.delete()
    event_data = {'id': pk}
    event_publisher.publish_event('TrainScheduleDeleted', event_data, 'train-schedule-stream')
    return Response({'detail': 'Train schedule deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def search_train_schedule(request):
    departure_time = request.query_params.get('departure_time')
    arrival_time = request.query_params.get('arrival_time')
    train_name = request.query_params.get('train_name')

    queryset = TrainSchedule.objects.all()

    if departure_time:
        queryset = queryset.filter(departure_time=departure_time)
    if arrival_time:
        queryset = queryset.filter(arrival_time=arrival_time)
    if train_name:
        queryset = queryset.filter(train_number=train_name)

    serializer = TrainScheduleSerializer(queryset, many=True)
    return Response(serializer.data)
