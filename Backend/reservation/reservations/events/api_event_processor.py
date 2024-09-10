from datetime import datetime

import pika
import threading
import logging
from django.conf import settings
from esdbclient import StreamState
from rest_framework.utils import json

from .event_types import EventBrokerNames, EventType
from ..serializers import ReservationSerializer
from ..service.command_service import CommandService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class APIEventProcessor(threading.Thread):
    def __init__(self, service: CommandService):
        super().__init__(daemon=True)
        self.service = service
        self.rabbitmq_connection = None
        self.rabbitmq_channel_train = None
        try:
            rabbitmq_uri = f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/"
            self.rabbitmq_connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_uri))
            self.rabbitmq_channel_train = self.rabbitmq_connection.channel()
            self.rabbitmq_channel_train.queue_declare(queue=EventBrokerNames.TRAIN_RESERVATION_COMMAND_QUEUE_NAME.value,
                                                      durable=True)

            logger.info("APIEventProcessor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize EventProcessor: {e}")

    def run(self):
        try:
            logger.info("APIEventProcessor starting to consume events")
            self.rabbitmq_channel_train.basic_consume(
                queue=EventBrokerNames.TRAIN_RESERVATION_COMMAND_QUEUE_NAME.value,
                on_message_callback=self.process_event,
                auto_ack=False
            )
            self.rabbitmq_channel_train.start_consuming()
        except Exception as e:
            logger.error(f"Exception in APIEventProcessor: {e}")
        finally:
            if self.rabbitmq_channel_train:
                self.rabbitmq_channel_train.close()
            if self.rabbitmq_connection:
                self.rabbitmq_connection.close()
            logger.info("APIEventProcessor stopped")

    def process_event(self, ch, method, properties, body):
        try:
            event = json.loads(body)
            event_type_str = event.get('event_type')
            event_data = event.get('data')

            try:
                event_type = EventType(event_type_str)
            except ValueError:
                logger.warning(f"Unknown event type: {event_type_str}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            logger.info(f"Processing api command event: {event_type}")
            if event_type == EventType.TRAIN_RESERVED:
                self._handle_train_reservation(event_data)
            elif event_type == EventType.TRAIN_RESERVATION_UPDATED:
                logger.warning(f"I'm not handling this event: {event_type}")
            elif event_type == EventType.TRAIN_RESERVATION_CANCELLED:
                logger.warning(f"I'm not handling this event: {event_type}")
            else:
                logger.warning(f"Unknown event type: {event_type}")

            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def _handle_train_reservation(self, event_data):
        from ..models import ReservationCommand
        try:
            serializer = ReservationSerializer(data=event_data)
            if serializer.is_valid():
                reservation_command = ReservationCommand.data_to_obj(event_data)
                expected_version = event_data.get('version')

                if not expected_version:
                    reservation_command.is_finished = False
                    reservation_command.message = "Version is required"
                    self.service.send_status_to_query_db_if_failed(
                        event_type=EventType.TRAIN_RESERVATION_FAIL_STATUS_PROPAGATION.value,
                        command=reservation_command
                    )
                    return

                logger.error("passed expected version")

                expected_version = int(expected_version) if expected_version != str(
                    StreamState.NO_STREAM) else StreamState.NO_STREAM
                if not self.service.can_add_new_reservation(reservation_command):
                    reservation_command.is_finished = False
                    reservation_command.message = "Could not add new reservation due to logic conflicts"
                    self.service.send_status_to_query_db_if_failed(
                        event_type=EventType.TRAIN_RESERVATION_FAIL_STATUS_PROPAGATION.value,
                        command=reservation_command
                    )
                    return

                logger.error("passed can add new reservation")

                if not self.service.create_train_reservation(
                        reservation_command,
                        expected_version,
                ):
                    reservation_command.is_finished = False
                    reservation_command.message = "Failed to create train schedule. Please try again later"
                    self.service.send_status_to_query_db_if_failed(
                        event_type=EventType.TRAIN_RESERVATION_FAIL_STATUS_PROPAGATION.value,
                        command=reservation_command
                    )
                    return

            logger.info(f"Successfully created train schedule: {event_data.get('train_number')}")
        except Exception as e:
            logger.error(f"Failed to create train schedule: {e}")
            raise
