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
        rider_arrival_time = self.current_time + Distributions.generate_rider_interarival()
        rider_patience_time = rider_arrival_time + Distributions.generate_rider_patience()
        first_rider = Riders(arrival_time=rider_arrival_time,
                             origin=Distributions.generate_location(), 
                             destination=Distributions.generate_location(), 
                             patience_time=rider_patience_time)

        # create 1st driver
        driver_arrival_time = self.current_time + Distributions.generate_driver_interarival()
        driver_shift_time   = driver_arrival_time + Distributions.generate_driver_shift_time()
        first_driver = Drivers(driver_id=self._counter,
                               arrival_time=driver_arrival_time,
                               shift_end_time=driver_shift_time,
                               location=Distributions.generate_location())
        
        # add to event calendar:
        # first rider arrival
        self.event_calendar.add_event(first_rider.arrival_time, event_type=EventType.RIDER_ARRIVAL, data=first_rider)
        # add abandon times as well
        self.event_calendar.add_event(first_rider.patience_time, event_type=EventType.RIDER_ABANDONS, data=first_rider)
        
        # first driver arrival
        self.event_calendar.add_event(first_driver.arrival_time, event_type=EventType.DRIVER_ARRIVAL, data=first_driver)
        # add driver shift end time
        self.event_calendar.add_event(first_driver.shift_end_time, event_type=EventType.DRIVER_SHIFT_ENDS, data=first_driver)

    


    def run(self) -> None:
        pass