from datetime import datetime
import pika
import threading
import logging
from django.conf import settings
from esdbclient import StreamState
from rest_framework.utils import json
from .event_types import EventBrokerNames, EventType
from ..service.query_service import QueryService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventProcessor(threading.Thread):
    def __init__(self, service: QueryService):
        super().__init__(daemon=True)
        self.service = service
        self.rabbitmq_connection = None
        self.rabbitmq_channel_train = None
        try:
            rabbitmq_uri = f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/"
            self.rabbitmq_connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_uri))
            self.rabbitmq_channel_train = self.rabbitmq_connection.channel()
            self.rabbitmq_channel_train.exchange_declare(exchange=EventBrokerNames.TRAIN_RESERVATION_EVENT_EXCHANGE_NAME.value,
                                                         exchange_type='topic',
                                                         durable=True)
            self.rabbitmq_channel_train.queue_declare(queue=EventBrokerNames.TRAIN_RESERVATION_EVENT_QUEUE_NAME.value,
                                                      durable=True)
            self.rabbitmq_channel_train.queue_bind(exchange=EventBrokerNames.TRAIN_RESERVATION_EVENT_EXCHANGE_NAME.value,
                                                   queue=EventBrokerNames.TRAIN_RESERVATION_EVENT_QUEUE_NAME.value,
                                                   routing_key=EventBrokerNames.TRAIN_RESERVATION_EVENT_ROUTING_KEY.value)

            logger.info("EventProcessor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize EventProcessor: {e}")

    def run(self):
        try:
            logger.info("EventProcessor starting to consume events")
            self.rabbitmq_channel_train.basic_consume(
                queue=EventBrokerNames.TRAIN_RESERVATION_EVENT_QUEUE_NAME.value,
                on_message_callback=self.process_event,
                auto_ack=False
            )
            self.rabbitmq_channel_train.start_consuming()
        except Exception as e:
            logger.error(f"Exception in EventProcessor: {e}")
        finally:
            if self.rabbitmq_channel_train:
                self.rabbitmq_channel_train.close()
            if self.rabbitmq_connection:
                self.rabbitmq_connection.close()
            logger.info("EventProcessor stopped")

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

            logger.info(f"Processing event: {event_type}")
            if event_type == EventType.TRAIN_RESERVED:
                self._handle_train_reserved(event_data)
            elif event_type == EventType.TRAIN_RESERVATION_UPDATED:
                logger.warning(f"I'm not handling this event: {event_type}")
            elif event_type == EventType.TRAIN_RESERVATION_CANCELLED:
                logger.warning(f"I'm not handling this event: {event_type}")
            elif event_type == EventType.TRAIN_RESERVATION_FAIL_STATUS_PROPAGATION:
                self._handle_train_reservation_fail_status_propagation(event_data)
            else:
                logger.warning(f"Unknown event type: {event_type}")

            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def _handle_train_reserved(self, event_data):
        from ..models import ReservationCommand
        try:
            command = ReservationCommand.data_to_obj(event_data)
            self.service.create_schedule(command)
            logger.info(f"Successfully added train reservation: {ReservationCommand.train_number}")
        except Exception as e:
            logger.error(f"Failed to add train reservation: {e}")
            raise

    def _handle_train_reservation_fail_status_propagation(self, event_data):
        from ..models import ReservationCommand
        try:
            command = ReservationCommand.data_to_obj(event_data)
            self.service.create_schedule(command)
            logger.info(f"Successfully added failed train reservation: {ReservationCommand.train_number}")
        except Exception as e:
            logger.error(f"Failed to add failed train reservation: {e}")
            raise
