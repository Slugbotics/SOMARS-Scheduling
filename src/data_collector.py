#!/usr/bin/env python3
import csv, os
import matplotlib.pyplot as plt
import numpy as np
from enum import Enum

import plotly.express as px
import pandas as pd

import matplotlib.pyplot as plt
from datetime import datetime, timedelta


def rounded_down_hour(minute):
    return int(minute // 60)

def plot_latencies(latencies):
    plt.figure(figsize=(10, 5))
    plt.plot(latencies, marker='o', linestyle='-', color='b')
    plt.xlabel('Passenger Index')
    plt.ylabel('Latency (minutes)')
    plt.title('Passenger Latency Over Time')
    plt.grid(True)
    plt.show()


def plot_latency_histogram(latencies):
    valid_latencies = [lat for lat in latencies if lat is not None]

    if not valid_latencies:
        print("No valid latencies to plot.")
        return

    max_latency = max(valid_latencies)
    bins = range(0, int(max_latency) + 10, 10)

    # Plot the histogram
    plt.hist(valid_latencies, bins=bins)
    plt.title("Latency Histogram")
    plt.xlabel("Latency (seconds)")
    plt.ylabel("Frequency")
    plt.show()


def calculate_average_latency(reader):
    N = 0
    PDepart = {}
    PBook = {}
    total_latency = 0.0
    for row in reader:
        if row["event_type"] == "passengerdeparture":
            if row["join_id"] not in PDepart:
                PDepart[row["join_id"]] = {"time": float(row["time"])}
        if row["event_type"] == "passengerbook":
            if row["join_id"] not in PBook:
                PBook[row["join_id"]] = {"time": float(row["time"])}
            N += 1

    latencies = [None] * N
    for key in PDepart:
        if key in PBook:
            latency = PDepart[key]["time"] - PBook[key]["time"]
            total_latency += latency 
            latencies.insert(int(key), latency)

    plot_latencies(latencies)
    plot_latency_histogram(latencies)

    return total_latency / N if N > 0 else 0.0, N

def plot_throughput_histogram(throughput_per_hour_map):
    hours = sorted(throughput_per_hour_map.keys())
    throughputs = [throughput_per_hour_map[hour] for hour in hours]

    plt.figure() 
    plt.bar(hours, throughputs)
    plt.xlabel('Hour')
    plt.ylabel('Throughput')
    plt.title('Hourly Throughput')
    plt.show()

def calculate_average_throughput(reader):
    T = 0.0
    throughput_per_hour_map = {}
    for row in reader:
        if row["event_type"] == "passengerarrival":
            hour = rounded_down_hour(float(row["time"]))
            if hour not in throughput_per_hour_map:
                throughput_per_hour_map[hour] = 0
            throughput_per_hour_map[hour] += 1
            T = max(T, hour)

    plot_throughput_histogram(throughput_per_hour_map)

    return sum(throughput_per_hour_map.values()) / T 
    
def average_flight_load(reader):
    load = []
    for row in reader:
        if row["event_type"] == "aircraftdeparture":
            data = row["data"]
            load.append(int(data.split(" ")[5]))

    print("Mean Flight Capacity: " +  str(np.mean(load)))
    print("Std Flight Capacity: " + str(np.std(load)))

    n, bins, patches = plt.hist(load, bins=4)

    # Add the frequency above each bar
    for i in range(len(n)):
        if n[i] > 0:  # Only annotate if there's at least one count in the bin
            bar_center = (bins[i] + bins[i+1]) / 2
            bar_height = n[i]
            plt.text(bar_center, bar_height, str(int(bar_height)),
                     ha='center', va='bottom')  # ha='center' aligns horizontally
    plt.title("Histogram of Flight Load")
    plt.xlabel("Load")
    plt.ylabel("Frequency")
    plt.show()

def passenger_book_rate(reader):
    T = 0.0
    passenger_book_rate_per_hour_map = {}
    for row in reader:
        if row["event_type"] == "passengerbook":
            hour = rounded_down_hour(float(row["time"]))
            if hour not in passenger_book_rate_per_hour_map:
                passenger_book_rate_per_hour_map[hour] = 0
            passenger_book_rate_per_hour_map[hour] += 1
            T = max(T, hour)

    plot_throughput_histogram(passenger_book_rate_per_hour_map)

    return sum(passenger_book_rate_per_hour_map.values()) / T 

def get_charge_information(aircraft_map, reader):
    all_charge_times = []

    for row in reader:
        if row["event_type"] == "chargeevent":
            data = row["data"]
            aircraft_id = int(data.split(" ")[0])
            charge_time = float(data.split(" ")[1])
            aircraft_map[aircraft_id].setdefault("charge_event", []).append(charge_time)
            all_charge_times.append(charge_time)

    for aircraft_id in aircraft_map:
        total_charge_time = np.sum(aircraft_map[aircraft_id]["charge_event"])
        mean_charge_time = np.mean(aircraft_map[aircraft_id]["charge_event"])
        std_charge_time = np.std(aircraft_map[aircraft_id]["charge_event"])

        print(f"Total Charge Time For Aircraft {aircraft_id}: {total_charge_time}")
        print(f"Mean Charge Time For Aircraft {aircraft_id}: {mean_charge_time}")
        print(f"Std Charge Time For Aircraft {aircraft_id}: {std_charge_time}")


    total_charge_time = np.sum(all_charge_times)
    mean_charge_time = np.mean(all_charge_times)
    std_charge_time = np.std(all_charge_times)

    print(f"Total Charge Time For All Aircraft: {total_charge_time}")
    print(f"Mean Charge Time For All Aircraft: {mean_charge_time}")
    print(f"Std Charge Time For All Aircraft: {std_charge_time}")


    return total_charge_time, mean_charge_time, std_charge_time

class AIRCRAFT_STATE(Enum):
    STATIONARY = 0,
    FLIGHT = 1,
    CHARGING = 2


def compute_state_proportions_per_cycle(aircraft_data):
    timeline = sorted(aircraft_data["timeline"], key=lambda x: x[0])
    
    flight_starts = []
    for i in range(len(timeline) - 1):
        if timeline[i][1] == AIRCRAFT_STATE.FLIGHT:
            flight_starts.append(timeline[i][0])

    results = []
    
    for idx in range(len(flight_starts) - 1):
        cycle_start = flight_starts[idx]
        cycle_end   = flight_starts[idx+1]
        
        state_durations = {
            AIRCRAFT_STATE.STATIONARY: 0,
            AIRCRAFT_STATE.FLIGHT: 0,
            AIRCRAFT_STATE.CHARGING: 0
        }

        for i in range(len(timeline) - 1):
            t_start, state_start = timeline[i]
            t_end,   _          = timeline[i+1]

            if t_end <= cycle_start or t_start >= cycle_end:
                continue

            overlap_start = max(t_start, cycle_start)
            overlap_end   = min(t_end, cycle_end)
            duration      = overlap_end - overlap_start

            state_durations[state_start] += duration

        cycle_duration = cycle_end - cycle_start
        
        cycle_proportions = {
            st.name: state_durations[st] / cycle_duration
            for st in state_durations
        }
        
        results.append({
            "start_of_flight": cycle_start,
            "end_of_flight": cycle_end,
            "proportions": cycle_proportions
        })

    overall_proportions = {
        AIRCRAFT_STATE.STATIONARY.name: 0,
        AIRCRAFT_STATE.FLIGHT.name:    0,
        AIRCRAFT_STATE.CHARGING.name:  0
    }

    num_cycles = len(results)
    if num_cycles > 0:
        for r in results:
            for state_name, prop in r["proportions"].items():
                overall_proportions[state_name] += prop
        
        for state_name in overall_proportions:
            overall_proportions[state_name] /= num_cycles


    return  {
        "cycles": num_cycles,
        "per_cycle": results,
        "average_proportions": overall_proportions
    }

import collections

def calculate_state_proportions(aircraft_map):
    all_aircraft_total = collections.Counter()
    total_cycles_across_fleet = 0

    for aircraft_id, aircraft_data in aircraft_map.items():
        results = compute_state_proportions_per_cycle(aircraft_data)
        print(f"Aircraft {aircraft_id} State Proportions:")
        for cycle in results["per_cycle"]: 
            print(cycle)
            pass

        print(f"Number of Cycles: {results['cycles']}")
        print(f"Average Proportions: {results['average_proportions']}")

        cycles_for_this_aircraft = results["cycles"]
        total_cycles_across_fleet += cycles_for_this_aircraft
        for state_name, proportion in results["average_proportions"].items():
            all_aircraft_total[state_name] += proportion * cycles_for_this_aircraft

    if total_cycles_across_fleet > 0:
        fleet_wide_avg = {
            state_name: (all_aircraft_total[state_name] / total_cycles_across_fleet)
            for state_name in all_aircraft_total
        }
    else:
        fleet_wide_avg = {}

    print("\n--- Fleet-Wide Average Proportions ---")
    print(fleet_wide_avg)

    
def plot_aircraft_gantt(aircraft_map):
    all_intervals = []
    base_date = datetime.today() + timedelta(hours=7)

    route_i = 0
    for aircraft_id, aircraft_data in aircraft_map.items():
        timeline = aircraft_data["timeline"]
        timeline.sort(key=lambda x: x[0])

        for i in range(len(timeline) - 1):
            start_time, start_state = timeline[i]
            end_time, _ = timeline [i+1]
            if abs(end_time - start_time) > 1:
                start_dt = base_date + timedelta(minutes=start_time)
                end_dt = base_date + timedelta(minutes=end_time)
                if start_state == AIRCRAFT_STATE.CHARGING:
                    all_intervals.append(dict(
                        Task=f"Aircraft {aircraft_id}",
                        Start=start_dt,
                        Finish=end_dt,
                        State=start_state,
                        Departure=None,
                        Arrival=None,
                    ))
                elif start_state == AIRCRAFT_STATE.FLIGHT:
                    all_intervals.append(dict(
                        Task=f"Aircraft {aircraft_id}",
                        Start=start_dt,
                        Finish=end_dt,
                        State=start_state,
                        Departure=aircraft_data["route"][str(aircraft_id) + "/" + str(start_time)][0],
                        Arrival=aircraft_data["route"][str(aircraft_id) + "/" + str(start_time)][1],
                    ))
                    route_i += 1


    df = pd.DataFrame(all_intervals)
    fig = px.timeline(
        df,
        x_start="Start",
        x_end="Finish",
        y="Task",
        color="State",
        hover_data=["Departure", "Arrival"],
    )

    # Reverse the Y-axis so tasks (aircraft) list top-down
    fig.update_yaxes(autorange="reversed")

    fig.update_layout(
        title="Aircraft Timelines",
        xaxis_title="Time",
        yaxis_title="Aircraft"
    )

    # Display the figure
    fig.show()

def create_timelines(aircraft_map, reader):
    for row in reader:
        if row["event_type"] == "aircraftdeparture":
            data = row["data"]
            aircraft_id = int(data.split(" ")[0])
            departure_loc = data.split(" ")[1]
            arrival_loc = data.split(" ")[2]
            aircraft_map[aircraft_id].setdefault("timeline", []).append((float(row["time"]), AIRCRAFT_STATE.FLIGHT))
            aircraft_map[aircraft_id].setdefault("route", {})[str(aircraft_id) + "/" + str(row["time"])] = (departure_loc, arrival_loc)
        elif row["event_type"] == "aircraftarrival":
            data = row["data"]
            aircraft_id = int(data.split(" ")[0])
            aircraft_map[aircraft_id].setdefault("timeline", []).append((float(row["time"]), AIRCRAFT_STATE.STATIONARY))
        elif row["event_type"] == "chargeevent":
            data = row["data"]
            aircraft_id = int(data.split(" ")[0])
            charge_time = float(data.split(" ")[1])
            aircraft_map[aircraft_id].setdefault("timeline", []).append((float(row["time"]) - charge_time, AIRCRAFT_STATE.CHARGING))
            aircraft_map[aircraft_id]["timeline"].append((float(row["time"]), AIRCRAFT_STATE.STATIONARY))
        
    for aircraft_id in aircraft_map:
        aircraft_map[aircraft_id]["timeline"].sort(key=lambda x: x[0])
        print(f"Timeline for Aircraft {aircraft_id}:")
        for time, state in aircraft_map[aircraft_id]["timeline"]:
            print(f"\tTime: {time}, State: {state}")
        print()

    calculate_state_proportions(aircraft_map)
    plot_aircraft_gantt(aircraft_map)

def per_aircraft_statistics(file, reader):
    aircraft_map = {}
    for row in reader:
        if row["event_type"] == "aircraftinit":
            aircraft_map[int(row["join_id"])] = {}

    file.seek(0)

    get_charge_information(aircraft_map, reader)
    file.seek(0)

    create_timelines(aircraft_map, reader)
    file.seek(0)

def parse_csv(filename):
    with open(filename, mode='r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)

        # Latency
        average_latency, N = calculate_average_latency(reader)
        print(f"Average Latency: {average_latency}, Total Number of Passengers: {N}")
        csvfile.seek(0)

        # Throughput
        average_throughput = calculate_average_throughput(reader)
        print(f"Average Throughput: {average_throughput} passengers/hour")
        csvfile.seek(0)

        # Passenger Book Rate
        average_passenger_book_rate = passenger_book_rate(reader)
        print(f"Passenger Book Rate: {average_passenger_book_rate} passengers/hour")
        csvfile.seek(0)

        per_aircraft_statistics(csvfile, reader)
        csvfile.seek(0)

        average_flight_load(reader)


def get_log_file_path():
    i = 0
    while True:
        candidate = f"logged_events_{i}.csv"
        if not os.path.exists(candidate):
            return f"logged_events_{i-1}.csv"
        i += 1

if __name__ == "__main__":
    print("Data Collector")
    filename = get_log_file_path()
    print(f"Log file path: {filename}")
    parse_csv(filename)
