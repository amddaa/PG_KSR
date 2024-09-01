import pika
from esdbclient import EventStoreDBClient, NewEvent, StreamState
from django.conf import settings
from rest_framework.utils import json

from train.train.settings import ESDB_HOST, ESDB_PORT


class TrainEventHandler:
    def __init__(self):
        self.rabbitmq_uri = f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/"
        self.client = EventStoreDBClient(uri=f"esdb://{ESDB_HOST}:{ESDB_PORT}?Tls=false")

    def publish_event(self, event_type, data, stream_name):
        event = NewEvent(type=event_type, data=data)
        self.client.append_to_stream(stream_name=stream_name, events=[event], current_version=StreamState.ANY)

        connection = pika.BlockingConnection(pika.URLParameters(self.rabbitmq_uri))
        channel = connection.channel()
        channel.exchange_declare(exchange='events', exchange_type='fanout')

        channel.basic_publish(
            exchange='events',
            routing_key='',
            body=json.dumps(data),
            properties=pika.BasicProperties(headers={'event_type': event_type})
        )

    def close(self):
        self.client.close()
