from entities import EventCalendar, Riders, Drivers, Queue, EventType
from distributions import Distributions

print("We're in simulation.py")

class Simulation:
    def __init__(self) -> None:
        self.simulation_length = 1000
        self.current_time = 0
        self._counter = 0
        
        self.event_calendar  = EventCalendar()
        self.rider_queue     = Queue[Riders]()
        self.driver_queue    = Queue[Drivers]()

        # add termination to event calendar
        self.event_calendar.add_event(self.simulation_length, event_type=EventType.TERMINATION)

        # create 1st rider
        first_rider = Riders(arrival_time=Distributions.generate_rider_interarival(),
                             origin=Distributions.generate_location(), 
                             destination=Distributions.generate_location(), 
                             patience_time=Distributions.generate_rider_patience())

        # create 1st driver
        first_driver = Drivers(driver_id=self._counter,
                               location=Distributions.generate_location())
        
        self.event_calendar.add_event()