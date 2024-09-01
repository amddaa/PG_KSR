import pika
import json
from django.db import transaction
from train.trains.models import TrainSchedule


def update_read_model(properties, body):
    event_data = json.loads(body)
    event_type = properties.headers['event_type']

    with transaction.atomic():
        if event_type == 'TrainScheduleCreated':
            TrainSchedule.objects.create(**event_data)
        elif event_type == 'TrainScheduleUpdated':
            schedule = TrainSchedule.objects.get(train_number=event_data['train_number'])
            for key, value in event_data.items():
                setattr(schedule, key, value)
            schedule.save()
        elif event_type == 'TrainScheduleDeleted':
            TrainSchedule.objects.filter(train_number=event_data['train_number']).delete()


def start_synchronization():
    connection = pika.BlockingConnection(pika.URLParameters('amqp://user:password@rabbitmq_host:5672/'))
    channel = connection.channel()
    channel.exchange_declare(exchange='events', exchange_type='fanout')

    result = channel.queue_declare('', exclusive=True)
    queue_name = result.method.queue
    channel.queue_bind(exchange='events', queue=queue_name)

    channel.basic_consume(queue=queue_name, on_message_callback=update_read_model, auto_ack=True)
    channel.start_consuming()
