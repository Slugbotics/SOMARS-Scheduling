import random
from load_data import (
    load_vertiports,
    load_passenger_demand,
    load_transport_times,
    load_ground_transport,
    load_starting_state,
)
from eventprocessor import EventProcessor
from models import Aircraft, Passenger
from event import PassengerEvent, AircraftFlight, Charge
from collections import Counter
from debug import log_flight_scheduling, log_boarding


def create_scheduler_from_data(data_folder: str, total_fly_time=90):
    vertiports = load_vertiports(f"{data_folder}/vertiport.txt")
    aircraft = load_starting_state(f"{data_folder}/starting_state.txt", total_fly_time)
    passenger_demands = load_passenger_demand(f"{data_folder}/passenger_demand.csv")
    transport_times = load_transport_times(f"{data_folder}/transport_time.csv")
    ground_transports = load_ground_transport(f"{data_folder}/ground_transport.csv")

    scheduler = EventProcessor(vertiports, transport_times, ground_transports)

    for ac in aircraft:
        scheduler.init_aircraft(ac)

    for demand in passenger_demands:
        for i, num_passengers in enumerate(demand.demand):
            if num_passengers > 0:
                event_time = i * demand.unit_time + random.uniform(0, demand.unit_time)
                for _ in range(num_passengers):
                    passenger = Passenger(demand.src, demand.dest)
                    event = PassengerEvent(
                        time=event_time,
                        passenger=passenger,
                        event_type="add_passenger_to_vertiport",
                        event_id=scheduler.get_next_event_id()
                    )
                    scheduler.add_passenger_event(event)

    return scheduler


def try_to_schedule_flight(scheduler: EventProcessor):
    for vertiport in scheduler.vertiports:
        # Group passengers by destination
        dest_groups = {}
        for passenger in vertiport.current_passengers:
            dest_groups.setdefault(passenger.dest, []).append(passenger)

        # Sort by number of waiting passengers
        sorted_destinations = sorted(dest_groups.items(), key=lambda x: len(x[1]), reverse=True)

        for destination, group in sorted_destinations:
            if not group:
                continue

            # Look up transport time
            transport_time = next(
                (t.time for t in scheduler.transport_times if t.src == vertiport.name and t.dest == destination),
                None
            )

            if transport_time is None:
                print(f" No transport time from {vertiport.name} to {destination}")
                continue

            for aircraft in vertiport.current_aircraft:
                if aircraft.in_flight:
                    continue

                # Battery check
                if aircraft.bat_per < transport_time:
                    print(f"Aircraft {aircraft.id} too low on battery ({aircraft.bat_per}min) — scheduling charge.")
                    scheduler.add_charge(Charge(aircraft, charge_time=30))
                    continue

                passengers_to_board = group[:min(len(group), aircraft.capacity)]
                if not passengers_to_board:
                    print(f"Skipping flight for Aircraft {aircraft.id} — no passengers to board.")
                    continue

                # Board passengers
                for p in passengers_to_board:
                    aircraft.add_passenger(p)
                    vertiport.current_passengers.remove(p)

                # Schedule flight
                departure_time = scheduler.current_time + 1
                flight = AircraftFlight(
                    flight_id=scheduler.get_next_event_id(),
                    aircraft=aircraft,
                    departure_airport=vertiport.name,
                    arrival_airport=destination,
                    departure_time=departure_time,
                    enroute_time=transport_time
                )
                scheduler.add_aircraft_flight(flight)

                # Mark aircraft busy
                aircraft.in_flight = True
                vertiport.current_aircraft.remove(aircraft)

                # Log activity
                log_boarding(aircraft,scheduler.current_time)
                log_flight_scheduling(aircraft, vertiport.name, destination, departure_time, aircraft.load,scheduler.current_time)

                print(f"Scheduled flight from {vertiport.name} to {destination} with {len(passengers_to_board)} pax")
                return  # Only schedule one flight per time step



def run_simulation(scheduler: EventProcessor):
    while scheduler.event_queue:
        event = scheduler.run(step_mode=True)
        if event:
            scheduler.process_event(event)

            if event.event_type in ["add_passenger_to_vertiport", "arrival", "chargeevent"]:
                try_to_schedule_flight(scheduler)

    scheduler.generate_report("simulation_report.txt")







if __name__ == "__main__":
    scheduler = create_scheduler_from_data("../data/example_1")  
    run_simulation(scheduler)
