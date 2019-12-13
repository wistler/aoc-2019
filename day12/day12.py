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


class Moon(object):
    def __init__(self, pos, velocity):
        self.pos = pos
        self.vel = velocity
    
    def __str__(self):
        return 'pos={}, vel={}'.format(self.pos, self.vel)

    def energy(self):
        pot = self.pos.abs_sum()
        kin = self.vel.abs_sum()
        return pot * kin

def parse_vector(line):
    v = vector3.Vector3()
    for axis,value in map(lambda s: s.split('='), map(str.strip, line.lstrip('<').rstrip('>').split(','))):
        v[axis] = int(value)
    return v

def run_tests():

    m1 = Moon(pos=vector3.Vector3(1, 5, 10), velocity=vector3.Vector3())
    m2 = Moon(pos=vector3.Vector3(10, 5, 1), velocity=vector3.Vector3())
    moons = [m1, m2]
    simulation_step(1, moons, debug=True)
    print(*moons, sep='\n')
    assert m1.vel == vector3.Vector3(1, 0, -1)
    assert m1.pos == vector3.Vector3(2, 5, 9)
    assert m2.vel == vector3.Vector3(-1, 0, 1)
    assert m2.pos == vector3.Vector3(9, 5, 2)

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
    
