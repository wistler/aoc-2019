import queue
import sys, os, itertools

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from shared.intcode import intcode, Processor, Connector

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

def create_amp(id, code, phase, in_wire=None, out_wire=None, debug=False):
    if not in_wire:
        in_wire = queue.Queue()
    if not out_wire:
        out_wire = queue.Queue()
    in_wire.put(phase)
    p = Processor(id, code, in_wire, out_wire, debug=debug)
    return (p, in_wire, out_wire)

def create_circuit(code, phase_seq, debug=False):
    amps = {}

    in_wire = queue.Queue()  # initial input
    next_in_wire = in_wire
    for id, phase in zip('ABCDE', phase_seq):
        amp, i, o = create_amp(id, code, phase, in_wire=next_in_wire, debug=debug)
        next_in_wire = o
        amps[id] = amp
    
    feedback_wire = Connector(
        'E -> A', 
        in_wire=amps['E'].out_wire,
        out_wire=amps['A'].in_wire,
        debug=debug
    )

    wires = ( feedback_wire, )
    out_wire = amps['E'].out_wire
    return (amps, wires, in_wire, out_wire)

def run_circuit(circuit, debug=False):
    (amps, wires, in_wire, out_wire) = circuit
    (feedback_wires, ) = wires

    # start all threads
    for th in list(amps.values()) + list(wires):
        th.start()

    in_wire.put(0)  # first input
    amps['A'].add_listener( feedback_wires.disconnect )

    # wait for all amps to halt
    for th in amps.values():
        if debug:
            print("WAITING ON: {}".format(th))
        th.join()
        if debug:
            print("TERMINATED: {}".format(th))
    
    if out_wire.empty():
        return None

    return out_wire.get()

def input_generator(min=0, max=4, n=5):
    return itertools.permutations(range(min, max + 1), n)

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
        run = find_best_score(task, input_generator(min=0, max=4), scoring_fn=IDENTITY)
        if run["inputs"] != test_data["ans-phase"] or run["result"] != test_data["ans-thrust"]:
            print("[B] Expected: Max output {} at phase {}\n Got: Max output {} at phase {}".format(
                test_data["ans-thrust"], test_data["ans-phase"], run["result"], run["inputs"]
            ))
            sys.exit(1)


    with open('./day7/input') as input:
        code = list(map(int, input.readline().split(',')))

        # part 1
        task = lambda phase_seq: run_amp_chain(code, phase_seq)
        run = find_best_score(task, input_generator(min=0, max=4), scoring_fn=IDENTITY)
        print("Best run: {run}".format(**locals()))


    # tests for part 2
    # tests
    test_data_set = [
        {
            "program": "3,26,1001,26,-4,26,3,27,1002,27,2,27,1,27,26,27,4,27,1001,28,-1,28,1005,28,6,99,0,0,5",
            "ans-phase": (9,8,7,6,5),
            "ans-thrust": 139629729,
        },
        {
            "program": "3,52,1001,52,-5,52,3,53,1,52,56,54,1007,54,5,55,1005,55,26,1001,54,-5,54,1105,1,12,1,53,54,53,1008,54,0,55,1001,55,1,55,2,53,55,53,4,53,1001,56,-1,56,1005,56,6,99,0,0,0,0,10",
            "ans-phase": (9,7,8,5,6),
            "ans-thrust": 18216,
        },
    ]
    for test_data in test_data_set:
        code = list(map(int, test_data["program"].split(',')))

        def task(phase_seq):
            circuit = create_circuit(code, phase_seq, debug=False)
            output = run_circuit(circuit, debug=False)
            return output

        output = task(test_data["ans-phase"])
        if output != test_data["ans-thrust"]:
            print("[A] Expected: Output {} at phase {}\n Got: Output {}".format(
                test_data["ans-thrust"], test_data["ans-phase"], output
            ))
            sys.exit(1)

        run = find_best_score(task, input_generator(min=5, max=9), scoring_fn=IDENTITY, debug=False)
        if run["inputs"] != test_data["ans-phase"] or run["result"] != test_data["ans-thrust"]:
            print("[B] Expected: Max output {} at phase {}\n Got: Max output {} at phase {}".format(
                test_data["ans-thrust"], test_data["ans-phase"], run["result"], run["inputs"]
            ))
            sys.exit(1)
        
    with open('./day7/input') as input:
        code = list(map(int, input.readline().split(',')))

        # part 2
        def task(phase_seq):
            circuit = create_circuit(code, phase_seq, debug=False)
            output = run_circuit(circuit, debug=False)
            return output

        run = find_best_score(task, input_generator(min=5, max=9), scoring_fn=IDENTITY)
        print("Best run: {run}".format(**locals()))
