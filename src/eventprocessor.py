import heapq
from models import Aircraft, PassengerDemand, Passenger
from event import Event, AircraftFlight, PassengerEvent, Charge

class EventProcessor:
    def __init__(self, vertiports=None, transport_times = None, ground_transport_schedule=None):
        self.event_queue = []
        self.flight_events = {}  
        self.current_time = 0 
        self.event_id = 0
        self.vertiports = vertiports
        self.transport_times = transport_times 
        self.ground_transport_schedule = ground_transport_schedule
        heapq.heapify(self.event_queue)

    def get_next_event_id(self):
        event_id = self.event_id
        self.event_id += 1
        return event_id

    def add_event(self, event):
        """Schedules a new event in the priority queue."""
        heapq.heappush(self.event_queue, event)
        event_id = event.event_id
        event_type = event.event_type
        
        # Track the event by flight number
        if event_id not in self.flight_events:
            self.flight_events[event_id] = {}
        self.flight_events[event_id][event_type] = event

    def add_passenger_event(self, passenger_event: PassengerEvent):
        self.add_event(passenger_event)
        print(f"Added Passenger at {passenger_event.get_passenger().src} with arrival at {passenger_event.get_passenger().dest} at time {passenger_event.time} with id {passenger_event.event_id}")


    def add_aircraft_flight(self, flight: AircraftFlight):
        """
        Schedules a new AircraftFlight by adding both its departure and arrival events.
        Uses the flight's unique flight_id as the event_id.
        """
        # Create the departure event using the flight's departure time
        departure_event = Event(
            self.get_next_event_id(),
            flight.departure_time,
            "departure",
            flight
        )
        self.add_event(departure_event)
        
        # Create the arrival event using the computed arrival time
        arrival_event = Event(
            self.get_next_event_id(),
            flight.arrival_time,
            "arrival",
            flight
        )
        self.add_event(arrival_event)
        print(f"Scheduled flight {flight.flight_id}: departure at {flight.departure_time} and arrival at {flight.arrival_time}")

    def add_charge(self, charge: Charge):
        event = Event(self.get_next_event_id(), self.current_time + charge.charge_time, "chargeevent", charge)
        self.add_event(event)
        print(f" Aircraft {charge.aircraft.id} will charge for {charge.charge_time} minutes.")
            

    def modify_event(self, event_id, event_type=None, new_time=None, new_data=None):
        """Modifies an existing event dynamically before it is processed."""
        if event_id in self.flight_events and event_type in self.flight_events[event_id]:
            old_event = self.flight_events[event_id][event_type]
            old_event.valid = False  # Invalidate old event

            # Create and schedule the updated event
            updated_event = Event(
                new_time if new_time is not None else old_event.time,
                event_type if event_type is not None else old_event.event_type,
                event_id,
                new_data if new_data is not None else old_event.data
            )

            heapq.heappush(self.event_queue, updated_event)
            self.flight_events[event_id][event_type] = updated_event
            print(f"Modified {event_type} for flight {event_id} at time {updated_event.time}")

    def step(self):
        """Processes the next event in the priority queue."""
        if not self.event_queue:
            print("Simulation complete. No more scheduled events.")
            return None

        next_event = heapq.heappop(self.event_queue)

        # Skip invalidated events
        while not next_event.valid and self.event_queue:
            next_event = heapq.heappop(self.event_queue)

        if not next_event.valid:
            print("No more valid events to process.")
            return None

        # Advance simulation time to event time
        self.current_time = next_event.time
        return next_event

    def init_aircraft(self, aircraft: Aircraft):
            print(f" Adding Aircraft {aircraft.id} to vertiport {aircraft.loc}")
            next(v for v in self.vertiports if v.name == aircraft.loc).current_aircraft.append(aircraft)

    def process_event(self, event):
        """Handles events based on their type in the discrete event simulation."""
        print(f"Time {self.current_time}: Processing {event}")

        if event.event_type == "add_passenger_to_vertiport":
            self.handle_add_passenger_to_vertiport(event.data)
        elif event.event_type == "departure":
            self.handle_departure(event.data)
        elif event.event_type == "arrival":
            self.handle_arrival(event.data)
        elif event.event_type == "chargeevent":
            self.handle_charge(event.data)

    def handle_add_passenger_to_vertiport(self, passenger: Passenger):
        print(f" Adding passenger to vertiport {passenger.src} with destination {passenger.dest}")
        next(v for v in self.vertiports if v.name == passenger.src).current_passengers.append(passenger)

    def handle_departure(self, flight: AircraftFlight):
        print(f" Aircraft {flight.aircraft.id} departing from {flight.departure_airport}")
        removed = False
        for vertiport in self.vertiports:
            if flight.aircraft in vertiport.current_aircraft:
                vertiport.current_aircraft.remove(flight.aircraft)
                removed = True
                print(f"Removed aircraft from {vertiport.name}")
                break
        if not removed:
            print("Aircraft not found in any vertiport.")

    def handle_arrival(self, flight: AircraftFlight):
        print(f" Aircraft {flight.aircraft.id} arrived at {flight.arrival_airport}")
        for vertiport in self.vertiports:
            if vertiport.name == flight.arrival_airport:
                vertiport.current_aircraft.append(flight.aircraft)
                print(f"Aircraft added to {vertiport.name}")
                break
        
        flight.aircraft.bat_per -= flight.enroute_time
        flight.aircraft.remove_passengers()

        ### Example
        # self.add_charge(Charge(flight.aircraft, 30))

    def handle_charge(self, charge: Charge):
        charge.update_charge()
        print(f" Aircraft {charge.aircraft.id} completed charging for {charge.charge_time} minutes with new range (minutes) of {charge.aircraft.bat_per}")
        

    def handle_delay(self, data):
        print(f" Processing delay: {data}")

    def run(self, step_mode=False):
        """Runs the discrete event simulation."""
        while self.event_queue:
            if step_mode:
                return self.step()  # Return the event for external algorithm modifications
            else:
                event = self.step()
                if event:
                    self.process_event(event)
                

if __name__ == "__main__":
    # Create a Scheduler instance
    scheduler = EventProcessor()
    
    aircraft1 = Aircraft(1, 90, 4, "SCZ")  
    aircraft2 = Aircraft(2, 80, 4, "BER")
                         
    # Schedule flight events using the new AircraftFlight and addAircraftFlight method
    flight1 = AircraftFlight(201, aircraft1, "SCZ", "BER", 30, 30)  # departure at 30, enroute time 30 => arrival at 60
    flight2 = AircraftFlight(202, aircraft2, "BER", "LAX", 45, 30)  # departure at 45, enroute time 30 => arrival at 75
    scheduler.add_aircraft_flight(flight1)
    scheduler.add_aircraft_flight(flight2)
    
    # Run the simulation with step mode enabled
    while scheduler.event_queue:
        event = scheduler.run(step_mode=True)
        if event:
            scheduler.process_event(event)
