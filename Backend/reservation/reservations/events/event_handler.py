import pika
import uuid
from django.conf import settings
from rest_framework.utils import json
from datetime import datetime

from .event_types import EventBrokerNames


class EventHandler:
    def __init__(self):
        rabbitmq_uri = f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/"
        self.rabbitmq_connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_uri))
        self.rabbitmq_channel = self.rabbitmq_connection.channel()
        self.rabbitmq_channel.exchange_declare(exchange=EventBrokerNames.TRAIN_RESERVATION_EVENT_EXCHANGE_NAME.value,
                                               exchange_type='topic',
                                               durable=True)
        self.rabbitmq_channel.queue_declare(queue=EventBrokerNames.TRAIN_RESERVATION_EVENT_QUEUE_NAME.value,
                                            durable=True)
        self.rabbitmq_channel.queue_bind(queue=EventBrokerNames.TRAIN_RESERVATION_EVENT_QUEUE_NAME.value,
                                         exchange=EventBrokerNames.TRAIN_RESERVATION_EVENT_EXCHANGE_NAME.value,
                                         routing_key=EventBrokerNames.TRAIN_RESERVATION_EVENT_ROUTING_KEY.value)

    def publish_event(self, event_type, event_data):
        event_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        message = {
            'event_id': event_id,
            'event_type': event_type,
            'data': event_data,
            'timestamp': timestamp,
        }

        self.rabbitmq_channel.basic_publish(
            exchange=EventBrokerNames.TRAIN_RESERVATION_EVENT_EXCHANGE_NAME.value,
            routing_key=EventBrokerNames.TRAIN_RESERVATION_EVENT_ROUTING_KEY.value,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )

    def close(self):
        if self.rabbitmq_connection:
            self.rabbitmq_connection.close()
