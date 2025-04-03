def log_flight_scheduling(aircraft, src, dest, dep_time, passengers, current_time):
    print(f"[t={current_time:.2f}]  Scheduled flight | Aircraft {aircraft.id} | {src} → {dest} "
          f"| Departure at {dep_time:.2f} | Passengers: {len(aircraft.load)} | Battery: {aircraft.bat_per:.2f}%")


def log_departure(flight, current_time):
    print(f"[t={current_time:.2f}] Aircraft {flight.aircraft.id} DEPARTED from {flight.departure_airport} "
          f"to {flight.arrival_airport} | Battery: {flight.aircraft.bat_per:.2f}%")


def log_arrival(flight, current_time):
    print(f"[t={current_time:.2f}] Aircraft {flight.aircraft.id} ARRIVED at {flight.arrival_airport} "
          f"from {flight.departure_airport} | Battery: {flight.aircraft.bat_per:.2f}%")


def log_boarding(aircraft, current_time):
    print(f" [t={current_time:.2f}] Boarded {len(aircraft.load)} passenger(s) onto Aircraft {aircraft.id}")


def log_charging(aircraft, current_time, charge_end_time):
    print(f" [t={current_time:.2f}]  Aircraft {aircraft.id} CHARGING | Will finish at {charge_end_time:.2f} | Location: {aircraft.loc}")
