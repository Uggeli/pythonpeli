from dataclasses import dataclass
import logging
logger = logging.getLogger(__name__)


@dataclass
class Event:
    """
    An event is a message that is sent to the event hub.
    name = listener name
    data = [
        'listener function'
        'args'
    ]
    callback is a function that is called when the event is resolved.
    """
    def __init__(self, name, data, callback=None):
        self.name = name
        self.data = data
        self.status = 0
        self.callback = callback

    def update_status(self, new_status):
        self.status = new_status


class EventHub:
    def __init__(self):
        self.listeners = {}
        self.listeners_priority = {}

    def setup(self, config):
        print("Setting up event hub")

    def add_listener(self, event_name, listener):
        print(f"Adding listener {listener} to event {event_name}")
        if event_name not in self.listeners:
            self.listeners[event_name] = []
        self.listeners[event_name].append(listener)

    def add_listener_priority(self, event_name, listener):
        print(f"Adding listener {listener} to event {event_name} with priority")
        if event_name not in self.listeners_priority:
            self.listeners_priority[event_name] = []
        self.listeners_priority[event_name].append(listener)

    def send_event(self, event: Event):
        """sends message to manager queue"""
        print(f"Sending event {event.name} with data {event.data}")
        if event.name in self.listeners:
            for listener in self.listeners[event.name]:
                listener(event)

    def remove_listener(self, event_name, listener):
        print(f"Removing listener {listener} from event {event_name}")
        if event_name in self.listeners:
            self.listeners[event_name].remove(listener)

    def direct_event(self, event_name, data):
        """Directly calls event without adding to queue"""
        print(f"Direct event {event_name} with data {data}")
        collected_data = []
        if event_name in self.listeners_priority:
            for listener in self.listeners_priority[event_name]:
                print(f"Calling listener {listener} with data {data}")
                collected_data.append(listener(data))
        return collected_data
