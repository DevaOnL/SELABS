RATES = {"bike": 10, "car": 30, "truck": 60}

def minutes_parked(times):
    entry, exit_time = times.split('-')
    h1, m1 = entry.split(':')
    h2, m2 = exit_time.split(':')
    return (int(h2) * 60 + int(m2)) - (int(h1) * 60 + int(m1))

def hourly_rate(vehicle):
    return RATES[vehicle.strip().lower()]

def format_plate(plate):
    p = plate.upper()
    return p[0] + p[1] + " " + p[2:4] + " " + p[4:6] + " " + p[6:10]

def main():
    print("==== Running minutes_parked ====")
    user_input = input("Enter entry and exit time (e.g. 09:30-11:45): ")
    result = minutes_parked(user_input)
    print("Minutes Parked:", result)

    print("\n==== Running hourly_rate ====")
    user_input = input("Enter vehicle type (bike/car/truck): ")
    result = hourly_rate(user_input)
    print("Hourly Rate:", result)

    print("\n==== Running format_plate ====")
    user_input = input("Enter a number plate (e.g. ka01ab1234): ")
    result = format_plate(user_input)
    print("Formatted Plate:", result)

if __name__ == "__main__":
    main()
