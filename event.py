from models import Aircraft, PassengerDemand


class Event:
    def __init__(self, event_id, time, event_type, data):
        self.time = time  # The scheduled time of the event
        self.event_type = event_type  # 'passenger_request', 'departure', 'arrival', 'delay'
        self.data = data  # Associated object (aircraft, passenger request, etc.)
        self.event_id = event_id
        self.valid = True  # Validity flag for outdated events

    def __lt__(self, other):
        """Sort events by time in the priority queue."""
        return self.time < other.time

    def __repr__(self):
        return (f"Event(time={self.time}, type={self.event_type}, event_id={self.event_id}, "
                f"data={self.data})")
    
    
class PassengerEvent(Event):
    def __init__(self, event_id, time, event_type, passenger):
        self.passenger = passenger
        super().__init__(event_id, time, event_type, passenger)

    def get_passenger(self):
        return self.passenger

class AircraftFlight:
    def __init__(self, flight_id, aircraft, departure_airport, arrival_airport, departure_time, enroute_time, return_leg=False):
        self.flight_id = flight_id
        self.aircraft = aircraft
        self.departure_airport = departure_airport
        self.arrival_airport = arrival_airport
        self.departure_time = departure_time
        self.enroute_time = enroute_time
        self.arrival_time = departure_time + enroute_time

        self.return_leg = return_leg 

    def __repr__(self):
        return (f"AircraftFlight(flight_id={self.flight_id}, aircraft={self.aircraft}, "
                f"departure={self.departure_airport}, arrival={self.arrival_airport}, "
                f"departure_time={self.departure_time}, enroute_time={self.enroute_time})")

class Charge:
    def __init__(self, aircraft, charge_time):
        self.aircraft = aircraft 
        self.charge_time = charge_time 
    
    def update_charge(self):
        self.aircraft.bat_per = min(self.aircraft.battery_capacity, self.aircraft.bat_per + (self.charge_time * self.aircraft.charge_rate))