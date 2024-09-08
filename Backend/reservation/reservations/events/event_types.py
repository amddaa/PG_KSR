from enum import Enum


class TrainEventType(Enum):
    TRAIN_SCHEDULE_CREATED = "TrainScheduleCreated"
    TRAIN_SCHEDULE_UPDATED = "TrainScheduleUpdated"
    TRAIN_SCHEDULE_DELETED = "TrainScheduleDeleted"

    def __str__(self):
        return self.value


class TrainEventBrokerNames(Enum):
    TRAIN_EVENT_ROUTING_KEY = "train-event-routing-key"
    TRAIN_EVENT_QUEUE_NAME = "train-event-reservation-queue"
    TRAIN_EVENT_EXCHANGE_NAME = "train-event-exchange"

    def __str__(self):
        return self.value
