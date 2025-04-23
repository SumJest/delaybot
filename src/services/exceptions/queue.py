class QueueError(Exception):
    pass


class QueueClosedError(QueueError):
    pass


class NotInQueueError(QueueError):
    pass


class AlreadyInQueueError(QueueError):
    pass
