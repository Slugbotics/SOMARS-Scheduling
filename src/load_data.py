from models import Vertiport, Aircraft, PassengerDemand, TransportTime, GroundTransport
import csv, ast


def load_vertiports(filepath):
    vertiports = []
    with open(filepath, 'r') as f:
        # First line: number of vertiports
        n = int(f.readline().strip())

        # Next n lines: name, id, capacity
        for _ in range(n):
            line = f.readline().strip()
            name, id_str, capacity_str = line.split(',')
            v = Vertiport(
                id=int(id_str),
                name=name,
                capacity=int(capacity_str)
            )
            vertiports.append(v)
    return vertiports


def load_starting_state(filepath, battery):
    """
    Parses the 'starting_state.txt' file, which has the structure:

    1) First line: total number of aircraft (e.g., 15).
    2) Then repeated blocks of two kinds of lines:
       - First line of a block: 'VertiportName,number_of_aircraft_here'
       - Next 'number_of_aircraft_here' lines: 'aircraft_id,battery'

    Example:
        15
        SCZ,2
        1,4
        2,4
        MOF,4
        3,4
        4,4
        5,4
        6,4
        ...

    Returns:
        A list of Aircraft objects, each with:
          - id       (parsed from file)
          - bat_per  (parsed from file)
          - loc      (the vertiport name, e.g. "SCZ", "MOF", etc.)
    """
    aircraft_list = []

    with open(filepath, 'r') as f:
        # Read total aircraft (first line)
        total_aircraft = int(f.readline().strip())

        # Keep track of how many aircraft we've created so far
        created_count = 0

        # Read until we create all aircraft or hit EOF
        while created_count < total_aircraft:
            # Read a line with: vertiport_name, number_of_aircraft
            vert_line = f.readline().strip()
            if not vert_line:
                # We reached EOF or empty line prematurely
                break

            vert_name, vert_count_str = vert_line.split(',')
            vert_count = int(vert_count_str)

            # For each aircraft at this vertiport, read the next line
            for _ in range(vert_count):
                ac_line = f.readline().strip()
                ac_id_str, ac_capacity_str = ac_line.split(',')
                ac_id = int(ac_id_str)
                ac_capacity = int(ac_capacity_str)

                # Create an Aircraft object
                ac = Aircraft(id=ac_id, bat_per=battery,
                              capacity=ac_capacity, loc=vert_name)
                aircraft_list.append(ac)

            # Update the count of created aircraft
            created_count += vert_count

    return aircraft_list


def load_passenger_demand(csv_filename):
    """
    Reads the given CSV file and returns a list of PassengerDemand objects.

    The CSV file is expected to have three columns: 'src', 'dest', and 'hourlyPassengers',
    where the 'hourlyPassengers' column contains a string representation of a list (e.g. "[4,5,2,...]").
    The unit_time is calculated as 24 divided by the length of the demand list.
    """
    passenger_demands = []

    with open(csv_filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            src = row['src']
            dest = row['dest']
            # Convert the string representation of the list to an actual list
            demand = ast.literal_eval(row['hourlyPassengers'])
            # Calculate unit_time as 24 / (number of demand entries)
            if len(demand) > 0:
                unit_time = 24 / len(demand)
            else:
                unit_time = 0  # Alternatively, raise an error if you expect a non-empty list.

            pd_obj = PassengerDemand(src=src, dest=dest, unit_time=unit_time, demand=demand)
            passenger_demands.append(pd_obj)

    return passenger_demands


def load_transport_times(csv_filename):
    """
    Reads the given CSV file and returns a list of TransportTime objects.

    The CSV file is expected to have three columns: 'src', 'dest', and 'transportTime'.
    """
    transport_times = []

    with open(csv_filename, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            src = row['src']
            dest = row['dest']
            time = float(row['transportTime'])
            t_obj = TransportTime(src=src, dest=dest, time=time)
            transport_times.append(t_obj)

    return transport_times


def load_ground_transport(file_path):
    """Load ground transport data from a CSV file and return a list of GroundTransport objects."""
    ground_transports = []
    with open(file_path, newline='') as csvfile:
        # Use DictReader to parse header fields automatically
        reader = csv.DictReader(csvfile)
        for row in reader:
            loc = row['loc']
            # The dep_times field is a quoted string of comma-separated times.
            times = row['dep_times'].split(',')
            ground_transports.append(GroundTransport(loc, times))
    return ground_transports


if __name__ == "__main__":
    # Example usage:
    filepath = "../data/example_1/vertiport.txt"
    vertiport_list = load_vertiports(filepath)

    # Print out the loaded vertiports
    for vp in vertiport_list:
        print(f"ID: {vp.id}, Name: {vp.name}, Capacity: {vp.capacity}")

    # Example usage
    starting_state_file = "../data/example_1/starting_state.txt"
    all_aircraft = load_starting_state(starting_state_file, 90)

    # Print all aircraft for verification
    for a in all_aircraft:
        print(f"Aircraft ID={a.id}, Battery={a.bat_per}, Capacity={a.capacity}, Location={a.loc}")

    filename = '../data/example_1/passenger_demand.csv'
    demands = load_passenger_demand(filename)
    for demand in demands:
        print(demand)
#        demand.graph()

    filename = '../data/example_1/transport_time.csv'
    transports = load_transport_times(filename)
    for transport in transports:
        print(f"Src={transport.src}, Dest={transport.dest}, Time={transport.time}")

    file_path = '../data/example_1/ground_transport.csv'  # Replace with the path to your file
    transports = load_ground_transport(file_path)
    for t in transports:
        print(f"Location: {t.loc}")
        print("Departure times:")
        for time in t.times:
            print(f"  {time}")
