# Action = who, what, where, when, why, how

# requirements = {
#     "move": ["entity", "direction", "speed"],
#     "attack": ["entity", "target", "damage"],
#     "spawn": ["entity", "location"],
#     "despawn": ["entity"]
# }

# required_events = {
#     'event_name': {
#         'status': '0'  # 0 = unresolved, -1 = failed, 1 = success
#         'data': None
#     }
# }
from GameData.EventHub import EventHub, Event


class Action:
    def __init__(self, name, required_events, event_hub: EventHub):
        self.name = name
        self.required_events = self.create_events(required_events)
        self.complete = False
        self.failed = False
        self.event_hub = event_hub

    def create_events(self, required_events):
        return [Event(event['event_name'], event['data'], self.callback) for event in required_events]

    def execute(self):
        if self.failed:
            return
        next_event = self.get_next_event()
        if next_event:
            self.trigger_event(next_event)
        else:
            self.complete = True

    def callback(self, event: Event):
        for required_event in self.required_events[:]:  # Iterate over a copy
            if required_event.name == event.name:
                if event.status == 1:  # Event successful
                    self.required_events.remove(required_event)
                elif event.status == -1:  # Event failed
                    self.failed = True
                break

    def get_next_event(self):
        return next((event for event in self.required_events if event.status == 0), None)

    def trigger_event(self, event: Event):
        self.event_hub.send_event(event)
