def get_mode(modes, index):
    try:
        return modes[-index]
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
    if not input:
        raise Exception("Input not connected")
    try:
        return input.pop()
    except:
        raise Exception("Cannot read from input")


def write_to_output(output, value):
    if not output:
        raise Exception("Output not connected")
    try:
        return output.append(value)
    except:
        raise Exception("Cannot write to output")


def intcode(memory, input=None, output=None):
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
            ip += 4
            
        elif opcode == 2:  # mult
            p1 = read_param(memory, ip, 1)
            p2 = read_param(memory, ip, 2)
            p3 = read_param(memory, ip, 3, output=True)
            prod = p1 * p2
            memory[p3] = prod
            ip += 4

        elif opcode == 3:  # input
            p1 = read_param(memory, ip, 1, output=True)
            memory[p1] = read_from_input(input)  # saving input
            ip += 2

        elif opcode == 4:  # output
            p1 = read_param(memory, ip, 1)
            write_to_output(output, p1)
            ip += 2

        elif opcode == 99:
            ip += 1
            break
        else:
            raise Exception("Unknown opcode: " + opcode)
    return {
        "memory": memory,
        "ip": ip,
    }
