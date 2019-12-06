
class Orbit(object):
    def __init__(self, center, orbiter):
        self.center = center
        self.orbiter = orbiter
    
    def __repr__(self):
        return "{}){}".format(self.center, self.orbiter)


def get_orbital_chain(orbits, orbiter, stop='COM'):
    if orbiter == stop:
        return []

    parent = None
    for o in orbits:
        if o.orbiter == orbiter:
            parent = o.center
            break
    
    if parent is None:
        raise Exception('Traversal error: Chain broken? Parent not found for: {}'.format(orbiter))

    return [parent] + get_orbital_chain(orbits, parent)


def parse_orbits(lines):
    return [Orbit(c,o) for c,o in list(map(lambda l: l.strip().split(')'), lines)) ]


def get_checksum(lines):
    orbits = parse_orbits(lines)
    return sum(len(get_orbital_chain(orbits, o.orbiter)) for o in orbits)


def get_jumps(lines, src='YOU', dst='SAN'):
    orbits = parse_orbits(lines)
    src_path = get_orbital_chain(orbits, src)
    dst_path = get_orbital_chain(orbits, dst)
    fork = next(filter(lambda p: p in dst_path, src_path))
    return src_path.index(fork) + dst_path.index(fork)


if __name__ == '__main__':

    # test run
    with open('./day6/test1') as input:
        checksum = get_checksum( input.readlines() )
        # print(checksum)
        assert checksum is 42

    with open('./day6/input') as input:
        checksum = get_checksum( input.readlines() )
        print("Part 1: Checksum = {}".format(checksum))

    # Part 2 
    # test run
    with open('./day6/test2') as input:
        jumps = get_jumps( input.readlines() )
        # print(jumps)
        assert jumps is 4

    with open('./day6/input') as input:
        jumps = get_jumps( input.readlines() )
        print("Part 2: Jumps = {}".format(jumps))

