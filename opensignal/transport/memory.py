# opensignal/transport/memory.py

from __future__ import annotations

from collections import defaultdict
from typing import Callable, Dict, List, Any


class MemoryTransport:
    """
    In-memory pub/sub transport for demos and tests.

    - subscribe(stream, handler): register a callable(handler) for a stream name
    - publish(stream, event): invoke handlers in subscription order
    """

    def __init__(self):
        self._subs: Dict[str, List[Callable[[dict], None]]] = defaultdict(list)

    def subscribe(self, stream_name: str, handler: Callable[[dict], None]) -> None:
        if not stream_name or not isinstance(stream_name, str):
            raise ValueError("stream_name must be a non-empty string")
        if not callable(handler):
            raise ValueError("handler must be callable")

        self._subs[stream_name].append(handler)

    def publish(self, stream_name: str, event: dict) -> None:
        if not stream_name or not isinstance(stream_name, str):
            raise ValueError("stream_name must be a non-empty string")
        if not isinstance(event, dict):
            raise ValueError("event must be a dict")

        handlers = self._subs.get(stream_name, [])
        # If nobody subscribed, do nothing (streaming systems often behave this way)
        for h in handlers:
            h(event)

    def subscriptions(self) -> Dict[str, int]:
        """Tiny helper for debugging."""
        return {k: len(v) for k, v in self._subs.items()}