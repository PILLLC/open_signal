import json
from .base import EventSink

class NDJSONSink(EventSink):
    """
    Writes events to newline-delimited JSON (NDJSON).
    """
    def __init__(self, path: str):
        self.path = path

    def write(self, events: list[dict]):
        with open(self.path, "w", encoding="utf-8") as f:
            for e in events:
                f.write(json.dumps(e, ensure_ascii=False) + "\n")
