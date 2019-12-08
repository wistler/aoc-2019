#!/usr/bin/python3

import math
import itertools

# Colors
TRANS = '2'
WHITE = '1'
BLACK = '0'

DISPLAY_TABLE = str.maketrans({
    TRANS: ' ',
    WHITE: '8',
    BLACK: '.'
})


def validate(layers):
    min_zeros = None
    counts = None
    for layer in layers:
        z = layer.count('0')
        if min_zeros is None or z < min_zeros:
            min_zeros = z
            counts = {
                'Layer': layers.index(layer),
                0: layer.count('0'),
                1: layer.count('1'),
                2: layer.count('2'),
            }
    
    print('Layer w/ most zeros: {}\n product = {}\n\n'.format(counts, counts[1] * counts[2]))


def display(layer, rows, cols):
    for r in range(rows):
        print(layer[r*cols:(r+1)*cols].translate(DISPLAY_TABLE))


def decode(image, rows, cols, validate_=False):
    layer_size = rows * cols

    layers = []
    for l in range(0, math.floor(len(image)/layer_size)):
        layers.append(image[layer_size*l : layer_size*(l+1)])
    
    if validate_:
        validate(layers)    

    merged = ''.join([next(filter(lambda x: x != TRANS, pixel), TRANS) for pixel in zip(*layers)])
    return merged
    

if __name__ == '__main__':

    # test:
    result = decode('0222112222120000', 2, 2)
    expected = '0110'
    if result != expected:
        display(result, 2, 2)
        raise BaseException('Assertion Error: \nExpected: {}\nActual: {}'.format(expected, result))


    cols = 25
    rows = 6
    with open('./day8/input') as input:
        image = input.readline()

    result = decode(image, rows, cols, validate_=True)
    display(result, rows, cols)
    