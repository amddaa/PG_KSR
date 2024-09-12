import uuid
from datetime import datetime

import pika
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.utils import json
from rest_framework.views import APIView
from django.conf import settings

from .authenticate import CustomAuthentication
from .events.event_types import EventBrokerNames, EventType
from .repository.event_repository import EventRepository
from .repository.read_repository import ReadRepository
from .serializers import ReservationSerializer
from .service.query_service import QueryService


@api_view(['GET'])
def healthcheck(request):
    return Response({"status": "ok"}, status=status.HTTP_200_OK)


class ReservationStatusView(APIView):
    authentication_classes = [CustomAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, operation_id):
        user_id = request.user.id
        repository = ReadRepository()
        query_service = QueryService(repository)

        try:
            reservation_data = query_service.get_reservation_status(user_id, operation_id)
            return Response(reservation_data, status=200)
        except ValueError as e:
            return Response({'error': str(e)}, status=404)


class ReservationCommandView(APIView):
    authentication_classes = [CustomAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ReservationSerializer(data=request.data)

        if serializer.is_valid():
            command_data = serializer.validated_data
            operation_id = str(uuid.uuid4())
            command_data['operation_id'] = operation_id
            command_data['is_finished'] = False
            command_data['arrival_time'] = command_data['arrival_time'].isoformat()
            command_data['departure_time'] = command_data['departure_time'].isoformat()
            command_data['user_id'] = request.user.id
            message = {
                'event_id': operation_id,
                'event_type': EventType.TRAIN_RESERVED.value,
                'data': command_data,
                'timestamp': datetime.utcnow().isoformat(),
            }

            try:
                rabbitmq_uri = f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/"
                connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_uri))
                channel = connection.channel()
                channel.queue_declare(queue=EventBrokerNames.TRAIN_RESERVATION_COMMAND_QUEUE_NAME.value, durable=True)
                channel.basic_publish(
                    exchange='',
                    routing_key=EventBrokerNames.TRAIN_RESERVATION_COMMAND_QUEUE_NAME.value,
                    body=json.dumps(message)
                )
                connection.close()
                return Response({
                    "message": "Reservation has been queued",
                    "operation_id": operation_id
                }, status=status.HTTP_202_ACCEPTED)

            except Exception as e:
                return Response({"error": "An error occurred: {}".format(str(e))},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_stream_version(request):
    try:
        event_repository = EventRepository()
        version = event_repository.get_stream_version(EventBrokerNames.TRAIN_RESERVATION_EVENT_STREAM_NAME.value)

        if version is not None:
            return Response({"version": version}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Unable to retrieve version."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)