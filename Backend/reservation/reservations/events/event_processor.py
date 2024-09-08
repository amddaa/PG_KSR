from datetime import datetime

import pika
import threading
import logging
from django.conf import settings
from esdbclient import StreamState
from rest_framework.utils import json

from .event_types import TrainEventType, TrainEventBrokerNames
from ..service.train_service import TrainQueryService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventProcessor(threading.Thread):
    def __init__(self, service: TrainQueryService):
        super().__init__(daemon=True)
        self.service = service
        self.rabbitmq_connection = None
        self.rabbitmq_channel_train = None
        try:
            rabbitmq_uri = f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/"
            self.rabbitmq_connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_uri))
            self.rabbitmq_channel_train = self.rabbitmq_connection.channel()
            self.rabbitmq_channel_train.exchange_declare(exchange=TrainEventBrokerNames.TRAIN_EVENT_EXCHANGE_NAME.value,
                                                         exchange_type='topic',
                                                         durable=True)
            self.rabbitmq_channel_train.queue_declare(queue=TrainEventBrokerNames.TRAIN_EVENT_QUEUE_NAME.value,
                                                      durable=True)
            self.rabbitmq_channel_train.queue_bind(exchange=TrainEventBrokerNames.TRAIN_EVENT_EXCHANGE_NAME.value,
                                                   queue=TrainEventBrokerNames.TRAIN_EVENT_QUEUE_NAME.value,
                                                   routing_key=TrainEventBrokerNames.TRAIN_EVENT_ROUTING_KEY.value)

            logger.info("EventProcessor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize EventProcessor: {e}")

    def run(self):
        try:
            logger.info("EventProcessor starting to consume events")
            self.rabbitmq_channel_train.basic_consume(
                queue=TrainEventBrokerNames.TRAIN_EVENT_QUEUE_NAME.value,
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
                event_type = TrainEventType(event_type_str)
            except ValueError:
                logger.warning(f"Unknown event type: {event_type_str}")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                return

            logger.info(f"Processing event: {event_type}")
            if event_type == TrainEventType.TRAIN_SCHEDULE_CREATED:
                self._handle_train_schedule_created(event_data)
            elif event_type == TrainEventType.TRAIN_SCHEDULE_UPDATED:
                logger.warning(f"I'm not handling this event: {event_type}")
            elif event_type == TrainEventType.TRAIN_SCHEDULE_DELETED:
                logger.warning(f"I'm not handling this event: {event_type}")
            else:
                logger.warning(f"Unknown event type: {event_type}")

            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def _handle_train_schedule_created(self, event_data):
        try:
            expected_version = int(event_data.get('expected_version')) if event_data.get('expected_version') != str(
                StreamState.NO_STREAM) else StreamState.NO_STREAM

            self.service.create_schedule(
                train_number=event_data.get('train_number'),
                departure_time=datetime.fromisoformat(event_data.get('departure_time')),
                arrival_time=datetime.fromisoformat(event_data.get('arrival_time')),
                max_seats=int(event_data.get('max_seats')),
                expected_version=expected_version,
            )

            logger.info(f"Successfully created train schedule: {event_data.get('train_number')}")
        except Exception as e:
            logger.error(f"Failed to create train schedule: {e}")
            raise
