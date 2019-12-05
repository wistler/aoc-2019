
def intcode(memory):
    ip = 0  # instruction pointer
    while True:
        opcode = memory[ip]
        if opcode == 1:
            p1 = memory[ip+1]  # parameters
            p2 = memory[ip+2]
            p3 = memory[ip+3]
            v1 = memory[p1]
            v2 = memory[p2]
            sum = v1 + v2
            memory[p3] = sum
            ip += 4
            
        elif opcode == 2:
            p1 = memory[ip+1]
            p2 = memory[ip+2]
            p3 = memory[ip+3]
            v1 = memory[p1]
            v2 = memory[p2]
            prod = v1 * v2
            memory[p3] = prod
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
