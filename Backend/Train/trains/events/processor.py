import pika
from esdbclient import EventStoreDBClient
from django.conf import settings
from rest_framework.utils import json


class EventProcessor:
    def __init__(self):
        esdb_uri = f"esdb://{settings.ESDB_HOST}:{settings.ESDB_PORT}?Tls=false"
        rabbitmq_uri = f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@{settings.RABBITMQ_HOST}:{settings.RABBITMQ_PORT}/"
        credentials = pika.PlainCredentials(settings.RABBITMQ_USER, settings.RABBITMQ_PASSWORD)
        parameters = pika.ConnectionParameters(settings.RABBITMQ_HOST,
                                               settings.RABBITMQ_PORT,
                                               '/',
                                               credentials)

        self.esdb_client = EventStoreDBClient(uri=esdb_uri)

        try:
            self.rabbitmq_connection = pika.BlockingConnection(parameters)
            self.rabbitmq_channel = self.rabbitmq_connection.channel()
            self.rabbitmq_channel.exchange_declare(exchange='events', exchange_type='fanout')
            print("Connected to RabbitMQ")
        except Exception as e:
            print(f"Failed to connect to RabbitMQ: {e}")
            self.rabbitmq_channel = None

    def start(self):
        result = self.rabbitmq_channel.queue_declare('', exclusive=True)
        queue_name = result.method.queue
        self.rabbitmq_channel.queue_bind(exchange='events', queue=queue_name)

        self.rabbitmq_channel.basic_consume(queue=queue_name, on_message_callback=self.process_event, auto_ack=True)
        self.rabbitmq_channel.start_consuming()

    def process_event(self, properties, body):
        from ..models import TrainSchedule

        event_data = json.loads(body)
        event_type = properties.headers['event_type']

        if event_type == 'TrainScheduleCreated':
            TrainSchedule.objects.create(
                train_number=event_data['train_number'],
                departure_time=event_data['departure_time'],
                arrival_time=event_data['arrival_time']
            )
        elif event_type == 'TrainScheduleUpdated':
            schedule = TrainSchedule.objects.get(pk=event_data['id'])
            schedule.train_number = event_data.get('train_number', schedule.train_number)
            schedule.departure_time = event_data.get('departure_time', schedule.departure_time)
            schedule.arrival_time = event_data.get('arrival_time', schedule.arrival_time)
            schedule.save()
        elif event_type == 'TrainScheduleDeleted':
            TrainSchedule.objects.filter(pk=event_data['id']).delete()

    def close(self):
        self.rabbitmq_connection.close()
