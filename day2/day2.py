import math
import sys

from intcode import intcode

if __name__ == '__main__':

    # test run
    for test in [
            {"init": [1,0,0,0,99],          "end": [2,0,0,0,99]},
            {"init": [2,3,0,3,99],          "end": [2,3,0,6,99]},
            {"init": [2,4,4,5,99,0],        "end": [2,4,4,5,99,9801]},
            {"init": [1,1,1,4,99,5,6,0,99], "end": [30,1,1,4,2,5,6,0,99]},
        ]:
        initMemory = test["init"]
        expectedEndStateMemory = test["end"]
        endState = intcode(initMemory.copy())
        if endState["memory"] != expectedEndStateMemory:
            print("Test Run of {} = {}. Expected: {}".format(initMemory, endState["memory"], expectedEndStateMemory))
            sys.exit(1)


    with open('./day2/input') as input:
        initMemory = [int(x) for x in input.readline().split(',')]

    # part 1
    print("# Part 1")
    memory = initMemory.copy()
    memory[1] = 12
    memory[2] = 2
    endState = intcode(memory)
    output = endState["memory"][0]
    print("Exxecution Result = {}\n".format(output))

    # part 2
    print("# Part 2")
    target = 19690720
    found = False
    for noun in range(0, 100):
        for verb in range(0, 100):

            # init memory
            memory = initMemory.copy()

            # inputs
            memory[1] = noun
            memory[2] = verb
            endState = intcode(memory)
            output = endState["memory"][0]
            
            if output == target:
                found = True
                break # for verb
        if found:
            break # for noun
    
    if found:
        print("noun = {}, verb = {}, result = {}".format(noun, verb, 100 * noun + verb))
    else:
        print("ERROR: Could not find match.")

