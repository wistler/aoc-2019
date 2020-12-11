import sys, os
import itertools

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from shared import vector3


def simulation_step(step_id, moons, debug=False):
    if debug:
        print('Sim Step #{}'.format(step_id))

    # apply gravity
    for moon1, moon2 in itertools.combinations(moons, 2):
        if debug:
            print('Analyzing Moons: {}, {}'.format(moons.index(moon1), moons.index(moon2)))

        for axis in vector3.Vector3.AXES:
            unit = vector3.Vector3.unit(axis)
            if debug:
                print('Unit vector for axis [{axis}] is: {unit}'.format(**locals()))

            inc, dec = None, None
            if moon1.pos[axis] < moon2.pos[axis]:
                inc, dec = moon1, moon2
            elif moon1.pos[axis] > moon2.pos[axis]:
                inc, dec = moon2, moon1

            if inc and dec:
                inc.vel += unit
                dec.vel -= unit
        
    # apply velocity
    for moon in moons:
        moon.pos += moon.vel        

def run_simulation(moons, steps, debug=False):
    if debug:
        print("After 0 steps:")
        print(*moons, sep='\n')
    for step in range(0, steps):
        step_id = step+1
        simulation_step(step_id, moons, debug=False)
        if debug:
            print("After {} steps:".format(step_id))
            print(*moons, sep='\n')


def run_simulation_2(moons, debug=False):
    if debug:
        print("After 0 steps:")
        print(*moons, sep='\n')
    step_id = 0
    initMoons = [m.clone() for m in moons]
    periods = vector3.ZERO.clone()
    while True:
        step_id = step_id+1
        simulation_step(step_id, moons, debug=False)
        moon_cycled = [
            {
                "i": i,
                "x": im.pos.x == nm.pos.x and im.vel.x == nm.vel.x,
                "y": im.pos.y == nm.pos.y and im.vel.y == nm.vel.y,
                "z": im.pos.z == nm.pos.z and im.vel.z == nm.vel.z,
            } for i, im, nm in zip(range(len(moons)), initMoons, moons)
        ]
        
        axis_cycled = { "x": True, "y": True, "z": True }
        for mc in moon_cycled:
            if debug:
                if mc["x"] and periods.x == 0:
                    print("Moon {} Axis {} cycled at step {}".format(mc["i"], "X", step_id))
                if mc["y"] and periods.y == 0:
                    print("Moon {} Axis {} cycled at step {}".format(mc["i"], "Y", step_id))
                if mc["z"] and periods.z == 0:
                    print("Moon {} Axis {} cycled at step {}".format(mc["i"], "Z", step_id))

            axis_cycled["x"] &= mc["x"]
            axis_cycled["y"] &= mc["y"]
            axis_cycled["z"] &= mc["z"]

        if axis_cycled["x"] and periods.x == 0:
            periods.x = step_id
            if debug:
                print("Global Axis {} cycled at step {}".format("X", step_id))

        if axis_cycled["y"] and periods.y == 0:
            periods.y = step_id
            if debug:
                print("Global Axis {} cycled at step {}".format("Y", step_id))

        if axis_cycled["z"] and periods.z == 0:
            periods.z = step_id
            if debug:
                print("Global Axis {} cycled at step {}".format("Z", step_id))

        # if debug:
        #     print("--- Periods: {}".format(periods))

        if periods.x and periods.y and periods.z:
            return periods


class Moon(object):
    def __init__(self, pos, velocity):
        self.pos = pos
        self.vel = velocity
        self.periods = vector3.ZERO.clone()
    
    def __str__(self):
        return 'pos={}, vel={}'.format(self.pos, self.vel)

    def energy(self):
        pot = self.pos.abs_sum()
        kin = self.vel.abs_sum()
        return pot * kin

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.pos == other.pos and 
            self.vel == other.vel
        )
    
    def __hash__(self):
        return hash(self.pos) * 3 + hash(self.vel)
    
    def clone(self):
        return Moon(self.pos.clone(), self.vel.clone())


def parse_vector(line):
    v = vector3.Vector3()
    for axis,value in map(lambda s: s.split('='), map(str.strip, line.lstrip('<').rstrip('>').split(','))):
        v[axis] = int(value)
    return v


def run_tests():
    m1 = Moon(pos=vector3.Vector3(1, 5, 10), velocity=vector3.Vector3())
    m2 = Moon(pos=vector3.Vector3(10, 5, 1), velocity=vector3.Vector3())
    moons = [m1, m2]
    simulation_step(1, moons, debug=False)
    print(*moons, sep='\n')
    assert m1.vel == vector3.Vector3(1, 0, -1)
    assert m1.pos == vector3.Vector3(2, 5, 9)
    assert m2.vel == vector3.Vector3(-1, 0, 1)
    assert m2.pos == vector3.Vector3(9, 5, 2)

    # Example 1
    print("Example 1:")
    data = """
    <x=-1, y=0, z=2>
    <x=2, y=-10, z=-7>
    <x=4, y=-8, z=8>
    <x=3, y=5, z=-1>
    """

    vectors = [parse_vector(line) for line in filter(len, map(str.strip, data.splitlines()))]
    moons = [Moon(pos, vector3.Vector3()) for pos in vectors]
    print("Parsed Moon Data:")
    print(*moons, sep='\n')
    run_simulation(moons, steps=10, debug=False)
    total_energy = sum(map(Moon.energy, moons))
    print("Sum of total energy: {}".format(total_energy))

    vectors = [parse_vector(line) for line in filter(len, map(str.strip, data.splitlines()))]
    moons = [Moon(pos, vector3.Vector3()) for pos in vectors]
    end_step = run_simulation_2(moons, debug=False)
    print("Step 2: Result is LCM of {}, {}, {}".format(end_step.x, end_step.y, end_step.z))

    # Example 2
    print("Example 2:")
    data = """
    <x=-8, y=-10, z=0>
    <x=5, y=5, z=10>
    <x=2, y=-7, z=3>
    <x=9, y=-8, z=-3>
    """
    vectors = [parse_vector(line) for line in filter(len, map(str.strip, data.splitlines()))]
    moons = [Moon(pos, vector3.Vector3()) for pos in vectors]
    end_step = run_simulation_2(moons, debug=False)
    print("Step 2: Result is LCM of {}, {}, {}".format(end_step.x, end_step.y, end_step.z))


if __name__ == '__main__':
    run_tests()
    print("# Part 1")

    with open('./day12/input') as input:
        vectors = [parse_vector(line) for line in filter(len, map(str.strip, input.readlines()))]
        moons = [Moon(pos, vector3.Vector3()) for pos in vectors]
        print("Parsed Moon Data:")
        print(*moons, sep='\n')
        run_simulation(moons, steps=1000, debug=False)
        print("Final Moon Data:")
        print(*moons, sep='\n')
        total_energy = sum(map(Moon.energy, moons))
        print("Sum of total energy: {}".format(total_energy))
    
    print("# Part 2")
    with open('./day12/input') as input:
        vectors = [parse_vector(line) for line in filter(len, map(str.strip, input.readlines()))]
        moons = [Moon(pos, vector3.Vector3()) for pos in vectors]
        periods = run_simulation_2(moons, debug=False)
        print("Step 2: Result is LCM of {}, {}, {}".format(periods.x, periods.y, periods.z))
    