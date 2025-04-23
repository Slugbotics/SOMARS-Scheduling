import pandas as pd
import numpy as np
import os
import argparse

def get_log_file_path():
    i = 0
    while True:
        candidate = f"logged_events_{i}.csv"
        if not os.path.exists(candidate):
            return f"logged_events_{i-1}.csv"
        i += 1


def main(datafolder):
    capex_df = pd.read_csv(datafolder + "capex.csv")
    opex_df = pd.read_csv(datafolder + "opex.csv")
    revenue_df = pd.read_csv(datafolder + "revenue.csv")
    log_df = pd.read_csv(get_log_file_path())

    # Depreciation
    capex_df["annual_depreciation"] = capex_df["cost"] / capex_df["useful_life"]

    # Sum total depreciation per year
    total_depreciation_year = capex_df["annual_depreciation"].sum()

    # (B) OPEX (annual “fixed” costs vs per-flight or per-aircraft costs)
    # We’ll separate OPEX items into:
    #   1) Fixed annual (like overhead, training, etc.)
    #   2) Per-aircraft-per-year (maintenance, insurance, etc.)
    #   3) Per-flight
    #   4) Variable by usage (energy cost in $/kWh)
    #   5) Taxes in fraction of net income (0.11)

    # Put them into a dictionary for easy reference:
    opex_dict = {}
    for idx, row in opex_df.iterrows():
        item = row["item"]
        cost = row["cost"]
        unit = row["unit"]
        opex_dict[item] = (cost, unit)

    # Just for quick reference:
    annual_fixed_costs = [
        "pilot_training",        # $20,000 / year (but in reality depends on # pilots)
        "general_and_adminstrative",
        "sales_and_marketing",
        "legal_and_compliance",
        "software_and_systems",
        "spare_parts"
    ]
    # We can sum these as a single line item for simplicity:
    annual_fixed_opex = sum(
        opex_dict[item][0] for item in annual_fixed_costs
    )

    num_pilots = 5
    num_flight_ops = 2
    num_ground_ops = 3

    pilot_salary_annual = opex_dict["pilot_salary"][0] * num_pilots
    flight_ops_annual = opex_dict["flight_operations_salary"][0] * num_flight_ops
    ground_ops_annual = opex_dict["ground_operations_salary"][0] * num_ground_ops

    maintenance_annual = opex_dict["maintenance"][0] * num_aircraft
    insurance_annual   = opex_dict["insurance"][0]   * num_aircraft

    landing_fee_per_flight = opex_dict["landing_fees"][0]
    kwh_rate = opex_dict["energy_cost"][0]

    tax_rate = opex_dict["taxes"][0]

    # flight data structure: each row is a dictionary:
    # {
    #   "time": float,
    #   "aircraft_id": str,
    #   "src": str,
    #   "dest": str,
    #   "flight_time_minutes": float,
    #   "distance_miles": float,
    #   "passenger_count": int,
    #   "ticket_price": float,
    #   "flight_revenue": float,
    #   "energy_consumed_kwh": float,
    #   "energy_cost": float,
    #   "landing_fee": float
    # }
    flights = []

    def get_ticket_price(src, dest):
        """
        Return ticket_price if route is in revenue_df, else None
        """
        row = revenue_df.loc[(revenue_df["src"] == src) & (revenue_df["dest"] == dest)]
        if not row.empty:
            return float(row["ticket_price"].values[0])
        else:
            return 0.0  # fallback if no match

    for idx, row in log_df.iterrows():
        event_type = row["event_type"]
        data_str = row["data"]
        
        if event_type == "aircraftdeparture":
            splitted = data_str.split()
            if len(splitted) == 6:
                plane_id = splitted[0]
                src = splitted[1]
                dest = splitted[2]
                flight_time_minutes = float(splitted[3])
                passenger_count = int(splitted[5])
                
                # Find ticket price from CSV
                ticket_price = get_ticket_price(src, dest)
                
                # Flight revenue = (ticket_price * passenger_count)
                flight_revenue = ticket_price * passenger_count

                # Assume 1 kWh per mile (placeholder assumption!)
                flight_energy_cost  = energy_consumed_kwh * kwh_rate
                
                flight_dict = {
                    "time": row["time"],
                    "aircraft_id": plane_id,
                    "src": src,
                    "dest": dest,
                    "flight_time_minutes": flight_time_minutes,
                    "passenger_count": passenger_count,
                    "ticket_price": ticket_price,
                    "flight_revenue": flight_revenue,
                    "energy_cost": flight_energy_cost,
                    "landing_fee": landing_fee_per_flight
                }
                
                flights.append(flight_dict)

    flights_df = pd.DataFrame(flights)

    # Aggregate flight-level statistics
    total_flights        = len(flights_df)
    total_passengers     = flights_df["passenger_count"].sum()
    total_distance       = flights_df["distance_miles"].sum()
    total_energy_kwh     = flights_df["energy_consumed_kwh"].sum()
    total_energy_cost    = flights_df["energy_cost"].sum()
    total_landing_fees   = flights_df["landing_fee"].sum()
    total_flight_revenue = flights_df["flight_revenue"].sum()

    # ------------------------------------------------------------------------------
    # 4. UNIT ECONOMICS
    # ------------------------------------------------------------------------------
    # Basic examples:
    cost_per_flight    = (total_energy_cost + total_landing_fees) / total_flights if total_flights > 0 else 0
    cost_per_passenger = (total_energy_cost + total_landing_fees) / total_passengers if total_passengers > 0 else 0
    revenue_per_flight = total_flight_revenue / total_flights if total_flights > 0 else 0
    revenue_per_passenger = total_flight_revenue / total_passengers if total_passengers > 0 else 0

    print("=== UNIT ECONOMICS ===")
    print(f"Total Flights: {total_flights}")
    print(f"Total Passengers: {total_passengers}")
    print(f"Cost per Flight (energy + landing): ${cost_per_flight:,.2f}")
    print(f"Cost per Passenger (energy + landing): ${cost_per_passenger:,.2f}")
    print(f"Revenue per Flight: ${revenue_per_flight:,.2f}")
    print(f"Revenue per Passenger: ${revenue_per_passenger:,.2f}")
    print("----------------------------------------------------\n")

    # ------------------------------------------------------------------------------
    # 5. DAILY ECONOMICS
    # ------------------------------------------------------------------------------
    # We'll look at the simulation time from min->max in the log to see how many minutes 
    # of operation are represented, then extrapolate to 1 day (1440 minutes).
    simulation_start = log_df["time"].min()
    simulation_end   = log_df["time"].max()
    simulation_minutes = simulation_end - simulation_start

    if simulation_minutes <= 0:
        # fallback if the log is empty or zero
        simulation_minutes = 1

    # Scale up flight revenue & costs to a 24-hour day.
    minutes_per_day = 24 * 60
    scaling_factor = minutes_per_day / simulation_minutes

    daily_revenue = total_flight_revenue * scaling_factor
    daily_energy_cost = total_energy_cost * scaling_factor
    daily_landing_fees = total_landing_fees * scaling_factor

    print("=== DAILY ECONOMICS (Extrapolated) ===")
    print(f"Simulation length: {simulation_minutes:.2f} minutes")
    print(f"Scaling factor to 24h: {scaling_factor:.2f}")
    print(f"Daily Flight Revenue: ${daily_revenue:,.2f}")
    print(f"Daily Energy Cost: ${daily_energy_cost:,.2f}")
    print(f"Daily Landing Fees: ${daily_landing_fees:,.2f}")
    print("----------------------------------------------------\n")

    # ------------------------------------------------------------------------------
    # 6. ANNUAL INCOME STATEMENT (Illustrative)
    # ------------------------------------------------------------------------------
    # We’ll assume the daily pattern repeats ~365 days/year. 
    # Then incorporate overhead OPEX, pilot salaries, depreciation, taxes, etc.

    days_per_year = 365
    annual_flight_revenue = daily_revenue * days_per_year
    annual_flight_energy_cost = daily_energy_cost * days_per_year
    annual_landing_fees = daily_landing_fees * days_per_year

    # Combine the “fixed” overhead OPEX and the per-aircraft OPEX
    annual_labor_costs = pilot_salary_annual + flight_ops_annual + ground_ops_annual
    annual_per_aircraft_costs = maintenance_annual + insurance_annual
    annual_fixed_overhead = annual_fixed_opex

    # Sum all operating costs except depreciation:
    #   - flight-driven costs: energy + landing
    #   - labor costs
    #   - overhead
    #   - per-aircraft costs
    operating_costs_before_depr = (
        annual_flight_energy_cost
        + annual_landing_fees
        + annual_labor_costs
        + annual_per_aircraft_costs
        + annual_fixed_overhead
    )

    # EBIT (Earnings before Interest & Taxes, ignoring interest for simplicity)
    ebit = annual_flight_revenue - operating_costs_before_depr - total_depreciation_year

    # Apply taxes on net income:
    # net_income = (ebit - interest) * (1 - tax_rate), but we skip interest for now
    taxable_income = ebit if ebit > 0 else 0  # if negative, no taxes
    taxes_paid = taxable_income * tax_rate
    net_income = ebit - taxes_paid

    print("=== ANNUAL INCOME STATEMENT (Approx) ===")

    print(f"Revenue                       : ${annual_flight_revenue:,.0f}")
    print(f"Operating Costs (no Depr)     : ${operating_costs_before_depr:,.0f}")
    print(f"   of which Energy            : ${annual_flight_energy_cost:,.0f}")
    print(f"   of which Landing Fees      : ${annual_landing_fees:,.0f}")
    print(f"   of which Labor (Pilots, Ops): ${annual_labor_costs:,.0f}")
    print(f"   of which Maintenance+Insur : ${annual_per_aircraft_costs:,.0f}")
    print(f"   of which Overhead (G&A,etc): ${annual_fixed_overhead:,.0f}")
    print(f"Depreciation                  : ${total_depreciation_year:,.0f}")

    ebit_str = f"${ebit:,.0f}"
    print(f"EBIT                          : {ebit_str}")

    taxes_str = f"${taxes_paid:,.0f}"
    print(f"Taxes                         : {taxes_str}")

    net_income_str = f"${net_income:,.0f}"
    print(f"Net Income                    : {net_income_str}")

    print("----------------------------------------------------")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Dynamic Scheduling Simulation",
        description="Script to process flight time and a folder containing data."
    )

    parser.add_argument(
        "--data-folder",
        type=str,
        default="../data/example_1/",
        help="Path to the folder that contains your data."
    )

    # Parse the arguments from the command line
    args = parser.parse_args()

    data_folder = args.data_folder
    print(f"Data folder location: {data_folder}")
    main(data_folder)
