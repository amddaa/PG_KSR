import pika
import uuid
from django.conf import settings
from rest_framework.utils import json
from datetime import datetime


class TrainEventHandler:
    def __init__(self):
        rabbitmq_uri = f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/"
        self.rabbitmq_connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_uri))
        self.rabbitmq_channel = self.rabbitmq_connection.channel()
        self.rabbitmq_channel.exchange_declare(exchange='events', exchange_type='topic')

    def publish_event(self, stream_name, event_type, event_data):
        event_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()

        message = {
            'event_id': event_id,
            'event_type': event_type,
            'stream_name': stream_name,
            'data': event_data,
            'timestamp': timestamp,
        }

        routing_key = f"{event_type}.{stream_name}"

        self.rabbitmq_channel.basic_publish(
            exchange='events',
            routing_key=routing_key,
            body=json.dumps(message)
        )

    def close(self):
        if self.rabbitmq_connection:
            self.rabbitmq_connection.close()
