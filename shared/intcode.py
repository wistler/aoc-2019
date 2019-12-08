import queue
import threading

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
        # assume Queue w/ blocking get
        return input.get()
    except:
        try:
            # assume List
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
        # assume queue
        output.put(value)
    except:
        try:
            # assume list
            output.append(value)
        except:
            raise Exception("Cannot write to output")


def intcode(memory, input=None, output=None, id='_', debug=False):
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
            # if debug:
            #     print("{id}: ADD   {p1} + {p2} = {sum} -> &{p3}".format(**locals()))
            ip += 4
            
        elif opcode == 2:  # mult
            p1 = read_param(memory, ip, 1)
            p2 = read_param(memory, ip, 2)
            p3 = read_param(memory, ip, 3, output=True)
            prod = p1 * p2
            memory[p3] = prod
            # if debug:
            #     print("{id}: MULT  {p1} x {p2} = {prod} -> &{p3}".format(**locals()))
            ip += 4

        elif opcode == 3:  # input
            p1 = read_param(memory, ip, 1, output=True)
            inp = read_from_input(input)  # saving input
            memory[p1] = inp
            if debug:
                print("{id}: INPUT {inp} -> &{p1}".format(**locals()))
            ip += 2

        elif opcode == 4:  # output
            p1 = read_param(memory, ip, 1)
            write_to_output(output, p1)
            if debug:
                print("{id}: OUTPT -> {p1}".format(**locals()))
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


class Processor(threading.Thread):
    def __init__(self, id, code,
                 in_wire=None, out_wire=None, debug=False):
        super(Processor, self).__init__(name='Proc <{id}>'.format(**locals()))

        self.id = id
        self.memory = code.copy()
        self.in_wire = in_wire
        self.out_wire = out_wire
        self.debug = debug
        self.listeners = []
        
        if self.debug:
            print('{self}: Initialized'.format(**locals()))

    def __str__(self):
        return 'Proc [{id}]'.format(id=self.id)

    def run(self):
        if self.debug:
            print('{self}: Started'.format(**locals()))
        intcode(self.memory,
            input=self.in_wire, output=self.out_wire,
            id=str(self), debug=self.debug)
        if self.debug:
            print('{self}: Stopped'.format(**locals()))
            
        for li in self.listeners:
            li()
    
    def add_listener(self, listener):
        self.listeners.append(listener)
    

class Connector(threading.Thread):
    def __init__(self, id, in_wire=None, out_wire=None, debug=False):
        super(Connector, self).__init__(name='Wire <{id}>'.format(id=id))

        self.id = id
        self.in_wire = in_wire
        self.out_wire = out_wire
        self.stop = False
        self.debug = debug
        
        if self.debug:
            print('{self}: Initialized'.format(**locals()))

    def __str__(self):
        return 'Wire [{id}]'.format(id=self.id)

    def disconnect(self):
        if self.debug:
            print('{self}: Disconnecting'.format(**locals()))
        self.stop = True

    def run(self):
        if self.debug:
            print('{self}: Started'.format(**locals()))
        while not self.stop:
            if self.in_wire.empty():
                with self.in_wire.not_empty:
                    self.in_wire.not_empty.wait(timeout=0.2)
            if self.stop:
                break

            i = self.in_wire.get()
            if self.debug:
                print('{self}: ---[ {i} ]-->'.format(**locals()))
            self.out_wire.put(i)

        if self.debug:
            print('{self}: Stopped'.format(**locals()))
