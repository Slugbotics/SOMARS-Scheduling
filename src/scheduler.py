from vars_types import get_load_time, generate_flight_id, get_transport_time
from event import AircraftFlight, Charge
import math


class Scheduler:
    def __init__(self):
        pass 

    def schedule(self, just_processed_event):
        """
        Called immediately after an event is processed. Uses the
        current simulation state (vertiports, aircraft, passengers)
        to decide if new flights should be scheduled.

        :param just_processed_event: The event that was just processed
                                     (with a `time` attribute).
        """
        pass

class NaiveScheduler(Scheduler):
    """
    A naive scheduler that can handle multiple destinations. After each event:
      1) Checks for any available aircraft at each vertiport.
      2) Groups waiting passengers by destination.
      3) Picks the largest passenger group (or any selection logic you choose).
      4) Loads as many as possible and schedules a flight event to that destination.
    """
    def __init__(self, simulation):
        self.simulation = simulation

    def schedule(self, just_processed_event):
        current_time = just_processed_event.time

        for vertiport in self.simulation.vertiports:
            # for aircraft in list(vertiport.current_aircraft):
            for aircraft in sorted(vertiport.current_aircraft, key=lambda x: x.bat_per, reverse=True):

                if not vertiport.current_passengers:
                    continue

                if aircraft.set_to_depart() or aircraft.is_charging():
                    continue

                destination_map = self._group_passengers_by_destination(vertiport.current_passengers)

                chosen_destination, passengers_for_dest, transport_time = self.select_trip_for_aircraft(aircraft, vertiport, destination_map)

                if chosen_destination is None:
                    continue

                # Load as many passengers as we can onto the aircraft
                loaded_passengers = []
                while len(passengers_for_dest) > 0 and len(aircraft.load) < aircraft.capacity:
                    p = passengers_for_dest.pop()
                    success = aircraft.add_passenger(p)
                    if success:
                        loaded_passengers.append(p)
                        vertiport.current_passengers.remove(p)
                    else:
                        # Aircraft is full or something else
                        break

                if not loaded_passengers:
                    print("Loaded passengers fail?")
                    continue


                # Create a new flight event. We assume you have a class like AircraftFlight:
                new_flight_id = generate_flight_id()
                departure_time = current_time + get_load_time(randomize=False)

                new_flight = AircraftFlight(
                    flight_id=new_flight_id,
                    aircraft=aircraft,
                    departure_airport=vertiport.name,
                    arrival_airport=chosen_destination,
                    departure_time=departure_time,
                    enroute_time=transport_time
                )

                # Add the flight to the event processor
                self.simulation.event_processor.add_aircraft_flight(new_flight)

    def _pick_nth_largest_group(self, destination_map, n=1):
        """
        Return the n-th largest passenger group from destination_map (sorted by size).
        destination_map is {dest: [passenger_list]}.
        If no valid n-th largest group exists, return (None, []).
        """
        # Sort destinations by descending passenger count
        sorted_destinations = sorted(destination_map.items(), key=lambda x: len(x[1]), reverse=True)

        # If empty or n out of range, no more valid groups
        if not sorted_destinations or n < 1 or n > len(sorted_destinations):
            return None, []

        chosen_destination, passenger_list = sorted_destinations[n - 1]
        return chosen_destination, passenger_list


    def select_trip_for_aircraft(self, aircraft, vertiport, destination_map):
        """
        Example of a while loop that keeps trying to find any group an aircraft
        can serve. If the aircraft does not have enough battery, it is scheduled
        for a 30-minute charge, then we try again.
        """
        # Try continuously until we find a valid group or exhaust them
        n=1
        while True:
            chosen_destination, passengers_for_dest = self._pick_nth_largest_group(destination_map, n=n)
            n+=1

            # If there are no more groups
            if chosen_destination is None:
                # print("No remaining passenger groups.")
                break  # or break, depending on your design

            # Compute the transport time for the chosen route
            transport_time = get_transport_time(
                self.simulation,
                vertiport_name=vertiport.name,
                dest_name=chosen_destination,
                randomize=False
            )


            if transport_time is None:
                del destination_map[chosen_destination]
                continue 

            if transport_time > aircraft.bat_per:
                # print(f"Aircraft {aircraft.id} does not have enough charge to fly "
                #     f"{vertiport.name} -> {chosen_destination}.")
                del destination_map[chosen_destination]
                continue
            
            aircraft.set_depart()
            return chosen_destination, passengers_for_dest, transport_time

        # print(f"Charging Aircraft {aircraft.id} with {aircraft.bat_per} to charge for 30 minutes.")
        self.simulation.event_processor.add_charge(Charge(aircraft, 30))
        return None, [], None


    def _group_passengers_by_destination(self, passengers):
        """
        Returns a dict: {destination_name: [list_of_passengers]}
        """
        destination_map = {}
        for p in passengers:
            if p.dest not in destination_map:
                destination_map[p.dest] = []
            destination_map[p.dest].append(p)
        return destination_map



