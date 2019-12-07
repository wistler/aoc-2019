def get_mode(modes, index):
    try:
        return int(modes[-index])
    except:
        return 0  # default parameter mode


def read(memory, parameter, mode):
    if mode == 0:  # position mode
        return memory[parameter]
    if mode == 1:  # immediate mode
        return parameter
        
    raise Exception("Unknown parameter mode: " + mode)


def read_param(memory, ip, index, output=False):
    instruction = str(memory[ip])
    pmodes = instruction[:-2]
    param = memory[ip + index]
    if output:
        return param
    mode = get_mode(pmodes, index)
    return read(memory, param, mode)


def read_from_input(input):
    if input is None:
        raise Exception("Input not connected")
    try:
        # I don't like this, need to re-design later.
        input.reverse()
        i = input.pop()
        input.reverse()
        return i
    except:
        raise Exception("Cannot read from input")


def write_to_output(output, value):
    if output is None:
        raise Exception("Output not connected")
    try:
        output.append(value)
    except:
        raise Exception("Cannot write to output")


def intcode(memory, input=None, output=None, debug=False):
    ip = 0  # instruction pointer
    while True:
        instruction = str(memory[ip])
        opcode = int(instruction[-2:])
        if opcode == 1:  # add
            p1 = read_param(memory, ip, 1)
            p2 = read_param(memory, ip, 2)
            p3 = read_param(memory, ip, 3, output=True)
            sum = p1 + p2
            memory[p3] = sum
            if debug:
                print("ADD   {p1} + {p2} = {sum} -> &{p3}".format(**locals()))
            ip += 4
            
        elif opcode == 2:  # mult
            p1 = read_param(memory, ip, 1)
            p2 = read_param(memory, ip, 2)
            p3 = read_param(memory, ip, 3, output=True)
            prod = p1 * p2
            memory[p3] = prod
            if debug:
                print("MULT  {p1} x {p2} = {prod} -> &{p3}".format(**locals()))
            ip += 4

        elif opcode == 3:  # input
            p1 = read_param(memory, ip, 1, output=True)
            inp = read_from_input(input)  # saving input
            memory[p1] = inp
            if debug:
                print("INPUT {inp} -> &{p1}".format(**locals()))
            ip += 2

        elif opcode == 4:  # output
            p1 = read_param(memory, ip, 1)
            write_to_output(output, p1)
            if debug:
                print("OUTPT {output} -> &{p1}".format(**locals()))
            ip += 2

        elif opcode == 5:  # jump-if-true
            p1 = read_param(memory, ip, 1)
            p2 = read_param(memory, ip, 2)
            if p1 != 0:
                ip = p2
            else:
                ip += 3
        
        elif opcode == 6:  # jump-if-false
            p1 = read_param(memory, ip, 1)
            p2 = read_param(memory, ip, 2)
            if p1 == 0:
                ip = p2
            else:
                ip += 3

        elif opcode == 7:  # less-than
            p1 = read_param(memory, ip, 1)
            p2 = read_param(memory, ip, 2)
            p3 = read_param(memory, ip, 3, output=True)
            memory[p3] = 1 if p1 < p2 else 0
            ip += 4

        elif opcode == 8:  # equals
            p1 = read_param(memory, ip, 1)
            p2 = read_param(memory, ip, 2)
            p3 = read_param(memory, ip, 3, output=True)
            memory[p3] = 1 if p1 == p2 else 0
            ip += 4

        elif opcode == 99:
            ip += 1
            break
        else:
            raise Exception("Unknown opcode: " + opcode)
    return {
        "memory": memory,
        "ip": ip,
    }
