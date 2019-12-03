import math
import sys

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

    print("# Part 1")

    # part 1 self-test
    for test in [
            [    12,     2],
            [    14,     2],
            [  1969,   654],
            [100756, 33583],
        ]:
        mass = test[0]
        expected_fuel = test[1]
        calculated_fuel = fuel_for_module(mass, include_fuel_cost=False)
        if calculated_fuel != expected_fuel:
            print("Calculated fuel for mass {} = {}. Expected = {}".format(mass, calculated_fuel, expected_fuel))
            sys.exit(1)

    with open('./day1/input') as input:
        fuel = 0
        for line in input.readlines():
            mass = int(line)
            fuel += fuel_for_module(mass, include_fuel_cost=False)
    
    print("Total Fuel = {}\n".format(fuel))

    print("# Part 2")

    # part 2 self-test
    for test in [
            [    12,     2],
            [    14,     2],
            [  1969,   966],
            [100756, 50346],
        ]:
        mass = test[0]
        expected_fuel = test[1]
        calculated_fuel = fuel_for_module(mass, include_fuel_cost=True)
        if calculated_fuel != expected_fuel:
            print("Calculated fuel for mass {} = {}. Expected = {}".format(mass, calculated_fuel, expected_fuel))
            sys.exit(1)

    with open('./day1/input') as input:
        fuel = 0
        for line in input.readlines():
            mass = int(line)
            fuel += fuel_for_module(mass, include_fuel_cost=True)
    
    print("Total Fuel = {}\n".format(fuel))
