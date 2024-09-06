from datetime import datetime

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .repository.read_repository import TrainReadRepository
from .serializers import TrainScheduleSerializer
from .service.command_service import TrainCommandService
from .service.query_service import TrainQueryService


@api_view(['GET'])
def healthcheck(request):
    return Response({"status": "ok"}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST', 'PUT'])
def train_schedules(request):
    try:
        if request.method == 'GET':
            repository = TrainReadRepository()
            service = TrainQueryService(repository)

            schedules = service.get_all_schedules()
            serializer = TrainScheduleSerializer(schedules, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        elif request.method == 'POST':
            serializer = TrainScheduleSerializer(data=request.data)
            if serializer.is_valid():
                data = serializer.validated_data
                train_number = data.get('train_number')
                departure_time = data.get('departure_time')
                arrival_time = data.get('arrival_time')

                service = TrainCommandService()
                if not service.can_add_new_schedule(train_number, departure_time, arrival_time):
                    return Response({'error': 'A train schedule for this train number already exists in the specified '
                                              'time window.'}, status=status.HTTP_409_CONFLICT)

                service.create_train_schedule(train_number, departure_time, arrival_time)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'PUT':
            serializer = TrainScheduleSerializer(data=request.data)

            if serializer.is_valid():
                data = serializer.validated_data
                train_number = data.get('train_number')
                new_departure_time = data.get('departure_time')
                new_arrival_time = data.get('arrival_time')

                old_departure_time = datetime.fromisoformat(request.data.get('old_departure_time'))
                old_arrival_time = datetime.fromisoformat(request.data.get('old_arrival_time'))

                if not old_departure_time or not old_arrival_time:
                    return Response(
                        {'error': 'Old schedule details (old_departure_time, old_arrival_time) are required.'},
                        status=status.HTTP_400_BAD_REQUEST)

                service = TrainCommandService()
                if not service.can_update_schedule(train_number, old_departure_time, old_arrival_time,
                                                   new_departure_time, new_arrival_time):
                    return Response({'error': 'The train schedule update cannot be made.'},
                                    status=status.HTTP_400_BAD_REQUEST)

                service.update_train_schedule(train_number, old_departure_time, old_arrival_time, new_departure_time,
                                              new_arrival_time)
                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_train_detail(request, pk):
    pass
