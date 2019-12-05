import math
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from shared.intcode import intcode


if __name__ == '__main__':
    for test in [
        {
            "init": [1002,4,3,4,33], 
            "input":[None],
            "output":[None],
            "end": [1002,4,3,4,99]
        },
        {
            "init": [1101,100,-1,4,0],
            "input":[None],
            "output": [None],
            "end": [1101,100,-1,4,99]
        },
        {
            "init": [3,9,8,9,10,9,4,9,99,-1,8],
            "input":[
                [4],
                [8]
            ],
            "output": [
                [0],
                [1]
            ],
        },
        {
            "init": [3,9,7,9,10,9,4,9,99,-1,8],
            "input":[
                [4],
                [9]
            ],
            "output": [
                [1],
                [0]
            ],
        },
        {
            "init": [3,3,1108,-1,8,3,4,3,99],
            "input":[
                [4],
                [8]
            ],
            "output": [
                [0],
                [1]
            ],
        },
        {
            "init": [3,3,1107,-1,8,3,4,3,99],
            "input":[
                [4],
                [9]
            ],
            "output": [
                [1],
                [0]
            ],
        },
        {
            "init": [3,21,1008,21,8,20,1005,20,22,107,8,21,20,1006,20,31,
                     1106,0,36,98,0,0,1002,21,125,20,4,20,1105,1,46,104,
                     999,1105,1,46,1101,1000,1,20,4,20,1105,1,46,98,99],
            "input":[
                [6],
                [8],
                [10]
            ],
            "output": [
                [999],
                [1000],
                [1001]
            ],
        },
    ]:
        initMemory = test["init"]
        for inp, expectedOutput in zip(test['input'], test['output']):
            output = []
            endState = intcode(
                initMemory.copy(), 
                input=inp.copy() if inp is not None else None, 
                output=output
            )
            if "end" in test:
                if endState["memory"] != test["end"]:
                    print("Test Run of {} = {}. Expected: {}".format(initMemory, endState["memory"], test["end"]))
                    sys.exit(1)
            if expectedOutput is not None:
                if output != expectedOutput:
                    print("Test Run of {} (input {}) = {}. Expected: {}".format(initMemory, inp, output, expectedOutput))
                    sys.exit(1)

    with open('./day5/input') as input:
        initMemory = [int(x) for x in input.readline().split(',')]

    # part 1
    memory = initMemory.copy()
    inp=[1]
    expectedOutput=[]
    endState = intcode(memory, inp, expectedOutput)
    
    print("Part 1: Exxecution Result = {}\n".format(expectedOutput))

    # part 2
    memory = initMemory.copy()
    inp=[5]
    expectedOutput=[]
    endState = intcode(memory, inp, expectedOutput)
    
    print("Part 2: Exxecution Result = {}\n".format(expectedOutput))

