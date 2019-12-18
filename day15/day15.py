import queue
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from shared.coord import Coord
from shared.intcode import intcode, Processor, Connector


def create_droid(code, debug=False):
    move_inst = queue.Queue()
    move_status = queue.Queue()
    droid = Processor('droid', code,
        in_wire=move_inst, out_wire=move_status, debug=debug)
    return (droid, move_inst, move_status)


class MazeGrid(dict):
    START = -2
    UNKNOWN = -1
    BLOCKED = 0
    OPEN = 1
    GOAL = 2
    DROID = 3

    def __init__(self):
        self.history = {}

    @staticmethod
    def render(state):
        if state == MazeGrid.UNKNOWN:
            return ' '
        if state == MazeGrid.BLOCKED:
            return '#'
        if state == MazeGrid.OPEN:
            return '.'
        if state == MazeGrid.GOAL:
            return '$'
        if state == MazeGrid.DROID:
            return 'D'
        if state == MazeGrid.START:
            return '+'

        raise Exception(f'Unknown state: {state}')

    def is_blocked(self, pos):
        return pos in self and self[pos] == MazeGrid.BLOCKED

    def explored(self, pos):
        for dir in [Directions.NORTH, Directions.WEST, Directions.SOUTH, Directions.EAST]:
            next_pos = pos + dir.step
            if next_pos not in self:
                return False
        return True

    def fully_explored(self):
        unexplored = [
            pos
            for pos, state in self.items()
            if state == MazeGrid.OPEN
            if not self.explored(pos)
        ]
        
        if len(unexplored) == 0:
            return True
        return False

    def track(self, pos):
        """ Assumes entry made before tracking """
        self.history[pos] = 1 + (self.history[pos] if pos in self.history else 0)

    def select_direction(self, pos):
        """ The intent of this fn is to do memory-mapping of entire maze """
        # To stop, return Directions.STOP
        if self.fully_explored():
            return Directions.STOP

        options = []
        for dir in [Directions.NORTH, Directions.WEST, Directions.SOUTH, Directions.EAST]:
            next_pos = pos + dir.step
            if not self.is_blocked(next_pos):
                options.append((dir, next_pos))
        sorted_options = sorted(options,
            key=lambda opt: self.history[opt[1]] if opt[1] in self.history else 0,
            reverse=True)
        # print(len(self.history), sorted_options)
        selected = sorted_options[-1]
        return selected[0]
    
    def gradient_descent(self, pos, cost=0, gradient=None):
        if gradient is None:
            gradient = dict()

        gradient[pos] = cost
        for dir in [Directions.NORTH, Directions.WEST, Directions.SOUTH, Directions.EAST]:
            next_pos = pos + dir.step
            if self[next_pos] != MazeGrid.BLOCKED:
                if next_pos in gradient:
                    if cost >= gradient[next_pos]:
                        # If current path is costlier than previously travered, abort.
                        continue
                self.gradient_descent(next_pos, cost=cost+1, gradient=gradient)
        
        return gradient


class Direction(object):
    def __init__(self, id, code, step):
        self.id = id
        self.code = code
        self.step = step
    
    def __repr__(self):
        return self.id


class Directions(object):
    NORTH = Direction('NORTH', 1, Coord(0, -1))
    SOUTH = Direction('SOUTH', 2, Coord(0, 1))
    WEST = Direction('WEST', 3, Coord(-1, 0))
    EAST = Direction('EAST', 4, Coord(1, 0))
    STOP = 'STOP'



class DroidController(Connector):
    def __init__(self, id,
                 pos=Coord(0,0),
                 grid=None, droid=None,
                 in_wire=None, out_wire=None,
                 debug=False):
        super(DroidController, self).__init__(id,
            in_wire=in_wire, out_wire=out_wire, debug=debug)
        self.grid = grid
        self.pos = pos

    def __str__(self):
        return 'Mover'

    def process(self):
        print_grid(self.grid, self.pos)

        dir = self.grid.select_direction(self.pos)
        if dir == Directions.STOP:
            Processor.abort()
            self.out_wire.put(Directions.NORTH)  # anything
            self.disconnect()
            return

        next_pos = self.pos + dir.step

        if self.debug:
            print('{self}: MOVING TO: {dir}, {next_pos}'.format(**locals()))

        self.out_wire.put(dir.code)
        status = self.in_wire.get()
        
        if self.debug:
            print('{self}: STATUS: {status}'.format(**locals()))

        if status == MazeGrid.BLOCKED:
            self.grid[next_pos] = MazeGrid.BLOCKED
        elif status == MazeGrid.OPEN:  # Also, robot has moved to new location
            self.grid[next_pos] = MazeGrid.OPEN
            self.pos = next_pos
            self.grid.track(self.pos)  # because we've moved here
        elif status == MazeGrid.GOAL:
            self.grid[next_pos] = MazeGrid.GOAL
            self.pos = next_pos
            self.grid.track(self.pos)  # because we've moved here



def create_droid_with_controller(code, grid, debug=False):
    droid, move_inst, move_status = create_droid(code)
    controller = DroidController(
        id='robot-mover',
        grid=grid, droid=droid,
        in_wire=move_status,
        out_wire=move_inst,
        debug=debug
    )
    chips = { 'droid': droid }
    wires = ( controller, )
    return (chips, wires, move_inst, move_status)


def run_robot(robot, debug=False):
    (chips, wires, move_inst, _) = robot
    ( mover, ) = wires

    for th in list(chips.values()) + list(wires):
        th.start()

    # # initial inputs ?
    # move_inst.put(mover.grid.get_color(mover.pos))

    chips['droid'].add_listener( mover.disconnect )
    
    for th in list(chips.values()) + list(wires):
        if debug:
            print("WAITING ON: {}".format(th))
        th.join()
        if debug:
            print("TERMINATED: {}".format(th))


def print_grid(grid, droid_pos):
    os.system('clear')
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
            status = MazeGrid.UNKNOWN
            if pos in grid:
                status = grid[pos]
            if pos == Coord(0,0):
                status = MazeGrid.START
            if pos == droid_pos:
                status = MazeGrid.DROID
            
            row__ += MazeGrid.render( status )
        marks.append(row__)

    print('\n'.join(marks))


def run_tests():    
    pass

if __name__ == '__main__':

    print("Reading input..")
    with open('./day15/input') as input:
        initMemory = [int(x) for x in input.readline().split(',')]

    grid = MazeGrid()
    start = Coord(0,0)
    grid[start] = MazeGrid.OPEN
    grid.track(start)
    robot = create_droid_with_controller(initMemory, grid, debug=False)
    run_robot(robot, debug=False)

    print('MazeGrid Size: {}'.format(len(grid)))

    print_grid(grid, start)

    goal = [k for k,v in grid.items() if v == MazeGrid.GOAL][0]
    print('Goal: {goal}'.format(**locals()))

    gradient = grid.gradient_descent(goal)
    print(f'Cost @ {start} = {gradient[start]}')
    print(f'Max Cost = {max(gradient.values())}')    
