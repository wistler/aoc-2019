import sys, os
import itertools

def repeat(pattern, times):
    # g = []
    # for h in [([x] * times) for x in pattern]:
    #     g.extend(h)
    # return g

    for x in pattern:
        for _ in range(times):
            yield x


def gen_phase(signal, base_pattern, start=0, stop=None):
    if stop is None:
        stop = len(signal)

    phase = []
    for i in range(start, stop):
        pattern = itertools.cycle(repeat(base_pattern, i+1))
        next(pattern)  # drop the first

        acc = sum(s*p for s, p in zip(signal, pattern))
        phase.append(abs(acc) % 10)
    return phase


def gen_phases(signal, base_pattern, phases):
    for _ in range(phases):
        signal = gen_phase(signal, base_pattern)
    return signal


def run_tests():
    signal = list(map(lambda ch: int(ch), '12345678'))
    base_pattern = [0, 1, 0, -1]

    print(list(repeat(base_pattern, 3)))
    ptn = itertools.cycle(repeat(base_pattern, 3))
    next(ptn)
    print(list(itertools.islice(ptn,0,20)))
    phase1 = gen_phase(signal, base_pattern)
    phase2 = gen_phase(phase1, base_pattern)
    print(phase1, phase2)

    signal = list(map(lambda ch: int(ch), '80871224585914546619083218645595'))
    print(gen_phases(signal, base_pattern, 100)[0:8])

    signal = list(map(lambda ch: int(ch), '19617804207202209144916044189917'))
    print(gen_phases(signal, base_pattern, 100)[0:8])

    signal = list(map(lambda ch: int(ch), '69317163492948606335995924319873'))
    print(gen_phases(signal, base_pattern, 100)[0:8])

    signal = list(map(lambda ch: int(ch), '03036732577212944063491565474664'))
    offset = int(''.join(map(lambda i: str(i), signal[0:7])))
    print(gen_phases(signal*10000, base_pattern, 1)[offset:offset+8])



if __name__ == '__main__':
    run_tests()
    sys.exit(1)
    print('Day 16')

    with open('./day16/input') as input:
        data = input.read()

    signal = list(map(lambda ch: int(ch), data))
    base_pattern = [0, 1, 0, -1]
    print('Part 1..')
    print(gen_phases(signal, base_pattern, 100)[0:8])

    print('Part 2..')
    offset = int(''.join(map(lambda i: str(i), signal[0:7])))
    print(gen_phases(signal*10000, base_pattern, 100)[offset:offset+8])
