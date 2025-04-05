from random import random

LOAD_TIME_DEFAULT = 15
FLIGHT_ID_RANDOM = 0


def get_load_time(load_time=LOAD_TIME_DEFAULT):
    offset = (random() - 0.5) * 20 
    return load_time + offset


def generate_flight_id():
    global FLIGHT_ID_RANDOM
    FLIGHT_ID_RANDOM += 1
    return FLIGHT_ID_RANDOM

def get_transport_time(simulation, vertiport_name, dest_name):
    """
    Utility function to look up the flight time between two vertiports
    in the simulation's 'transports' list. Adjust if you store them differently.
    """
    for t in simulation.transport_times:
        # If your TransportTime objects store numeric IDs, adjust accordingly.
        if t.src == vertiport_name and t.dest == dest_name:
            offset = (random() - 0.5) * 10  
            return t.time + offset
    return None

