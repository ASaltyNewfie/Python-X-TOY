import sys
import re

PC = 16
R = {}
M = {}
debug_mode = False

def debug(out):
    if debug_mode: print(out)

def execute():
    global PC

    instruction = M[hex(PC)]

    opcode = instruction[0]
    d = instruction[1]
    s = instruction[2]
    t = instruction[3]
    addr = instruction[2:4]

    a = int(R[s], 16)
    b = int(R[t], 16)

    if opcode == '1':
        debug(f'Adding register {s} ({R[s]}) to register {t} ({R[t]}) and storing the result in register {d}')
        math_op(d, a + b)
    if opcode == '2':
        debug(f'Subtracting register {t} ({R[t]}) from register {s} ({R[s]}) and storing the result in register {d}')
        math_op(d, a - b)
    if opcode == '3':
        debug(f'Performing binary AND on registers {s} and {t} and storing the result in register {d}')
        math_op(d, a & b)
    if opcode == '4':
        debug(f'Performing binary OR on registers {s} and {t} and storing the result in register {d}')
        math_op(d, a ^ b)
    if opcode == '5':
        debug(f'Performing binary LEFT SHIFT on registers {s} by {t} and storing the result in register {d}')
        math_op(d, a << b)
    if opcode == '6':
        debug(f'Performing binary RIGHT SHIFT on registers {s} by {t} and storing the result in register {d}')
        math_op(d, a >> b)

    if opcode == '7':
        debug(f'Storing {addr} in register {d}')
        store_register(d, addr)
    if opcode == '8':
        if addr == 'FF':
            debug(f'Storing input in memory {addr}')
            M[addr] = input(': ')
        debug(f'Storing memory {addr} ({M[addr]}) in register {d}')
        store_register(d, M[addr])
    if opcode == '9':
        if addr == 'FF':
            debug(f'Storing register {d} ({R[d]}) in memory {addr} and printing {R[d]}')
        else:
            debug(f'Storing register {d} ({R[d]}) in memory {addr}')
        store_memory(addr, R[d])
    if opcode == 'A':
        debug(f'Storing register {d} ({R[d]}) in memory {R[t]} and printing {R[d]}')
        store_register(d, load_memory(R[t]))
    if opcode == 'B':
        if R[t] == 'FF':
            debug(f'Storing register {d} ({R[d]}) in memory {R[t]} and printing {R[d]}')
        else:
            debug(f'Storing register {d} ({R[d]}) in memory {R[t]}')
        store_memory(R[t], R[d])

    if opcode == '0':
        debug('Halting')
        return True
    if opcode == 'C':
        if int(R[d], 16) == 0:
            debug(f'Checked if register {d} ({R[d]}) was equal to zero - it was, so set the PC to {int(addr, 16)}')
            PC = int(addr, 16) - 1
        else:
            debug(f'Checked if register {d} ({R[d]}) was equal to zero - it was not')
    if opcode == 'D':
        if int(R[d], 16) > 0:
            debug(f'Checked if register {d} ({R[d]}) was greater than zero - it was, so set the PC to {int(addr, 16)}')
            PC = int(addr, 16) - 1
        else:
            debug(f'Checked if register {d} ({R[d]}) was greater than zero - it was not')
    if opcode == 'E':
        debug(f'Setting the PC to register {d} ({int(R[d], 16) + 1})')
        PC = int(R[d], 16)
    if opcode == 'F':
        print(f'Storing the PC ({hex(PC)}) in register {d} and setting the PC to {int(addr, 16)}')
        store_register(d, hex(PC))
        PC = int(addr, 16) - 1

    PC += 1
    return False

def hex(i, digits = 2):
    return format(int(i), '0' + str(digits) + 'X')

def load_memory(addr):
    return M[addr[-2:]]

def main():
    global debug_mode

    if len(sys.argv) == 1:
        file_name = input('File name: ')
    elif len(sys.argv) >= 2:
        file_name = sys.argv[1]
        if len(sys.argv) >= 3:
            debug_mode = sys.argv[2] == '1'

    with open(file_name, 'r') as f:
        for line in f:
            if re.match(r'^[0-9A-F]{2}: [0-9A-F]{4}', line):
                M[line[0:2]] = line[4:8]

    while True:
        halt = execute()
        if halt or PC > 255: break

def math_op(d, value):
    if value < -32768 or 32767 < value:
        raise Exception(f'Error at {hex(PC)}: Operation outside the range of -32768 and 32767 ({str(value)})')
    store_register(d, hex(value, 4))

def store_memory(addr, value):
    addr = str(addr).zfill(2)[-2:]
    value = str(value).zfill(4)
    if addr == 'FF':
        print('> ' + value + ',', int(value, 16))
    M[addr] = value

def store_register(addr, value):
    addr = str(addr)[-1:]
    value = str(value).zfill(4)
    if addr == '00':
        raise Exception(f'Error at {hex(PC)}: Register 00 is reserved')
    R[addr] = value

if __name__ == '__main__':
    for i in range(16):
        R[hex(i, 1)] = '0000'
    for i in range(256):
        M[hex(i)] = '0000'

    main()
