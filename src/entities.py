# import random
from typing import Tuple, List, Optional, TypeVar, Generic
from uuid import uuid4

class Riders:
    def __init__(self, origin: Tuple = (), destination: Tuple = (), patience_time: float = 0) -> None:
        self.rider_id      = uuid4()                      # Random UUID to rider
        self.origin        = origin                       # random origin (X0, Y0)
        self.destination   = destination                  # random desitnation (X1, Y1)
        self.patience_time = patience_time                # random patience times


class Drivers:
    def __init__(self, driver_id: int = 0, location: Tuple = ()) -> None:
        self.driver_id = driver_id
        self.location: Tuple  = location
        self.earnings  = 0
        self.distance_travelled = 0
        self.busy_time = 0
        self.num_trips = 0
    
    def update_location(self, new_location: Tuple = ()) -> None:
        self.location = new_location

    def update_busy_time(self, busy_time: float) -> None:
        self.busy_time = busy_time


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