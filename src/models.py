import matplotlib.pyplot as plt

class Vertiport:
    def __init__(self, id=0, name="", current_aircraft=None, capacity=0):
        if current_aircraft is None:
            current_aircraft = []
        self.id = id
        self.name = name
        self.current_aircraft = current_aircraft
        self.capacity = capacity
    
    def __str__(self):
        return f"ID: {self.id}, Name: {self.name}, Capacity: {self.capacity}"
    
    def display_info(self):
        print(self)

class Aircraft:
    def __init__(self, id=0, bat_per=0, capacity=0, loc=""):
        self.id = id
        self.bat_per = bat_per
        self.capacity = capacity
        self.loc = loc
    
    def __str__(self):
        return f"Aircraft ID={self.id}, Battery={self.bat_per}, Capacity={self.capacity}, Location={self.loc}"
    
    def display_info(self):
        print(self)

class PassengerDemand:
    def __init__(self, src=0, dest=0, unit_time=1.0, demand=None):
        if demand is None:
            demand = []
        self.src = src
        self.dest = dest
        self.unit_time = unit_time
        self.demand = demand

    def __str__(self):
        return (f"PassengerDemand(src={self.src}, dest={self.dest}, "
                f"unit_time={self.unit_time}, demand={self.demand})")
    
    def display_info(self):
        print(self)
    
    def graph(self):
        if not self.demand:
            print("No demand data to graph.")
            return
        x_values = [i * self.unit_time for i in range(len(self.demand))]
        plt.figure(figsize=(10, 5))
        plt.plot(x_values, self.demand, marker='o', linestyle='-', color='b')
        plt.xlabel('Time (hours)')
        plt.ylabel('Number of Passengers')
        plt.title(f'Passenger Demand from {self.src} to {self.dest}')
        plt.grid(True)
        plt.xticks(x_values, rotation=45)
        plt.tight_layout()
        plt.show()

class TransportTime:
    def __init__(self, src=0, dest=0, time=0):
        self.src = src
        self.dest = dest
        self.time = time
    
    def __str__(self):
        return f"Src={self.src}, Dest={self.dest}, Time={self.time}"
    
    def display_info(self):
        print(self)

class GroundTransport:
    def __init__(self, loc=0, times=None):
        if times is None:
            times = []
        self.loc = loc
        self.times = times
    
    def __str__(self):
        times_str = ', '.join(map(str, self.times))
        return f"Location: {self.loc}\nDeparture times: {times_str}"
    
    def display_info(self):
        print(self)

class Simulation:
    def __init__(self, vertiports, aircraft, passenger_demand, transport_times, ground_transport_schedule):
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
        print("Vertiports:")
        for vp in self.vertiports:
            vp.display_info()
        print("\nAircraft:")
        for a in self.aircraft:
            a.display_info()
        print("\nPassenger Demands:")
        for demand in self.passenger_demand:
            demand.display_info()
        print("\nTransport Times:")
        for transport in self.transport_times:
            transport.display_info()
        print("\nGround Transport Schedules:")
        for t in self.ground_transport_schedule:
            t.display_info()

