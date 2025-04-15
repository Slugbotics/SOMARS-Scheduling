from random import random

LOAD_TIME_DEFAULT = 15
FLIGHT_ID_RANDOM = 0
PASSENGER_ID_RANDOM = 0
CHARGE_ID_RANDOM = 0

def generate_charge_id():
    global CHARGE_ID_RANDOM
    CHARGE_ID_RANDOM += 1
    return CHARGE_ID_RANDOM

def generate_passenger_id():
    global PASSENGER_ID_RANDOM
    PASSENGER_ID_RANDOM += 1
    return PASSENGER_ID_RANDOM

def get_load_time(load_time=LOAD_TIME_DEFAULT, randomize=True):
    if not randomize:
        return load_time
    offset = (random() - 0.5) * 20 
    return load_time + offset


def generate_flight_id():
    global FLIGHT_ID_RANDOM
    FLIGHT_ID_RANDOM += 1
    return FLIGHT_ID_RANDOM

def get_transport_time(simulation, vertiport_name, dest_name, randomize=True):
    """
    Utility function to look up the flight time between two vertiports
    in the simulation's 'transports' list. Adjust if you store them differently.
    """
    for t in simulation.transport_times:
        # If your TransportTime objects store numeric IDs, adjust accordingly.
        if t.src == vertiport_name and t.dest == dest_name:
            if not randomize:
                return t.time
            offset = (random() - 0.5) * 10  
            return t.time + offset
    return None

