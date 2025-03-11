import heapq
from models import Aircraft, PassengerDemand

class Event:
    def __init__(self, time, event_type, flight_number, data):
        self.time = time  # The scheduled time of the event
        self.event_type = event_type  # 'passenger_request', 'departure', 'arrival', 'delay'
        self.flight_number = flight_number  # Unique flight number
        self.data = data  # Associated object (aircraft, passenger request, etc.)
        self.valid = True  # Validity flag for outdated events

    def __lt__(self, other):
        """Sort events by time in the priority queue."""
        return self.time < other.time

    def __repr__(self):
        return (f"Event(time={self.time}, type={self.event_type}, flight_number={self.flight_number}, "
                f"data={self.data})")

class Scheduler:
    def __init__(self):
        self.event_queue = []  # Priority queue (min-heap) for event scheduling
        self.flight_events = {}  # Dictionary tracking events by flight number
        self.current_time = 0  # Tracks the simulation clock
        heapq.heapify(self.event_queue)

    def add_event(self, time, event_type, flight_number, data):
        """Schedules a new event in the priority queue."""
        event = Event(time, event_type, flight_number, data)
        heapq.heappush(self.event_queue, event)

        # Track the event by flight number
        if flight_number not in self.flight_events:
            self.flight_events[flight_number] = {}
        self.flight_events[flight_number][event_type] = event

    def modify_event(self, flight_number, event_type=None, new_time=None, new_data=None):
        """Modifies an existing event dynamically before it is processed."""
        if flight_number in self.flight_events and event_type in self.flight_events[flight_number]:
            old_event = self.flight_events[flight_number][event_type]
            old_event.valid = False  # Invalidate old event

            # Create and schedule the updated event
            updated_event = Event(
                new_time if new_time is not None else old_event.time,
                event_type if event_type is not None else old_event.event_type,
                flight_number,
                new_data if new_data is not None else old_event.data
            )

            heapq.heappush(self.event_queue, updated_event)
            self.flight_events[flight_number][event_type] = updated_event
            print(f"Modified {event_type} for flight {flight_number} at time {updated_event.time}")

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

    def process_event(self, event):
        """Handles events based on their type in the discrete event simulation."""
        print(f"Time {self.current_time}: Processing {event}")

        if event.event_type == "passenger_request":
            self.handle_passenger_request(event.data)
        elif event.event_type == "departure":
            self.handle_departure(event.data)
        elif event.event_type == "arrival":
            self.handle_arrival(event.data)
        elif event.event_type == "delay":
            self.handle_delay(event.data)

    def handle_passenger_request(self, passenger: PassengerDemand):
        print(f" Passenger request: {passenger.demand} passengers from {passenger.src} to {passenger.dest}")

    def handle_departure(self, aircraft: Aircraft):
        print(f" Aircraft {aircraft.id} departing from {aircraft.loc}")

    def handle_arrival(self, aircraft: Aircraft):
        print(f" Aircraft {aircraft.id} arrived at {aircraft.loc}")

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
    scheduler = Scheduler()
    
    # Example Aircraft
    aircraft1 = Aircraft(1, 90, 4, "SCZ")  
    aircraft2 = Aircraft(2, 80, 4, "BER")  

    # Schedule flight events
    scheduler.add_event(1, "passenger_request", "FL100", PassengerDemand("SCZ", "BER", 1, 5))
    scheduler.add_event(3, "departure", "FL100", aircraft1)
    scheduler.add_event(5, "arrival", "FL100", aircraft1)

    scheduler.add_event(2, "passenger_request", "FL101", PassengerDemand("BER", "LAX", 1, 3))
    scheduler.add_event(4, "departure", "FL101", aircraft2)
    scheduler.add_event(6, "arrival", "FL101", aircraft2)

    # Modify a flight event dynamically
    scheduler.modify_event("FL100", event_type="departure", new_time=4)  # Flight FL100 departure delayed

    # Run the simulation with step mode enabled
    while scheduler.event_queue:
        event = scheduler.run(step_mode=True)
        if event:
            # Example: Delay FL101 departure dynamically if the aircraft battery is low
            if event.flight_number == "FL101" and event.event_type == "departure" and event.data.bat_per < 50:
                scheduler.modify_event("FL101", event_type="departure", new_time=7)
                continue  # Skip processing this step
            
            scheduler.process_event(event)  # Process if no modifications needed
