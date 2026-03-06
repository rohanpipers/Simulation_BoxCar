import random
from typing import Tuple

class Distributions:
    def __init__(self) -> None:
        pass
    
    @staticmethod
    def generate_rider_interarival() -> float:
        return random.expovariate(30)
    
    @staticmethod
    def generate_rider_patience() -> float:
        return random.expovariate(5)
    
    @staticmethod
    def generate_driver_interarival() -> float:
        return random.expovariate(3)
    
    @staticmethod
    def generate_location() -> Tuple[float, float]:
        x_coordinate = random.uniform(0, 20)
        y_coordinate = random.uniform(0, 20)
        return (x_coordinate, y_coordinate)
    
    @staticmethod
    def generate_driver_shift_time() -> float:
        return random.uniform(5, 8)

    @staticmethod
    def estimated_trip_time(expected_trip_time: float) -> float:
        return random.uniform(0.8 * expected_trip_time, 1.2 * expected_trip_time)