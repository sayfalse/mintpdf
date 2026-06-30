from typing import Any, Callable, Dict, List, Optional


class EventDispatcher:
    """Lightweight publisher-subscriber event dispatcher for lifecycle hooks."""

    _instance: Optional["EventDispatcher"] = None
    _listeners: Dict[str, List[Callable[..., Any]]] = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._listeners = {}
        return cls._instance

    def subscribe(self, event_name: str, listener: Callable[..., Any]) -> None:
        """Subscribe a callback to an event."""
        if event_name not in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(listener)

    def publish(self, event_name: str, *args: Any, **kwargs: Any) -> None:
        """Publish an event to all subscribers."""
        if event_name in self._listeners:
            for listener in self._listeners[event_name]:
                try:
                    listener(*args, **kwargs)
                except Exception:
                    # Protect event chain from listener failure
                    pass
