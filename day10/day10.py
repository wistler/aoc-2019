import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from shared.coord import Coord


def process_map(map_, debug=False):
    map__ = list(filter(lambda s: len(s) != 0, map(lambda s: s.strip(), map_.splitlines())))
    
    rows = len(map__)
    cols = len(map__[0])
    asteroids = set()
    scores = {}

    for r in range(rows):
        for c in range(cols):
            if map__[r][c] == '#':
                asteroids.add(Coord(r,c))
    
    for a in asteroids:
        score = 0
        seen = set()
        blocked = []
        for b in asteroids:
            if a is b:
                continue

            # is b visible from a?
            visible = True
            for c in asteroids:
                if c is a or c is b:
                    continue

                if c.onLine(a, b):
                    blocked.append((a,c,b))
                    visible = False
                    break  # for c
            
            if visible:
                seen.add(b)
                score += 1

        scores[a] = (score, seen, blocked)
    
    maxScore = max(score for score, _, _ in scores.values())
    bestSpots = [k for k,v in scores.items() if v[0] == maxScore]

    if debug:
        hits = scores[bestSpots[0]][1]
        blocks = scores[bestSpots[0]][2]
        marks = []
        for r in range(rows):
            row__ = ""
            for c in range(cols):
                if map__[r][c] == '#':
                    pos = Coord(r,c)
                    if pos in hits:
                        row__ += "o"
                    elif pos == bestSpots[0]:
                        row__ += "@"
                    else:
                        row__ += "x"
                else:
                    row__ += '.'
            marks.append(row__)

        print('\n'.join(marks))

        for b in blocks:
            print(b)

        print(bestSpots, maxScore)

    # return best position, score
    return bestSpots[0], maxScore


if __name__ == '__main__':
    
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

    for m, c, s in maps:
        c_, s_ = process_map(m)
        if c_ != c and s_ != s:
            print("TEST ERROR: Expected @{c} ({s}); Got: @{c_} ({s_})".format(**locals()))
            sys.exit(1)

    with open('./day10/input') as input:
        m = '\n'.join(input.readlines())

    c, s = process_map(m)
    print("Best Location: @{c}, Score: {s}".format(c=c, s=s))
