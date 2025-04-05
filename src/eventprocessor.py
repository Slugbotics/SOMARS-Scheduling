import heapq
from models import Aircraft, PassengerDemand, Passenger
from event import Event, AircraftFlight, PassengerEvent, Charge
from collections import defaultdict

class EventProcessor:
    def __init__(self, vertiports=None, transport_times = None, ground_transport_schedule=None, scheduler=None):
        self.event_queue = []
        self.flight_events = {}  
        self.current_time = 0 
        self.event_id = 0
        self.vertiports = vertiports
        self.transport_times = transport_times 
        self.ground_transport_schedule = ground_transport_schedule
        self.scheduler = scheduler
        heapq.heapify(self.event_queue)


        self.hourly_throughput = defaultdict(int)
        self.passenger_arrival_time = {}
        self.passenger_boarding_delays = []
        self.ground_time_start = {}
        self.charge_time_by_location = defaultdict(float)
        self.ground_cycles = []
        self.charge_cycles = []
        self.loading_cycles = []
        self.charging_in_cycle = defaultdict(float)


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
        charge.aircraft.set_charging(True)
        # print(f" Aircraft {charge.aircraft.id} will charge for {charge.charge_time} minutes.")
            

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
            for v in self.vertiports:
                if v.name == aircraft.loc:
                    v.current_aircraft.append(aircraft)
                    self.ground_time_start[aircraft.id] = self.current_time
                    break


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
        self.passenger_arrival_time[passenger] = self.current_time
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
            return 

        a_id = flight.aircraft.id
        if a_id in self.ground_time_start:
            cycle_time = self.current_time - self.ground_time_start[a_id]
            charge_time = self.charging_in_cycle[a_id]
            loading_time = cycle_time - charge_time

            self.ground_cycles.append(cycle_time)
            self.charge_cycles.append(charge_time)
            self.loading_cycles.append(loading_time)

            # reset for the next cycle
            self.charging_in_cycle[a_id] = 0.0
            del self.ground_time_start[a_id]

        for p in flight.aircraft.load:
            arrival_t = self.passenger_arrival_time.get(p, None)
            if arrival_t is not None:
                delay = self.current_time - arrival_t
                self.passenger_boarding_delays.append(delay)


    def handle_arrival(self, flight: AircraftFlight):
        print(f" Aircraft {flight.aircraft.id} arrived at {flight.arrival_airport}")
        for vertiport in self.vertiports:
            if vertiport.name == flight.arrival_airport:
                vertiport.current_aircraft.append(flight.aircraft)
                print(f"Aircraft added to {vertiport.name}")
                break
        
        self.ground_time_start[flight.aircraft.id] = self.current_time

        # PASSENGERS COMPLETING THIS FLIGHT -> HOURLY THROUGHPUT
        hour_index = int(self.current_time // 60)  # which "hour" we are in
        num_passengers = len(flight.aircraft.load)
        self.hourly_throughput[hour_index] += num_passengers

        flight.aircraft.arrived(flight.enroute_time, flight.arrival_airport)

        ### Example
        # self.add_charge(Charge(flight.aircraft, 30))

    def handle_charge(self, charge: Charge):
        self.charge_time_by_location[charge.aircraft.loc] += charge.charge_time
        self.charging_in_cycle[charge.aircraft.id] += charge.charge_time


        charge.update_charge()
        # print(f" Aircraft {charge.aircraft.id} completed charging for {charge.charge_time} minutes with new range (minutes) of {charge.aircraft.bat_per}")
        

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

                    if self.scheduler:
                        self.scheduler.schedule(event)


    def print_results(self):
        """
        Prints the key metrics:
          - Hourly throughput
          - Average passenger delay (arrival -> takeoff)
          - Average ground times per cycle (charging vs. loading/idle vs. total)
          - Totals of each
        """
        print("\n=== Simulation Results ===")
        print(f"Final simulation time: {self.current_time:.2f}")

        # 1) HOURLY THROUGHPUT
        print("\n--- Hourly Passenger Throughput ---")
        if not self.hourly_throughput:
            print("No passengers completed.")
        else:
            val = 0
            i = 0
            for hour in sorted(self.hourly_throughput.keys()):
                print(f"  Hour {hour}: {self.hourly_throughput[hour]} passengers")
                val += self.hourly_throughput[hour]
                i+=1 
            val /= i
            print(f"Average Throughput: {val:.2f} passengers per hour")
            

        
        # 2) AVERAGE PASSENGER DELAY (Arrival -> Takeoff)
        if self.passenger_boarding_delays:
            avg_delay = sum(self.passenger_boarding_delays) / len(self.passenger_boarding_delays)
        else:
            avg_delay = 0.0
        print(f"\n--- Average Passenger Delay (arrival->takeoff) ---")
        print(f"Average delay: {avg_delay:.2f} minutes per passenger")

        # 3) GROUND CYCLE TIMES
        print("\n--- Aircraft Ground Times per Cycle (Arrival->Departure) ---")
        n_cycles = len(self.ground_cycles)
        if n_cycles > 0:
            total_ground = sum(self.ground_cycles)
            total_charging = sum(self.charge_cycles)
            total_loading = sum(self.loading_cycles)

            avg_ground = total_ground / n_cycles
            avg_charging = total_charging / n_cycles
            avg_loading = total_loading / n_cycles

            print(f"Number of ground cycles: {n_cycles}")
            print(f"Avg total ground time per cycle: {avg_ground:.2f} min")
            print(f"   - of which charging: {avg_charging:.2f} min")
            print(f"   - of which loading/idle: {avg_loading:.2f} min")

            print("\nTotals across all ground cycles:")
            print(f"   - Total ground time: {total_ground:.2f} min")
            print(f"   - Total charging time: {total_charging:.2f} min")
            print(f"   - Total loading/idle time: {total_loading:.2f} min")
        else:
            print("No completed ground cycles (no arrivals/departures).")
        print("")
                