import matplotlib.pyplot as plt
class Vertiport:
    def __init__(self,
                 id=0,
                 name="",
                 current_aircraft=None,
                 capacity=0):
        if current_aircraft is None:
            current_aircraft = []
        self.id = id
        self.name = name
        self.current_aircraft = current_aircraft
        self.capacity = capacity


class Aircraft:
    def __init__(self,
                 id=0,
                 bat_per=0,
                 capacity=0,
                 loc=""):
        self.id = id
        self.bat_per = bat_per
        self.capacity = capacity
        self.loc = loc


class PassengerDemand:
    def __init__(self,
                 src=0,
                 dest=0,
                 unit_time=1.0,
                 demand=None):
        if demand is None:
            demand = []
        self.src = src
        self.dest = dest
        self.unit_time = unit_time
        self.demand = demand

    def __repr__(self):
        return (f"PassengerDemand(src={self.src}, dest={self.dest}, "
                f"unit_time={self.unit_time}, demand={self.demand})")

    def graph(self):
        """
        Graph the passenger demand using matplotlib.
        The x-axis corresponds to time (in hours) calculated using unit_time.
        The y-axis corresponds to the number of passengers.
        """
        if not self.demand:
            print("No demand data to graph.")
            return

        # Create x coordinates based on the number of demand entries and unit_time.
        x_values = [i * self.unit_time for i in range(len(self.demand))]

        plt.figure(figsize=(10, 5))
        plt.plot(x_values, self.demand, marker='o', linestyle='-', color='b')
        plt.xlabel('Time (hours)')
        plt.ylabel('Number of Passengers')
        plt.title(f'Passenger Demand from {self.src} to {self.dest}')
        plt.grid(True)
        plt.xticks(x_values, rotation=45)  # Adjust x-ticks for clarity
        plt.tight_layout()
        plt.show()


class TransportTime:
    def __init__(self,
                 src=0,
                 dest=0,
                 time=0):
        self.src = src
        self.dest = dest
        self.time = time


class GroundTransport:
    def __init__(self,
                 loc=0,
                 times=None):
        if times is None:
            times = []
        self.loc = loc
        self.times = times


class Simulation:
    def __init__(self,
                 vertiports,
                 aircraft,
                 passenger_demand,
                 transport_times,
                 ground_transport_schedule):
        self.vertiports = vertiports
        self.aircraft = aircraft
        self.passenger_demand = passenger_demand
        self.transport_times = transport_times
        self.ground_transport_schedule = ground_transport_schedule

    def graph_passenger_demand(self):
        for demand in self.passenger_demand:
            demand.graph()

    def print_simulation_state(self):
        print("None")

    def print_simulation_initialization(self):
        for vp in self.vertiports:
            print(f"ID: {vp.id}, Name: {vp.name}, Capacity: {vp.capacity}")
        for a in self.aircraft:
            print(f"Aircraft ID={a.id}, Battery={a.bat_per}, Capacity={a.capacity}, Location={a.loc}")
        for demand in self.passenger_demand:
            print(demand)

        for transport in self.transport_times:
            print(f"Src={transport.src}, Dest={transport.dest}, Time={transport.time}")

        for t in self.ground_transport_schedule:
            print(f"Location: {t.loc}")
            print("Departure times:")
            for time in t.times:
                print(f"  {time}")
