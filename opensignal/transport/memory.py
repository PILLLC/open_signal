from .base import EventTransport

class MemoryTransport(EventTransport):
    """
    In-memory transport used for the runnable demo.

    This is intentionally simple and single-process.
    """
    def __init__(self):
        self.streams = {}

    def publish(self, stream: str, event: dict):
        self.streams.setdefault(stream, []).append(event)

    def subscribe(self, stream: str, handler):
        for event in self.streams.get(stream, []):
            handler(event)
