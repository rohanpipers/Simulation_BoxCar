from entities import EventCalendar, Rider, Driver, Trip, Queue, EventType
from typing import Tuple
from distributions import Distributions
import math

print("We're in simulation.py")

class Simulation:
    def __init__(self) -> None:
        self.simulation_length = 100
        self.current_time = 0
        self._counter = 1
        self.avg_speed = 20 # avg speed of cab
        
        self.event_calendar  = EventCalendar()
        self.rider_queue     = Queue[Rider]()
        self.driver_queue    = Queue[Driver]()

        self.total_rider_requests = 0
        self.total_completed_rides = 0
        self.total_abandonments = 0

        self.total_pickup_wait_time = 0.0
        self.total_system_time = 0.0

        self.all_drivers = {}

        # add termination to event calendar
        self.event_calendar.add_event(self.simulation_length, event_type=EventType.TERMINATION)

        # create 1st rider
        rider_arrival_time = self.current_time + Distributions.generate_rider_interarival()
        rider_patience_time = rider_arrival_time + Distributions.generate_rider_patience()
        first_rider = Rider(arrival_time=rider_arrival_time,
                             origin=Distributions.generate_location(), 
                             destination=Distributions.generate_location(), 
                             patience_time=rider_patience_time)

        # create 1st driver
        driver_arrival_time = self.current_time + Distributions.generate_driver_interarival()
        driver_shift_time   = driver_arrival_time + Distributions.generate_driver_shift_time()
        first_driver = Driver(driver_id=self._counter,
                               arrival_time=driver_arrival_time,
                               shift_end_time=driver_shift_time,
                               location=Distributions.generate_location())
        
        self.all_drivers[first_driver.driver_id] = first_driver

        # add to event calendar:
        # first rider arrival
        self.event_calendar.add_event(first_rider.arrival_time, event_type=EventType.RIDER_ARRIVAL, data=first_rider)
        # add abandon times as well
        self.event_calendar.add_event(first_rider.patience_time, event_type=EventType.RIDER_ABANDONS, data=first_rider)
        
        # first driver arrival
        self.event_calendar.add_event(first_driver.arrival_time, event_type=EventType.DRIVER_ARRIVAL, data=first_driver)
        # add driver shift end time
        self.event_calendar.add_event(first_driver.shift_end_time, event_type=EventType.DRIVER_SHIFT_ENDS, data=first_driver)

        self._counter += 1
    
    # def matching_algo(self):
    # while rider queue or driver queue is empty
    # keep running matching pattern algo
    # if matched, create Trip instance with rider_id, driver_id, trip_start_time, trip_end_time

    @staticmethod
    def calculate_distance(loc1: Tuple[float, float], loc2: Tuple[float, float]):
        distance = math.sqrt((loc1[0] - loc2[0])**2 + (loc1[1] - loc2[1])**2)
        return distance


    def matching_algo(self, current_time: float):
        # current_rider = Rider()
        if self.driver_queue.is_empty() or self.rider_queue.is_empty():
            return
        current_rider = self.rider_queue.dequeue()
        matched_driver = None
        min_distance_to_driver = float('inf')
            
        for current_driver in self.driver_queue.items.values():
            distance_to_driver = self.calculate_distance(loc1=current_driver.location, loc2=current_rider.origin)
            if distance_to_driver < min_distance_to_driver:
                min_distance_to_driver = distance_to_driver
                matched_driver = current_driver
            
        if matched_driver is None:
            # Safety: if something went wrong, put the rider back and stop
            self.rider_queue.enqueue(current_rider.rider_id, current_rider)
            return

        # Matched driver!
        print(f"Rider {current_rider.rider_id} matched with Driver {matched_driver.driver_id}")

        # Calculate Trip end times, update distance to be travelled by driver, 
        pickup_distance = min_distance_to_driver
        trip_distance = self.calculate_distance(
            loc1=current_rider.origin,
            loc2=current_rider.destination
        )

        expected_time_driver_to_rider = pickup_distance / self.avg_speed
        estimated_time_driver_to_rider = Distributions.estimated_trip_time(
            expected_trip_time=expected_time_driver_to_rider
        )

        pickup_time = current_time + estimated_time_driver_to_rider

        new_trip = Trip(
            driver=matched_driver,
            rider=current_rider,
            trip_start_time=current_time,
            pickup_time=pickup_time,
            pickup_distance=pickup_distance,
            trip_distance=trip_distance
        )

        self.event_calendar.add_event(
            time=pickup_time,
            event_type=EventType.DRIVER_REACHES_PICKUP,
            data=new_trip
        )

        self.driver_queue.remove_by_id(item_id=matched_driver.driver_id)

    def print_kpis(self) -> None:
    total = self.total_rider_requests
    completed = self.total_completed_rides
    abandoned = self.total_abandonments

    abandonment_rate = abandoned / total if total > 0 else 0.0
    avg_pickup_wait = self.total_pickup_wait_time / completed if completed > 0 else 0.0
    avg_system_time = self.total_system_time / completed if completed > 0 else 0.0

    earnings_per_hour = []
    idle_proportions = []

    for driver in self.all_drivers.values():
        offline_time = driver.actual_offline_time if driver.actual_offline_time is not None else self.current_time
        online_time = max(0.0, offline_time - driver.arrival_time)

        if online_time > 0:
            earnings_per_hour.append(driver.earnings / online_time)
            idle_proportions.append(max(0.0, online_time - driver.busy_time) / online_time)

    avg_driver_earnings_per_hour = (
        sum(earnings_per_hour) / len(earnings_per_hour)
        if earnings_per_hour else 0.0
    )

    avg_idle_proportion = (
        sum(idle_proportions) / len(idle_proportions)
        if idle_proportions else 0.0
    )

    if earnings_per_hour:
        mean_eph = avg_driver_earnings_per_hour
        std_eph = (sum((x - mean_eph) ** 2 for x in earnings_per_hour) / len(earnings_per_hour)) ** 0.5
        fairness_cv = std_eph / mean_eph if mean_eph > 0 else 0.0
    else:
        fairness_cv = 0.0

    print("===== KPI SUMMARY =====")
    print(f"Total rider requests: {total}")
    print(f"Completed rides: {completed}")
    print(f"Abandonments: {abandoned}")
    print(f"Abandonment rate: {abandonment_rate:.4f}")
    print(f"Average pickup wait (hours): {avg_pickup_wait:.4f}")
    print(f"Average rider system time (hours): {avg_system_time:.4f}")
    print(f"Average driver earnings per hour: {avg_driver_earnings_per_hour:.4f}")
    print(f"Fairness (CV of earnings/hour): {fairness_cv:.4f}")
    print(f"Average driver idle proportion: {avg_idle_proportion:.4f}")

    def run(self) -> None:
        # print(self.event_calendar.size())

        # print(self.rider_queue.items)
        # print(self.driver_queue.items)

        while  not self.event_calendar.is_empty():
            next_event = self.event_calendar.next_event()

            self.current_time = next_event.time
            if next_event.event_type == EventType.RIDER_ARRIVAL:
                # Start matching algo
                # matching algo until rider queue or driver queue is empty
                print(f"Rider arrival: {next_event.data.rider_id}")
                self.total_rider_requests += 1
                # add to rider queue
                self.rider_queue.enqueue(next_event.data.rider_id, next_event.data)
                print("start matching algo...")
                self.matching_algo(current_time=next_event.time)
                print("moving to next event.....")
                print("-----------------------------------")

                # Add new rider arrival
                # Add new driver arrival
                rider_arrival_time = self.current_time + Distributions.generate_rider_interarival()
                rider_patience_time = rider_arrival_time + Distributions.generate_rider_patience()
                new_rider = Rider(arrival_time=rider_arrival_time,
                                origin=Distributions.generate_location(), 
                                destination=Distributions.generate_location(), 
                                patience_time=rider_patience_time)
                
                # add to event calendar:
                # first rider arrival
                self.event_calendar.add_event(new_rider.arrival_time, event_type=EventType.RIDER_ARRIVAL, data=new_rider)
                # add abandon times as well
                self.event_calendar.add_event(new_rider.patience_time, event_type=EventType.RIDER_ABANDONS, data=new_rider)

            elif next_event.event_type == EventType.DRIVER_ARRIVAL:
                print(f"driver arrival: {next_event.data.driver_id}")
                # add driver to driver queue
                self.driver_queue.enqueue(next_event.data.driver_id, next_event.data)
                print("starting matching algo...")
                self.matching_algo(current_time=next_event.time)
                print("moving to next event..")
                print("-----------------------------------")
                # create 1st driver
                driver_arrival_time = self.current_time + Distributions.generate_driver_interarival()
                driver_shift_time   = driver_arrival_time + Distributions.generate_driver_shift_time()
                new_driver = Driver(driver_id=self._counter,
                                    arrival_time=driver_arrival_time,
                                    shift_end_time=driver_shift_time,
                                    location=Distributions.generate_location())
                self.all_drivers[new_driver.driver_id] = new_driver
                self._counter += 1 # to assign id to next driver

                # first driver arrival
                self.event_calendar.add_event(new_driver.arrival_time, event_type=EventType.DRIVER_ARRIVAL, data=new_driver)
                # add driver shift end time
                self.event_calendar.add_event(new_driver.shift_end_time, event_type=EventType.DRIVER_SHIFT_ENDS, data=new_driver)

            elif next_event.event_type == EventType.DRIVER_REACHES_PICKUP:
                print("Driver reaches pickup..")
                trip_data = next_event.data
                driver = trip_data.driver
                rider = trip_data.rider

                # driver has now actually reached the rider
                driver.update_location(new_location=rider.origin)

                self.total_pickup_wait_time += (self.current_time - rider.arrival_time)

                # compute rider leg travel time
                expected_time_trip = trip_data.trip_distance / self.avg_speed
                estimated_time_trip = Distributions.estimated_trip_time(
                    expected_trip_time=expected_time_trip
                )

                dropoff_time = self.current_time + estimated_time_trip

                # store total busy time now that both legs are known
                total_trip_time = (trip_data.pickup_time - trip_data.trip_start_time) + estimated_time_trip
                driver.update_busy_time(busy_time=total_trip_time)

                self.event_calendar.add_event(
                    time=dropoff_time,
                    event_type=EventType.DRIVER_REACHES_DROPOFF,
                    data=trip_data
                )

                print("-----------------------------------")

            elif next_event.event_type == EventType.DRIVER_REACHES_DROPOFF:
                print("Driver reaches dropoff..")
                trip_data = next_event.data
                driver = trip_data.driver
                rider = trip_data.rider

                # driver has now actually arrived at destination
                driver.update_location(new_location=rider.destination)

                self.total_completed_rides += 1
                self.total_system_time += (self.current_time - rider.arrival_time)

                # update driver trip stats
                driver.distance_travelled += (trip_data.pickup_distance + trip_data.trip_distance)
                driver.num_trips += 1

                # earnings/costs
                fare = 3 + 2 * trip_data.trip_distance
                petrol_cost = 0.20 * (trip_data.pickup_distance + trip_data.trip_distance)
                driver.earnings += (fare - petrol_cost)

                # decide what happens to driver next
                if driver.offline_pending or self.current_time >= driver.shift_end_time:
                    driver.actual_offline_time = self.current_time
                    print(f"Driver {driver.driver_id} goes offline after trip")
                else:
                    self.driver_queue.enqueue(driver.driver_id, driver)
                    self.matching_algo(current_time=self.current_time)

                print("-----------------------------------")
            
            elif next_event.event_type == EventType.RIDER_ABANDONS:
                # remove rider from queue if available
                remove = self.rider_queue.remove_by_id(next_event.data.rider_id)
                if remove:
                    self.total_abandonments += 1
                    print(f"Rider abandoned: {next_event.data.rider_id}")
                else:
                    print(f"Rider {next_event.data.rider_id} already matched or completed")

                print("-----------------------------------")
            
            elif next_event.event_type == EventType.DRIVER_SHIFT_ENDS:
                print("Driver shift ends..")
                driver = next_event.data

                if driver.driver_id in self.driver_queue.items:
                    self.driver_queue.remove_by_id(driver.driver_id)
                    driver.actual_offline_time = self.current_time
                    print(f"Driver {driver.driver_id} leaves immediately")
                else:
                    driver.offline_pending = True
                    print(f"Driver {driver.driver_id} will leave after current trip")

                print("-----------------------------------")
            
            elif next_event.event_type == EventType.TERMINATION:
                print("Simulation Termination")
                print("-----------------------------------")
                self.print_kpis()
                return
            
            else:
                print("Something wrong..")
                print("-----------------------------------")
            
        
        print(self.rider_queue)
        print(self.driver_queue)