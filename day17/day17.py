import sys, os, time, datetime, queue

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from shared.coord import Coord
from shared.intcode import intcode, Processor, Connector


GRID = {
    10: 'EOL',
    ord('.'): '.',
    ord('#'): '#',
    ord('^'): '^',
    ord('v'): 'v',
    ord('<'): '<',
    ord('>'): '>',
    ord('X'): 'X',
}


class Direction(object):
    def __init__(self, id, step):
        self.id = id
        self.step = step
    
    def __repr__(self):
        return self.id


DIRS = [
    Direction('^', Coord(0, -1)),
    Direction('>', Coord(1, 0)),
    Direction('v', Coord(0, 1)),
    Direction('<', Coord(-1, 0)),
]


def getTurns(facingDir):
    fdi = DIRS.index(facingDir)
    return {
        "R": DIRS[(fdi + 1) % len(DIRS)],
        "L": DIRS[(fdi - 1 + len(DIRS)) % len(DIRS)],
    }
     

def isBot(ch):
    return ch == '<' or ch == '^' or ch == '>' or ch == 'v'


def create_controller(code, debug=False):
    robot_inst = queue.Queue()
    camera_feed = [] # queue.Queue()
    controller = Processor('ascii', code,
        in_wire=robot_inst, out_wire=camera_feed, debug=debug)
    return (controller, robot_inst, camera_feed)


def create_unit_with_controller(code, debug=False):
    controller, robot_inst, camera_feed = create_controller(code, debug=debug)
    chips = { 'ascii': controller }
    wires = ()
    return (chips, wires, robot_inst, camera_feed)


def run_unit(unit, debug=False):
    (chips, wires, _, _) = unit

    for th in list(chips.values()) + list(wires):
        th.start()

    for th in list(chips.values()) + list(wires):
        if debug:
            print("WAITING ON: {}".format(th))
        th.join()
        if debug:
            print("TERMINATED: {}".format(th))
    

def print_grid(grid, droid_pos):
    # os.system('clear')
    xMin, xMax = None, None
    yMin, yMax = None, None
    for coord, _ in grid.items():
        x, y = coord.x, coord.y
        if xMin is None or xMin > x:
            xMin = x
        if xMax is None or xMax < x:
            xMax = x
        if yMin is None or yMin > y:
            yMin = y
        if yMax is None or yMax < y:
            yMax = y
    
    marks = []
    for y in range(yMin, yMax+1):
        row__ = ""
        for x in range(xMin, xMax+1):
            pos = Coord(x, y)
            ch = grid[pos]
            
            row__ += ch
        marks.append(row__)

    print('\n'.join(marks))


def nextDir(gr, pt, facingDir):
    opts = getTurns(facingDir)
    # print("nextDir", facingDir, opts)

    for k, v in opts.items():
        try:
            if gr[pt + v.step] == '#':
                return k, v
        except KeyError:
            # out of bounds ..
            pass
    
    raise Exception("Cannot find nextDir", pt, facingDir)


SEG_NAMES = ['A', 'B', 'C']
SEG_SIZE_MAX = 20


