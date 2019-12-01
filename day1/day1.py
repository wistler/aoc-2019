import math

def fuel_for_module(mass, include_fuel_cost=True):
    if mass == 0:
        return 0
    else:
        fuel = max(0, math.floor( mass/3 ) - 2)
        fuel_cost = 0
        if include_fuel_cost:
            fuel_cost = fuel_for_module(fuel) 
        return fuel + fuel_cost


if __name__ == '__main__':

    for test in [12, 14, 1969, 100756]:
        print("Fuel for mass {} = {}".format(
                test, fuel_for_module(test, include_fuel_cost=True)
            ))

    with open('./day1/input') as input:
        fuel = 0
        for line in input.readlines():
            mass = int(line)
            fuel += fuel_for_module(mass, include_fuel_cost=True)
    
    print("Total Fuel = {}".format(fuel))
