from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .serializers import TrainScheduleSerializer
from .service.command_service import TrainCommandService


@api_view(['GET'])
def healthcheck(request):
    return Response({"status": "ok"}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST'])
def train_schedules(request):
    if request.method == 'GET':
        return Response()

    elif request.method == 'POST':
        serializer = TrainScheduleSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            train_number = data.get('train_number')
            departure_time = data.get('departure_time')
            arrival_time = data.get('arrival_time')

            service = TrainCommandService()
            if not service.can_add_new_schedule(train_number, departure_time, arrival_time):
                return Response({"error": "A train schedule for this train number already exists in the specified "
                                          "time window."}, status=status.HTTP_409_CONFLICT)

            service.create_train_schedule(train_number, departure_time, arrival_time)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_train_detail(request, pk):
    pass


@api_view(['PUT'])
def update_train_schedule(request, pk):
    pass


@api_view(['DELETE'])
def delete_train_schedule(request, pk):
    pass


@api_view(['GET'])
def search_train_schedule(request):
    pass