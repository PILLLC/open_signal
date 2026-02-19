class EventTransport:
    """
    Transport abstraction for moving events between components.

    Implementations should provide at-least-once semantics where applicable,
    and should not mutate event structure.
    """
    def publish(self, stream: str, event: dict):
        raise NotImplementedError

    def subscribe(self, stream: str, handler):
        raise NotImplementedError
