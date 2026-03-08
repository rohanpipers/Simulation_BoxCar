# main() file
import random
from simulation import Simulation

def main():
    random.seed(0)
    simulation = Simulation()
    simulation.run()

if __name__ == "__main__":
    main()