class RewardScheduler(Scheduler):
    def __init__(self, simulation):
        self.simulation = simulation

    def total_passenger_f(self, x):
        return 30*x
    
    def highest_latency_f(self, x):
        # return math.exp(x/10) - 2.5
        return (3/4)*x - 20
    
    def average_latency_f(self, x):
        # return math.exp(x/5) - 2.5
        return 2*x - 2.5

    def total_passengers_at_vertiport_f(self, x):
        return (1/2)*x
    
    def next_ground_time_f(self, x):
        return max((-x + 100)/5, 0)

    def reward_value(self, total_passengers, highest_latency, average_latency, total_passengers_at_vertiport, next_ground_time):
        return (self.total_passenger_f(total_passengers) + self.highest_latency_f(highest_latency) + self.average_latency_f(average_latency) + self.total_passengers_at_vertiport_f(total_passengers_at_vertiport)) + self.next_ground_time_f(next_ground_time)

    def reward_ranking(self, current_time, destination_map):
        reward_rank = {}
        for v in destination_map:
            total_passengers = len(destination_map[v])

            highest_latency = max([current_time - p.book_time for p in destination_map[v]])
            average_latency = sum([current_time - p.book_time for p in destination_map[v]]) / len(destination_map[v])

            for vert in self.simulation.vertiports:
                if vert.name == v:
                    total_passengers_at_vertiport = len(vert.current_passengers)

            reward_rank[v] = self.reward_value(total_passengers, highest_latency, average_latency, total_passengers_at_vertiport, 0)
        
        return sorted(reward_rank.items(), key=lambda x: x[1], reverse=True)


    def schedule(self, just_processed_event):
        current_time = just_processed_event.time

        for vertiport in self.simulation.vertiports:
            for aircraft in sorted(vertiport.current_aircraft, key=lambda x: x.bat_per, reverse=True):
                destination_map = self._group_passengers_by_destination(vertiport.current_passengers)
                ranked_routes = self.reward_ranking(current_time, destination_map)

                if not vertiport.current_passengers:
                    continue

                if aircraft.set_to_depart() or aircraft.is_charging():
                    continue

                chosen_destination, passengers_for_dest, transport_time = self.select_trip_for_aircraft_2(aircraft, ranked_routes, vertiport, destination_map)

                if chosen_destination is None:
                    continue

                # Load as many passengers as we can onto the aircraft
                loaded_passengers = []
                while len(passengers_for_dest) > 0 and len(aircraft.load) < aircraft.capacity:
                    p = passengers_for_dest.pop()
                    success = aircraft.add_passenger(p)
                    if success:
                        loaded_passengers.append(p)
                        vertiport.current_passengers.remove(p)
                    else:
                        # Aircraft is full or something else
                        break

                if not loaded_passengers:
                    print("Loaded passengers fail?")
                    continue


                # Create a new flight event. We assume you have a class like AircraftFlight:
                new_flight_id = generate_flight_id()
                departure_time = current_time + get_load_time(randomize=False)

                new_flight = AircraftFlight(
                    flight_id=new_flight_id,
                    aircraft=aircraft,
                    departure_airport=vertiport.name,
                    arrival_airport=chosen_destination,
                    departure_time=departure_time,
                    enroute_time=transport_time
                )

                # Add the flight to the event processor
                self.simulation.event_processor.add_aircraft_flight(new_flight)

            
    def select_trip_for_aircraft(self, aircraft, ranked_routes, vertiport, destination_map):
            for i in range(len(ranked_routes)):
                chosen_destination = ranked_routes[i][0]
                passengers_for_dest = destination_map[chosen_destination]


                transport_time = get_transport_time(
                    self.simulation,
                    vertiport_name=vertiport.name,
                    dest_name=chosen_destination,
                    randomize=False
                )

                if transport_time is None:
                    del destination_map[chosen_destination]
                    continue 

                if transport_time > aircraft.bat_per:
                    del destination_map[chosen_destination]
                    continue
                
                aircraft.set_depart()
                return chosen_destination, passengers_for_dest, transport_time
             
            charge_time = 0
            if len(destination_map) != 0:
                charge_time = sum(2 * len(destination_map[dest_name]) * get_transport_time(self.simulation, vertiport.name, dest_name, randomize=False) for dest_name in destination_map.keys()) / len(destination_map)
            
            charge_time = min(90, max(charge_time, 15))
            self.simulation.event_processor.add_charge(Charge(aircraft, charge_time))
            return None, [], None
   

    def select_trip_for_aircraft_2(self, aircraft, ranked_routes, vertiport, destination_map):
            chosen_destination = ranked_routes[0][0]
            passengers_for_dest = destination_map[chosen_destination]


            transport_time = get_transport_time(
                self.simulation,
                vertiport_name=vertiport.name,
                dest_name=chosen_destination,
                randomize=False
            )

            if transport_time is None or transport_time > aircraft.bat_per:
                del destination_map[chosen_destination]
                charge_time = 0
                # if len(destination_map) != 0:
                    # charge_time = sum(2 * len(destination_map[dest_name]) * get_transport_time(self.simulation, vertiport.name, dest_name, randomize=False) for dest_name in destination_map.keys()) / len(destination_map)
                
                charge_time = min(90, max(charge_time, 15))
                self.simulation.event_processor.add_charge(Charge(aircraft, charge_time))
                return None, [], None     
                   
            aircraft.set_depart()
            return chosen_destination, passengers_for_dest, transport_time
            


    def _group_passengers_by_destination(self, passengers):
        """
        Returns a dict: {destination_name: [list_of_passengers]}
        """
        destination_map = {}
        for p in passengers:
            if p.dest not in destination_map:
                destination_map[p.dest] = []
            destination_map[p.dest].append(p)
        return destination_map
