from enum import Enum


class TrainEventType(Enum):
    TRAIN_SCHEDULE_CREATED = "TrainScheduleCreated"
    TRAIN_SCHEDULE_UPDATED = "TrainScheduleUpdated"
    TRAIN_SCHEDULE_DELETED = "TrainScheduleDeleted"
