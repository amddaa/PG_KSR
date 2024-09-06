from enum import Enum


class TrainEventType(Enum):
    TRAIN_SCHEDULE_CREATED = "TrainScheduleCreated"
    TRAIN_SCHEDULE_UPDATED = "TrainScheduleUpdated"
    TRAIN_SCHEDULE_DELETED = "TrainScheduleDeleted"


class TrainEventStreamName(Enum):
    TRAIN_EVENT_STREAM_NAME = "train-schedule-stream"

    def __str__(self):
        return self.value
