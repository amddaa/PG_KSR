from enum import Enum


class EventType(Enum):
    TRAIN_RESERVED = "TrainReserved"
    TRAIN_RESERVATION_UPDATED = "TrainReservationUpdated"
    TRAIN_RESERVATION_CANCELLED = "TranReservationCancelled"
    TRAIN_RESERVATION_FAIL_STATUS_PROPAGATION = "TrainReservationFailStatusPropagation"

    def __str__(self):
        return self.value


class EventBrokerNames(Enum):
    TRAIN_RESERVATION_COMMAND_QUEUE_NAME = "train-reservation-command-queue"  # front api call handler
    TRAIN_RESERVATION_EVENT_STREAM_NAME = "train-reservation-stream"
    TRAIN_RESERVATION_EVENT_EXCHANGE_NAME = "train-reservation-exchange"
    TRAIN_RESERVATION_EVENT_QUEUE_NAME = "train-reservation-event-queue"  # event propagation
    TRAIN_RESERVATION_EVENT_ROUTING_KEY = "train-reservation-routing-key"

    def __str__(self):
        return self.value