def factorizeSteps(steps, segments=None, debug=False):
    """
        returns (True, segments) or (False, None)
    """
    if not segments:
        segments = []

    if debug:
        print("factorize(): called with segments: \n\t ->{}"
                .format("\n\t ->".join("["+str(s)+"]" for s in segments)))

    mainFn = ",".join(steps)
    stepPos = 0
    while True:
        changed = False
        for s in range(len(segments)):
            segFn = ",".join(segments[s])
            mainFn = mainFn.replace(segFn, SEG_NAMES[s])

            # Avoid portions matched by previous segments..
            # Eg: A,A,...
            while ",".join(steps[stepPos:]).startswith(segFn):
                stepPos += len(segments[s])
                changed = True
        if not changed:
            break

    searchPos = 0
    while True:
        changed = False
        for s in range(len(segments)):
            while mainFn[searchPos:].startswith(SEG_NAMES[s]):
                searchPos += 2  # skip past "A," or "B," or "C,"
                changed = True
        if not changed:
            break

    if len(segments) == len(SEG_NAMES):
        if debug:
            print("factorize(): validating segment formation .. ")

        factorized = [
            mainFn,
            ','.join(segments[0]),
            ','.join(segments[1]),
            ','.join(segments[2]),
        ]

        remainingMainFn = mainFn
        for t in SEG_NAMES + [',']:
            remainingMainFn = remainingMainFn.replace(t, '')

        if len(remainingMainFn) != 0:
            return False, None

        if debug:
            print("factorize(): factorized segments: \n\t =>{}"
                    .format("\n\t =>".join("["+fs+"]" for fs in factorized)))

        for f in factorized:
            if len(f) > SEG_SIZE_MAX:
                return False, None

        if debug:
            print("factorize(): FOUND SOLUTION! \n\t ->{}"
                    .format("\n\t =>".join("["+fs+"]" for fs in factorized)))
        return True, factorized

    if debug:
        print("factorize(): main: {}\n\tsearchStr: {}".format(",".join(steps[stepPos:]), mainFn[searchPos:]))

    segOpts = []
    for i in range(stepPos+2, len(steps), 2):  # skip in pairs [R,5] or [L,6], etc
        seg = steps[stepPos:i]
        segFn = ",".join(seg)

        if len(segFn) > SEG_SIZE_MAX or not mainFn[searchPos:].startswith(segFn):
            # crossed the limits; not going to find anymore valid options.
            break

        count = mainFn[searchPos:].count(segFn)
        if count >= 1:
            segOpts.append(seg)

    if debug:
        print("factorize(): options: \n\t{}".format("\n\t".join(str(so) for so in segOpts)))

    for so in segOpts:
        valid, seg = factorizeSteps(steps, segments + [so], debug=debug)
        if valid:
            return True, seg
    
    # if we're in this loop, but haven't found any viable options, no path forward.
    return False, None


if __name__ == '__main__':
    print('Day 17')

    print("Reading input..")
    with open('./day17/input') as input:
        initMemory = [int(x) for x in input.readline().split(',')]

    feed = []
    intcode(initMemory, input=None, output=feed, debug=False)

    grid = dict()
    x, y = 0, 0
    X, Y = 0, 0
    for f in feed:
        ch = GRID[f]
        if ch == 'EOL':
            if y == 0:
                X = x
            
            y += 1
            x = 0
        else:
            pos = Coord(x, y)
            grid[pos] = ch
            x += 1
    Y = y-1

    print(X, Y)

    start = None
    intersections = []
    part1Ans = 0
    for y in range(0, Y):
        for x in range(0, X):
            o = Coord(x, y)

            if isBot(grid[o]):
                start = o

            border = x == 0 or y == 0 or x == X-1 or y == Y-1
            if not border:
                w = Coord(x-1, y)
                e = Coord(x+1, y)
                n = Coord(x, y-1)
                s = Coord(x, y+1)

                if grid[o] == '#' and \
                    grid[n] == '#' and \
                    grid[s] == '#' and \
                    grid[e] == '#' and \
                    grid[w] == '#':

                    intersections.append(o)
                    part1Ans += x*y


    if start is None:
        raise Exception("Start not found.")

    faceDir = None
    for d in DIRS:
        if d.id == grid[start]:
            faceDir = d
            break

    print(start, grid[start], faceDir)

    steps = []
    if faceDir is None:
        raise Exception("Direction not initialized.")


    pos = start
    try:
        while grid[pos] != '.':
            lr, nDir = nextDir(grid, pos, faceDir)
            steps.append(lr)
            faceDir = nDir
            move = 0
            try:
                while grid[pos+faceDir.step] == '#':
                    move += 1
                    pos += faceDir.step
            except KeyError:
                pass
            steps.append(str(move))
    except Exception:
        # End of the line
        pass

    for o in intersections:
        grid[o] = 'O'
    
    print_grid(grid, Coord(0,0))
    print("Part 1: Answer =", part1Ans)

    print(','.join(steps))
    valid, fs = factorizeSteps(steps)
    print("FactorizedSteps: {}, {}".format(valid, fs))

    with open('./day17/input') as input:
        initMemory = [int(x) for x in input.readline().split(',')]

    initMemory[0] = 2
    feed = []
    data = [ord(i) for i in fs[0] + '\n' + fs[1] + '\n' + fs[2] + '\n' + fs[3] + '\n' + 'n' + '\n']
    intcode(initMemory, input=data, output=feed, debug=False)
    print("Part 2: Answer =", feed[-1])
