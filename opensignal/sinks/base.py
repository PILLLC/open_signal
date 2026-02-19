class EventSink:
    """
    Sink abstraction for persisting processed events.
    """
    def write(self, events: list[dict]):
        raise NotImplementedError
