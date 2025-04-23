distribution = {
    "SCZ": 8,
    "MOF": 36,
    "BER": 4,
    "MER": 11,
    "DAV": 16
}

import itertools

# Create a repeating pattern of 4,4,6 for 75 aircraft
capacities_pattern = [4,4,6]
pattern = list(itertools.islice(itertools.cycle(capacities_pattern), 75))

print(75)  # line 1: total number of aircraft

start_id = 1
for vertiport, count in distribution.items():
    print(f"{vertiport},{count}")  # e.g. SCZ,8
    for i in range(count):
        print(f"{start_id},{pattern[start_id-1]}")
        start_id += 1

