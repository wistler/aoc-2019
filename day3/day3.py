import math
import sys

class Coord(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
    
    def __repr__(self):
        return "[{},{}]".format(self.x, self.y)

    def __add__(self, other):
        return Coord(self.x + other.x, self.y + other.y)

    def manhattenDist(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y)

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.x == other.x and 
            self.y == other.y
        )
    
    def __hash__(self):
        return hash(self.x) * 3 + hash(self.y)


ORIGIN = Coord(0,0)
STEPPER = {
    'R': Coord(1, 0),
    'L': Coord(-1, 0),
    'U': Coord(0, 1),
    'D': Coord(0, -1)
}


def gen_path(chain, start=ORIGIN):
    pos = start
    path = []

    # path.append(pos) # Don't add origion

    for link in chain:
        dir = link[0]  # 'R','L','U' or 'D'
        dist = int(link[1:])

        if dir not in STEPPER.keys():
            raise Exception("Unknown Direction: {}".format(dir))

        stepper = STEPPER[dir] 

        for _ in range(dist):
            pos += stepper
            path.append(pos)

    return path


def find_closest_intersection(paths, ref=ORIGIN):
    points = None
    for path in paths:
        if points is None:
            points = set(path)
        else:
            points = points.intersection(set(path))

    minDist = None
    closest = None
    for p in points:
        dist = p.manhattenDist(ref)
        if minDist is None or dist < minDist:
            minDist = dist
            closest = p
    
    return {'intersection': closest, 'distance': minDist}


def find_shortest_intersection(paths, ref=ORIGIN):
    points = None
    for path in paths:
        if points is None:
            points = set(path)
        else:
            points = points.intersection(set(path))

    minSteps = None
    shortest = None
    for p in points:
        steps = 0
        for path in paths:
            # print("Segment: {}".format(path[:path.index(p)+1]))
            steps += path.index(p) + 1
         
        if minSteps is None or steps < minSteps:
            minSteps = steps
            shortest = p
    
    return {'intersection': shortest, 'steps': minSteps}



if __name__ == '__main__':

    # test runs
    s = set([Coord(1,1)]).intersection(set([Coord(1,1)]))
    if len(s) == 0:
        print("ERROR: Set Intersection not working")
        sys.exit(1)

    for test in [
            {
                "input": """U7,R6,D4,L4
                            R8,U5,L5,D3""",
                "dist": 6,
                "steps": 30
            },
            {
                "input": """R75,D30,R83,U83,L12,D49,R71,U7,L72
                            U62,R66,U55,R34,D71,R55,D58,R83""",
                "dist": 159,
                "steps": 610
            },
            {
                "input": """R98,U47,R26,D63,R33,U87,L62,D20,R33,U53,R51
                            U98,R91,D20,R16,D67,R40,U7,R15,U6,R7""",
                "dist": 135,
                "steps": 410
            },
        ]:
        lines = test["input"].splitlines()
        paths = [gen_path(line.strip().split(',')) for line in lines]
        closest = find_closest_intersection(paths)
        shortest = find_shortest_intersection(paths)
        
        if closest["distance"] != test["dist"]:
            print("Expected: {}, Calculated: {}".format(test["dist"], closest["distance"]))
            print("Input:{}".format(test["input"]))
            # for path in paths:
            #     print(path)
            sys.exit(1)
        
        if shortest["steps"] != test["steps"]:
            print("Expected: {}, Calculated: {}".format(test["steps"], shortest["steps"]))
            print("Input:{}\nPaths:".format(test["input"]))
            for path in paths:
                print(path)
            sys.exit(1)


    with open('./day3/input') as input:
        lines = input.readlines()
    
    paths = [gen_path(line.strip().split(',')) for line in lines]

    # Part 1
    closest = find_closest_intersection(paths)
    print("Closest Intersetction To Origin: {}".format(closest))

    # Part 2
    shortest = find_shortest_intersection(paths)
    print("Intersetction with shortest Path: {}".format(shortest))
