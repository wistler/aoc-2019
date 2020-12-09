import sys, os, time, datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from shared.progress import Progress
from shared.repeater import SignalRepeater, SignalDataRepeater


def gen_phases(signal, pattern, num_phases, 
               start=0, stop=None, optimize=False,
               debug=False, progress=None):
    len_signal = len(signal)
    len_half_signal = len_signal // 2
    if stop is None:
        stop = len_signal

    if progress:
        progress.total = num_phases 

    prev_phase = signal
    for p in range(num_phases):
        phase = [0]*len_signal

        for i in range(len_signal-1,
                       -1 if not optimize else start-1,   # only computing what is needed
                       -1):
            acc = 0
            if i == len_signal-1:
                acc = prev_phase[i]              # s'[end] = s[end]
            elif i >= len_half_signal:
                acc = prev_phase[i] + phase[i+1] # s'[end-2]=(s[end-2]+s'[end-1])%10
            else:
                pat = SignalDataRepeater(pattern, i+1)
                for j in range(i,len_signal): # Skipping i entries in signal because pattern[0] is 0
                    b = pat[j+1]              # The +1 is for skipping first index in pattern
                    if b != 0 :
                        a = prev_phase[j]
                        acc += a*b

            phase[i] = abs(acc) % 10

        if progress:
            progress.add(1)

        prev_phase = phase
        if debug:
            if progress:
                progress.clear()
            print("After {:3} phases: {}".format(p+1, out_T(phase)))

    return phase


def in_T(signal):
    return list(ord(ch)-48 for ch in signal)


def out_T(signal):
    return ''.join(str(ch) for ch in signal)


def run_tests():
    base_pattern = [0, 1, 0, -1]

    test_signal = in_T('1'*32)
    print("Signal  : {}".format(out_T(test_signal)))
    for i in range(1,10):
        phase_i = out_T(gen_phases(test_signal, base_pattern, i, start=1, stop=1+8))
        print("Phase {:2}: {}".format(i, phase_i))

    ##########################################

    signal = in_T('12345678')

    phase1 = out_T(gen_phases(signal, base_pattern, 1))
    wanted = '48226158'
    if phase1 != wanted:
        print("Assertion Error:\n\tInput:\t{i}\n\tOutput:\t{o}\n\tWanted:\t{e}"
                .format(i=signal, o=phase1, e=wanted))
        sys.exit(1)

    phase4 = out_T(gen_phases(signal, base_pattern, 4))
    wanted = '01029498'
    if phase4 != wanted:
        print("Assertion Error:\n\tInput:\t{i}\n\tOutput:\t{o}\n\tWanted:\t{e}"
                .format(i=signal, o=phase4, e=wanted))
        sys.exit(1)
    
    ##########################################

    print('Day 16: Testing for Part 1..')
    testData = [
        ('80871224585914546619083218645595', '24176176'),
        ('19617804207202209144916044189917', '73745418'),
        ('69317163492948606335995924319873', '52432133'),
    ]
    for i,e in testData:
        o1 = out_T(gen_phases(in_T(i), base_pattern, 100,
                              start=0, stop=8, optimize=False
                              ))[0:8]
        o2 = out_T(gen_phases(in_T(i), base_pattern, 100,
                              start=0, stop=8, optimize=True
                              ))[0:8]
        if o1 != e:
            print("Assertion Error:\n\tInput:\t{i}\n\tOutput:\t{o}\n\tWanted:\t{e}"
                    .format(i=i, o=o1, e=e))
            sys.exit(1)

        if o1 != o2:
            print("Optimization Error:\n\tInput:\t{i}\n\tOutput:\t{o}\n\tWanted:\t{e}"
                    .format(i=i, o=o2, e=o1))
            sys.exit(1)

    ##########################################

    print('Day 16: Testing for Part 2..')
    testData = [
        ('03036732577212944063491565474664', '84462026'),
        ('02935109699940807407585447034323', '78725270'),
        ('03081770884921959731165446850517', '53553731'),
    ]
    for i,e in testData:
        sig = SignalRepeater(in_T(i), 10000)
        start = int(i[0:7])
        stop = start + 8
        phases = 100
        prog = None #Progress(phases)
        print("Signal size: {}, Offset: {}".format(len(sig), start))
        o = out_T(gen_phases(sig, base_pattern, phases,
                             start=start, stop=stop, optimize=True,
                             debug=False, progress=prog))[start:stop]
        if o != e:
            print("Assertion Error:\n\tOutput:\t{o}\n\tWanted:\t{e}"
                    .format(i=i, o=o, e=e))
            sys.exit(1)


if __name__ == '__main__':
    run_tests()
    print('Day 16')

    with open('./day16/input') as input:
        data = input.read()

    signal = in_T(data)
    base_pattern = [0, 1, 0, -1]
    print('Part 1..')
    r_signal = signal
    phases = 100
    prog = None #Progress(phases * pow(len(r_signal),1))
    print(out_T(gen_phases(r_signal, base_pattern, phases, progress=prog))[0:8])

    print('Part 2..')
    r_signal = SignalRepeater(signal, 10000)
    start = int(out_T(signal[0:7]))
    stop = start + 8
    phases = 100
    prog = None # Progress(phases * pow(len(r_signal),1))
    o = out_T(gen_phases(r_signal, base_pattern, phases,
                            start=start, stop=stop, optimize=True,
                            debug=False, progress=prog))[start:stop]
    print(o)
