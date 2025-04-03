from load_data import load_passenger_demand, load_transport_times, load_ground_transport
from models import Aircraft, PassengerDemand
from Scheduler import Scheduler

# Load data from CSVs
passenger_demands = load_passenger_demand('../data/example_1/passenger_demand.csv')
transport_times = load_transport_times('../data/example_1/transport_time.csv')
ground_transport = load_ground_transport('../data/example_1/ground_transport.csv')

# Sample aircraft setup
aircraft1 = Aircraft(1, 90, 4, "SCZ")  
aircraft2 = Aircraft(2, 80, 4, "BER")

# Initialize the Scheduler (Discrete Event Simulation)
scheduler = Scheduler()

# Schedule passenger requests based on demand
for demand in passenger_demands:
    for i, num_passengers in enumerate(demand.demand):
        if num_passengers > 0:
            event_time = i * demand.unit_time  # Convert index to time
            flight_number = f"FL{100 + i}"  # Unique flight number
            scheduler.add_event(event_time, "passenger_request", flight_number, demand)

# Load transport times

# Schedule departures and arrivals based on passenger requests
for demand in passenger_demands:
    for i, num_passengers in enumerate(demand.demand):
        if num_passengers > 0:
            event_time = i * demand.unit_time
            flight_number = f"FL{100 + i}"

            # Find transport time between src and dest
            transport_time = next(
                (t.time for t in transport_times if t.src == demand.src and t.dest == demand.dest),
                2  # Default to 2 hours if not found
            )

            # Assign aircraft dynamically (simple round-robin)
            aircraft = aircraft1 if i % 2 == 0 else aircraft2

            # Schedule departure and arrival
            scheduler.add_event(event_time + 1, "departure", flight_number, aircraft)
            scheduler.add_event(event_time + 1 + transport_time, "arrival", flight_number, aircraft)
while scheduler.event_queue:
    event = scheduler.run(step_mode=True)
    
    if event:
        # If the aircraft battery is low, delay the flight
        if event.event_type == "departure" and event.data.bat_per < 50:
            print(f"🔋 Flight {event.flight_number} has low battery. Delaying departure.")
            scheduler.modify_event(event.flight_number, event_type="departure", new_time=event.time + 5)
            continue  # Skip processing this step
        
        # Process event if no modification is needed
        scheduler.process_event(event)