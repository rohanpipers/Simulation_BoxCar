# import random
from typing import Tuple, List, Optional, TypeVar, Generic, Any
from uuid import uuid4
import heapq
from enum import Enum, auto
from dataclasses import dataclass, field

class Riders:
    def __init__(
            self, 
            origin: Tuple[float, float] = (0.0, 0.0), 
            destination: Tuple[float, float] = (0.0, 0.0), 
            patience_time: float = 0 ) -> None:
        self.rider_id      = uuid4()                      # Random UUID to rider
        self.origin        = origin                       # random origin (X0, Y0)
        self.destination   = destination                  # random desitnation (X1, Y1)
        self.patience_time = patience_time                # random patience times


class Drivers:
    def __init__(self, driver_id: int = 0, location: Tuple[float, float] = (0.0, 0.0)) -> None:
        self.driver_id = driver_id
        self.location: Tuple[float, float]  = location
        self.earnings  = 0
        self.distance_travelled = 0
        self.busy_time = 0
        self.num_trips = 0
    
    def update_location(self, new_location: Tuple[float, float]) -> None:
        self.location = new_location

    def update_busy_time(self, busy_time: float) -> None:
        self.busy_time += busy_time


T = TypeVar('T')
class Queue(Generic[T]):
    def __init__(self) -> None:
        self.items: List[T] = []

    def enqueue(self, item: T) -> None:
        """Adds an item to the back of the queue."""
        self.items.append(item)

    def dequeue(self) -> Optional[T]:
        """Removes and returns the item at the front of the queue."""
        if not self.is_empty():
            return self.items.pop(0)
        return None

    def is_empty(self) -> bool:
        """Returns True if the queue is empty."""
        return len(self.items) == 0

    def size(self) -> int:
        """Returns the current number of items in the queue."""
        return len(self.items)

    def peek(self) -> Optional[T]:
        """Looks at the first item in the queue without removing it."""
        if not self.is_empty():
            return self.items[0]
        return None


# 1. Define the specific events you requested
class EventType(Enum):
    TERMINATION = auto()
    TRIP = auto()
    RIDER_ARRIVAL = auto()
    DRIVER_ARRIVAL = auto()
    RIDER_ABANDONS = auto()
    DRIVER_SHIFT_ENDS = auto()

# 2. Define the Event object
@dataclass(order=True)
class Event:
    time: float
    # We use compare=False so the heap only sorts by the 'time' attribute.
    # The 'event_id' is used as a tie-breaker if two events happen at the exact same time.
    event_id: int 
    event_type: EventType = field(compare=False)
    data: Any = field(default=None, compare=False)

# 3. Define the Event Calendar
class EventCalendar:
    def __init__(self) -> None:
        self._events = []
        self._counter = 0  # Used to generate unique event_ids for tie-breaking

    def schedule(self, time: float, event_type: EventType, data: Any = None) -> None:
        """Schedules a new event on the calendar."""
        self._counter += 1
        new_event = Event(time=time, event_id=self._counter, event_type=event_type, data=data)
        heapq.heappush(self._events, new_event)

    def next_event(self) -> Optional[Event]:
        """Pops and returns the chronologically next event to process."""
        if not self.is_empty():
            return heapq.heappop(self._events)
        return None

    def is_empty(self) -> bool:
        """Returns True if there are no pending events."""
        return len(self._events) == 0

    def size(self) -> int:
        """Returns the number of scheduled events."""
        return len(self._events)