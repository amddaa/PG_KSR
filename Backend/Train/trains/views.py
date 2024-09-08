from datetime import datetime

from esdbclient import StreamState
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .events.event_types import TrainEventBrokerNames
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
                max_seats = data.get('max_seats')
                expected_version = request.data.get('version')

                if not expected_version:
                    return Response(
                        {'error': 'Version is required.'},
                        status=status.HTTP_400_BAD_REQUEST)

                expected_version = int(expected_version) if expected_version != str(StreamState.NO_STREAM) else StreamState.NO_STREAM

                service = TrainCommandService()
                if not service.can_add_new_schedule(train_number, departure_time, arrival_time):
                    return Response({'error': 'A train schedule for this train number already exists in the specified '
                                              'time window.'}, status=status.HTTP_409_CONFLICT)

                if not service.create_train_schedule(train_number, departure_time, arrival_time, max_seats, expected_version):
                    return Response({'error': 'Failed to create train schedule. Please try again later.'},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.method == 'PUT':
            serializer = TrainScheduleSerializer(data=request.data)

            if serializer.is_valid():
                data = serializer.validated_data
                train_number = data.get('train_number')
                new_departure_time = data.get('departure_time')
                new_arrival_time = data.get('arrival_time')
                expected_version = int(request.data.get('version'))
                old_departure_time = datetime.fromisoformat(request.data.get('old_departure_time'))
                old_arrival_time = datetime.fromisoformat(request.data.get('old_arrival_time'))

                if not expected_version:
                    return Response(
                        {'error': 'Version is required.'},
                        status=status.HTTP_400_BAD_REQUEST)

                expected_version = int(expected_version) if expected_version != str(StreamState.NO_STREAM) else StreamState.NO_STREAM

                if not old_departure_time or not old_arrival_time:
                    return Response(
                        {'error': 'Old schedule details (old_departure_time, old_arrival_time) are required.'},
                        status=status.HTTP_400_BAD_REQUEST)

                service = TrainCommandService()
                if not service.can_update_schedule(train_number, old_departure_time, old_arrival_time,
                                                   new_departure_time, new_arrival_time):
                    return Response({'error': 'The train schedule update cannot be made.'},
                                    status=status.HTTP_400_BAD_REQUEST)

                if not service.update_train_schedule(train_number, old_departure_time, old_arrival_time,
                                                     new_departure_time,
                                                     new_arrival_time, expected_version):
                    return Response({'error': 'Failed to update train schedule. Please try again later.'},
                                    status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                return Response(serializer.data, status=status.HTTP_200_OK)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_train_detail(request):
    pass


@api_view(['GET'])
def get_stream_version(request):
    try:
        service = TrainCommandService()
        version = service.event_repository.get_stream_version(TrainEventBrokerNames.TRAIN_EVENT_STREAM_NAME.value)

        if version is not None:
            return Response({"version": version}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Unable to retrieve version."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
