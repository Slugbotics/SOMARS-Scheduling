#!/usr/bin/env python3
import argparse
import os
import sys

from load_data import load_vertiports, load_ground_transport, load_transport_times, load_passenger_demand, load_starting_state 
from models import Simulation

def main(data_folder, total_fly_time):
    # Check if the specified folder exists
    if not os.path.isdir(data_folder):
        print(f"Error: The specified folder '{data_folder}' does not exist.")
        sys.exit(1)

    # At this point you can continue with the rest of your code logic
    print(f"Total Flight Time: {total_fly_time}")
    print(f"Data folder location: {data_folder}")

    vertiport_list = load_vertiports(data_folder + 'vertiport.txt')
    all_aircraft = load_starting_state(data_folder + 'starting_state.txt', total_fly_time)
    demands = load_passenger_demand(data_folder + 'passenger_demand.csv')
    transports = load_transport_times(data_folder + 'transport_time.csv')
    ground_transports = load_ground_transport(data_folder + 'ground_transport.csv')

    simulation = Simulation(vertiport_list, all_aircraft, demands, transports, ground_transports)
    simulation.print_simulation_initialization()
    simulation.graph_passenger_demand()

if __name__ == "__main__":
    # Set up the argument parser
    parser = argparse.ArgumentParser(
        prog="Dynamic Scheduling Simulation",
        description="Script to process flight time and a folder containing data."
    )

    # Define the expected arguments
    parser.add_argument(
        "--total-fly-time",
        type=float,
        default=90.0,
        help="Total flight time (e.g., in minutes)."
    )
    parser.add_argument(
        "--data-folder",
        type=str,
        default="../data/example_1/",
        help="Path to the folder that contains your data."
    )

    # Parse the arguments from the command line
    args = parser.parse_args()

    total_fly_time = args.total_fly_time
    data_folder = args.data_folder

    main(data_folder, total_fly_time)
