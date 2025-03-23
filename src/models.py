import matplotlib.pyplot as plt

class Vertiport:
    def __init__(self, id=0, name="", capacity=0, current_aircraft=None, current_passengers=None):
        if current_aircraft is None:
            current_aircraft = []
        if current_passengers is None:
            current_passengers = []
        self.id = id
        self.name = name
        self.capacity = capacity
        self.current_aircraft = current_aircraft
        self.current_passengers = current_passengers
    
    def __str__(self):
        passengers_str = ', '.join(str(p) for p in self.current_passengers)
        aircraft_str = ', '.join(str(a) for a in self.current_aircraft)
        return (
            f"ID: {self.id}, Name: {self.name}, Capacity: {self.capacity}\n"
            f"Aircraft: [{aircraft_str}]\n"
            f"Passengers: [{passengers_str}]"
        )
      
    def display_info(self):
        print(self)

    def display_aircraft(self):
        aircraft_str = ', '.join(str(a) for a in self.current_aircraft)
        print (
            f"ID: {self.id}, Name: {self.name}, Capacity: {self.capacity}\n"
            f"Aircraft: [{aircraft_str}]\n"
        )
    
class Passenger:
    def __init__(self, src, dest):
        self.src = src 
        self.dest = dest

    def __str__(self):
        return f"\nOrigin={self.src}, Destination={self.dest}"
    
    def display_info(self):
        print(self)

class Aircraft:
    def __init__(self, id=0, bat_per=0, capacity=0, loc=""):
        self.id = id
        self.bat_per = bat_per
        self.battery_capacity = 90
        self.charge_rate = 1
        self.capacity = capacity
        self.loc = loc
        self.load = []
    
    def add_passenger(self, passenger: Passenger) -> bool:
        if len(self.load) >= self.capacity:
            print("Cannot add passenger (Full Aircraft)")
            return False 
        self.load.append(passenger)
        return True
    
    def remove_passengers(self):
        self.load.clear()

    def __str__(self):
        return f"\nAircraft ID={self.id}, Battery={self.bat_per}, Capacity={self.capacity}, Location={self.loc}"
    
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


