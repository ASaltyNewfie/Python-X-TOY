import sys
import re

program_counter = 16
registers = {}
memory = {}
debug_mode = False


def debug(out):
    if debug_mode: print(out)


def execute():
    global program_counter

    instruction = load_memory(convert_to_hex_string(program_counter))

    opcode = instruction[0]
    d = instruction[1]
    s = instruction[2]
    t = instruction[3]
    addr = instruction[2:4]

    a = int(registers[s], 16)
    b = int(registers[t], 16)

    if opcode == '1':
        debug(f'Adding register {s} ({registers[s]}) to register {t} ({registers[t]}) and storing the result in register {d}')
        math_op(d, a + b)
    if opcode == '2':
        debug(f'Subtracting register {t} ({registers[t]}) from register {s} ({registers[s]}) and storing the result in register {d}')
        math_op(d, a - b)
    if opcode == '3':
        debug(f'Performing binary AND on registers {s} and {t} and storing the result in register {d}')
        math_op(d, a & b)
    if opcode == '4':
        debug(f'Performing binary OR on registers {s} and {t} and storing the result in register {d}')
        math_op(d, a ^ b)
    if opcode == '5':
        debug(f'Performing binary left shift on registers {s} by {t} and storing the result in register {d}')
        math_op(d, a << b)
    if opcode == '6':
        debug(f'Performing binary right shift on registers {s} by {t} and storing the result in register {d}')
        math_op(d, a >> b)

    if opcode == '7':
        debug(f'Storing {addr} in register {d}')
        store_register(d, addr)
    if opcode == '8':
        if addr == 'FF':
            debug(f'Storing input in memory {addr}')
            memory[addr] = input(': ')
        debug(f'Storing memory {addr} ({memory[addr]}) in register {d}')
        store_register(d, memory[addr])
    if opcode == '9':
        if addr == 'FF':
            debug(f'Storing register {d} ({registers[d]}) in memory {addr} and printing {registers[d]}')
        else:
            debug(f'Storing register {d} ({registers[d]}) in memory {addr}')
        store_memory(addr, registers[d])
    if opcode == 'A': # Store
        debug(f'Storing register {d} ({registers[d]}) in memory {registers[t]} and printing {registers[d]}')
        store_register(d, load_memory(registers[t]))
    if opcode == 'B':
        if registers[t] == 'FF':
            debug(f'Storing register {d} ({registers[d]}) in memory {registers[t]} and printing {registers[d]}')
        else:
            debug(f'Storing register {d} ({registers[d]}) in memory {registers[t]}')
        store_memory(registers[t], registers[d])

    if opcode == '0':
        debug('Halting')
        return True
    if opcode == 'C':
        if int(registers[d], 16) == 0:
            debug(f'Checked if register {d} ({registers[d]}) was equal to zero - it was, so set the program counter to {int(addr, 16)}')
            program_counter = int(addr, 16) - 1
        else:
            debug(f'Checked if register {d} ({registers[d]}) was equal to zero - it was not')
    if opcode == 'D':
        if int(registers[d], 16) > 0:
            debug(f'Checked if register {d} ({registers[d]}) was greater than zero - it was, so set the program counter to {int(addr, 16)}')
            program_counter = int(addr, 16) - 1
        else:
            debug(f'Checked if register {d} ({registers[d]}) was greater than zero - it was not')
    if opcode == 'E':
        debug(f'Setting the program counter to register {d} ({int(registers[d], 16) + 1})')
        program_counter = int(registers[d], 16)
    if opcode == 'F':
        print(f'Storing the program counter ({convert_to_hex_string(program_counter)}) in register {d} and setting the program counter to {int(addr, 16)}')
        store_register(d, convert_to_hex_string(program_counter))
        program_counter = int(addr, 16) - 1

    program_counter += 1
    return False


def convert_to_hex_string(i, digits = 2):
    return format(int(i), '0' + str(digits) + 'X')


def load_memory(location):
    return memory[location[-2:]]


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
                memory[line[0:2]] = line[4:8]

    while True:
        halt = execute()
        if halt or program_counter > 255: break


def math_op(destination, value):
    if value < -32768 or 32767 < value:
        raise Exception(f'Error at {convert_to_hex_string(program_counter)}: Operation outside the range of -32768 and 32767 ({str(value)})')
    store_register(destination, convert_to_hex_string(value, 4))


def store_memory(address, value):
    addr = str(address).zfill(2)[-2:]
    value = str(value).zfill(4)
    if addr == 'FF':
        print('> ' + value + ',', int(value, 16))
    memory[addr] = value


def store_register(address, value):
    addr = str(address)[-1:]
    value = str(value).zfill(4)
    if addr == '00':
        raise Exception(f'Error at {convert_to_hex_string(program_counter)}: Register 00 is reserved')
    registers[addr] = value


if __name__ == '__main__':
    for i in range(16):
        registers[convert_to_hex_string(i, 1)] = '0000'
    for i in range(256):
        memory[convert_to_hex_string(i)] = '0000'

    main()
