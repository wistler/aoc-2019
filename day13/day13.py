import sys, os, queue
import itertools, time

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from shared.coord import Coord
from shared.intcode import intcode, Processor, Connector

# Tile types
EMPTY = 0
WALL = 1
BLOCK = 2
PADDLE = 3
BALL = 4

JOYSTICK_NEUTRAL = 0
JOYSTICK_TILT_LEFT = -1
JOYSTICK_TILT_RIGHT = 1

class DisplayGrid(dict):
    def __init__(self):
        self.tiles = {}
    
    def numBlocks(self):
        return len(list(filter(lambda x: x == BLOCK, self.values())))


def RateLimited(maxPerSecond):
    minInterval = 1.0 / float(maxPerSecond)
    def decorate(func):
        lastTimeCalled = [0.0]
        def rateLimitedFunction(*args,**kargs):
            elapsed = time.time() - lastTimeCalled[0]
            leftToWait = minInterval - elapsed
            if leftToWait>0:
                time.sleep(leftToWait)
            ret = func(*args,**kargs)
            lastTimeCalled[0] = time.time()
            return ret
        return rateLimitedFunction
    return decorate


class Joystick(object):
    def __init__(self, debug=False):
        self.state = JOYSTICK_NEUTRAL
        self.debug = debug
        pass

    def set(self, state):
        self.state = state

    @RateLimited(25)
    def get(self):
        if self.debug:
            print('Joystick: Returning state as: {}'.format(
                'TILT LEFT' if self.state is JOYSTICK_TILT_LEFT else
                'TILT_RIGHT' if self.state is JOYSTICK_TILT_RIGHT else
                'NEUTRAL'
            ))
        return self.state


class GameController(Connector):
    def __init__(self, id,
                 grid=None, joystick=None,
                 in_wire=None, out_wire=None,
                 debug=False):
        super(GameController, self).__init__(id,
            in_wire=in_wire, out_wire=out_wire, debug=debug)
        self.grid = grid
        self.joystick = joystick
        self.score = 0
        self.paddle_pos = None
        self.ball_pos = None

    def __str__(self):
        return 'GameController'

    def process(self):
        posX = self.in_wire.get()
        posY = self.in_wire.get()
        third = self.in_wire.get()

        pos = Coord(posX, posY)
        if pos == Coord(-1, 0):  # third is "score"
            if self.debug:
                print('{self}: SCORE: {tid}'.format(self=self, pos=pos, tid=third))

            self.score = third
        else:                    # third is "tile id"
            # if self.debug:
            #     print('{self}: Update Tile: Pos: {pos}, Type: {tid}'.format(self=self, pos=pos, tid=third))

            self.grid[pos] = third

            update_joystick = False

            if third == PADDLE:
                self.paddle_pos = pos
                update_joystick = True
                if self.debug:
                    print('{self}: PADDLE: moved to: {pos}'.format(self=self, pos=pos))
            elif third == BALL:
                self.ball_pos = pos
                update_joystick = True
                if self.debug:
                    print('{self}: BALL: moved to: {pos}'.format(self=self, pos=pos))

            if update_joystick and \
                self.joystick is not None and \
                self.paddle_pos and self.ball_pos:

                blocks = self.grid.numBlocks()

                if blocks == 0:
                    self.joystick.set( JOYSTICK_NEUTRAL )
                    print('*********************************')
                    print('*********** BLOCKS: 0 ***********')
                    print('*********************************')
                else:
                    if self.paddle_pos.x > self.ball_pos.x:
                        self.joystick.set( JOYSTICK_TILT_LEFT )
                        if self.debug:
                            print('{self}: Joystick: TILT LEFT (PADDLE: {paddle}, BALL: {ball}, BLOCKS: {blocks})'.format(
                                self=self, paddle=self.paddle_pos, ball=self.ball_pos, blocks=blocks)
                            )
                    elif self.paddle_pos.x < self.ball_pos.x:
                        self.joystick.set( JOYSTICK_TILT_RIGHT )
                        if self.debug:
                            print('{self}: Joystick: TILT RIGHT (PADDLE: {paddle}, BALL: {ball}, BLOCKS: {blocks})'.format(
                                self=self, paddle=self.paddle_pos, ball=self.ball_pos, blocks=blocks)
                            )
                    else:
                        self.joystick.set( JOYSTICK_NEUTRAL )
                        if self.debug:
                            print('{self}: Joystick: NEUTRAL (PADDLE: {paddle}, BALL: {ball}, BLOCKS: {blocks})'.format(
                                self=self, paddle=self.paddle_pos, ball=self.ball_pos, blocks=blocks)
                            )
                    

def create_game(code, debug=False):
    joystick = Joystick(debug=debug)
    output_display = queue.Queue()
    game = Processor('game', code,
        in_wire=joystick,
        out_wire=output_display,
        debug=debug
    )
    return (game, joystick, output_display)


def create_arcage(code, grid, debug=False):
    game, joystick, output_display = create_game(code, debug=debug)
    controller = GameController(
        id='game-controller',
        grid=grid,
        in_wire=output_display,
        joystick=joystick,
        debug=debug
    )
    chips = { 'game': game }
    wires = (controller, )
    arcade = (chips, wires, joystick, output_display)
    return arcade


def run_arcade(arcade, debug=False):
    (chips, wires, _, _) = arcade
    (controller, ) = wires

    for th in list(chips.values()) + list(wires):
        th.start()

    chips['game'].add_listener( controller.disconnect )

    for th in list(chips.values()) + list(wires):
        if debug:
            print("WAITING ON: {}".format(th))
        th.join()
        if debug:
            print("TERMINATED: {}".format(th))


def run_tests():
    pass

if __name__ == '__main__':
    run_tests()
    print("Part #1")

    print("Reading input..")
    with open('./day13/input') as input:
        initMemory = [int(x) for x in input.readline().split(',')]

    grid = DisplayGrid()
    arcade = create_arcage(initMemory, grid, debug=False)
    run_arcade(arcade, debug=False)

    print('DisplayGrid Size: {}'.format(len(grid)))
    print('Number of "block" tiles: {}'.format( grid.numBlocks() ))

    print("Part #2")
    # Hack number of quarters
    initMemory[0] = 2
    print("Playing game..")

    grid = DisplayGrid()
    arcade = create_arcage(initMemory, grid, debug=False)
    run_arcade(arcade, debug=False)

    (_, wires,_, _) = arcade
    (controller, ) = wires
    print('Current Score: {}'.format( controller.score ))