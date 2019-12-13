import queue
import threading

relative_base = 0

def get_mode(modes, index):
    try:
        return int(modes[-index])
    except:
        return 0  # default parameter mode


def read(memory, parameter, mode):
    try:
        if mode == 0:  # position mode
            return memory[parameter]
        if mode == 1:  # immediate mode
            return parameter
        if mode == 2:  # relative mode
            return memory[relative_base + parameter]
    except:
        print("ERROR Reading Memory: {}".format(locals()))
        raise
    raise Exception("Unknown parameter mode: " + mode)


def read_param(memory, ip, index):
    instruction = str(memory[ip])
    pmodes = instruction[:-2]
    param = memory[ip + index]
    mode = get_mode(pmodes, index)
    return read(memory, param, mode)


def write_to_param(memory, ip, index, output):
    instruction = str(memory[ip])
    pmodes = instruction[:-2]
    param = memory[ip + index]
    mode = get_mode(pmodes, index)
    if mode == 1:
        raise Exception("PROGRAM ERROR: IMMEDIATE MODE NOT SUPPORTED FOR OUTPUT PARAMETER!")
    if mode == 0:  # position mode
        memory[param] = output
        return
    if mode == 2:  # relative mode
        memory[relative_base + param] = output
        return
    raise Exception("Unknown parameter mode: {}".format(mode))


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

class SparseList(list):
  def __setitem__(self, index, value):
    missing = index - len(self) + 1
    if missing > 0:
      self.extend([0] * missing)
    list.__setitem__(self, index, value)

  def __getitem__(self, index):
    try: return list.__getitem__(self, index)
    except IndexError: return 0

def intcode(memory, input=None, output=None, id='_', debug=False):
    global relative_base
    ip = 0  # instruction pointer
    relative_base = 0  # reset relative base on start
    memory = SparseList(memory)
    try:
        while True:
            instruction = str(memory[ip])
            opcode = int(instruction[-2:])
            if opcode == 1:  # add
                p1 = read_param(memory, ip, 1)
                p2 = read_param(memory, ip, 2)
                sum = p1 + p2
                if debug:
                    print("{id}:#{ip} ADD   {p1} + {p2} = {sum}".format(**locals()))
                write_to_param(memory, ip, 3, sum)
                ip += 4
                
            elif opcode == 2:  # mult
                p1 = read_param(memory, ip, 1)
                p2 = read_param(memory, ip, 2)
                prod = p1 * p2
                if debug:
                    print("{id}:#{ip} MULT  {p1} x {p2} = {prod}".format(**locals()))
                write_to_param(memory, ip, 3, prod)
                ip += 4

            elif opcode == 3:  # input
                inp = read_from_input(input)  # saving input
                if debug:
                    print("{id}:#{ip} INPUT {inp}".format(**locals()))
                write_to_param(memory, ip, 1, inp)
                ip += 2

            elif opcode == 4:  # output
                p1 = read_param(memory, ip, 1)
                if debug:
                    print("{id}:#{ip} OUTPT {p1}".format(**locals()))
                write_to_output(output, p1)
                ip += 2

            elif opcode == 5:  # jump-if-true
                p1 = read_param(memory, ip, 1)
                p2 = read_param(memory, ip, 2)
                if debug:
                    print("{id}:#{ip} JMP IF TRUE {p1} ==> &{p2}".format(**locals()))
                if p1 != 0:
                    ip = p2
                else:
                    ip += 3
            
            elif opcode == 6:  # jump-if-false
                p1 = read_param(memory, ip, 1)
                p2 = read_param(memory, ip, 2)
                if debug:
                    print("{id}:#{ip} JMP IF FALSE {p1} ==> &{p2}".format(**locals()))
                if p1 == 0:
                    ip = p2
                else:
                    ip += 3

            elif opcode == 7:  # less-than
                p1 = read_param(memory, ip, 1)
                p2 = read_param(memory, ip, 2)
                if debug:
                    print("{id}:#{ip} LESS THAN {p1} < {p2}".format(**locals()))
                result = 1 if p1 < p2 else 0
                write_to_param(memory, ip, 3, result)
                ip += 4

            elif opcode == 8:  # equals
                p1 = read_param(memory, ip, 1)
                p2 = read_param(memory, ip, 2)
                if debug:
                    print("{id}:#{ip} EQUALS {p1} == {p2}".format(**locals()))
                result = 1 if p1 == p2 else 0
                write_to_param(memory, ip, 3, result)
                ip += 4

            elif opcode == 9:  # adjust relative base
                p1 = read_param(memory, ip, 1)
                relative_base += p1
                if debug:
                    print("{id}:#{ip} ADJ REL_BASE -> {relative_base}".format(relative_base=relative_base, **locals()))
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
    except:
        print("ERROR: Program crashed! {}".format(locals()))
        raise


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

            self.process()

        if self.debug:
            print('{self}: Stopped'.format(**locals()))

    def process(self):
        """
        Base implementation is to simply transfer the data.
        Override this for custom behavior.
        """
        i = self.in_wire.get()
        if self.debug:
            print('{self}: ---[ {i} ]-->'.format(**locals()))
        self.out_wire.put(i)
