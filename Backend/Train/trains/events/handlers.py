import pika
from django.conf import settings
from rest_framework.utils import json


class TrainEventHandler:
    def __init__(self):
        rabbitmq_uri = f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/"
        self.rabbitmq_connection = pika.BlockingConnection(pika.URLParameters(rabbitmq_uri))
        self.rabbitmq_channel = self.rabbitmq_connection.channel()
        self.rabbitmq_channel.exchange_declare(exchange='events', exchange_type='fanout')

    def publish_event(self, event_type, event_data, stream_name):
        message = {
            'event_type': event_type,
            'stream_name': stream_name,
            'data': event_data,
        }
        self.rabbitmq_channel.basic_publish(
            exchange='events',
            routing_key='',
            body=json.dumps(message)
        )

    def close(self):
        if self.rabbitmq_connection:
            self.rabbitmq_connection.close()
