#!/usr/bin/env python3
import csv, os
import matplotlib.pyplot as plt
import numpy as np
from enum import Enum

import plotly.express as px
import pandas as pd


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


import matplotlib.pyplot as plt
from datetime import datetime, timedelta


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
