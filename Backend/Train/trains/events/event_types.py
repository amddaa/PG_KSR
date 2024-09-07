from enum import Enum


class TrainEventType(Enum):
    TRAIN_SCHEDULE_CREATED = "TrainScheduleCreated"
    TRAIN_SCHEDULE_UPDATED = "TrainScheduleUpdated"
    TRAIN_SCHEDULE_DELETED = "TrainScheduleDeleted"

    def __str__(self):
        return self.value


class TrainEventBrokerNames(Enum):
    TRAIN_EVENT_ROUTING_KEY = "train-event_routing_key"
    TRAIN_EVENT_QUEUE_NAME = "train_event_queue"
    TRAIN_EVENT_EXCHANGE_NAME = "train_event_exchange"
    TRAIN_EVENT_STREAM_NAME = "train-schedule-stream"

    def __str__(self):
        return self.value
