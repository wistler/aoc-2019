import queue
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from shared.coord import Coord
from shared.intcode import intcode, Processor, Connector


def create_robot_brain(code, debug=False):
    input_from_camera = queue.Queue()
    output_instructions = queue.Queue()
    brain = Processor('brain', code,
        in_wire=input_from_camera, out_wire=output_instructions, debug=debug)
    return (brain, input_from_camera, output_instructions)


class PaintGrid(dict):
    BLACK = 0
    WHITE = 1

    DEFAULT_COLOR = BLACK

    @staticmethod
    def render_color(color):
        if color == PaintGrid.BLACK:
            return '.'
        if color == PaintGrid.WHITE:
            return '#'
        return '?'

    def get_color(self, pos):
        if pos in self:
            return self[pos]
        return PaintGrid.DEFAULT_COLOR


class Direction(object):
    def __init__(self, id, step):
        self.id = id
        self.step = step
    
    def __str__(self):
        return self.id


class Directions(object):
    NORTH = Direction('NORTH', Coord(0, -1))
    WEST = Direction('WEST', Coord(-1, 0))
    SOUTH = Direction('SOUTH', Coord(0, 1))
    EAST = Direction('EAST', Coord(1, 0))

    @staticmethod
    def left(dir):
        if dir == Directions.NORTH:
            return Directions.WEST
        elif dir == Directions.WEST:
            return Directions.SOUTH
        elif dir == Directions.SOUTH:
            return Directions.EAST
        elif dir == Directions.EAST:
            return Directions.NORTH
        else:
            raise Exception("Unsupported direction: {}".format(dir))

    @staticmethod
    def right(dir):
        if dir == Directions.NORTH:
            return Directions.EAST
        elif dir == Directions.EAST:
            return Directions.SOUTH
        elif dir == Directions.SOUTH:
            return Directions.WEST
        elif dir == Directions.WEST:
            return Directions.NORTH
        else:
            raise Exception("Unsupported direction: {}".format(dir))


def move(curr_pos, curr_dir, turnLeft):
    new_dir = Directions.left(curr_dir) if turnLeft else Directions.right(curr_dir)
    new_pos = curr_pos + new_dir.step
    
    return new_pos, new_dir


class RobotMover(Connector):
    def __init__(self, id,
                 pos=Coord(0,0), dir=Directions.NORTH,
                 grid=None,
                 in_wire=None, out_wire=None,
                 debug=False):
        super(RobotMover, self).__init__(id,
            in_wire=in_wire, out_wire=out_wire, debug=debug)
        self.grid = grid
        self.pos = pos
        self.dir = dir

    def __str__(self):
        return 'Mover'

    def process(self):
        color = self.in_wire.get()
        direction = self.in_wire.get()
        turnLeft = direction == 0
        if self.debug:
            print('{self}: PAINT-n-MOVE: [ color: {color}, dir: {direction} ]'.format(
                self=self,
                color='BLACK' if color == PaintGrid.BLACK else 'WHITE',
                direction='TURN LEFT' if turnLeft else 'TURN RIGHT'
            ))

        if self.debug:
            print('{self}: CURRENT: [ pos: {pos}, dir: {dir}, color: {color} ]'.format(
                self=self,
                pos=self.pos, dir=self.dir,
                color=self.grid.get_color(self.pos)
            ))

        self.grid[self.pos] = color
        self.pos, self.dir = move(self.pos, self.dir, turnLeft)
        curr_color = self.grid.get_color(self.pos)

        if self.debug:
            print('{self}: MOVED: [ NEW pos: {pos}, NEW dir: {dir}, NEW color: {color} ]'.format(
                self=self,
                pos=self.pos, dir=self.dir,
                color='BLACK' if curr_color == PaintGrid.BLACK else 'WHITE',
            ))

        self.out_wire.put(curr_color)


def create_robot(code, grid, debug=False):
    brain, brain_in, brain_out = create_robot_brain(code)
    mover = RobotMover(
        id='robot-mover',
        grid=grid,
        in_wire=brain_out,  # output instructions
        out_wire=brain_in,  # input from camera
        debug=debug
    )
    chips = { 'brain': brain }
    wires = ( mover, )
    return (chips, wires, brain_in, brain_out)


def run_robot(robot, debug=False):
    (chips, wires, brain_in, _) = robot
    ( mover, ) = wires

    for th in list(chips.values()) + list(wires):
        th.start()

    # initial read from camera
    brain_in.put(mover.grid.get_color(mover.pos))

    chips['brain'].add_listener( mover.disconnect )

    for th in list(chips.values()) + list(wires):
        if debug:
            print("WAITING ON: {}".format(th))
        th.join()
        if debug:
            print("TERMINATED: {}".format(th))


def print_grid(grid):
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
            color = PaintGrid.BLACK
            if pos in grid:
                color = grid[pos]
            
            row__ += PaintGrid.render_color( color )
        marks.append(row__)

    print('\n'.join(marks))


def run_tests():    
    pass

if __name__ == '__main__':

    print("Reading input..")
    with open('./day11/input') as input:
        initMemory = [int(x) for x in input.readline().split(',')]

    grid = PaintGrid()
    grid[Coord(0,0)] = PaintGrid.WHITE
    robot = create_robot(initMemory, grid, debug=False)
    run_robot(robot, debug=False)

    # print('PaintGrid End State: {}'.format(grid))
    print('PaintGrid Size: {}'.format(len(grid)))

    print_grid(grid)
