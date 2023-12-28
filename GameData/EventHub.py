from dataclasses import dataclass
import logging
logger = logging.getLogger(__name__)


@dataclass
class Event:
    def __init__(self, name, data):
        self.name = name
        self.data = data


class EventHub:
    def __init__(self):
        self.listeners = {}

    def add_listener(self, event_name, listener):
        logger.info(f"Adding listener {listener} to event {event_name}")
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(listener)

    def send_event(self, event):
        logger.info(f"Sending event {event.name} with data {event.data}")
        if event.name in self.listeners:
            for listener in self.listeners[event.name]:
                listener(event)

    def remove_listener(self, event_name, listener):
        logger.info(f"Removing listener {listener} from event {event_name}")
        if event_name in self.listeners:
            self.listeners[event_name].remove(listener)
