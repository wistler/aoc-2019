import math
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from shared.intcode import intcode


if __name__ == '__main__':
    for test in [
        {
            "init": [1102,34915192,34915192,7,4,7,99,0],
            "input":[[]],
            "output":[[1219070632396864]],
        },
        {
            "init": [104,1125899906842624,99],
            "input":[
                [],
            ],
            "output": [
                [1125899906842624],
            ],
        },
        {
            "init": [109,1,204,-1,1001,100,1,100,1008,100,16,101,1006,101,0,99], 
            "input":[[]],
            "output":[[109,1,204,-1,1001,100,1,100,1008,100,16,101,1006,101,0,99]],
        },
    ]:
        initMemory = test["init"]
        for inp, expectedOutput in zip(test['input'], test['output']):
            output = []
            endState = intcode(
                initMemory.copy(), 
                input=inp.copy() if inp is not None else None, 
                output=output,
                debug=False
            )
            if "end" in test:
                if endState["memory"] != test["end"]:
                    print("Test Run of {} = {}. Expected: {}".format(initMemory, endState["memory"], test["end"]))
                    sys.exit(1)
            if expectedOutput is not None:
                if output != expectedOutput:
                    print("Test Run of {} (input {}) = {}. Expected: {}".format(initMemory, inp, output, expectedOutput))
                    sys.exit(1)

    with open('./day9/input') as input:
        initMemory = [int(x) for x in input.readline().split(',')]

    # part 1
    memory = initMemory.copy()
    inp=[1]
    output=[]
    endState = intcode(memory, inp, output, debug=False)
    
    print("Part 1: Execution Result = {}\n".format(output))

    # part 2
    memory = initMemory.copy()
    inp=[2]
    output=[]
    endState = intcode(memory, inp, output, debug=False)
    
    print("Part 2: Execution Result = {}\n".format(output))
