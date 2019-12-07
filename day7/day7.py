import sys, os, itertools

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from shared.intcode import intcode

def run_amp(program, phase, input_signal=0, debug=False):
    output = []
    intcode(program.copy(), input=[phase, input_signal], output=output, debug=debug)
    return output.pop()

def run_amp_chain(program, phase_seq, input_signal=0, debug=False):
    for amp, phase in zip('ABCDE', phase_seq):
        output = run_amp(program, phase=phase, input_signal=input_signal, debug=debug)
        if debug:
            print("Amp {}: Phase: {}, Input: {} => Output: {}".format(amp, phase, input_signal, output))
        input_signal = output  # for next amp in chain
    return output

def input_generator():
    return itertools.permutations(range(0, 5), 5)

# Scoring fn
IDENTITY = lambda x: x

def find_best_score(task, inputs, scoring_fn=IDENTITY, debug=False):
    best_score = None
    best_run = None
    for i in inputs:
        result = task(i)
        score = scoring_fn(result)
        run = {
            "inputs": i,
            "result": result,
            "score": score
        }
        if debug:
            print(run)
        if best_score is None or score > best_score:
            best_score = score
            best_run = run
    return best_run


if __name__ == '__main__':

    # tests
    test_data_set = [
        {
            "program": "3,15,3,16,1002,16,10,16,1,16,15,15,4,15,99,0,0",
            "ans-phase": (4,3,2,1,0),
            "ans-thrust": 43210,
        },
        {
            "program": "3,23,3,24,1002,24,10,24,1002,23,-1,23,101,5,23,23,1,24,23,23,4,23,99,0,0",
            "ans-phase": (0,1,2,3,4),
            "ans-thrust": 54321,
        },
        {
            "program": "3,31,3,32,1002,32,10,32,1001,31,-2,31,1007,31,0,33,1002,33,7,33,1,33,31,31,1,32,31,31,4,31,99,0,0,0",
            "ans-phase": (1,0,4,3,2),
            "ans-thrust": 65210,
        },
    ]
    for test_data in test_data_set:
        code = list(map(int, test_data["program"].split(',')))

        output = run_amp_chain(code.copy(), test_data["ans-phase"], input_signal=0)
        if output != test_data["ans-thrust"]:
            print("[A] Expected: Output {} at phase {}\n Got: Output {}".format(
                test_data["ans-thrust"], test_data["ans-phase"], output
            ))
            sys.exit(1)


        task = lambda phase_seq: run_amp_chain(code, phase_seq)
        run = find_best_score(task, input_generator(), scoring_fn=IDENTITY)
        if run["inputs"] != test_data["ans-phase"] or run["result"] != test_data["ans-thrust"]:
            print("[B] Expected: Max output {} at phase {}\n Got: Max output {} at phase {}".format(
                test_data["ans-thrust"], test_data["ans-phase"], run["result"], run["inputs"]
            ))
            sys.exit(1)


    with open('./day7/input') as input:
        code = list(map(int, input.readline().split(',')))

        # part 1
        task = lambda phase_seq: run_amp_chain(code, phase_seq)
        run = find_best_score(task, input_generator(), scoring_fn=IDENTITY)
        print("Best run: {run}".format(**locals()))

        