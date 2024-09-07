from datetime import datetime

import pika
import threading
import logging
from django.conf import settings
from rest_framework.utils import json

from .event_types import TrainEventType, TrainEventBrokerNames
from ..service.query_service import TrainQueryService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EventProcessor(threading.Thread):
    def __init__(self, service: TrainQueryService):
        super().__init__(daemon=True)
        self.service = service
        self.rabbitmq_connection = None
        self.rabbitmq_channel = None
        try:
            rabbitmq_uri = f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/"
            self.rabbitmq_connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_uri))
            self.rabbitmq_channel = self.rabbitmq_connection.channel()
            self.rabbitmq_channel.exchange_declare(exchange=TrainEventBrokerNames.TRAIN_EVENT_EXCHANGE_NAME.value,
                                                   exchange_type='direct',
                                                   durable=True)
            self.rabbitmq_channel.queue_declare(queue=TrainEventBrokerNames.TRAIN_EVENT_QUEUE_NAME.value,
                                                durable=True)
            self.rabbitmq_channel.queue_bind(exchange=TrainEventBrokerNames.TRAIN_EVENT_EXCHANGE_NAME.value,
                                             queue=TrainEventBrokerNames.TRAIN_EVENT_QUEUE_NAME.value,
                                             routing_key=TrainEventBrokerNames.TRAIN_EVENT_ROUTING_KEY.value)

            logger.info("EventProcessor initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize EventProcessor: {e}")

    def run(self):
        try:
            logger.info("EventProcessor starting to consume events")
            self.rabbitmq_channel.basic_consume(
                queue=TrainEventBrokerNames.TRAIN_EVENT_QUEUE_NAME.value,
                on_message_callback=self.process_event,
                auto_ack=False
            )
            self.rabbitmq_channel.start_consuming()
        except Exception as e:
            logger.error(f"Exception in EventProcessor: {e}")
        finally:
            if self.rabbitmq_channel:
                self.rabbitmq_channel.close()
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
                self._handle_train_schedule_updated(event_data)
            elif event_type == TrainEventType.TRAIN_SCHEDULE_DELETED:
                self._handle_train_schedule_deleted(event_data)
            else:
                logger.warning(f"Unknown event type: {event_type}")

            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error processing event: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def _handle_train_schedule_created(self, event_data):
        self.service.create_schedule(
            train_number=event_data.get('train_number'),
            departure_time=datetime.fromisoformat(event_data.get('departure_time')),
            arrival_time=datetime.fromisoformat(event_data.get('arrival_time'))
        )

    def _handle_train_schedule_updated(self, event_data):
        self.service.update_schedule(
            train_number=event_data.get('train_number'),
            old_departure_time=datetime.fromisoformat(event_data.get('old_departure_time')),
            old_arrival_time=datetime.fromisoformat(event_data.get('old_arrival_time')),
            new_departure_time=datetime.fromisoformat(event_data.get('departure_time')),
            new_arrival_time=datetime.fromisoformat(event_data.get('arrival_time'))
        )

    def _handle_train_schedule_deleted(self, event_data):
        self.service.delete_schedule(
            train_number=event_data.get('train_number'),
            departure_time=datetime.fromisoformat(event_data.get('departure_time')),
            arrival_time=datetime.fromisoformat(event_data.get('arrival_time'))
        )
