import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from shared.coord import Coord


def get_asteroids(map_data):
    rows = len(map_data)
    cols = len(map_data[0])
    asteroids = set()

    for y in range(rows):
        for x in range(cols):
            if map_data[y][x] == '#':
                asteroids.add(Coord(x,y))  # X,Y -> X is dist from left

    return asteroids, rows, cols


def rotary_laser_hits(raw_map, station, debug=False):
    map_data = list(filter(lambda s: len(s) != 0, map(lambda s: s.strip(), raw_map.splitlines())))
    asteroids, rows, cols = get_asteroids(map_data)

    destroyed = []
    # rotation = 0  # start at Due North

    while len(destroyed) < len(asteroids) - 1:
        remaining = asteroids - set(destroyed)
        seen, _ = observe(remaining, station)
        ordered = sorted(
            map(
                lambda s: (s.theta(station), s),
                seen),
            key = lambda ts: ts[0]
        )
        if debug:
            # print(*ordered[:9], sep='\n')
            hits = dict(
                list(
                    map(lambda ts: (ts[1], ordered.index(ts)+1), ordered)
                )
            )
            debug_map(
                rows, cols,
                remaining,
                hits,
                station
            )
            print()
        destroyed.extend(map(lambda ts: ts[1], ordered))

    if debug:
        print(destroyed[:10])

    return destroyed


def observe(asteroids, station):
    seen = set()
    blocked = set()
    for b in asteroids:
        if station == b:
            continue

        # is b visible from a?
        visible = True
        for c in asteroids:
            if c == station or c == b:
                continue

            if c.onLine(station, b):
                blocked.add((station,c,b))
                visible = False
                break  # for c
        
        if visible:
            seen.add(b)

    return seen, blocked


def debug_map(rows, cols, asteroids, hits, station):
    marks = []
    for y in range(rows):
        row__ = ""
        for x in range(cols):
            pos = Coord(x, y)
            if pos in asteroids:
                if pos in hits:
                    try:
                        # access as a dict
                        row__ += str(hits[pos])[-1]
                    except:
                        # access as list
                        row__ += "o"

                elif pos == station:
                    row__ += "@"
                else:
                    # erm ..
                    row__ += "#"
            else:
                row__ += '.'
        marks.append(row__)

    print('\n'.join(marks))


def process_map(raw_map, debug=False):
    map_data = list(filter(lambda s: len(s) != 0, map(lambda s: s.strip(), raw_map.splitlines())))
    asteroids, rows, cols = get_asteroids(map_data)

    scores = {}
    for a in asteroids:
        seen, blocked = observe(asteroids, a)
        scores[a] = (len(seen), seen, blocked)
    
    maxScore = max(score for score, _, _ in scores.values())
    bestSpots = [k for k,v in scores.items() if v[0] == maxScore]

    if debug:
        hits = scores[bestSpots[0]][1]
        blocks = scores[bestSpots[0]][2]
        debug_map(rows, cols, asteroids, hits, bestSpots[0])

        for b in blocks:
            print(b)

        print(bestSpots, maxScore)

    # return best position, score
    return bestSpots[0], maxScore


def run_tests():    
    maps = [
    ("""
    .#..#
    .....
    #####
    ....#
    ...##
    """, Coord(3,4), 8),
    ("""
    ......#.#.
    #..#.#....
    ..#######.
    .#.#.###..
    .#..#.....
    ..#....#.#
    #..#....#.
    .##.#..###
    ##...#..#.
    .#....####
    """, Coord(5,8), 33),
    ("""
    #.#...#.#.
    .###....#.
    .#....#...
    ##.#.#.#.#
    ....#.#.#.
    .##..###.#
    ..#...##..
    ..##....##
    ......#...
    .####.###.
    """, Coord(1,2), 35),
    ("""
    .#..#..###
    ####.###.#
    ....###.#.
    ..###.##.#
    ##.##.#.#.
    ....###..#
    ..#.#..#.#
    #..#.#.###
    .##...##.#
    .....#.#..
    """, Coord(6,3), 41),
    ("""
    .#..##.###...#######
    ##.############..##.
    .#.######.########.#
    .###.#######.####.#.
    #####.##.#.##.###.##
    ..#####..#.#########
    ####################
    #.####....###.#.#.##
    ##.#################
    #####.##.###..####..
    ..######..##.#######
    ####.##.####...##..#
    .#####..#.######.###
    ##...#.##########...
    #.##########.#######
    .####.#.###.###.#.##
    ....##.##.###..#####
    .#.#.###########.###
    #.#.#.#####.####.###
    ###.##.####.##.#..##
    """, Coord(11,13), 210)
    ]

    # part 1

    for m, c, s in maps:
        c_, s_ = process_map(m)
        if c_ != c and s_ != s:
            print("TEST ERROR: Expected @{c} ({s}); Got: @{c_} ({s_})".format(**locals()))
            sys.exit(1)


    # part 2

    print("\nTest Pattern #1")

    test_map = """
    ...............
    ...#...#...#...
    ...............
    ...#...#...#...
    ...............
    ...#...#...#...
    ...............
    """

    rotary_laser_hits(test_map, Coord(7,3), debug=False)
    # sys.exit(1)

    test_map = """
    ...............
    ...#########...
    ...#.......#...
    ...#...#...#...
    ...#.......#...
    ...#########...
    ...............
    """

    rotary_laser_hits(test_map, Coord(7,3), debug=False)

    test_map = """
    ###############
    #..#########..#
    #..#.......#..#
    #..#...#...#..#
    #..#.......#..#
    #..#########..#
    ###############
    """

    rotary_laser_hits(test_map, Coord(7,3), debug=False)
    # sys.exit(1)

    print("\nTest Pattern #2")

    test_map = """
    .#....#####...#..
    ##...##.#####..##
    ##...#...#.#####.
    ..#.....#...###..
    ..#.#.....#....##
    """

    rotary_laser_hits(test_map, Coord(8,3), debug=False)

    print("\nTest Pattern #3")

    test_map = maps[4]
    test_hits = {
        1: Coord(11, 12),
        2: Coord(12, 1),
        3: Coord(12, 2),
        10: Coord(12, 8),
        20: Coord(16, 0),
        50: Coord(16, 9),
        100: Coord(10, 16),
        199: Coord(9, 6),
        200: Coord(8, 2),
        201: Coord(10, 9),
        299: Coord(11, 1)
    }
    hits = rotary_laser_hits(test_map[0], test_map[1], debug=False)
    for index, test_hit in test_hits.items():
        if hits[index - 1] != test_hit:
            print("TEST ERROR: Expected Hit #{} is {}, found: {}".format(index, test_hit, hits[index]))
            sys.exit(1)


if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1] == '-t':
        print("Running tests..")
        run_tests()
        print("All tests PASSED.")
        sys.exit(0)

    print("Reading input..")
    with open('./day10/input') as input:
        m = '\n'.join(input.readlines())

    station, s = process_map(m)
    print("Best Location: @{c}, Score: {s}".format(c=station, s=s))

    hits = rotary_laser_hits(m, station)
    print("200th hit is: {}".format(hits[200-1]))